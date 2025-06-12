# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Record curation service errors."""

from invenio_i18n import lazy_gettext as _


class OpenRecordCurationRequestAlreadyExistsError(Exception):
    """An open request already exists for the record."""

    description = _("An open curation request for this record exists already.")


class CurationRequestNotAcceptedError(Exception):
    """No curation request exists yet."""

    description = _("The record has not been curated yet.")


class RoleNotFoundError(Exception):
    """The role does not exist."""

    def __init__(self, role_name: str) -> None:
        """Initialise error."""
        super().__init__(
            _("A role with name '%(name)s' does not exist.", name=role_name),
        )
