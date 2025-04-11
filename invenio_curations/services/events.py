# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

import marshmallow as ma
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    unit_of_work,
)
from invenio_requests.customizations.event_types import CommentEventType
from invenio_requests.services import RequestEventsService
from marshmallow import RAISE, fields, validate
from marshmallow_utils import fields as utils_fields


class CurationCommentEventType(CommentEventType):
    """Comment event type."""

    def payload_schema():
        """Return payload schema as a dictionary."""
        # we need to import here because of circular imports
        from invenio_requests.records.api import RequestEventFormat

        return dict(
            content=utils_fields.SanitizedHTML(
                required=True, validate=validate.Length(min=1)
            ),
            # base_content_object represents the actual object from which the content was generated
            # this helps to avoid parsing actual HTML comments.
            base_content_object=fields.Str(required=False),
            format=fields.Str(
                validate=validate.OneOf(choices=[e.value for e in RequestEventFormat]),
                load_default=RequestEventFormat.HTML.value,
            ),
        )

    payload_required = True


class CurationsEventsService(RequestEventsService):

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None, expand=False):
        """Update a comment (only comments can be updated)."""
        event = self._get_event(id_)
        request = self._get_request(event.request.id)
        self.require_permission(
            identity, "update_comment", request=request, event=event
        )
        self.check_revision_id(event, revision_id)

        schema = self._wrap_schema(event.type.marshmallow_schema())
        data, _ = schema.load(
            data,
            context=dict(identity=identity, record=event, event_type=event.type),
        )
        event["payload"]["content"] = data["payload"]["content"]
        event["payload"]["base_content_object"] = data["payload"]["base_content_object"]
        event["payload"]["format"] = data["payload"]["format"]

        uow.register(RecordCommitOp(event, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            event,
            schema=schema,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )
