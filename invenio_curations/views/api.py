# SPDX-FileCopyrightText: 2024-2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""View functions for curations."""

from typing import cast

from flask import Blueprint, Flask


def create_curations_bp(app: Flask) -> Blueprint:
    """Create curations blueprint."""
    ext = app.extensions["invenio-curations"]
    return cast(Blueprint, ext.curations_resource.as_blueprint())
