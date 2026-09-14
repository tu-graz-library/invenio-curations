// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import CurationTimelineActionEvent from "./CurationTimelineActionEvent";
import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";

export const TimelineCritiqueEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="exclamation circle"
    event={event}
    eventContent={i18next.t("requested changes")}
    iconColor="negative"
  />
);

export const TimelineResubmitEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="paper hand outline"
    event={event}
    eventContent={i18next.t("resubmitted the record for review")}
    iconColor="neutral"
  />
);

export const TimelineReviewEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="eye"
    event={event}
    eventContent={i18next.t("started a review")}
    iconColor="neutral"
  />
);

export const TimelinePendingResubmission = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="eye"
    event={event}
    eventContent={i18next.t("edited the record")}
    iconColor="neutral"
  />
);

export const TimelineAcceptEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="check circle"
    event={event}
    eventContent={i18next.t("accepted and published the record")}
    iconColor="positive"
  />
);

export const TimelineDeclineEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="times circle"
    event={event}
    eventContent={i18next.t("declined the curation request")}
    iconColor="negative"
  />
);

export const TimelineCancelEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="times circle"
    event={event}
    eventContent={i18next.t("cancelled the curation request")}
    iconColor="neutral"
  />
);

export const TimelineSubmitEvent = ({ event }) => (
  <CurationTimelineActionEvent
    iconName="paper hand outline"
    event={event}
    eventContent={i18next.t("submitted the record for curation")}
    iconColor="neutral"
  />
);
