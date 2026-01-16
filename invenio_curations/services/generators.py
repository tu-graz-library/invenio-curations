# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations related generators."""

from collections.abc import Callable
from itertools import chain
from typing import Any, cast

from flask_principal import Need, RoleNeed
from invenio_access.permissions import Permission, system_identity
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records.records.api import RDMDraft
from invenio_rdm_records.requests.entity_resolvers import RDMRecordProxy
from invenio_records_permissions.generators import ConditionalGenerator, Generator
from invenio_requests.customizations.request_types import RequestType
from invenio_requests.records.api import Request

from ..proxies import current_curations_service, unproxy
from .service import CurationRequestService


class IfRequestTypes(ConditionalGenerator):
    """Request-oriented generator checking for requests of certain types."""

    def __init__(
        self,
        request_types: list[type[RequestType]],
        then_: list[Generator],
        else_: list[Generator],
    ) -> None:
        """Constructor."""
        self.request_types = set(request_types)
        super().__init__(then_, else_)

    def _condition(self, request: Request | None = None, **__: Any) -> bool:
        """Check if the request type matches a configured type."""
        if request is not None:
            for request_type in self.request_types:
                if isinstance(request.type, request_type):
                    return True

        return False


class CurationRequestsConditionalGenerator(ConditionalGenerator):
    """Base class for request-based curation condition generators."""

    _curations_service: CurationRequestService = unproxy(current_curations_service)

    def __init__(
        self,
        record_access_func: Callable[
            [Request],
            RDMDraft,
        ] = lambda request: request.topic.resolve(),
        then_: list[Generator] | None = None,
        else_: list[Generator] | None = None,
    ) -> None:
        """Constructor."""
        self.record_access_func = record_access_func
        super().__init__(then_ or [], else_ or [])

    def _condition(self, **__: Any) -> bool:
        """To be overridden by children classes."""
        raise NotImplementedError


class IfCurationRequestAccepted(CurationRequestsConditionalGenerator):
    """Request-oriented generator checking if a curation request has been accepted."""

    def _condition(self, request: Request | None = None, **__: Any) -> bool:
        """Check if the curation request for the record has been accepted."""
        if request is not None:
            record_to_curate = self.record_access_func(request)
            return (
                self._curations_service.accepted_record(
                    system_identity,
                    record_to_curate,
                )
                is not None
            )

        return False


class IfCurationRequestBasedExists(CurationRequestsConditionalGenerator):
    """Request-oriented generator checking if a curation request exists."""

    def _condition(self, request: Request | None = None, **__: Any) -> bool:
        """Check if the curation request for the record has been accepted."""
        if request is not None:
            record_to_curate = self.record_access_func(request)
            return (
                self._curations_service.get_review(
                    system_identity,
                    record_to_curate,
                )
                is not None
            )

        return False


class EntityReferenceServicePermission(Generator):
    """Request-oriented generator accessing a named permission from the entity's service config."""

    entity_field: str | None = None

    def __init__(self, permission_name: str, **__: Any) -> None:
        """Constructor specifying permission_name."""
        self.permission_name = permission_name
        assert self.entity_field is not None, "Subclass must define entity_field."
        super().__init__()

    def _get_permission(self, entity: RDMRecordProxy) -> list[Permission]:
        """Get the specified permission from the request entity service config."""
        permission_policy_cls = (
            entity.get_resolver().get_service().config.permission_policy_cls
        )

        return cast(
            list[Permission],
            getattr(permission_policy_cls, self.permission_name),
        )

    def _get_entity(self, request: Request) -> RDMRecordProxy:
        """Get the specified entity of the request."""
        return getattr(request, self.entity_field)  # type: ignore[arg-type]

    def needs(self, request: Request | None = None, **kwargs: Any) -> set[Need]:
        """Set of needs granting permission."""
        if request is None:
            return set()

        entity = self._get_entity(request)
        permission = self._get_permission(entity)
        try:
            record = entity.resolve()
        except PIDDoesNotExistError:
            # Could not resolve topic. This may happen when trying to serialize a request and checking its permissions.
            # The referenced entity could be deleted, which would result in not being able to serialize instead. Instead,
            # an empty set is returned for this permission.
            return set()
        popped_record = kwargs.pop("record")
        needs = [g.needs(record=record, **kwargs) for g in permission]

        kwargs["record"] = popped_record
        return set(chain.from_iterable(needs))

    def excludes(self, request: Request | None = None, **kwargs: Any) -> set[Need]:
        """Set of excludes denying permission."""
        if request is None:
            return set()

        entity = self._get_entity(request)
        permission = self._get_permission(entity)
        try:
            record = entity.resolve()
        except PIDDoesNotExistError:
            # Could not resolve topic. This may happen when trying to serialize a request and checking its permissions.
            # The referenced entity could be deleted, which would result in not being able to serialize instead. Instead,
            # an empty set is returned for this permission.
            return set()
        popped_record = kwargs.pop("record")
        excludes = [g.excludes(record=record, **kwargs) for g in permission]

        kwargs["record"] = popped_record
        return set(chain.from_iterable(excludes))


class TopicPermission(EntityReferenceServicePermission):
    """Request-oriented generator to get generators of specified permission name from the topic of the request."""

    entity_field: str = "topic"


class CurationModerators(Generator):
    """Permission generator that allows users with the `moderation` role."""

    _curations_service: CurationRequestService = unproxy(current_curations_service)

    def needs(self, **__: Any) -> list[Need]:
        """Allow access for the moderation role."""
        return [RoleNeed(self._curations_service.moderation_role_name)]


class IfCurationRecordBasedExists(ConditionalGenerator):
    """Record-oriented generator checking if a curation request exists."""

    _curations_service: CurationRequestService = unproxy(current_curations_service)

    def _condition(self, record: RDMDraft | None = None, **__: Any) -> bool:
        """Check if the record has a curation request or not."""
        if record is not None:
            # We use the system identity here to avoid visibility issues
            request = self._curations_service.get_review(
                identity=system_identity,
                topic=record,
            )
            return request is not None

        return False
