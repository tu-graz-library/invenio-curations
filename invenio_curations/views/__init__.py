# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations views module."""

from flask import Blueprint

from .api import create_curations_bp
from .ui import create_ui_blueprint

blueprint = Blueprint("invenio-curations-ext", __name__)

__all__ = (
    "blueprint",
    "create_ui_blueprint",
    "create_curations_bp",
)
