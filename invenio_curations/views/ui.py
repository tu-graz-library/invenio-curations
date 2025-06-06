# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Curations ui views module."""

from flask import Blueprint, Flask, abort, g, render_template
from flask_login import current_user
from flask_principal import Identity
from invenio_records_resources.services.records.service import RecordService
from invenio_users_resources.proxies import current_user_resources

from invenio_curations.searchapp import search_app_context
from invenio_curations.services import CurationRequestService

from ..proxies import current_curations_service, unproxy


def user_has_curations_management_role(identity: Identity) -> bool:
    """Check if provided identity provides the curation role."""
    _curations_service: CurationRequestService = unproxy(current_curations_service)
    role = _curations_service.moderation_role
    if not role:
        return False
    return identity.user.has_role(role)  # type: ignore[attr-defined]


def curation_requests_overview() -> str:
    """Display user dashboard page."""
    if not user_has_curations_management_role(g.identity):
        abort(403)

    user_service_unproxied: RecordService = unproxy(current_user_resources.users_service)  # type: ignore[attr-defined]
    url = user_service_unproxied.links_item_tpl.expand(g.identity, current_user)[
        "avatar"
    ]

    return render_template(
        "invenio_curations/overview.html",
        searchbar_config=dict(searchUrl="/"),
        user_avatar=url,
    )


def create_ui_blueprint(app: Flask) -> Blueprint:
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
    return blueprint
