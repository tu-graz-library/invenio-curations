# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021-2022 TU Wien.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource."""

from typing import Any, cast

from flask import Blueprint, g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference
from invenio_records_resources.services.records.results import RecordItem, RecordList


#
# Resource
#
class CurationsResource(RecordResource):
    """Resource for curations."""

    def create_blueprint(self, **options: Any) -> Blueprint:
        """Create the blueprint."""
        # We avoid passing url_prefix to the blueprint because we need to
        # install URLs under both /records and /user/records. Instead we
        # add the prefix manually to each route (which is anyway what Flask
        # does in the end)
        options["url_prefix"] = ""
        return cast(Blueprint, super().create_blueprint(**options))

    def as_blueprint(self, **options: Any) -> Blueprint:
        """Creating the blueprint and registering error handlers on the application.

        This is required, as the CurationComponent will throw inside another blueprint.
        """
        blueprint = cast(Blueprint, super().as_blueprint(**options))

        for exc_or_code, error_handler in self.create_error_handlers():
            blueprint.record_once(
                lambda s, exc_or_code=exc_or_code, error_handler=error_handler: s.app.errorhandler(
                    exc_or_code,
                )(
                    error_handler,
                ),
            )

        return blueprint

    def create_url_rules(
        self,
    ) -> list[dict]:
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        def p(route: str) -> str:
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        def s(route: str) -> str:
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        return [
            route("GET", p(routes["list"]), self.search),
            route("POST", p(routes["list"]), self.create),
            route("GET", p(routes["data"]), self.get_curations_data),
        ]

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self) -> tuple[dict[str, Any], int]:
        """Perform a search over the items."""
        hits: RecordList = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

    @request_extra_args
    @request_data
    @response_handler()
    def create(self) -> tuple[dict[str, Any], int]:
        """Create an item."""
        item: RecordItem = self.service.create(
            g.identity,
            resource_requestctx.data or {},
            expand=resource_requestctx.args.get("expand", True),
        )
        return item.to_dict(), 201

    @request_extra_args
    @request_data
    @response_handler()
    def get_curations_data(self) -> tuple[dict[str, Any], int]:
        """Create an item."""
        return self.service.get_curations_data(g.identity), 200
