/*
 * SPDX-FileCopyrightText: 2024 TU Wien.
 * SPDX-FileCopyrightText: 2024 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";
import { Label } from "semantic-ui-react";

export const LabelTypeRDMCuration = () => (
  <Label horizontal className="primary" size="small">
    {i18next.t("Curation review")}
  </Label>
);
