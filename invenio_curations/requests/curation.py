# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio-Curation is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

""" Curation request type."""

from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.uow import ParentRecordCommitOp
from invenio_i18n import lazy_gettext as _
from invenio_notifications.services.uow import NotificationOp
# TODO: provide service in a different way to not depend on rdm-records
from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_requests.customizations import RequestType, actions
from invenio_requests.customizations.states import RequestState


class CurationSubmitAction(actions.CreateAndSubmitAction):
    """Submit action for user access requests."""

    def execute(self, identity, uow):
        """Execute the submit action."""

        # self.request["title"] = self.request.topic.resolve().metadata["title"]
        receiver = self.request.receiver.resolve()
        record = self.request.topic.resolve()

        data = {
            "permission": "preview",
            "subject": {
                "type": "role",
                "id": str(receiver.id),
            },
            "origin": f"request:{self.request.id}",
        }

        service = current_rdm_records_service
        # NOTE: we're using the system identity here to avoid the grant creation
        #       potentially being blocked by the requesting user's profile visibility
        service.access.create_grant(system_identity, record.pid.pid_value, data)
        uow.register(
            ParentRecordCommitOp(record.parent, indexer_context=dict(service=service))
        )

        # TODO: send notification to group
        # uow.register(
        #     NotificationOp(
        #         UserAccessRequestSubmitNotificationBuilder.build(request=self.request)
        #     )
        # )
        super().execute(identity, uow)


class CurationAcceptAction(actions.AcceptAction):
    """Decline a request."""

    status_from = ["in_review"]

    def execute(self, identity, uow):
        """Execute the accept action."""

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


class CurationInReviewAction(actions.RequestAction):
    """Mark request as in review."""

    status_from = ["submitted", "revised"]
    status_to = "in_review"


class CurationReviewAction(actions.RequestAction):
    """Request changes for request."""

    status_from = ["in_review"]
    status_to = "reviewed"


class CurationReviseAction(actions.RequestAction):
    """Mark request as ready for review."""

    status_from = ["reviewed", "accepted", "cancelled", "declined"]
    status_to = "revised"


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
        "create": CurationSubmitAction,
        "submit": CurationSubmitAction,
        "accept": CurationAcceptAction,
        "decline": CurationDeclineAction,
        "cancel": CurationCancelAction,
        "expire": CurationExpireAction,
        "in_review": CurationInReviewAction,
        "review": CurationReviewAction,
        "revise": CurationReviseAction,
    }

    available_statuses = {
        **RequestType.available_statuses,
        "in_review": RequestState.OPEN,
        "reviewed": RequestState.OPEN,
        "revised": RequestState.OPEN,
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
