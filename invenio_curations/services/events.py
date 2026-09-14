# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Custom events module."""


from invenio_requests.customizations.event_types import (
    CommentEventType,
    FileDetailsSchema,
)
from invenio_requests.records.api import RequestEventFormat
from marshmallow import fields, validate
from marshmallow_utils import fields as utils_fields


class CurationCommentEventType(CommentEventType):
    """Curation Comment event type with extended payload (reference_draft, files)."""

    @staticmethod
    def payload_schema():
        """Extend CommentEventType schema with reference_draft and files fields."""
        return dict(
            content=utils_fields.SanitizedHTML(
                required=True, validate=validate.Length(min=1),
            ),
            format=fields.Str(
                validate=validate.OneOf(choices=[e.value for e in RequestEventFormat]),
                load_default=RequestEventFormat.HTML.value,
            ),
            # Stores the draft snapshot used as the comparison base for future comment updates,
            # avoiding the need for draft revisions.
            reference_draft=fields.Str(required=False),
            files=fields.List(fields.Nested(FileDetailsSchema)),
        )
