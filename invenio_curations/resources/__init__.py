# SPDX-FileCopyrightText: 2024 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Resources module."""

from .config import CurationsResourceConfig
from .resource import CurationsResource

__all__ = (
    "CurationsResource",
    "CurationsResourceConfig",
)
