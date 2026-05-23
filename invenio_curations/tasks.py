# SPDX-FileCopyrightText: 2024-2025 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Celery tasks for curations."""

from celery import shared_task
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_rdm_records.records.api import RDMDraft

from .proxies import current_curations_service, unproxy
from .services import CurationRequestService
from .services.errors import OpenRecordCurationRequestAlreadyExistsError


@shared_task(ignore_result=True)
def request_record_curation(topic: RDMDraft, user_id: str) -> None:
    """Creates a task to request moderation for a RDM record."""
    _curations_service: CurationRequestService = unproxy(current_curations_service)
    try:
        _curations_service.create(system_identity, topic=topic, user_id=user_id)
    except OpenRecordCurationRequestAlreadyExistsError as ex:
        # Request already exists. Just log the warning.
        current_app.logger.warning(ex.description)
