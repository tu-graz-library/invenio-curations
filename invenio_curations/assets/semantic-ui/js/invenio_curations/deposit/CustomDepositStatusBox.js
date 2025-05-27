// This file is part of InvenioRDM
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { StatusDisplay } from "./StatusDisplay";
import { connect } from "react-redux";
import { withCurationStatus } from "./withCurationStatus";

const EnhancedStatusDisplay = withCurationStatus(StatusDisplay);

// create the connected component that gets record state
const mapStateToProps = (state) => {
  const record = state.deposit.record;
  return {
    record: state.deposit.record,
    request: record?.parent?.review || null,
  };
};

export const CustomDepositStatusBox = connect(mapStateToProps)(EnhancedStatusDisplay);
