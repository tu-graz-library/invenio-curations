# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Notification related filters for notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import current_app
from invenio_notifications.models import Recipient
from invenio_notifications.services.filters import RecipientFilter

if TYPE_CHECKING:
    from invenio_notifications.models import Notification


class OverrideEmailRecipientFilter(RecipientFilter):
    """Redirect all recipients to a single configured email address.

    If ``CURATIONS_NOTIFICATIONS_OVERRIDE_EMAIL`` is set, every curation
    notification is sent only to that address instead of the resolved
    recipients (e.g. all members of the curation group). This is meant to be
    the last filter in the chain, as it discards any previously resolved
    recipients.
    """

    def __call__(
        self,
        notification: Notification,  # noqa: ARG002
        recipients: dict[str, Recipient],
    ) -> dict[str, Recipient]:
        """Filter recipients."""
        override_email = current_app.config.get(
            "CURATIONS_NOTIFICATIONS_OVERRIDE_EMAIL",
        )
        if not override_email:
            return recipients

        return {
            "override": Recipient(data={"email": override_email}),
        }
