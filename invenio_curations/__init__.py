# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Invenio module for curation support."""

from .ext import InvenioCurations
from .proxies import current_curations, current_curations_service

__version__ = "0.8.4"

__all__ = (
    "InvenioCurations",
    "__version__",
    "current_curations",
    "current_curations_service",
)
