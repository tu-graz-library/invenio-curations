# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curation request type."""

from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_requests.customizations import RequestState, RequestType, actions

from invenio_curations.notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestCritiqueNotificationBuilder,
    CurationRequestResubmitNotificationBuilder,
    CurationRequestReviewNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)


class CurationCreateAndSubmitAction(actions.CreateAndSubmitAction):
    """Create and submit a request."""

    def execute(self, identity, uow):
        """Execute the create & submit action."""
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

    # submit can only happen once.
    status_from = ["created"]

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

    # Require to go through review before accepting.
    status_from = ["review"]

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

    # Instead of declining, the record should be critiqued.
    status_from = []


class CurationCancelAction(actions.CancelAction):
    """Cancel a request."""

    # A user might want to cancel their request.
    # Also done when a draft for an already published record is deleted/discarded
    status_from = [
        "accepted",
        "cancelled",
        "created",
        "critiqued",
        "declined",
        "expired",
        "resubmitted",
        "review",
        "submitted",
    ]


class CurationExpireAction(actions.ExpireAction):
    """Expire a request."""

    status_from = ["submitted", "critiqued", "resubmitted"]


class CurationDeleteAction(actions.DeleteAction):
    """Delete a request."""

    # When a user deletes their draft, the request will get deleted. Should be possible from every state.
    # Usually delete is only possible programmatically, as the base permissions allow user driven deletion
    # only during `created` status
    status_from = [
        "accepted",
        "cancelled",
        "created",
        "critiqued",
        "declined",
        "expired",
        "resubmitted",
        "review",
        "submitted",
    ]


class CurationReviewAction(actions.RequestAction):
    """Mark request as review."""

    status_from = ["submitted", "resubmitted"]
    status_to = "review"

    def execute(self, identity, uow):
        """Execute the review action."""
        uow.register(
            NotificationOp(
                CurationRequestReviewNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )

        super().execute(identity, uow)


class CurationCritiqueAction(actions.RequestAction):
    """Request changes for request."""

    status_from = ["review"]
    status_to = "critiqued"

    def execute(self, identity, uow):
        """Execute the critique action."""
        uow.register(
            NotificationOp(
                CurationRequestCritiqueNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )

        super().execute(identity, uow)


class CurationResubmitAction(actions.RequestAction):
    """Mark request as ready for review."""

    status_from = ["critiqued", "accepted", "cancelled", "declined"]
    status_to = "resubmitted"

    def execute(self, identity, uow):
        """Execute the resubmit action."""
        uow.register(
            NotificationOp(
                CurationRequestResubmitNotificationBuilder.build(
                    identity=identity, request=self.request
                )
            )
        )
        super().execute(identity, uow)


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
        "review": CurationReviewAction,
        "critique": CurationCritiqueAction,
        "resubmit": CurationResubmitAction,
    }

    available_statuses = {
        **RequestType.available_statuses,
        "review": RequestState.OPEN,
        "critiqued": RequestState.OPEN,
        "resubmitted": RequestState.OPEN,
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
