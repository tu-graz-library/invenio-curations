# -*- coding: utf-8 -*-
#
# Copyright (C)      2023 CERN.
# Copyright (C) 2023-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Facet definitions."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_requests.services.requests import facets

type = TermsFacet(  # noqa: A001
    field="type",
    label=_("Type"),
    value_labels={
        **facets.type._value_labels,  # noqa: SLF001
        "rdm-curation": _("RDM Curation"),
    },
)

status = TermsFacet(
    field="status",
    label=_("Status"),
    value_labels={
        **facets.status._value_labels,  # noqa: SLF001
        "review": _("In review"),
        "critiqued": _("Changes requested"),
        "resubmitted": _("Resubmitted"),
    },
)
