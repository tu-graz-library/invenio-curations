// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { i18next } from "@translations/invenio_curations/i18next";
import {
  RequestCritiqueButton,
  RequestResubmitButton,
  RequestReviewButton,
} from "./Buttons";
import { RDMCurationIcon } from "./Icons";
import {
  RequestCritiqueModalTrigger,
  RequestResubmitModalTrigger,
  RequestReviewModalTrigger,
} from "./ModalTriggers";
import { CritiquedStatus, ResubmittedStatus, ReviewStatus } from "./Status.js";
import {
  LabelStatusCritique,
  LabelStatusResubmit,
  LabelStatusReview,
} from "./StatusLabel.js";
import { LabelTypeRDMCuration } from "./TypeLabel.js";
import {
  TimelineCritiqueEvent,
  TimelineResubmitEvent,
  TimelineReviewEvent,
} from "./timelineActionEvents.js";

export const curationComponentOverrides = {
  ...defaultContribComponents,

  // label for the request type
  "RequestTypeLabel.layout.rdm-curation": LabelTypeRDMCuration,

  // icon for the request in the search
  "InvenioRequests.RequestTypeIcon.layout.rdm-curation": RDMCurationIcon,

  // labels for the request status
  "RequestStatusLabel.layout.critiqued": LabelStatusCritique,
  "RequestStatusLabel.layout.resubmitted": LabelStatusResubmit,
  "RequestStatusLabel.layout.review": LabelStatusReview,

  // status label for the request details page
  "RequestStatus.layout.review": ReviewStatus,
  "RequestStatus.layout.resubmitted": ResubmittedStatus,
  "RequestStatus.layout.critiqued": CritiquedStatus,

  // buttons for opening the action modal
  "RequestActionModalTrigger.critique": RequestCritiqueModalTrigger,
  "RequestActionModalTrigger.resubmit": RequestResubmitModalTrigger,
  "RequestActionModalTrigger.review": RequestReviewModalTrigger,

  // custom titles for modals
  "RequestActionModal.title.review": () => i18next.t("Start curation review"),
  "RequestActionModal.title.resubmit": () => i18next.t("Resubmit record for review"),
  "RequestActionModal.title.critique": () => i18next.t("Request changes"),

  // buttons for the action modal (to add an optional comment)
  "RequestActionButton.critique": RequestCritiqueButton,
  "RequestActionButton.resubmit": RequestResubmitButton,
  "RequestActionButton.review": RequestReviewButton,

  // the request status are called "review" (as it's in progress), "resubmitted", and "critiqued"
  "TimelineEvent.layout.review": TimelineReviewEvent,
  "TimelineEvent.layout.resubmitted": TimelineResubmitEvent,
  "TimelineEvent.layout.critiqued": TimelineCritiqueEvent,
};
