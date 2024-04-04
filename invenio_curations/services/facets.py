# -*- coding: utf-8 -*-
#
# Copyright (C)      2023 CERN.
# Copyright (C) 2023-2024 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

type = TermsFacet(
    field="type",
    label=_("Type"),
    value_labels={
        "curation": _("Curation review"),
    },
)

status = TermsFacet(
    field="status",
    label=_("Status"),
    value_labels={
        "submitted": _("Submitted"),
        "expired": _("Expired"),
        "accepted": _("Accepted"),
        "declined": _("Declined"),
        "cancelled": _("Cancelled"),
        # TODO: add other stati
    },
)


is_open = TermsFacet(
    field="is_open",
    label=_("Open"),
    value_labels={
        "true": _("Open"),
        "false": _("Closed"),
    },
)
