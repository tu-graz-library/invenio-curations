# SPDX-FileCopyrightText: 2024-2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Curations views module."""

from flask import Blueprint

from .api import create_curations_bp
from .ui import create_ui_blueprint

blueprint = Blueprint("invenio-curations-ext", __name__)

__all__ = (
    "blueprint",
    "create_curations_bp",
    "create_ui_blueprint",
)
