# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for curations."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity

from invenio_curations.services.errors import OpenRecordCurationRequestAlreadyExists

from .proxies import current_curations_service


@shared_task(ignore_result=True)
def request_record_curation(topic, user_id):
    """Creates a task to request moderation for a RDM record."""
    try:
        current_curations_service.create(system_identity, topic=topic, user_id=user_id)
    except OpenRecordCurationRequestAlreadyExists as ex:
        # Request already exists. Just log the warning.
        current_app.logger.warning(ex.description)
