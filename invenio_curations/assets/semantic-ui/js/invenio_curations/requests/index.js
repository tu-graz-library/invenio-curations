// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024-2026 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { i18next } from "@translations/invenio_curations/i18next";
import {
  RequestAcceptButton,
  RequestCritiqueButton,
  RequestResubmitButton,
  RequestReviewButton,
} from "./Buttons";
import { RDMCurationIcon } from "./Icons";
import {
  RequestAcceptModalTrigger,
  RequestCritiqueModalTrigger,
  RequestResubmitModalTrigger,
  RequestReviewModalTrigger,
} from "./ModalTriggers";
import {
  CritiquedStatus,
  PendingResubmissionStatus,
  ResubmittedStatus,
  ReviewStatus,
} from "./Status.js";
import {
  LabelStatusCritique,
  LabelStatusPendingResubmission,
  LabelStatusResubmit,
  LabelStatusReview,
} from "./StatusLabel.js";
import { LabelTypeRDMCuration } from "./TypeLabel.js";
import { CurationRequestsResultsItemTemplateDashboard } from "./OverviewRequestItem.js";
import {
  TimelineCritiqueEvent,
  TimelineResubmitEvent,
  TimelineReviewEvent,
  TimelinePendingResubmission,
  TimelineAcceptEvent,
  TimelineDeclineEvent,
  TimelineCancelEvent,
  TimelineSubmitEvent,
} from "./timelineActionEvents.js";
import { RequestMetadata } from "./RequestMetadataLayout.js";

export const curationComponentOverrides = {
  ...defaultContribComponents,

  // label for the request type
  "RequestTypeLabel.layout.rdm-curation": LabelTypeRDMCuration,

  // icon for the request in the search
  "InvenioRequests.RequestTypeIcon.layout.rdm-curation": RDMCurationIcon,

  "InvenioRequest.RequestMetadata.Layout": RequestMetadata,

  // requests overview dashboard card (/curations/overview): show who started review
  "InvenioAppRdm.DashboardRequests.ResultsList.item":
    CurationRequestsResultsItemTemplateDashboard,

  // labels for the request status
  "RequestStatusLabel.layout.critiqued": LabelStatusCritique,
  "RequestStatusLabel.layout.resubmitted": LabelStatusResubmit,
  "RequestStatusLabel.layout.review": LabelStatusReview,
  "RequestStatusLabel.layout.pending_resubmission": LabelStatusPendingResubmission,

  // status label for the request details page
  "RequestStatus.layout.review": ReviewStatus,
  "RequestStatus.layout.resubmitted": ResubmittedStatus,
  "RequestStatus.layout.critiqued": CritiquedStatus,
  "RequestStatus.layout.pending_resubmission": PendingResubmissionStatus,

  // buttons for opening the action modal
  "RequestActionModalTrigger.accept": RequestAcceptModalTrigger,
  "RequestActionModalTrigger.critique": RequestCritiqueModalTrigger,
  "RequestActionModalTrigger.resubmit": RequestResubmitModalTrigger,
  "RequestActionModalTrigger.review": RequestReviewModalTrigger,
  "RequestActionModalTrigger.pending_resubmission": () => null,

  // custom titles for modals
  "RequestActionModal.title.review": () => i18next.t("Start curation review"),
  "RequestActionModal.title.resubmit": () => i18next.t("Resubmit record for review"),
  "RequestActionModal.title.critique": () => i18next.t("Request changes"),

  // buttons for the action modal (to add an optional comment)
  "RequestActionButton.accept": RequestAcceptButton,
  "RequestActionButton.critique": RequestCritiqueButton,
  "RequestActionButton.resubmit": RequestResubmitButton,
  "RequestActionButton.review": RequestReviewButton,
  "RequestActionButton.pending_resubmission": () => null,

  // the request status are called "review" (as it's in progress), "resubmitted", and "critiqued"
  "TimelineEvent.layout.review": TimelineReviewEvent,
  "TimelineEvent.layout.resubmitted": TimelineResubmitEvent,
  "TimelineEvent.layout.critiqued": TimelineCritiqueEvent,
  "TimelineEvent.layout.pending_resubmission": TimelinePendingResubmission,
  "TimelineEvent.layout.accept": TimelineAcceptEvent,
  "TimelineEvent.layout.accepted": TimelineAcceptEvent,
  "TimelineEvent.layout.decline": TimelineDeclineEvent,
  "TimelineEvent.layout.declined": TimelineDeclineEvent,
  "TimelineEvent.layout.cancel": TimelineCancelEvent,
  "TimelineEvent.layout.cancelled": TimelineCancelEvent,
  "TimelineEvent.layout.submit": TimelineSubmitEvent,
  "TimelineEvent.layout.submitted": TimelineSubmitEvent,

};
