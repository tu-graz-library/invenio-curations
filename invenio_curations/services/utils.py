# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Utils module."""

from html.parser import HTMLParser
from io import StringIO


class HTMLParseException(Exception):
    """Custom HTML parsing exception."""


class TagStripper(HTMLParser):
    """Utility class used to strip text of html tags."""

    def __init__(self):
        """Custom Constructor."""
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        """Write."""
        self.text.write(d)

    def get_data(self):
        """Get the untagged data."""
        return self.text.getvalue()


def cleanup_html_tags(text):
    """Strip html tags from a given text using an utility class."""
    if not isinstance(text, str):
        raise HTMLParseException("Could not parse html input")

    if "<" not in text and ">" not in text:
        return text

    try:
        s = TagStripper()
        s.feed(text)

        return s.get_data()
    except Exception:
        raise HTMLParseException("Could not parse html input")
