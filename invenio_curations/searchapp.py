# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 CERN.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Configuration helper for React-SearchKit."""

from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context():
    """Search app context processor."""
    return {
        "search_app_curations_requests_config": partial(
            search_app_config,
            config_name="CURATIONS_SEARCH_REQUESTS",
            available_facets=current_app.config["REQUESTS_FACETS"],
            sort_options=current_app.config["RDM_SORT_OPTIONS"],
            endpoint="/api/curations/",
            headers={"Accept": "application/json"},
            initial_filters=[["is_open", "true"]],
            hidden_params=[["expand", "1"]],
        ),
    }
