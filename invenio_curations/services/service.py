# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curation service."""

from typing import Any, cast

from flask import current_app
from flask_principal import Identity
from flask_security import SQLAlchemyUserDatastore
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_accounts.proxies import current_datastore
from invenio_db.uow import UnitOfWork
from invenio_i18n import gettext as _
from invenio_rdm_records.records.api import RDMDraft
from invenio_records_resources.services.records.results import RecordItem, RecordList
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.customizations.request_types import RequestType
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.registry import TypeRegistry
from invenio_requests.services import RequestsService
from invenio_requests.services.results import ResolverRegistry
from invenio_search.engine import dsl
from werkzeug.datastructures import ImmutableMultiDict

from ..proxies import unproxy
from ..requests import CurationRequest
from .diff import DiffElement
from .errors import OpenRecordCurationRequestAlreadyExistsError, RoleNotFoundError
from .utils import is_identity_privileged


class CurationRequestService:
    """Service for User Moderation requests."""

    _request_type_registry: TypeRegistry = unproxy(current_request_type_registry)
    _datastore: SQLAlchemyUserDatastore = unproxy(current_datastore)

    def __init__(self, requests_service: RequestsService, **__: Any) -> None:
        """Service initialisation as a sub-service of requests."""
        self.requests_service = requests_service

    @property
    def allow_publishing_edits(self) -> bool:
        """Get the configured value of ``CURATIONS_ALLOW_PUBLISHING_EDITS``."""
        return cast(
            bool,
            current_app.config.get("CURATIONS_ALLOW_PUBLISHING_EDITS", False),
        )

    @property
    def moderation_role_name(self) -> str:
        """Get the configured name of the ``CURATIONS_MODERATION_ROLE``."""
        role = current_app.config["CURATIONS_MODERATION_ROLE"]

        if isinstance(role, Role):
            # As of InvenioRDM v12, the role's name and ID should be the same anyway
            name: str = role.name or role.id
            return name

        # If it's not a role, we assume it's a string
        return cast(str, role)

    @property
    def moderation_role(self) -> str:
        """Get the configured ``CURATIONS_MODERATION_ROLE`` role."""
        return cast(str, self._datastore.find_role(self.moderation_role_name))

    @property
    def request_type_cls(self) -> type[RequestType]:
        """Curation request type."""
        return cast(
            type[RequestType],
            self._request_type_registry.lookup(CurationRequest.type_id),
        )

    @property
    def comments_enabled(self) -> bool:
        """Get the configured value of ``CURATIONS_ENABLE_REQUEST_COMMENTS``."""
        return cast(
            bool,
            current_app.config.get("CURATIONS_ENABLE_REQUEST_COMMENTS", False),
        )

    @property
    def comments_mapping(self) -> list[DiffElement]:
        """Curations specific comment classes."""
        return cast(
            list[DiffElement],
            current_app.config.get("CURATIONS_COMMENTS_CLASSES"),
        )

    @property
    def comment_template_file(self) -> str:
        """Curations specific comment html template."""
        return cast(str, current_app.config.get("CURATIONS_COMMENT_TEMPLATE_FILE"))

    @property
    def privileged_roles(self) -> list[str]:
        """Curations roles that can bypass the curation approvals."""
        return cast(list[str], current_app.config.get("CURATIONS_PRIVILEGED_ROLES"))

    def get_review(
        self,
        identity: Identity,
        topic: RDMDraft,
        **kwargs: Any,
    ) -> dict[str, Any] | None:
        """Get the curation review for a topic."""
        topic_reference: dict = ResolverRegistry.reference_entity(topic)
        # Assume there is only one item in the reference dict
        topic_key, topic_value = next(iter(topic_reference.items()))

        results: RecordList = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    dsl.Q("term", **{f"topic.{topic_key}": topic_value}),
                ],
            ),
            **kwargs,
        )

        if results.total == 0:
            return None

        return cast(dict[str, Any], next(results.hits))

    def accepted_record(
        self,
        identity: Identity,
        record: RDMDraft,
    ) -> dict[str, Any] | None:
        """Check if current version of record has been accepted."""
        topic_reference = ResolverRegistry.reference_entity(record)
        # Assume there is only one item in the reference dict
        topic_key, topic_value = next(iter(topic_reference.items()))

        results: RecordList = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    dsl.Q("term", **{f"topic.{topic_key}": topic_value}),
                    dsl.Q("term", **{"is_open": False}),
                    dsl.Q("term", **{"status": "accepted"}),
                ],
            ),
        )
        return next(results.hits) if results.total > 0 else None

    @unit_of_work()
    def create(
        self,
        identity: Identity,
        data: dict[str, Any] | None = None,
        uow: UnitOfWork | None = None,
        **kwargs: Any,
    ) -> RecordItem:
        """Create a RDMCuration request and submit it."""
        role = self.moderation_role
        if not role:
            raise RoleNotFoundError(self.moderation_role_name)
        assert role, _(
            "Curation request moderation role must exist to enable record curation requests.",
        )

        # Allowed entities for the request type will be checked in the request service
        topic = ResolverRegistry.resolve_entity_proxy(data.pop("topic", None)).resolve()  # type: ignore[union-attr]
        creator = (
            ResolverRegistry.resolve_entity_proxy(data.pop("created_by")).resolve()  # type: ignore[union-attr]
            if "created_by" in data  # type: ignore[operator]
            else None
        )

        receiver = (
            ResolverRegistry.resolve_entity_proxy(data.pop("receiver", None)).resolve()  # type: ignore[union-attr]
            if "receiver" in data  # type: ignore[operator]
            else role
        )

        default_data = {
            "title": "RDM Curation: {title}".format(
                title=topic.metadata.get("title", topic["id"]),
            ),
        }

        # using system identity to ensure a request is fetched, if it exists. Even if the user would not have access.
        if self.get_review(system_identity, topic):
            raise OpenRecordCurationRequestAlreadyExistsError

        if data:
            default_data.update(data)

        return self.requests_service.create(
            identity,
            default_data,
            self.request_type_cls,
            receiver,
            creator=creator,
            topic=topic,
            uow=uow,
            **kwargs,
        )

    def search(
        self,
        identity: Identity,
        params: ImmutableMultiDict | None = None,
        search_preference: str | None = None,
        *,
        expand: bool = False,
        **kwargs: Any,
    ) -> RecordList:
        """Search for curation requests."""
        return self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                ],
            ),
            params=params,
            search_preference=search_preference,
            expand=expand,
            **kwargs,
        )

    def get_publishing_data(
        self,
        identity: Identity,
        **kwargs: Any,  # noqa: ARG002
    ) -> dict:
        """Get the necessary info to determine some curation UI states."""
        return {
            "is_privileged": is_identity_privileged(self.privileged_roles, identity),
            "publishing_edits": self.allow_publishing_edits,
        }
