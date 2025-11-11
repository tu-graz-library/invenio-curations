# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2025 Graz University of Technology.
#
# Invenio-Curation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Curation request type."""

from __future__ import annotations

from typing import ClassVar

from flask_principal import Identity
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
from invenio_records_resources.services.uow import UnitOfWork
from invenio_requests.customizations import RequestState, RequestType, actions
from invenio_requests.customizations.actions import RequestAction

from invenio_curations.notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestCritiqueNotificationBuilder,
    CurationRequestResubmitNotificationBuilder,
    CurationRequestReviewNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)


class CurationCreateAndSubmitAction(actions.CreateAndSubmitAction):
    """Create and submit a request."""

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the create & submit action."""
        uow.register(
            NotificationOp(
                CurationRequestSubmitNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )

        super().execute(identity, uow)


class CurationSubmitAction(actions.SubmitAction):
    """Submit action for user access requests."""

    # list of statuses this action can be performed from
    status_from: ClassVar[list[str]] = ["created"]

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the submit action."""
        uow.register(
            NotificationOp(
                CurationRequestSubmitNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )
        super().execute(identity, uow)


class CurationAcceptAction(actions.AcceptAction):
    """Accept a request."""

    # Require to go through review before accepting.
    status_from: ClassVar[list[str]] = ["review"]

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the accept action."""
        uow.register(
            NotificationOp(
                CurationRequestAcceptNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )

        super().execute(identity, uow)


class CurationDeclineAction(actions.DeclineAction):
    """Decline a request."""

    # Instead of declining, the record should be critiqued.
    status_from: ClassVar[list[str]] = []


class CurationCancelAction(actions.CancelAction):
    """Cancel a request."""

    # A user might want to cancel their request.
    # Also done when a draft for an already published record is deleted/discarded
    status_from: ClassVar[list[str]] = [
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

    status_from: ClassVar[list[str]] = ["submitted", "critiqued", "resubmitted"]


class CurationDeleteAction(actions.DeleteAction):
    """Delete a request."""

    # When a user deletes their draft, the request will get deleted. Should be possible from every state.
    # Usually delete is only possible programmatically, as the base permissions allow user driven deletion
    # only during `created` status
    status_from: ClassVar[list[str]] = [
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

    status_from: ClassVar[list[str]] = ["submitted", "resubmitted"]
    status_to: ClassVar[str] = "review"

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the review action."""
        uow.register(
            NotificationOp(
                CurationRequestReviewNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )

        super().execute(identity, uow)


class CurationCritiqueAction(actions.RequestAction):
    """Request changes for request."""

    status_from: ClassVar[list[str]] = ["review"]
    status_to: ClassVar[str] = "critiqued"

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the critique action."""
        uow.register(
            NotificationOp(
                CurationRequestCritiqueNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )

        super().execute(identity, uow)


class CurationResubmitAction(actions.RequestAction):
    """Mark request as ready for review."""

    status_from: ClassVar[list[str]] = [
        "critiqued",
        "pending_resubmission",
        "cancelled",
        "declined",
    ]
    status_to: ClassVar[str] = "resubmitted"

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the resubmit action."""
        uow.register(
            NotificationOp(
                CurationRequestResubmitNotificationBuilder.build(
                    identity=identity,
                    request=self.request,
                ),
            ),
        )
        super().execute(identity, uow)


class CurationPendingResubmissionAction(actions.RequestAction):
    """Mark request in a pending state, waiting to be resubmitted."""

    status_from: ClassVar[list[str]] = [
        "accepted",
        "cancelled",
        "declined",
    ]
    status_to: ClassVar[str] = "pending_resubmission"

    def execute(self, identity: Identity, uow: UnitOfWork) -> None:
        """Execute the pending_resubmit action."""
        super().execute(identity, uow)


#
# Request
#
class CurationRequest(RequestType):
    """Curation request type."""

    type_id: ClassVar[str] = "rdm-curation"
    name: ClassVar[str] = _("Curation")

    # Dict mapping action names to action classes
    available_actions: ClassVar[dict[str, type[RequestAction]]] = {
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
        "pending_resubmission": CurationPendingResubmissionAction,
    }

    # Dict mapping status names to RequestState values
    available_statuses: ClassVar[dict[str, RequestState]] = {
        **RequestType.available_statuses,
        "review": RequestState.OPEN,
        "critiqued": RequestState.OPEN,
        "resubmitted": RequestState.OPEN,
        "pending_resubmission": RequestState.CLOSED,
    }
    """Available statuses for the request.

    The keys in this dictionary is the set of available statuses, and their
    values are indicators whether this request is considered to be open, closed
    or undefined.
    """

    create_action: ClassVar[str] = "create"
    """Defines the action that's able to create this request.

    This must be set to one of the available actions for the custom request type.
    """

    creator_can_be_none: ClassVar[bool] = False
    topic_can_be_none: ClassVar[bool] = False
    allowed_creator_ref_types: ClassVar[list[str]] = ["user", "community"]
    allowed_receiver_ref_types: ClassVar[list[str]] = ["group"]
    allowed_topic_ref_types: ClassVar[list[str]] = ["record"]
