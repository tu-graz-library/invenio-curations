# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021-2022 TU Wien.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource."""


from flask import g
from flask_resources import resource_requestctx, response_handler, route
from invenio_records_resources.resources import RecordResource
from invenio_records_resources.resources.records.resource import (
    request_data,
    request_extra_args,
    request_headers,
    request_search_args,
    request_view_args,
)
from invenio_records_resources.resources.records.utils import search_preference


#
# Resource
#
class CurationsResource(RecordResource):
    """Resource for curations."""

    def create_blueprint(self, **options):
        """Create the blueprint."""
        # We avoid passing url_prefix to the blueprint because we need to
        # install URLs under both /records and /user/records. Instead we
        # add the prefix manually to each route (which is anyway what Flask
        # does in the end)
        options["url_prefix"] = ""
        return super().create_blueprint(**options)

    def create_url_rules(self):
        """Create the URL rules for the record resource."""
        routes = self.config.routes

        def p(route):
            """Prefix a route with the URL prefix."""
            return f"{self.config.url_prefix}{route}"

        def s(route):
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        return [
            route("GET", p(routes["list"]), self.search),
            route("POST", p(routes["list"]), self.create),
        ]

    @request_extra_args
    @request_search_args
    @request_view_args
    @response_handler(many=True)
    def search(self):
        """Perform a search over the items."""
        hits = self.service.search(
            identity=g.identity,
            params=resource_requestctx.args,
            search_preference=search_preference(),
            expand=resource_requestctx.args.get("expand", False),
        )
        return hits.to_dict(), 200

    @request_extra_args
    @request_data
    @response_handler()
    def create(self):
        """Create an item."""
        item = self.service.create(
            g.identity,
            resource_requestctx.data or {},
            expand=resource_requestctx.args.get("expand", True),
        )
        return item.to_dict(), 201

    # @request_extra_args
    # @request_search_args
    # @request_view_args
    # @response_handler(many=True)
    # def search_user_requests(self):
    #     """Perform a search over user requets.

    #     /GET /user/requests
    #     """
    #     hits = self.service.search_user_requests(
    #         identity=g.identity,
    #         params=resource_requestctx.args,
    #         search_preference=search_preference(),
    #         expand=resource_requestctx.args.get("expand", False),
    #     )
    #     return hits.to_dict(), 200

    # @request_extra_args
    # @request_view_args
    # @response_handler()
    # def read(self):
    #     """Read an item."""
    #     item = self.service.read(
    #         id_=resource_requestctx.view_args["id"],
    #         identity=g.identity,
    #         expand=resource_requestctx.args.get("expand", False),
    #     )
    #     return item.to_dict(), 200

    # @request_extra_args
    # @request_headers
    # @request_view_args
    # @request_data
    # @response_handler()
    # def update(self):
    #     """Update an item."""
    #     # TODO should we allow updating of requests in this general resource?
    #     item = self.service.update(
    #         id_=resource_requestctx.view_args["id"],
    #         identity=g.identity,
    #         data=resource_requestctx.data,
    #         expand=resource_requestctx.args.get("expand", False),
    #     )
    #     return item.to_dict(), 200

    # @request_headers
    # @request_view_args
    # def delete(self):
    #     """Delete an item."""
    #     self.service.delete(
    #         id_=resource_requestctx.view_args["id"],
    #         identity=g.identity,
    #     )
    #     return "", 204

    # @request_extra_args
    # @request_view_args
    # @request_headers
    # @request_data
    # @response_handler()
    # def execute_action(self):
    #     """Execute action."""
    #     item = self.service.execute_action(
    #         identity=g.identity,
    #         id_=resource_requestctx.view_args["id"],
    #         action=resource_requestctx.view_args["action"],
    #         data=resource_requestctx.data,
    #         expand=resource_requestctx.args.get("expand", False),
    #     )
    #     return item.to_dict(), 200
