/*
 * SPDX-FileCopyrightText: 2025 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { StatusDisplay } from "./StatusDisplay";
import { connect } from "react-redux";
import { withCurationStatus } from "./withCurationStatus";

const EnhancedStatusDisplay = withCurationStatus(StatusDisplay);

// create the connected component that gets record state
const mapStateToProps = (state) => ({
  record: state.deposit.record,
});

export const CustomDepositStatusBox = connect(mapStateToProps)(EnhancedStatusDisplay);
