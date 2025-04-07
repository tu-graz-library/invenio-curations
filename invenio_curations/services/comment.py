# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module for request comments handling."""

import ast
from typing import Any, Final, cast

import dictdiffer
from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_requests.proxies import current_events_service

from .diff import DIFF_TYPE, DiffProcessorBase
from .events import CurationCommentEventType


class CurationCommentError(Exception):
    """Custom exception for comment exceptions."""


class CommentProcessor:
    """Class for creating and updating curation request comments."""

    _comment_error: Final[dict] = {
        "field": "custom_fields.rdm-curation",
        "messages": [
            _("Record saved successfully, but failed to update request comment."),
        ],
    }

    def __init__(self, identity: Any, diff_processor: DiffProcessorBase) -> None:
        """Constructs."""
        self._identity = identity
        self._diff_processor = diff_processor

    def _validate_request(self, request: dict) -> bool:
        """Sanity check."""
        return request.get("is_open")  # type: ignore[return-value]

    def _is_comment_hit_created_by_curations_comment_processor(
        self,
        hit: dict,
    ) -> bool:
        """Check if a comment was automatically created by this processor."""
        type_ = hit.get("type")
        payload = hit.get("payload")
        return bool(type_ and payload and type_ == "C" and "reference_draft" in payload)

    def _cleanup_other_comments(
        self,
        events: list[dict],
    ) -> list[dict]:
        """Filter all comments created by users or by system but are not created by this processor."""
        return [
            hit
            for hit in events
            if self._is_comment_hit_created_by_curations_comment_processor(
                hit,
            )
        ]

    def _get_current_diffs(
        self,
        base_data: dict,
        new_data: dict,
    ) -> list[DIFF_TYPE] | None:
        """Return the diffs between old and new data.

        :param base_data: The data to compare against.
        :param new_data: New data.

        :returns: A list of dictdiffer.diff-style tuples.
        """
        diffs = dictdiffer.diff(base_data, new_data)
        diff_list = cast(list[DIFF_TYPE], list(diffs))

        if not diff_list:
            return None

        return diff_list

    def _create_new_comment(
        self,
        request: dict,
        content: str,
        reference_draft: str | None,
    ) -> None:
        """Build and send comment create event.

        :param request: The curation request.
        :param content: The actual comment.
        :param reference_draft: The draft to store for future updates.
        """
        payload = {"payload": {"content": content}}

        if reference_draft is not None:
            payload["payload"]["reference_draft"] = reference_draft

        try:
            current_events_service.create(
                self._identity,
                request["id"],
                payload,
                CurationCommentEventType(),
            )
        except Exception as e:  # noqa: BLE001
            # TODO: revise the exception handling for comment feature
            current_app.logger.warning(e, exc_info=True)

    def _update_existing_comment(
        self,
        new_data: str,
        crt_comment_event: dict,
    ) -> None:
        """Build and send comment update event.

        :param new_data: The updated comment.
        :param crt_comment_event: The existing comment.
        """
        if crt_comment_event is None:
            raise CurationCommentError

        payload = {"payload": {"content": new_data}}

        try:
            current_events_service.update(
                self._identity,
                crt_comment_event.get("id"),
                payload,
                revision_id=crt_comment_event.get("revision_id"),
            )
        except Exception as e:  # noqa: BLE001
            # TODO: revise the exception handling for comment feature
            current_app.logger.warning(e, exc_info=True)

    def _handle_critiqued_resubmit_status(
        self,
        request: dict,
        current_draft: dict,
        new_data: dict,
        msg: str,
        errors: list[dict] | None,
    ) -> None:
        """Handle the draft save when request is in status critiqued or resubmitted.

         Flow:
            Update draft while critiqued without resubmitting immediately: create
            comment and then update the same comment if new updates of this sort come.
         OR
             Update draft while request is in resubmitted status. The same principle
             applies: each time update the last comment or create a new one if none
             is found.

        :param request: The curation request.
        :param current_draft: The state of the draft used to compare against to get the changes.
        :param new_data: Latest state of the record.
        :param msg: Flag to differentiate between request states.
        :param errors: Add to errors list to display a message if something bad happens.
        """
        last_event = list(
            current_events_service.search(self._identity, request["id"]).hits,
        )[-1]

        # if last event is an action OR a comment created manually by the user
        if last_event.get(
            "type",
        ) == "L" or not self._is_comment_hit_created_by_curations_comment_processor(
            last_event,
        ):
            self._create_comment_with_latest_changes(
                request,
                current_draft,
                new_data,
                msg,
                errors,
            )
        # if last event is a comment generated by this processor
        elif self._is_comment_hit_created_by_curations_comment_processor(last_event):
            self._compute_diff_and_update_event(last_event, new_data, msg, errors)

    def _compute_diff_and_update_event(
        self,
        event: dict,
        new_data: dict,
        msg: str,
        errors: list[dict] | None,  # noqa: ARG002
    ) -> None:
        """Compute diff between 2 draft states and update the comment with the result.

        :param event: The comment event to update.
        :param new_data: Latest state of the record.
        :param msg: Flag to differentiate between request states.
        :param errors: Add to errors list to display a message if something bad happens.
        """
        payload = event.get("payload")
        if payload is None:
            msg = "Got empty payload from event"
            raise CurationCommentError(msg)

        ref_draft = payload.get("reference_draft")
        if ref_draft is None:
            msg = "Got emtpy reference draft flag from event payload"
            raise CurationCommentError(msg)

        base_draft = ast.literal_eval(ref_draft)
        diffs = self._get_current_diffs(base_draft, new_data)
        if diffs is None:
            return
        self._diff_processor.map_and_build_diffs(diffs)

        self._update_existing_comment(
            self._diff_processor.to_html(msg),
            event,
        )

    def _create_comment_with_latest_changes(
        self,
        request: dict,
        current_draft: dict,
        new_data: dict,
        msg: str,
        errors: list[dict] | None,  # noqa: ARG002
        reference_draft: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        """Compute diff between 2 draft states and create comment with the result.

        :param request: The curation request.
        :param current_draft: The state of the draft used to compare against to get the changes.
        :param new_data: Latest state of the record.
        :param msg: Flag to differentiate between request states.
        :param errors: Add to errors list to display a message if something bad happens.
        :param reference_draft: Flag that can be unset to omit the storing of a reference draft.
        """
        diffs = self._get_current_diffs(current_draft, new_data)
        if diffs is None:
            return
        self._diff_processor.map_and_build_diffs(diffs)

        self._create_new_comment(
            request,
            self._diff_processor.to_html(msg),
            str(current_draft) if reference_draft else None,
        )

    def process_comment(
        self,
        request: dict,
        new_data: dict,
        current_draft: dict,
        errors: list[dict] | None,
    ) -> None:
        """Dispatch the handling of request comments based on request status.

        :param request: The curation request.
        :param new_data: Latest state of the record.
        :param current_draft: The state of the draft used to compare against to get the changes.
        :param errors: Add to errors list to display a message if something bad happens.
        """
        if not self._validate_request(request):
            errors.append(self._comment_error)  # type: ignore[union-attr]
            return

        try:
            if request["status"] == "resubmitted":
                self._handle_critiqued_resubmit_status(
                    request,
                    current_draft,
                    new_data,
                    "resubmit",
                    errors,
                )

            elif request["status"] == "critiqued":
                self._handle_critiqued_resubmit_status(
                    request,
                    current_draft,
                    new_data,
                    "update_while_critiqued",
                    errors,
                )

            elif request["status"] == "review":
                # on review status, just create comments with new diffs, hopefully to notify the curator more easily
                self._create_comment_with_latest_changes(
                    request,
                    current_draft,
                    new_data,
                    "update_while_review",
                    errors,
                    reference_draft=False,
                )

        except Exception as e:  # noqa: BLE001
            # fail-safe in case of any unexpected error
            # TODO: improve error handling in this workflow
            current_app.logger.warning(e, exc_info=True)
