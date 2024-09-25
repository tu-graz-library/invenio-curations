# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for curations."""

from invenio_curations.notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestCritiqueNotificationBuilder,
    CurationRequestResubmitNotificationBuilder,
    CurationRequestReviewNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)
from invenio_curations.services import facets

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
