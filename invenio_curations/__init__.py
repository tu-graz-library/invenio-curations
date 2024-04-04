# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Invenio module for curation support."""

from .ext import InvenioCurations
from .proxies import current_curations, current_curations_service

__version__ = "0.1.0"

__all__ = (
    "__version__",
    "current_curations",
    "current_curations_service",
    "InvenioCurations",
)
