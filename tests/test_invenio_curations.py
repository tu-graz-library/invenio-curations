# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_curations import InvenioCurations, __version__
from invenio_curations.views import ui


def test_version() -> None:
    """Test version import."""
    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    app.config["APP_RDM_RECORD_LANDING_PAGE_TEMPLATE"] = (
        "invenio_app_rdm/records/detail.html"
    )
    InvenioCurations(app)
    assert "invenio-curations" in app.extensions
    assert (
        app.config["APP_RDM_RECORD_LANDING_PAGE_TEMPLATE"]
        == "invenio_curations/records/detail.html"
    )

    app = Flask("testapp")
    ext = InvenioCurations()
    assert "invenio-curations" not in app.extensions
    ext.init_app(app)
    assert "invenio-curations" in app.extensions


def test_get_curation_request_for_record_disabled() -> None:
    """Disabled edit blocking skips curation lookup."""
    app = Flask("testapp")
    app.config["CURATIONS_BLOCK_EDIT_DURING_REVIEW"] = False

    with app.app_context():
        assert ui.get_curation_request_for_record({"id": "abc"}) is None


def test_get_curation_request_for_record(monkeypatch) -> None:
    """Enabled edit blocking looks up the draft curation request."""
    app = Flask("testapp")
    app.config["CURATIONS_BLOCK_EDIT_DURING_REVIEW"] = True
    review = object()
    draft = object()

    class DummyPid:
        @staticmethod
        def resolve(record_id: str, *, registered_only: bool = False) -> object:
            assert record_id == "abc"
            assert registered_only is False
            return draft

    class DummyService:
        @staticmethod
        def get_review(*, identity: object, topic: object, expand: bool = False) -> object:
            assert identity is ui.system_identity
            assert topic is draft
            assert expand is False
            return review

    monkeypatch.setattr(ui.RDMDraft, "pid", DummyPid)
    monkeypatch.setattr(ui, "current_curations_service", DummyService)

    with app.app_context():
        assert ui.get_curation_request_for_record({"id": "abc"}) is review


def test_curation_record_context_uses_record_detail_endpoint(monkeypatch) -> None:
    """Record detail requests inject the current draft curation request."""
    app = Flask("testapp")
    app.add_url_rule(
        "/records/<pid_value>",
        endpoint="invenio_app_rdm_records.record_detail",
        view_func=lambda pid_value: pid_value,
    )
    review = object()

    monkeypatch.setattr(
        ui,
        "get_curation_request_for_record",
        lambda record: review if record == {"id": "abc"} else None,
    )

    with app.test_request_context("/records/abc"):
        app.preprocess_request()
        context = ui.curation_record_context()

    assert context["draft_curation_request"] is review
    assert context["get_curation_request_for_record"] is ui.get_curation_request_for_record
