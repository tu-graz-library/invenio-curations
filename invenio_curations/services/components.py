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

import dictdiffer
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PIDStatus
from invenio_requests.proxies import current_requests_service

from ..proxies import current_curations_service
from .errors import CurationRequestNotAccepted


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

        # TODO: Should updates be disallowed if the record/request is currently being reviewed?
        # It could be possible that the record gets updated while a curator performs a review. The curator would be looking at an outdated record and the review might not be correct.

        # If a request is open, it still has to be reviewed eventually.
        if request["is_open"]:
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
