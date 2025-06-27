// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { AppMedia } from "@js/invenio_theme/Media";
import PropTypes from "prop-types";
import React from "react";
import { Dropdown } from "semantic-ui-react";
import {
  RequestCritiqueButton,
  RequestResubmitButton,
  RequestReviewButton,
} from "./Buttons";

const { MediaContextProvider, Media } = AppMedia;

const RequestBaseModalTrigger = (props) => {
  const { onClick, button } = props;

  return (
    <MediaContextProvider>
      <Media greaterThanOrEqual="tablet">{button}</Media>
      <Media at="mobile">
        <Dropdown.Item
          icon={{
            name: button.props.icon,
            color: button.props.color,
            className: "mr-5",
          }}
          onClick={onClick}
          content={button.props.content}
        />
      </Media>
    </MediaContextProvider>
  );
};

export const RequestCritiqueModalTrigger = (props) => {
  const { onClick } = props;
  return (
    <RequestBaseModalTrigger
      onClick={onClick}
      button={<RequestCritiqueButton {...props} />}
    />
  );
};

export const RequestResubmitModalTrigger = (props) => {
  const { onClick } = props;
  return (
    <RequestBaseModalTrigger
      onClick={onClick}
      button={<RequestResubmitButton {...props} />}
    />
  );
};

export const RequestReviewModalTrigger = (props) => {
  const { onClick } = props;
  return (
    <RequestBaseModalTrigger
      onClick={onClick}
      button={<RequestReviewButton {...props} />}
    />
  );
};

RequestBaseModalTrigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  button: PropTypes.func.isRequired,
};

RequestCritiqueModalTrigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  button: PropTypes.func.isRequired,
};

RequestResubmitModalTrigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  button: PropTypes.func.isRequired,
};

RequestReviewModalTrigger.propTypes = {
  onClick: PropTypes.func.isRequired,
  button: PropTypes.func.isRequired,
};
