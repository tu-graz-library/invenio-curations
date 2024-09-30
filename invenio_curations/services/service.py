# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curation service."""

from flask import current_app
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_accounts.proxies import current_datastore
from invenio_i18n import gettext as _
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.results import ResolverRegistry
from invenio_search.engine import dsl

from ..requests import CurationRequest
from .errors import OpenRecordCurationRequestAlreadyExists, RoleNotFound


class CurationRequestService:
    """Service for User Moderation requests."""

    def __init__(self, requests_service, **kwargs):
        """Service initialisation as a sub-service of requests."""
        self.requests_service = requests_service

    @property
    def allow_publishing_edits(self):
        """Get the configured value of ``CURATIONS_ALLOW_PUBLISHING_EDITS``."""
        return current_app.config.get("CURATIONS_ALLOW_PUBLISHING_EDITS", False)

    @property
    def moderation_role_name(self):
        """Get the configured name of the ``CURATIONS_MODERATION_ROLE``."""
        role = current_app.config["CURATIONS_MODERATION_ROLE"]

        if isinstance(role, Role):
            # As of InvenioRDM v12, the role's name and ID should be the same anyway
            return role.name or role.id

        # If it's not a role, we assume it's a string
        return role

    @property
    def moderation_role(self):
        """Get the configured ``CURATIONS_MODERATION_ROLE`` role."""
        return current_datastore.find_role(self.moderation_role_name)

    @property
    def request_type_cls(self):
        """Curation request type."""
        return current_request_type_registry.lookup(CurationRequest.type_id)

    def get_review(self, identity, topic, **kwargs):
        """Get the curation review for a topic."""
        topic_reference = ResolverRegistry.reference_entity(topic)
        # Assume there is only one item in the reference dict
        topic_key, topic_value = next(iter(topic_reference.items()))

        results = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    dsl.Q("term", **{"topic.{}".format(topic_key): topic_value}),
                ],
            ),
            **kwargs,
        )

        if results.total == 0:
            return None

        return next(results.hits)

    def accepted_record(self, identity, record):
        """Check if current version of record has been accepted."""
        topic_reference = ResolverRegistry.reference_entity(record)
        # Assume there is only one item in the reference dict
        topic_key, topic_value = next(iter(topic_reference.items()))

        results = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    dsl.Q("term", **{"topic.{}".format(topic_key): topic_value}),
                    dsl.Q("term", **{"is_open": False}),
                    dsl.Q("term", **{"status": "accepted"}),
                ],
            ),
        )
        return next(results.hits) if results.total > 0 else None

    @unit_of_work()
    def create(self, identity, data=None, uow=None, **kwargs):
        """Create a RDMCuration request and submit it."""
        role = self.moderation_role
        if not role:
            raise RoleNotFound(self.moderation_role_name)
        assert role, _(
            "Curation request moderation role must exist to enable record curation requests."
        )

        # Allowed entities for the request type will be checked in the request service
        topic = ResolverRegistry.resolve_entity_proxy(data.pop("topic", None)).resolve()
        creator = (
            ResolverRegistry.resolve_entity_proxy(data.pop("created_by")).resolve()
            if "created_by" in data
            else None
        )

        receiver = (
            ResolverRegistry.resolve_entity_proxy(data.pop("receiver", None)).resolve()
            if "receiver" in data
            else role
        )

        default_data = {
            "title": "RDM Curation: {title}".format(
                title=topic.metadata.get("title", topic["id"])
            ),
        }

        # using system identity to ensure a request is fetched, if it exists. Even if the user would not have access.
        if self.get_review(system_identity, topic):
            raise OpenRecordCurationRequestAlreadyExists()

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
        self, identity, params=None, search_preference=None, expand=False, **kwargs
    ):
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
