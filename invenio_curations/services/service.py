# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Curation service."""
from flask import current_app
from invenio_accounts.models import Role
from invenio_i18n import gettext as _
from invenio_records_resources.services.uow import unit_of_work
from invenio_requests.proxies import current_request_type_registry
from invenio_requests.services.results import ResolverRegistry
from invenio_search.engine import dsl

from ..requests import CurationRequest
from .errors import OpenRecordCurationRequestAlreadyExists


class CurationRequestService:
    """Service for User Moderation requests."""

    def __init__(self, requests_service, **kwargs):
        """Service initialisation as a sub-service of requests."""
        self.requests_service = requests_service

    def role(self):
        """Creates a RDMCuration request and submits it."""
        role_name = current_app.config.get("CURATIONS_MODERATION_ROLE")
        return Role.query.filter(Role.name == role_name).one_or_none()

    @property
    def request_type_cls(self):
        """User moderation request type."""
        return current_request_type_registry.lookup(CurationRequest.type_id)

    def get_review(self, identity, topic, **kwargs):
        topic_reference = ResolverRegistry.reference_entity(topic)
        results = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    # TODO: make type independent search
                    dsl.Q("term", **{"topic.record": topic_reference["record"]}),
                ],
            ),
            **kwargs,
        )

        if results.total == 0:
            return None

        return next(results.hits)

    def accepted_record(self, identity, record):
        """Check if current version of record has been accepted."""

        results = self.requests_service.search(
            identity,
            extra_filter=dsl.query.Bool(
                "must",
                must=[
                    dsl.Q("term", **{"type": self.request_type_cls.type_id}),
                    # TODO: make type independent search
                    dsl.Q("term", **{"topic.record": record["id"]}),
                    dsl.Q("term", **{"is_open": False}),
                    dsl.Q("term", **{"status": "accepted"}),
                    # dsl.Q("range", **{"updated": {"gte": record.updated}}),
                ],
            ),
        )
        return next(results.hits) if results.total > 0 else None

    @unit_of_work()
    def create(self, identity, data=None, uow=None, **kwargs):
        """Creates a RDMCuration request and submits it."""

        role = self.role()
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
            "title": "RDM Curation: {title}".format(title=topic.metadata["title"]),
        }

        if self.get_review(identity, topic):
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
