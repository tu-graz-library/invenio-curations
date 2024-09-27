# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_notifications.models import Notification
from invenio_notifications.registry import EntityResolverRegistry
from invenio_notifications.services.builders import NotificationBuilder
from invenio_notifications.services.generators import EntityResolve, UserEmailBackend
from invenio_requests.notifications.filters import UserRecipientFilter
from invenio_users_resources.notifications.filters import UserPreferencesRecipientFilter
from invenio_users_resources.notifications.generators import UserRecipient

from invenio_curations.notifications.generators import GroupMembersRecipient


class CurationRequestActionNotificationBuilder(NotificationBuilder):
    """Notification builder for curation actions."""

    type = "curation-request"

    @classmethod
    def build(cls, identity, request):
        """Build notification with request context."""
        return Notification(
            type=cls.type,
            context={
                "executing_user": EntityResolverRegistry.reference_identity(identity),
                "request": EntityResolverRegistry.reference_entity(request),
            },
        )

    context = [
        EntityResolve(key="request"),
        EntityResolve(key="request.created_by"),
        EntityResolve(key="request.topic"),
        EntityResolve(key="request.receiver"),
        EntityResolve(key="executing_user"),
    ]

    recipients = []

    recipient_filters = [
        UserPreferencesRecipientFilter(),
        UserRecipientFilter("executing_user"),
    ]

    recipient_backends = [
        UserEmailBackend(),
    ]


class CurationRequestSubmitNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for submit action."""

    type = f"{CurationRequestActionNotificationBuilder.type}.submit"
    recipients = [GroupMembersRecipient("request.receiver")]


class CurationRequestResubmitNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for resubmit action."""

    type = f"{CurationRequestActionNotificationBuilder.type}.resubmit"
    recipients = [GroupMembersRecipient("request.receiver")]


class CurationRequestReviewNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for review action."""

    type = f"{CurationRequestActionNotificationBuilder.type}.review"
    recipients = [UserRecipient("request.created_by")]


class CurationRequestAcceptNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for accept action."""

    type = f"{CurationRequestActionNotificationBuilder.type}.accept"
    recipients = [UserRecipient("request.created_by")]


class CurationRequestCritiqueNotificationBuilder(
    CurationRequestActionNotificationBuilder
):
    """Notification builder for critique action."""

    type = f"{CurationRequestActionNotificationBuilder.type}.critique"
    recipients = [UserRecipient("request.created_by")]
