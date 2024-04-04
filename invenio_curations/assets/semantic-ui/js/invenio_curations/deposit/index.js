// This file is part of InvenioRDM
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import { CurationsContainer } from "./CurationRequestForm";
import { OverridableContext, overrideStore } from "react-overridable";

const overriddenComponents = overrideStore.getAll();

// Copied from rdm-records to not depend on it.
export const getInputFromDOM = (elementName) => {
  const element = document.getElementsByName(elementName);
  if (element.length > 0 && element[0].hasAttribute("value")) {
    return JSON.parse(element[0].value);
  }
  return null;
};

const depositSidebar = document.getElementsByClassName("deposit-sidebar")[0];
if (depositSidebar) {
  const stickyMenu = depositSidebar.getElementsByClassName("sticky")[0];

  let curationsContainer = document.createElement("div", {
    id: "curations-container",
  });
  curationsContainer = stickyMenu.appendChild(curationsContainer);
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
