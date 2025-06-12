# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from __future__ import annotations

from typing import ClassVar

from flask_principal import Identity
from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.filters import RecipientFilter
from invenio_notifications.services.generators import (
    ContextGenerator,
    EntityResolve,
    RecipientGenerator,
    UserEmailBackend,
)
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_requests.records.api import Request
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient

from .generators import GroupMembersRecipient


class CurationRequestActionNotificationBuilder(NotificationBuilder):
    """Notification builder for curation actions."""

    type: ClassVar[str] = "curation-request"

    context: ClassVar[list[ContextGenerator]] = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
        EntityResolve(key="executing_user"),
    ]

    # recipientGenerator: class for all recipient finder classes
    # (e.g., UserRecipient, GroupMembersRecipient) - defines who gets notifications
    recipients: ClassVar[list[RecipientGenerator]] = []

    recipient_filters: ClassVar[list[RecipientFilter]] = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter("executing_user"),
    ]

    recipient_backends: ClassVar[list[UserEmailBackend]] = [
        UserEmailBackend(),
    ]

    @classmethod
    def build(cls, identity: Identity, request: Request) -> Notification:
        """Build notification with request context.

        Args:
            identity: The identity performing the action
            request: The curation request

        Returns:
            Notification object with proper context

        """
        return Notification(
            type=cls.type,
            context={
                "executing_user": EntityResolverRegistry.reference_identity(identity),
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )


class CurationRequestSubmitNotificationBuilder(
    CurationRequestActionNotificationBuilder,
):
    """Notification builder for submit action."""

    type: ClassVar[str] = f"{CurationRequestActionNotificationBuilder.type}.submit"
    recipients: ClassVar[list[RecipientGenerator]] = [
        GroupMembersRecipient("request.receiver"),
    ]


class CurationRequestResubmitNotificationBuilder(
    CurationRequestActionNotificationBuilder,
):
    """Notification builder for resubmit action."""

    type: ClassVar[str] = f"{CurationRequestActionNotificationBuilder.type}.resubmit"
    recipients: ClassVar[list[RecipientGenerator]] = [
        GroupMembersRecipient("request.receiver"),
    ]


class CurationRequestReviewNotificationBuilder(
    CurationRequestActionNotificationBuilder,
):
    """Notification builder for review action."""

    type: ClassVar[str] = f"{CurationRequestActionNotificationBuilder.type}.review"
    recipients: ClassVar[list[RecipientGenerator]] = [
        UserRecipient("request.created_by"),
    ]


class CurationRequestAcceptNotificationBuilder(
    CurationRequestActionNotificationBuilder,
):
    """Notification builder for accept action."""

    type: ClassVar[str] = f"{CurationRequestActionNotificationBuilder.type}.accept"
    recipients: ClassVar[list[RecipientGenerator]] = [
        UserRecipient("request.created_by"),
    ]


class CurationRequestCritiqueNotificationBuilder(
    CurationRequestActionNotificationBuilder,
):
    """Notification builder for critique action."""

    type: ClassVar[str] = f"{CurationRequestActionNotificationBuilder.type}.critique"
    recipients: ClassVar[list[RecipientGenerator]] = [
        UserRecipient("request.created_by"),
    ]
