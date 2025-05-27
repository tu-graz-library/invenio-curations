// This file is part of InvenioRDM
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { OverridableContext, overrideStore } from "react-overridable";

import { CurationsContainer } from "./CurationRequestForm";
import { CustomDepositStatusBox } from "./CustomDepositStatusBox";
import { DepositBox } from "./DepositBox";
import React from "react";
import ReactDOM from "react-dom";
import { StatusDisplay } from "./StatusDisplay";
import { getInputFromDOM } from "./utils";
import { withCurationStatus } from "./withCurationStatus";

const overriddenComponents = overrideStore.getAll();

// Export components for use in overridable registry
export {
  DepositBox,
  CustomDepositStatusBox,
  withCurationStatus,
  StatusDisplay,
};

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
  )
}
