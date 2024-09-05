# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 KTH Royal Institute of Technology
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests resource config."""


import marshmallow as ma
from flask_resources import HTTPJSONException, create_error_handler
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig
from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema

from invenio_curations.services.errors import (
    CurationRequestNotAccepted,
    OpenRecordCurationRequestAlreadyExists,
    RoleNotFound,
)


#
# Request args
#
class CurationsSearchRequestArgsSchema(RequestSearchRequestArgsSchema):
    """Add parameter to parse tags."""


request_error_handlers = {
    OpenRecordCurationRequestAlreadyExists: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=str(e),
        )
    ),
    CurationRequestNotAccepted: create_error_handler(
        lambda e: HTTPJSONException(
            code=400,
            description=str(e),
            errors=[
                {
                    "field": "metadata.title",
                    "messages": ["."],
                }
            ],
        )
    ),
    RoleNotFound: create_error_handler(
        lambda e: HTTPJSONException(
            code=404,
            description=str(e),
        )
    ),
}


#
# Resource config
#
class CurationsResourceConfig(RecordResourceConfig, ConfiguratorMixin):
    """Requests resource configuration."""

    blueprint_name = "curations"
    url_prefix = "/curations"
    routes = {
        "list": "/",
    }

    request_view_args = {
        "reference_type": ma.fields.Str(),
        "reference_id": ma.fields.Str(),
    }

    request_extra_args = {
        **RecordResourceConfig.request_extra_args,
        "reference_type": ma.fields.Str(),
        "reference_id": ma.fields.Str(),
    }
    request_search_args = CurationsSearchRequestArgsSchema

    error_handlers = FromConfig(
        "CURATIONS_ERROR_HANDLERS", default=request_error_handlers
    )

    response_handlers = {
        "application/vnd.inveniordm.v1+json": RecordResourceConfig.response_handlers[
            "application/json"
        ],
        **RecordResourceConfig.response_handlers,
    }
