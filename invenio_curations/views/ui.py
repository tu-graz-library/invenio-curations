# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Curations ui views module."""

from typing import Any, cast

from flask import Blueprint, Flask, abort, current_app, g, render_template, request
from flask_login import current_user
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.records.api import RDMDraft
from invenio_records_resources.services.records.service import RecordService
from invenio_users_resources.proxies import current_user_resources

from ..proxies import current_curations_service, unproxy
from ..searchapp import search_app_context
from ..services import CurationRequestService


def user_has_curations_management_role(identity: Identity) -> bool:
    """Check if provided identity provides the curation role."""
    _curations_service: CurationRequestService = unproxy(current_curations_service)
    role = _curations_service.moderation_role
    if not role:
        return False
    return cast(bool, identity.user.has_role(role))


def curation_requests_overview() -> str:
    """Display user dashboard page."""
    if not user_has_curations_management_role(g.identity):
        abort(403)

    user_service_unproxied: RecordService = unproxy(
        current_user_resources.users_service,
    )
    url = user_service_unproxied.links_item_tpl.expand(g.identity, current_user)[
        "avatar"
    ]

    return render_template(
        "invenio_curations/overview.html",
        searchbar_config=dict(searchUrl="/"),
        user_avatar=url,
    )


def get_curation_request_for_record(record: dict | None) -> Any | None:
    """Get the curation request for a draft record."""
    if not current_app.config.get("CURATIONS_BLOCK_EDIT_DURING_REVIEW", False):
        return None

    if not record or not isinstance(record, dict):
        return None

    record_id = record.get("id")
    if not record_id:
        return None

    try:
        draft = RDMDraft.pid.resolve(record_id, registered_only=False)
        return current_curations_service.get_review(
            identity=system_identity,
            topic=draft,
            expand=False,
        )
    except Exception as e:  # noqa: BLE001
        current_app.logger.debug("Error getting curation request: %s", e)
        return None


def curation_record_context() -> dict[str, Any]:
    """Inject curation request information into record preview templates."""
    curation_request = None

    if request.endpoint and "record_detail" in request.endpoint:
        record_id = request.view_args.get("pid_value") if request.view_args else None
        if record_id:
            curation_request = get_curation_request_for_record({"id": record_id})

    return {
        "draft_curation_request": curation_request,
        "get_curation_request_for_record": get_curation_request_for_record,
    }


def create_ui_blueprint(app: Flask) -> Blueprint:  # noqa: ARG001
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "invenio_curations",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Add URL rules
    blueprint.add_url_rule("/curations/overview", view_func=curation_requests_overview)

    # Add context processor for search
    blueprint.app_context_processor(search_app_context)
    blueprint.app_context_processor(curation_record_context)
    return blueprint
