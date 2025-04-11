# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

from invenio_i18n import lazy_gettext as _
from .diff import DiffProcessor
from .events import CurationCommentEventType
from ..proxies import current_curations_service, current_events_service

class CommentProcessor:

    _comment_error = {
                    "field": "custom_fields.rdm-curation",
                    "messages": [
                        _(
                            "Record saved successfully, but failed to update request comment."
                        )
                    ],
                }

    def __init__(self, identity, diff_processor):
        self._identity = identity
        self._diff_processor = diff_processor

    def _validate_request(self, request):
        # sanity check
        return isinstance(request, dict) and request.get("is_open")

    def _is_comment_hit(self, hit):
        return hit.get("type") == "C" and hit.get("created_by").get("user") == "system"

    def _create_new_comment(self, request, content, base_content_object):
        payload = {
            "payload": {
                "content": content,
                "base_content_object": base_content_object
            }
        }

        try:
            current_events_service.create(self._identity, request["id"], payload, CurationCommentEventType())
        except Exception as e:
            return self._comment_error

    def _update_existing_comment(self, new_data, base_content_object, crt_comment_event):
        if crt_comment_event is None:
            return self._comment_error

        payload = {
            "payload": {
                "content": new_data,
                "base_content_object": base_content_object
            }
        }

        try:
            current_events_service.update(self._identity, crt_comment_event.get("id"), payload, revision_id=crt_comment_event.get("revision_id"))
        except Exception as e:
            return self._comment_error

    def process_comment(self, request, errors):
        if not self._validate_request(request):
            errors.append(self._comment_error)
            return

        try:
            if request["status"] == "resubmitted":
                # if the user resubmits the record for review, we should add a comment that describes
                # what was changed from the previous attempt (creation/other resubmission)
                last_request_log_event = None
                last_created_comment = None
                for hit in list(current_events_service.search(self._identity, request["id"]).hits):
                    if self._is_comment_hit(hit):
                        # saved record while critiqued, store this
                        last_created_comment = hit
                        continue

                    if hit.get("type") == "L" :
                        last_request_log_event = hit.get("payload").get("event")

                if (last_request_log_event in ["resubmitted", "critiqued"] and
                        last_created_comment is None):
                    # happy path: critiqued - resubmitted, no intermediate saves
                    errors.append(
                        self._create_new_comment(
                            request,
                            self._diff_processor.to_html("resubmit"),
                            self._diff_processor.get_base_content_object()
                        ))
                else:
                    # if there were draft saves between critiqued - in review, be sure to capture
                    # the diff between these 2 statuses, not between draft saves.
                    last_diff = DiffProcessor(
                        configured_elements=current_curations_service.comments_mapping).from_base_content_object(
                        last_created_comment.get("payload").get("base_content_object")
                    )
                    errors.append(
                        self._update_existing_comment(
                            self._diff_processor.compare(last_diff).to_html("resubmit"),
                            self._diff_processor.get_base_content_object(),
                            last_created_comment
                        ))

            elif request["status"] == "critiqued" and len(self._diff_processor.get_diffs()) > 0:
                # update draft while critiqued without resubmitting immediately, create comment and
                # then update the same comment if new updates of this sort come
                last_event = list(current_events_service.search(self._identity, request["id"]).hits)[-1]

                if last_event.get("type") == "L":
                    errors.append(
                        self._create_new_comment(
                            request,
                            self._diff_processor.to_html("update_while_critiqued"),
                            self._diff_processor.get_base_content_object()
                        )
                    )

                elif self._is_comment_hit(last_event):
                    last_diff = DiffProcessor(
                        configured_elements=current_curations_service.comments_mapping).from_base_content_object(
                        last_event.get("payload").get("base_content_object")
                    )
                    errors.append(
                        self._update_existing_comment(
                            self._diff_processor.compare(last_diff).to_html("update_while_critiqued"),
                            self._diff_processor.get_base_content_object(),
                            last_event
                        )
                    )

            elif request["status"] == "review":
                # on review status, just create comments with new diffs, hopefully to notify the curator more easily
                errors.append(
                    self._create_new_comment(
                        request,
                        self._diff_processor.to_html("update_while_review"),
                        self._diff_processor.get_base_content_object()
                    )
                )

        except Exception as e:
            # fail-safe in case of any unexpected error
            # TODO improve error handling in this workflow
            errors.append(self._comment_error)
