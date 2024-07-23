# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations permissions."""

from invenio_requests.services.generators import Creator, Receiver, Status
from invenio_requests.services.permissions import (
    PermissionPolicy as RequestPermissionPolicy,
)


class CurationPermissionPolicy(RequestPermissionPolicy):
    """Permission policy for curations."""

    can_read = RequestPermissionPolicy.can_read + [
        Status(
            ["review", "critiqued", "resubmitted"],
            [Creator(), Receiver()],
        ),
    ]
    can_create_comment = can_read
    can_action_review = RequestPermissionPolicy.can_action_accept
    can_action_critique = RequestPermissionPolicy.can_action_accept
    can_action_resubmit = RequestPermissionPolicy.can_action_cancel
