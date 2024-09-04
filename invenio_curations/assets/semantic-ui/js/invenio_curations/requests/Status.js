// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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
