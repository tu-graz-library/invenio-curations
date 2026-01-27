# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Custom events module."""

from typing import cast

from invenio_requests.customizations.event_types import CommentEventType
from marshmallow import fields


class CurationCommentEventType(CommentEventType):
    """Curation Comment event type."""

    def payload_schema() -> dict:
        """Return payload schema as a dictionary."""
        schema = cast(dict, CommentEventType.payload_schema())

        # reference_draft represents the base of comparison for the content (a custom display of a diff)
        # if the comment needs an update, new data is compared with the data present in this field, thus
        # avoiding the need for draft revisions.
        schema["reference_draft"] = fields.Str(required=False)

        return schema
