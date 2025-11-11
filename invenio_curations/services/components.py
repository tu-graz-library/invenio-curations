# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
# Copyright (C) 2024 TU Wien.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Component for checking curations."""

from abc import ABC
from typing import Any, cast

import dictdiffer
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_pidstore.models import PIDStatus
from invenio_rdm_records.records.api import RDMDraft, RDMRecord
from invenio_requests.proxies import current_requests_service
from invenio_requests.services import RequestsService

from ..proxies import current_curations_service
from . import CurationRequestService
from .comment import CommentProcessor
from .diff import DiffProcessor
from .errors import CurationRequestNotAcceptedError
from .utils import is_identity_privileged


def _get_curations_service() -> CurationRequestService:
    return cast(CurationRequestService, current_curations_service)


def _get_requests_service() -> RequestsService:
    return cast(RequestsService, current_requests_service)


def _skip_curations_flow(privileged_roles: list[str], identity: Identity) -> bool:
    """Admins and system can bypass curations workflow.

    Check for actual user roles because identity can be incomplete
    (e.g. see https://github.com/inveniosoftware/invenio-rdm-records/blob/7c47cdcb133b3b88228d5157687514f0ec7eecc4/invenio_rdm_records/fixtures/tasks.py#L41)
    """
    if identity == system_identity:
        return True

    return is_identity_privileged(privileged_roles, identity)


class CurationComponent(ServiceComponent, ABC):
    """Service component for access integration."""

    def publish(
        self,
        identity: Identity,
        draft: RDMDraft | None = None,
        record: RDMRecord | None = None,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Check if record curation request has been accepted."""
        # The `PIDComponent` takes care of calling `record.register()` which sets the
        # status for `record.pid.status` to "R", but the draft's dictionary data
        # only gets updated via `record.commit()` (which is performed by the `uow`).
        # Thus, if we spot a discrepancy here we can deduce that this is the first time
        # the record gets published.
        if draft is None:
            msg = "Unexpected publish action with undefined draft."
            raise RuntimeError(msg)

        if _skip_curations_flow(_get_curations_service().privileged_roles, identity):
            # configured roles can publish without curation workflow
            return

        has_been_published = (
            draft.pid.status == draft["pid"]["status"] == PIDStatus.REGISTERED
        )
        if has_been_published and _get_curations_service().allow_publishing_edits:
            return

        review_accepted = _get_curations_service().accepted_record(
            system_identity,
            draft,
        )

        if not review_accepted:
            raise CurationRequestNotAcceptedError

    def delete_draft(
        self,
        identity: Identity,  # noqa: ARG002
        draft: RDMDraft | None = None,
        record: RDMRecord | None = None,
        *,
        force: bool = False,  # noqa: ARG002
    ) -> None:
        """Delete a draft."""
        request = _get_curations_service().get_review(
            system_identity,
            draft,
            expand=True,
        )

        # No open request. Nothing to do.
        if request is None:
            return

        # New record or new version -> request can be removed.
        if record is None:
            _get_requests_service().delete(system_identity, request["id"], uow=self.uow)
            return

        # Delete draft for a published record.
        # Since only one request per record should exist, it is not deleted. Instead, put it back to accepted.
        _get_requests_service().execute_action(
            system_identity,
            request["id"],
            "cancel",
            uow=self.uow,
        )

    def _check_update_request(
        self,
        identity: Identity,  # noqa: ARG002
        request: dict,
        data: dict | None = None,
        record: RDMDraft | None = None,
        errors: list[dict] | None = None,  # noqa: ARG002
    ) -> None:
        """Update request title if record title has changed."""
        updated_draft_title = (data or {}).get("metadata", {}).get("title")
        current_draft_title = (record or {}).get("metadata", {}).get("title")

        if current_draft_title != updated_draft_title:
            title = updated_draft_title or record["id"]  # type: ignore[index]
            request["title"] = f"RDM Curation: {title}"

            # Using system identity, to not have to update the default request can_update permission.
            # Data will be checked in the requests service.
            _get_requests_service().update(
                system_identity,
                request["id"],
                request,
                uow=self.uow,
            )

    def _prepare_data(
        self,
        data: dict,
        current_draft: RDMDraft,
    ) -> tuple[dict, dict]:
        """Build and return fresh new maps only with fields that should be compared later in the process.

        Method used in context of comment processing.
        """
        supported_fields = ["metadata", "custom_fields"]
        new_data = {}
        new_crt_draft = {}
        for field in supported_fields:
            new_data[field] = data[field]
            new_crt_draft[field] = current_draft[field]

        return new_data, new_crt_draft

    def _process_comment(
        self,
        data: dict,
        current_draft: RDMDraft,
        request: dict,
        errors: list[dict] | None,
    ) -> None:
        """Prepare and call all needed structures in order to successfully create/update a request comment."""
        prepared_data, prepared_current_draft = self._prepare_data(data, current_draft)

        diff_processor = DiffProcessor(
            configured_elements=current_curations_service.comments_mapping,
            comment_template_file=current_curations_service.comment_template_file,
        )
        comment_processor = CommentProcessor(system_identity, diff_processor)

        comment_processor.process_comment(
            request,
            prepared_data,
            prepared_current_draft,
            errors,
        )

    def update_draft(
        self,
        identity: Identity,
        data: dict | None = None,
        record: RDMDraft | None = None,
        errors: list[dict] | None = None,
    ) -> None:
        """Update draft handler."""
        has_published_record = record is not None and record.is_published
        if has_published_record and _get_curations_service().allow_publishing_edits:
            return

        if _skip_curations_flow(_get_curations_service().privileged_roles, identity):
            return

        request = _get_curations_service().get_review(
            system_identity,
            record,
            expand=True,
        )

        if not request:
            return

        current_draft: RDMDraft = self.service.draft_cls.pid.resolve(
            record["id"],  # type: ignore[index]
            registered_only=False,
        )

        self._check_update_request(
            identity,
            request,
            data=data,
            record=current_draft,
            errors=errors,
        )

        # TODO: Should updates be disallowed if the record/request is currently being reviewed?
        # It could be possible that the record gets updated while a curator performs a review. The curator would be looking at an outdated record and the review might not be correct.

        # If a request is open, it still has to be reviewed eventually.
        if request["is_open"]:
            if current_curations_service.comments_enabled:
                # prepare and process a comment if config is enabled
                self._process_comment(data, current_draft, request, errors)  # type: ignore[arg-type]
            return

            # Compare metadata of current draft and updated draft.

        # Sometimes the metadata differs between the passed `record` and resolved
        # `current_draft` in references (e.g. in the `record` object, the creator's
        # affiliation has an ID & name, but in the `current_draft` it's only the ID)
        # this discrepancy can be removed by resolving or cleaning the relations
        current_draft.relations.clean()
        record.relations.clean()  # type: ignore[union-attr]

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
                pid=record.pid,  # type: ignore[union-attr]
                record=record,
            ),
        )
        # TODO: File updates are not picked up. File actions are handled in dedicated files service.
        #       Files service is not configurable per default and we can not add a component there.
        diff = dictdiffer.diff(current_data, updated_data)
        diff_list = list(diff)

        # Request is closed but draft was updated with new data. Flag that as a pending resubmission.
        if diff_list and request["status"] != "pending_resubmission":
            _get_requests_service().execute_action(
                identity,
                request["id"],
                "pending_resubmission",
                uow=self.uow,
            )
