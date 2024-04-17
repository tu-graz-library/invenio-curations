# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Curations ui views module."""

from flask import Blueprint, g, render_template
from flask_login import current_user
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _
from invenio_users_resources.proxies import current_user_resources

from invenio_curations.searchapp import search_app_context

from ..proxies import current_curations_service


def _user_has_role():
    role = current_curations_service.curation_role
    if not role:
        return False
    return current_user.has_role(role)


def curation_requests_overview():
    """Display user dashboard page."""
    url = current_user_resources.users_service.links_item_tpl.expand(
        g.identity, current_user
    )["avatar"]

    return render_template(
        "invenio_curations/overview.html",
        searchbar_config=dict(searchUrl="/"),
        user_avatar=url,
        has_permission=_user_has_role(),
    )


def create_ui_blueprint(app):
    """Register blueprint routes on app."""

    blueprint = Blueprint(
        "invenio_curations",
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # Add URL rules
    blueprint.add_url_rule("/curations/overview", view_func=curation_requests_overview)

    @blueprint.before_app_first_request
    def register_menus():
        user_dashboard = current_menu.submenu("dashboard")
        user_dashboard.submenu("curation-overview").register(
            "invenio_curations.curation_requests_overview",
            text=_("Curation Requests"),
            order=4,
            visible_when=_user_has_role,
        )


    blueprint.app_context_processor(search_app_context)
    return blueprint
