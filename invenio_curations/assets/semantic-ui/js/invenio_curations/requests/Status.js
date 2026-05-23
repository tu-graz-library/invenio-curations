/*
 * SPDX-FileCopyrightText: 2024 TU Wien.
 * SPDX-FileCopyrightText: 2024-2025 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";
import { Icon } from "semantic-ui-react";

export const CritiquedStatus = () => (
  <div>
    <Icon name="exclamation circle" />
    <span>{i18next.t("Changes requested")}</span>
  </div>
);

export const ResubmittedStatus = () => (
  <div>
    <Icon name="paper hand outline" />
    <span>{i18next.t("Resubmitted for review")}</span>
  </div>
);

export const ReviewStatus = () => (
  <div>
    <Icon name="eye" />
    <span>{i18next.t("In review")}</span>
  </div>
);

export const PendingResubmissionStatus = () => (
  <div>
    <Icon name="eye" />
    <span>{i18next.t("Pending resubmission")}</span>
  </div>
);
