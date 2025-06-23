# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utils module."""

import nh3


class HTMLParseError(Exception):
    """Custom HTML parsing exception."""


def cleanup_html_tags(text: str) -> str:
    """Strip given text of HTML tags using nh3 library."""
    if not nh3.is_html(text):
        return text
    try:
        return nh3.clean(text, tags=set(), attributes={})
    except Exception as e:
        msg = "Could not parse html input"
        raise HTMLParseError(msg) from e
