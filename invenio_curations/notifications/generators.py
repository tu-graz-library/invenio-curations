# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Notification related utils for notifications."""

from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_notifications.models import Recipient
from invenio_notifications.services.generators import RecipientGenerator
from invenio_records.dictutils import dict_lookup
from invenio_search.engine import dsl
from invenio_users_resources.proxies import current_users_service


class GroupMembersRecipient(RecipientGenerator):
    """Group/Role member recipient generator for notifications."""

    def __init__(self, key):
        """Ctor."""
        self.key = key

    def __call__(self, notification, recipients: dict):
        """Fetch group members as recipients."""
        group = dict_lookup(notification.context, self.key)

        # Group service does not contain information about users.
        role = Role.query.filter(Role.id == group["id"]).one()

        user_ids = []
        for u in role.users:
            user_ids.append(u.id)

        if not user_ids:
            return recipients

        filter_ = dsl.Q("terms", **{"id": user_ids})
        users = current_users_service.scan(system_identity, extra_filter=filter_)
        for u in users:
            recipients[u["id"]] = Recipient(data=u)
        return recipients
