// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";
import { Icon, Label } from "semantic-ui-react";

export const LabelStatusCritique = () => {
  return (
    <Label horizontal className="critiqued" size="small">
      <Icon name="exclamation circle" />
      {i18next.t("Review available")}
    </Label>
  );
};

export const LabelStatusResubmit = () => {
  return (
    <Label horizontal className="resubmitted" size="small">
      <Icon name="hand paper outline" />
      {i18next.t("Resubmitted")}
    </Label>
  );
};

export const LabelStatusReview = () => {
  return (
    <Label horizontal className="review" size="small">
      <Icon name="eye" />
      {i18next.t("In review")}
    </Label>
  );
};
