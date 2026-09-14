# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for curations."""

from .notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestCritiqueNotificationBuilder,
    CurationRequestResubmitNotificationBuilder,
    CurationRequestReviewNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)
from .services import facets
from .services.diff import DiffDescription

CURATIONS_FACETS = {
    "type": {
        "facet": facets.type,
        "ui": {
            "field": "type",
        },
    },
    "status": {
        "facet": facets.status,
        "ui": {
            "field": "status",
        },
    },
}
"""Invenio requests facets."""


CURATIONS_ALLOW_PUBLISHING_EDITS = False
"""Allow publishing of metadata edits for already published records.

This allows users to modify their record's metadata and publish those changes
without going through another curation review.
The idea here is that the record has already passed through an initial quality check
anyway and it's very unlikely that anybody would update the metadata afterwards in
a way that decreases their quality.
Even if that happens, InvenioRDM stores `revisions` for record metadata.
"""

CURATIONS_TIMELINE_PAGE_SIZE = 15
"""Amount of items per page on the request details timeline"""


CURATIONS_MODERATION_ROLE = "administration-rdm-records-curation"
"""ID of the Role used for record curation."""

CURATIONS_SEARCH_REQUESTS = {
    "facets": ["type", "status"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Curation requests search configuration (i.e list of curations requests)"""

CURATIONS_NOTIFICATIONS_BUILDERS = {
    builder.type: builder
    for builder in [
        CurationRequestAcceptNotificationBuilder,
        CurationRequestCritiqueNotificationBuilder,
        CurationRequestResubmitNotificationBuilder,
        CurationRequestReviewNotificationBuilder,
        CurationRequestSubmitNotificationBuilder,
    ]
}
"""Curation related notification builders as map for easy import."""

CURATIONS_ENABLE_REQUEST_COMMENTS = False
"""Enable or disable the generation of diff comments on ``rdm-curation`` requests.

Set this in order to activate the automatic creation/update of request comments
based on the difference found between draft states of an unpublished record
that is in the curation phase.
"""

CURATIONS_COMMENTS_CLASSES = [DiffDescription]
"""Extend curations comment classes for more diff customization.

List with all custom classes defined for rendering a change in a draft field.
"""

CURATIONS_COMMENT_TEMPLATE_FILE = "comment-template.html"
"""Curation comment template file.

Choose a file from the instance's templates folder to render the request comment.
More details in README.
"""

CURATIONS_AUTO_PUBLISH_ON_ACCEPT = False
"""Automatically publish the record when a curation request is accepted."""

CURATIONS_AUTO_SUBMIT_COMMUNITY = False
"""Automatically submit pending community inclusion requests after curation accept."""

CURATIONS_COMMENTS_USE_USER_IDENTITY = False
"""Use the user's identity for comment actions instead of system identity."""

CURATIONS_BLOCK_EDIT_DURING_REVIEW = False
"""Block editing of drafts while a curation request is under review."""

CURATIONS_ALLOW_CREATOR_CANCEL = False
"""Allow record creators to cancel their own curation requests."""

CURATIONS_PRIVILEGED_ROLES = ["administration"]
"""Curation privileged roles.

Users or processes with these roles can bypass curation checks.
Note: this does not apply for community curations. This config should be used just
to allow admins to publish records without having to perform the extra steps necessary
for approval.
Also used for creating rdm-records demo records in testing.
"""

CURATIONS_NOTIFICATIONS_OVERRIDE_EMAIL = None
"""If set, redirect all curation request notification emails to this address.

When set to a single email address, all curation-related notification emails
(submit, resubmit, review, accept, critique) are sent only to this address,
instead of the actually resolved recipients (e.g. all members of the curation
group, or the request creator).

Leave unset (``None``) to send notifications to the normal recipients.
"""

CURATIONS_TIMELINE_ABSOLUTE_DATES = False
"""Display absolute dates instead of relative dates in the curation timeline.

When set to ``True``, timestamps in timeline events and the request metadata sidebar
are rendered as locale-formatted datetime strings (e.g. "Jun 30, 2026, 2:30 PM")
instead of relative values (e.g. "3 minutes ago").

Can be toggled via the environment variable
``INVENIO_CURATIONS_TIMELINE_ABSOLUTE_DATES=true``.
"""
