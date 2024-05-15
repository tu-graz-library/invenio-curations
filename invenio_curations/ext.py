# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable curations."""


from flask import g
from flask_menu import current_menu
from invenio_i18n import lazy_gettext as _
from invenio_requests.proxies import current_requests_service

from . import config
from .resources import CurationsResource, CurationsResourceConfig
from .services import CurationRequestService, CurationsServiceConfig
from .views.ui import user_has_curations_management_role


def finalize_app(app):
    """Finalize app."""
    init_menu(app)


def init_menu(app):
    """Initialize flask menu."""
    user_dashboard = current_menu.submenu("dashboard")
    user_dashboard.submenu("curation-overview").register(
        "invenio_curations.curation_requests_overview",
        text=_("Curation Requests"),
        order=100,
        visible_when=lambda: user_has_curations_management_role(g.identity),
    )


class InvenioCurations(object):
    """Invenio-Curations extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        self.curations_service = None
        self.curations_resource = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-curations"] = self

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith("CURATIONS_"):
                app.config.setdefault(k, getattr(config, k))

    def service_configs(self, app):
        """Customized service configs."""

        class ServiceConfigs:
            curations = CurationsServiceConfig.build(app)

        return ServiceConfigs

    def init_services(self, app):
        """Initialize the service and resource for curations."""
        service_configs = self.service_configs(app)

        self.curations_service = CurationRequestService(
            config=service_configs.curations,
            requests_service=current_requests_service,
        )

    def init_resources(self, app):
        """Init resources."""
        self.curations_resource = CurationsResource(
            service=self.curations_service,
            config=CurationsResourceConfig.build(app),
        )
