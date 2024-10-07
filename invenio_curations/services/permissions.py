# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Curations permissions."""

from invenio_rdm_records.requests import CommunitySubmission
from invenio_rdm_records.services.generators import IfFileIsLocal
from invenio_rdm_records.services.permissions import (
    RDMRecordPermissionPolicy,
    RDMRequestsPermissionPolicy,
)
from invenio_records_permissions.generators import SystemProcess
from invenio_requests.services.generators import Creator, Receiver, Status

from invenio_curations.requests.curation import CurationRequest
from invenio_curations.services.generators import (
    CurationModerators,
    IfCurationRequestAccepted,
    IfCurationRequestExists,
    IfRequestTypes,
    TopicPermission,
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


class CurationRDMRequestsPermissionPolicy(RDMRequestsPermissionPolicy):
    """Customized permission policy for sane handling of curation requests."""

    curation_request_record_review = IfRequestTypes(
        [CurationRequest],
        then_=[TopicPermission(permission_name="can_review")],
        else_=[],
    )

    # Only allow community-submission requests to be accepted after the rdm-curation request has been accepted
    can_action_accept = [
        IfRequestTypes(
            request_types=[CommunitySubmission],
            then_=[
                IfCurationRequestAccepted(
                    then_=RDMRequestsPermissionPolicy.can_action_accept, else_=[]
                )
            ],
            else_=RDMRequestsPermissionPolicy.can_action_accept,
        )
    ]

    # Update can read and can comment with new states
    can_read = [
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
        )
    ]
    can_create_comment = can_read

    # Update submit to also allow record reviewers/managers for curation requests
    can_action_submit = RDMRequestsPermissionPolicy.can_action_submit + [
        curation_request_record_review
    ]

    # Add new actions
    can_action_review = RDMRequestsPermissionPolicy.can_action_accept
    can_action_critique = RDMRequestsPermissionPolicy.can_action_accept
    can_action_resubmit = can_action_submit
