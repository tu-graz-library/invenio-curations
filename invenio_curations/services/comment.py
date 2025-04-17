# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Module for request comments handling."""

import ast
from traceback import print_exception

import dictdiffer
from flask import current_app
from invenio_i18n import lazy_gettext as _
from invenio_requests.proxies import current_events_service

from .events import CurationCommentEventType


class CommentProcessor:
    """Class for creating and updating curation request comments."""

    _comment_error = {
        "field": "custom_fields.rdm-curation",
        "messages": [
            _("Record saved successfully, but failed to update request comment.")
        ],
    }

    def __init__(self, identity, diff_processor):
        """Constructs."""
        self._identity = identity
        self._diff_processor = diff_processor

    def _validate_request(self, request):
        """Sanity check."""
        return isinstance(request, dict) and request.get("is_open")

    def _is_comment_hit(self, hit):
        """Check if a comment was automatically created by this processor."""
        return hit.get("type") == "C" and hit.get("created_by").get("user") == "system"

    def _get_current_diffs(self, base_data, new_data):
        """Return the diffs between old and new data.

        :param base_data: The data to compare against.
        :type base_data: dict

        :param new_data: New data.
        :type new_data: dict

        :returns: A list of dictdiffer.diff-style tuples.
        :rtype: list
        """
        diffs = dictdiffer.diff(base_data, new_data)
        diff_list = list(diffs)

        if not diff_list:
            return None

        return diff_list

    def _create_new_comment(self, request, content, reference_draft):
        """Build and send comment create event.

        :param request: The curation request.
        :type request: dict

        :param content: The actual comment.
        :type content: str

        :param reference_draft: The draft to store for future updates.
        :type reference_draft: str
        """
        payload = {"payload": {"content": content}}

        if reference_draft is not None:
            payload["payload"]["reference_draft"] = reference_draft

        try:
            current_events_service.create(
                self._identity, request["id"], payload, CurationCommentEventType()
            )
        except Exception as e:
            current_app.logger.warning(e)
            return self._comment_error

    def _update_existing_comment(self, new_data, crt_comment_event):
        """Build and send comment update event.

        :param new_data: The updated comment.
        :type new_data: str

        :param crt_comment_event: The existing comment.
        :type crt_comment_event: dict
        """
        if crt_comment_event is None:
            return self._comment_error

        payload = {"payload": {"content": new_data}}

        try:
            current_events_service.update(
                self._identity,
                crt_comment_event.get("id"),
                payload,
                revision_id=crt_comment_event.get("revision_id"),
            )
        except Exception as e:
            current_app.logger.warning(e)
            return self._comment_error

    def _handle_critiqued_resubmit_status(
        self, request, current_draft, new_data, msg, errors
    ):
        """Handle the draft save when request is in status critiqued or resubmitted.

         Flow:
            Update draft while critiqued without resubmitting immediately: create
          comment and then update the same comment if new updates of this sort come.
         OR
             Update draft while request is in resubmitted status. The same principle
          applies: each time update the last comment or create a new one if none
          is found.

        :param request: The curation request.
        :type request: dict

        :param current_draft: The state of the draft used to compare against to get the changes.
        :type current_draft: dict

        :param new_data: Latest state of the record.
        :type new_data: dict

        :param msg: Flag to differentiate between request states.
        :type msg: str

        :param errors: Add to errors list to display a message if something bad happens.
        :type errors: list
        """
        last_event = list(
            current_events_service.search(self._identity, request["id"]).hits
        )[-1]

        if last_event.get("type") == "L":
            self._create_comment_with_latest_changes(
                request, current_draft, new_data, msg, errors
            )

        elif self._is_comment_hit(last_event):
            self._compute_diff_and_update_event(last_event, new_data, msg, errors)

    def _compute_diff_and_update_event(self, event, new_data, msg, errors):
        """Compute diff between 2 draft states and update the comment with the result.

        :param event: The comment event to update.
        :type event: dict

        :param new_data: Latest state of the record.
        :type new_data: dict

        :param msg: Flag to differentiate between request states.
        :type msg: str

        :param errors: Add to errors list to display a message if something bad happens.
        :type errors: list
        """
        base_draft = ast.literal_eval(event.get("payload").get("reference_draft"))
        diffs = self._get_current_diffs(base_draft, new_data)
        if diffs is None:
            return
        self._diff_processor.map_and_build_diffs(diffs)

        self._update_existing_comment(
            self._diff_processor.to_html(msg),
            event,
        )

    def _create_comment_with_latest_changes(
        self, request, current_draft, new_data, msg, errors, reference_draft=True
    ):
        """Compute diff between 2 draft states and create comment with the result.

        :param request: The curation request.
        :type request: dict

        :param current_draft: The state of the draft used to compare against to get the changes.
        :type current_draft: dict

        :param new_data: Latest state of the record.
        :type new_data: dict

        :param msg: Flag to differentiate between request states.
        :type msg: str

        :param errors: Add to errors list to display a message if something bad happens.
        :type errors: list

        :param reference_draft: Flag that can be unset to omit the storing of a reference draft.
        :type reference_draft: bool
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

    def process_comment(self, request, new_data, current_draft, errors):
        """Dispatch the handling of request comments based on request status.

        :param request: The curation request.
        :type request: dict

        :param new_data: Latest state of the record.
        :type new_data: dict

        :param current_draft: The state of the draft used to compare against to get the changes.
        :type current_draft: dict

        :param errors: Add to errors list to display a message if something bad happens.
        :type errors: list
        """
        if not self._validate_request(request):
            errors.append(self._comment_error)
            return

        try:
            if request["status"] == "resubmitted":
                self._handle_critiqued_resubmit_status(
                    request, current_draft, new_data, "resubmit", errors
                )

            elif request["status"] == "critiqued":
                self._handle_critiqued_resubmit_status(
                    request, current_draft, new_data, "update_while_critiqued", errors
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

        except Exception as e:
            # fail-safe in case of any unexpected error
            # TODO improve error handling in this workflow
            current_app.logger.warning(e)
            errors.append(self._comment_error)
