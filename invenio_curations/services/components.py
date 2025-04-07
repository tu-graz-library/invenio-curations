# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
# Copyright (C) 2024 TU Wien.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Component for checking curations."""

from abc import ABC
from threading import Thread
from time import sleep

import dictdiffer
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PIDStatus
from invenio_requests.customizations import CommentEventType
from invenio_requests.proxies import current_requests_service, current_events_service

from ..proxies import current_curations_service
from .errors import CurationRequestNotAccepted


# TODO
class DiffProcessor:
    """
    DiffProcessor class.
    """
    _diffs = None

    def __init__(self, diffs):
        self._diffs = diffs

    def from_html(self, html):
        pass

    def from_invenio_diff_list(self, diff_list):
        pass

    def to_html(self):
        pass


class CurationComponent(ServiceComponent, ABC):
    """Service component for access integration."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Check if record curation request has been accepted."""
        # The `PIDComponent` takes care of calling `record.register()` which sets the
        # status for `record.pid.status` to "R", but the draft's dictionary data
        # only gets updated via `record.commit()` (which is performed by the `uow`).
        # Thus, if we spot a discrepancy here we can deduce that this is the first time
        # the record gets published.
        has_been_published = (
                draft.pid.status == draft["pid"]["status"] == PIDStatus.REGISTERED
        )
        if has_been_published and current_curations_service.allow_publishing_edits:
            return

        review_accepted = current_curations_service.accepted_record(
            system_identity,
            draft,
        )

        if not review_accepted:
            raise CurationRequestNotAccepted()

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        request = current_curations_service.get_review(
            system_identity,
            draft,
            expand=True,
        )

        # No open request. Nothing to do.
        if request is None:
            return

        # New record or new version -> request can be removed.
        if record is None:
            current_requests_service.delete(
                system_identity, request["id"], uow=self.uow
            )
            return

        # Delete draft for a published record.
        # Since only one request per record should exist, it is not deleted. Instead, put it back to accepted.
        current_requests_service.execute_action(
            system_identity, request["id"], "cancel", uow=self.uow
        )

    def _check_update_request(
            self, identity, request, data=None, record=None, errors=None
    ):
        """Update request title if record title has changed."""
        updated_draft_title = (data or {}).get("metadata", {}).get("title")
        current_draft_title = (record or {}).get("metadata", {}).get("title")
        if current_draft_title != updated_draft_title:
            request["title"] = "RDM Curation: {title}".format(
                title=updated_draft_title or record["id"]
            )
            # Using system identity, to not have to update the default request can_update permission.
            # Data will be checked in the requests service.
            current_requests_service.update(
                system_identity, request["id"], request, uow=self.uow
            )

    def _pretty_html_diff_view(self, diffs):
        return "<p> test edi </>"

    def _diff_crt_comment_new_diffs(self, crt_comment, new_diffs):
        return "<p> updated changes <p>"

    def _build_and_send_comment(self, request, content, update=False, crt_comment_event=None):
        if update and crt_comment_event is None:
            # TODO add error
            return

        if update:
            content = self._diff_crt_comment_new_diffs(crt_comment_event.get("payload").get("content"), content)
        payload = {
            "payload": {
                "content": content
            }
        }

        if update:
            current_events_service.update(system_identity, crt_comment_event.get("id"), payload,
                                          revision_id=crt_comment_event.get("revision_id"))
        else:
            current_events_service.create(system_identity, request["id"], payload, CommentEventType())

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        has_published_record = record is not None and record.is_published
        if has_published_record and current_curations_service.allow_publishing_edits:
            return

        request = current_curations_service.get_review(
            system_identity,
            record,
            expand=True,
        )

        # Inform user to create a curation request
        if not request:
            errors.append(
                {
                    "field": "custom_fields.rdm-curation",
                    "messages": [
                        _(
                            "Missing curation request. Please create a curation request, if the record is ready to be published."
                        )
                    ],
                }
            )
            return

        current_draft = self.service.draft_cls.pid.resolve(
            record["id"], registered_only=False
        )

        self._check_update_request(
            identity, request, data=data, record=current_draft, errors=errors
        )

        diff = dictdiffer.diff(current_draft, data)
        diff_list = list(diff)
        diff_processor = DiffProcessor(diff_list)

        # TODO: Should updates be disallowed if the record/request is currently being reviewed?
        # It could be possible that the record gets updated while a curator performs a review. The curator would be looking at an outdated record and the review might not be correct.

        # If a request is open, it still has to be reviewed eventually.

        if request["is_open"] and request["status"] == "resubmitted":
            # if the user resubmits the record for review, we should add a comment that describes
            # what was changed from the previous attempt (creation/other resubmission)

            # TODO add extra comment validation for auto-generated
            last_request_log_event = None
            crt_critiqued = False
            last_critiqued_comment_event = None
            for hit in list(current_events_service.search(system_identity, request["id"]).hits)[:-1]:
                if crt_critiqued and hit.get("type") == "C":
                    # saved record while critiqued, store this
                    last_critiqued_comment_event = hit
                    continue

                if hit.get("type") == "L":
                    last_request_log_event = hit.get("payload").get("event")

                if last_request_log_event == "critiqued":
                    crt_critiqued = True
                else:
                    crt_critiqued = False

            if last_request_log_event in ["resubmitted", "critiqued"] and not last_critiqued_comment_event:
                # user updates the draft while in resubmission, comment every change detected.
                # OR happy path: critiqued - resubmitted, no intermediate saves
                self._build_and_send_comment(request, self._pretty_html_diff_view(diff_list))
            else:
                # if there were draft saves between critiqued - resubmitted, be sure to capture
                # the diff between these 2 statuses, not between draft saves.
                self._build_and_send_comment(
                    request,
                    diff_list,
                    update=True,
                    crt_comment_event=last_critiqued_comment_event)

            return

        elif request["is_open"] and request["status"] == "critiqued":
            return
        elif request["is_open"]:
            return

        # Compare metadata of current draft and updated draft.

        # Sometimes the metadata differs between the passed `record` and resolved
        # `current_draft` in references (e.g. in the `record` object, the creator's
        # affiliation has an ID & name, but in the `current_draft` it's only the ID)
        # this discrepancy can be removed by resolving or cleaning the relations
        current_draft.relations.clean()
        record.relations.clean()

        current_data = self.service.schema.dump(
            current_draft,
            context=dict(
                identity=identity,
                pid=current_draft.pid,
                record=current_draft,
            ),
        )
        # Load updated data with service schema
        updated_data = self.service.schema.dump(
            record,
            context=dict(
                identity=identity,
                pid=record.pid,
                record=record,
            ),
        )
        # TODO: File updates are not picked up. File actions are handled in dedicated files service.
        #       Files service is not configurable per default and we can not add a component there.
        diff = dictdiffer.diff(current_data, updated_data)
        diff_list = list(diff)

        # Request is closed but draft was updated with new data. Put back for review
        if diff_list:
            current_requests_service.execute_action(
                identity, request["id"], "resubmit", uow=self.uow
            )
