// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import React from "react";
import { Label } from "semantic-ui-react";

export const LabelTypeRDMCuration = (props) => (
  <Label horizontal className="primary" size="small">
    {i18next.t("Curation review")}
  </Label>
);
