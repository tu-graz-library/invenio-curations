// This file is part of InvenioRDM
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { OverridableContext, overrideStore } from "react-overridable";
import { CurationsContainer } from "./CurationRequestForm";
import { getInputFromDOM } from "./utils";

const overriddenComponents = overrideStore.getAll();

const depositForm = document.getElementById("rdm-deposit-form");
if (depositForm) {
  const curationsContainer = document.createElement("div", {
    id: "curations-container",
  });

  depositForm.prepend(curationsContainer);
  ReactDOM.render(
    <OverridableContext.Provider value={overriddenComponents}>
      <CurationsContainer
        record={getInputFromDOM("deposits-record")}
        config={getInputFromDOM("deposits-config")}
        permissions={getInputFromDOM("deposits-record-permissions")}
      />
    </OverridableContext.Provider>,
    curationsContainer
  );
}
