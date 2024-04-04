# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable curations."""


from invenio_requests.proxies import current_requests_service

from . import config
from .resources import CurationsResource, CurationsResourceConfig
from .services import CurationRequestService, CurationsServiceConfig


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
