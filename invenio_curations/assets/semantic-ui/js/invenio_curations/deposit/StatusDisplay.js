// This file is part of InvenioRDM
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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
