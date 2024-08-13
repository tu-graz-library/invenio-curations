// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Label, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_requests/i18next";

export const LabelStatusCritique = (props) => {
  return (
    <Label horizontal className="critiqued" size="small">
      <Icon name="exclamation circle" />
      {i18next.t("Review available")}
    </Label>
  );
};

export const LabelStatusResubmit = (props) => {
  return (
    <Label horizontal className="resubmitted" size="small">
      <Icon name="hand paper outline" />
      {i18next.t("Resubmitted")}
    </Label>
  );
};

export const LabelStatusReview = (props) => {
  return (
    <Label horizontal className="review" size="small">
      <Icon name="eye" />
      {i18next.t("In review")}
    </Label>
  );
};
