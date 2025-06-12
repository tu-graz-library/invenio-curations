# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_curations import InvenioCurations


def test_version() -> None:
    """Test version import."""
    from invenio_curations import __version__

    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    InvenioCurations(app)
    assert "invenio-curations" in app.extensions

    app = Flask("testapp")
    ext = InvenioCurations()
    assert "invenio-curations" not in app.extensions
    ext.init_app(app)
    assert "invenio-curations" in app.extensions
