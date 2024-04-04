# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for curations."""

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

CURATIONS_TIMELINE_PAGE_SIZE = 15
"""Amount of items per page on the request details timeline"""


CURATIONS_MODERATION_ROLE = "administration-rdm-records-curation"
"""ID of the Role used for record curation."""

CURATIONS_SEARCH_REQUESTS = {
    "facets": ["type", "status"],
    "sort": ["bestmatch", "newest", "oldest"],
}
"""Curation requests search configuration (i.e list of curations requests)"""
