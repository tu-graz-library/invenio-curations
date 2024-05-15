# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curation request type."""

from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_requests.customizations import RequestType, actions

from invenio_curations.notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)


class CurationCreateAndSubmitAction(actions.CreateAndSubmitAction):
    """Create and submit a request."""

    def execute(self, identity, uow):
        """Execute the create action."""
        receiver = self.request.receiver.resolve()
        record = self.request.topic.resolve()

        data = {
            "grants": [
                {
                    "permission": "preview",
                    "subject": {
                        "type": "role",
                        "id": str(receiver.id),
                    },
                    "origin": f"request:{self.request.id}",
                }
            ]
        }

        service = self.request.topic.get_resolver().get_service()
        # NOTE: we're using the system identity here to avoid the grant creation
        #       potentially being blocked by the requesting user's profile visibility
        service.access.bulk_create_grants(system_identity, record.pid.pid_value, data)
        uow.register(
            ParentRecordCommitOp(record.parent, indexer_context=dict(service=service))
        )

        uow.register(
            NotificationOp(
                CurationRequestSubmitNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )

        super().execute(identity, uow)


class CurationSubmitAction(actions.SubmitAction):
    """Submit action for user access requests."""

    status_from = ["created", "accepted", "cancelled"]

    def execute(self, identity, uow):
        """Execute the submit action."""
        uow.register(
            NotificationOp(
                CurationRequestSubmitNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )
        super().execute(identity, uow)


class CurationAcceptAction(actions.AcceptAction):
    """Accept a request."""

    # status_from = ["in_review"]
    status_from = ["submitted"]

    def execute(self, identity, uow):
        """Execute the accept action."""
        uow.register(
            NotificationOp(
                CurationRequestAcceptNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )

        super().execute(identity, uow)


class CurationDeclineAction(actions.DeclineAction):
    """Decline a request."""

    status_from = ["in_review"]


class CurationCancelAction(actions.CancelAction):
    """Cancel a request."""

    status_from = ["submitted", "in_review", "reviewed", "revised"]


class CurationExpireAction(actions.ExpireAction):
    """Expire a request."""

    status_from = ["submitted", "in_review", "reviewed", "revised"]


class CurationDeleteAction(actions.DeleteAction):
    """Delete a request."""

    status_from = ["created", "submitted", "accepted", "cancelled"]
    status_to = "deleted"


# class CurationInReviewAction(actions.RequestAction):
#     """Mark request as in review."""

#     status_from = ["submitted", "revised"]
#     status_to = "in_review"


# class CurationReviewAction(actions.RequestAction):
#     """Request changes for request."""

#     status_from = ["in_review"]
#     status_to = "reviewed"


# class CurationReviseAction(actions.RequestAction):
#     """Mark request as ready for review."""

#     status_from = ["reviewed", "accepted", "cancelled", "declined"]
#     status_to = "revised"


#
# Request
#
class CurationRequest(RequestType):
    """Curation request type."""

    type_id = "rdm-curation"
    name = _("Curation")

    create_action = "create"
    available_actions = {
        **RequestType.available_actions,
        "create": CurationCreateAndSubmitAction,
        "submit": CurationSubmitAction,
        "accept": CurationAcceptAction,
        "decline": CurationDeclineAction,
        "cancel": CurationCancelAction,
        "expire": CurationExpireAction,
        "delete": CurationDeleteAction,
        # "in_review": CurationInReviewAction,
        # "review": CurationReviewAction,
        # "revise": CurationReviseAction,
    }

    available_statuses = {
        **RequestType.available_statuses,
        # "in_review": RequestState.OPEN,
        # "reviewed": RequestState.OPEN,
        # "revised": RequestState.OPEN,
    }
    """Available statuses for the request.

    The keys in this dictionary is the set of available statuses, and their
    values are indicators whether this request is considered to be open, closed
    or undefined.
    """

    create_action = "create"
    """Defines the action that's able to create this request.

    This must be set to one of the available actions for the custom request type.
    """

    creator_can_be_none = False
    topic_can_be_none = False
    allowed_creator_ref_types = ["user", "community"]
    allowed_receiver_ref_types = ["group"]
    allowed_topic_ref_types = ["record"]
