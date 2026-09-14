# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations permissions."""

from typing import Final

from invenio_rdm_records.requests import CommunitySubmission
from invenio_rdm_records.services.permissions import (
    RDMRecordPermissionPolicy,
    RDMRequestsPermissionPolicy,
)
from invenio_records_permissions.generators import SystemProcess
from invenio_records_resources.services.files.generators import IfTransferType
from invenio_records_resources.services.files.transfer import LOCAL_TRANSFER_TYPE
from invenio_requests.services.generators import Creator, Receiver

from ..requests.curation import CurationRequest
from .generators import (
    CurationModerators,
    IfCurationCreatorCancelEnabled,
    IfCurationRecordBasedExists,
    IfCurationRequestAccepted,
    IfCurationRequestBasedExists,
    IfCurationRequestBlocksEdit,
    IfRequestTypes,
    TopicPermission,
)


class CurationRDMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """RDM record policy for curations."""

    can_preview = RDMRecordPermissionPolicy.can_preview + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]
    can_view = RDMRecordPermissionPolicy.can_view + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]
    can_read = RDMRecordPermissionPolicy.can_read + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]
    can_read_files = RDMRecordPermissionPolicy.can_read_files + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]

    can_review = RDMRecordPermissionPolicy.can_review + [CurationModerators()]

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    # Use CurationModerators() directly to avoid re-evaluating can_read_files (which may trigger an ES query).
    can_get_content_files = RDMRecordPermissionPolicy.can_get_content_files + [
        IfTransferType(LOCAL_TRANSFER_TYPE, [CurationModerators()]),
        SystemProcess(),
    ]

    can_read_draft = RDMRecordPermissionPolicy.can_read_draft + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]
    can_draft_read_files = RDMRecordPermissionPolicy.can_draft_read_files + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    # Use CurationModerators() directly to avoid re-evaluating can_draft_read_files (which may trigger an ES query).
    can_draft_get_content_files = (
        RDMRecordPermissionPolicy.can_draft_get_content_files
        + [
            IfTransferType(LOCAL_TRANSFER_TYPE, [CurationModerators()]),
            SystemProcess(),
        ]
    )

    # in order to get all base permissions in, we just add ours instead of adapting the then_ clause of the base permission
    # Use CurationModerators() directly to avoid re-evaluating can_preview (which may trigger an ES query).
    can_draft_media_get_content_files = (
        RDMRecordPermissionPolicy.can_draft_media_get_content_files
        + [
            IfTransferType(LOCAL_TRANSFER_TYPE, [CurationModerators()]),
            SystemProcess(),
        ]
    )

    # When CURATIONS_BLOCK_EDIT_DURING_REVIEW is True and request is in a blocking state,
    # allow moderators to still update the draft (e.g. to make corrections during review).
    can_update_draft = [  # noqa: RUF012
        IfCurationRequestBlocksEdit(
            then_=[CurationModerators()],
            else_=RDMRecordPermissionPolicy.can_update_draft,
        ),
    ]

    # RDMRecordPermissionPolicy.can_publish references the base can_review list
    # object directly, so it does not pick up our can_review extension above -
    # curators need this granted separately to publish edits themselves.
    can_publish = RDMRecordPermissionPolicy.can_publish + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]

    can_media_read_files = RDMRecordPermissionPolicy.can_media_read_files + [
        IfCurationRecordBasedExists(then_=[CurationModerators()], else_=[]),
    ]
    can_media_get_content_files = (
        RDMRecordPermissionPolicy.can_media_get_content_files
        + [
            IfTransferType(LOCAL_TRANSFER_TYPE, can_read),
            SystemProcess(),
        ]
    )


class CurationRDMRequestsPermissionPolicy(RDMRequestsPermissionPolicy):
    """Customized permission policy for sane handling of curation requests."""

    curation_request_record_review = IfRequestTypes(
        [CurationRequest],
        then_=[TopicPermission(permission_name="can_review")],
        else_=[],
    )

    # Only allow community-submission requests to be accepted after the rdm-curation request has been accepted
    # (if curation request exists).
    _can_communities_curation_accept: Final = [
        IfCurationRequestBasedExists(
            then_=[
                IfCurationRequestAccepted(
                    then_=RDMRequestsPermissionPolicy.can_action_accept,
                    else_=[],
                ),
            ],
            else_=RDMRequestsPermissionPolicy.can_action_accept,
        ),
    ]

    can_action_accept: Final = [
        IfRequestTypes(
            request_types=[CommunitySubmission],
            then_=_can_communities_curation_accept,
            else_=RDMRequestsPermissionPolicy.can_action_accept,
        ),
    ]

    # Update can read and can comment with new states
    can_read: Final = [
        # Have to explicitly check the request type and circumvent using status, as creator/receiver will add a query filter where one entity must be the user.
        IfRequestTypes(
            [CurationRequest],
            then_=[
                Creator(),
                Receiver(),
                TopicPermission(permission_name="can_review"),
                SystemProcess(),
            ],
            else_=RDMRequestsPermissionPolicy.can_read,
        ),
    ]
    can_create_comment = can_read
    can_reply_comment = can_create_comment

    # Update submit to also allow record reviewers/managers for curation requests
    can_action_submit = RDMRequestsPermissionPolicy.can_action_submit + [
        curation_request_record_review,
    ]

    # Add new actions
    can_action_review = RDMRequestsPermissionPolicy.can_action_accept
    can_action_critique = RDMRequestsPermissionPolicy.can_action_accept
    can_action_resubmit = can_action_submit
    can_action_pending_resubmission = can_action_resubmit

    # Allow creators to cancel their own curation requests
    can_action_cancel = RDMRequestsPermissionPolicy.can_action_cancel + [
        IfCurationCreatorCancelEnabled(then_=[Creator()], else_=[]),
    ]
