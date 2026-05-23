# SPDX-FileCopyrightText: 2024 CERN.
# SPDX-License-Identifier: MIT

"""Configuration helper for React-SearchKit."""

from collections.abc import Callable
from functools import partial
from typing import Any

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context() -> dict[str, Callable[..., dict[str, Any]]]:
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
