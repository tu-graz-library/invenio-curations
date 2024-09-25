# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations permissions."""

from invenio_rdm_records.services.generators import IfFileIsLocal
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import SystemProcess
from invenio_requests.services.generators import Creator, Receiver, Status
from invenio_requests.services.permissions import (
    PermissionPolicy as RequestPermissionPolicy,
)

from invenio_curations.services.generators import (
    CurationModerators,
    IfCurationRequestExists,
)


class CurationRDMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """RDM record policy for curations."""

    can_preview = RDMRecordPermissionPolicy.can_preview + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]
    can_view = RDMRecordPermissionPolicy.can_view + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]
    can_read = RDMRecordPermissionPolicy.can_read + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]
    can_read_files = RDMRecordPermissionPolicy.can_read_files + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    can_get_content_files = RDMRecordPermissionPolicy.can_get_content_files + [
        IfFileIsLocal(then_=can_read_files, else_=[SystemProcess()])
    ]

    can_read_draft = RDMRecordPermissionPolicy.can_read_draft + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]
    can_draft_read_files = RDMRecordPermissionPolicy.can_draft_read_files + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    can_draft_get_content_files = (
        RDMRecordPermissionPolicy.can_draft_get_content_files
        + [IfFileIsLocal(then_=can_draft_read_files, else_=[SystemProcess()])]
    )

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    can_draft_media_get_content_files = (
        RDMRecordPermissionPolicy.can_draft_media_get_content_files
        + [IfFileIsLocal(then_=can_preview, else_=[SystemProcess()])]
    )

    can_media_read_files = RDMRecordPermissionPolicy.can_media_read_files + [
        IfCurationRequestExists(then_=[CurationModerators()], else_=[])
    ]
    can_media_get_content_files = (
        RDMRecordPermissionPolicy.can_media_get_content_files
        + [IfFileIsLocal(then_=can_read, else_=[SystemProcess()])]
    )


class CurationRDMRequestPermissionPolicy(RequestPermissionPolicy):
    """Request permission policy for curations."""

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
