# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Resources module."""

from .config import CurationsResourceConfig
from .resource import CurationsResource

__all__ = (
    "CurationsResource",
    "CurationsResourceConfig",
)
