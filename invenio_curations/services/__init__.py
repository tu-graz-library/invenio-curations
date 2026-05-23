# SPDX-FileCopyrightText: 2024-2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Resources module."""

from .config import CurationsServiceConfig
from .service import CurationRequestService

__all__ = (
    "CurationRequestService",
    "CurationsServiceConfig",
)
