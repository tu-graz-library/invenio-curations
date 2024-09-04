// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import TimelineActionEvent from "@js/invenio_requests/components/TimelineActionEvent";
import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";

export const TimelineCritiqueEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="exclamation circle"
    event={event}
    eventContent={i18next.t("requested changes")}
    iconColor="negative"
  />
);

export const TimelineResubmitEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="paper hand outline"
    event={event}
    eventContent={i18next.t("resubmitted the record for review")}
    iconColor="neutral"
  />
);

export const TimelineReviewEvent = ({ event }) => (
  <TimelineActionEvent
    iconName="eye"
    event={event}
    eventContent={i18next.t("started a review")}
    iconColor="neutral"
  />
);
