/*
 * SPDX-FileCopyrightText: 2025 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Icon, Popup } from "semantic-ui-react";

import PropTypes from "prop-types";
import React from 'react';

/**
 * Presentational component for displaying status information
 */
export const StatusDisplay = ({ statusInfo }) => {
  return (
    <div className="status">
      <Popup
        content={statusInfo.tooltip}
        trigger={
          <span>
            <Icon
              name="info circle"
              color={statusInfo.color}
            />
            {statusInfo.text}
          </span>
        }
      />
    </div>
  );
};

StatusDisplay.propTypes = {
  statusInfo: PropTypes.shape({
    icon: PropTypes.string.isRequired,
    color: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    tooltip: PropTypes.string.isRequired,
  }).isRequired,
};
