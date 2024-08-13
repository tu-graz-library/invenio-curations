// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import { Button } from "semantic-ui-react";
import { Dropdown } from "semantic-ui-react";
import { AppMedia } from "@js/invenio_theme/Media";

const { MediaContextProvider, Media } = AppMedia;

const RequestBaseModalTrigger = (props) => {
  const {
    onClick,
    requestType,
    loading,
    ariaAttributes,
    size,
    className,
    icon,
    text,
    color,
  } = props;

  return (
    <MediaContextProvider>
      <Media greaterThanOrEqual="tablet">
        <Button
          icon={icon}
          labelPosition="left"
          content={text}
          onClick={onClick}
          positive={color === "positive"}
          negative={color === "negative"}
          loading={loading}
          disabled={loading}
          size={size}
          className={className}
          {...ariaAttributes}
        />
      </Media>
      <Media at="mobile">
        <Dropdown.Item
          icon={{
            name: icon,
            color: color,
            className: "mr-5",
          }}
          onClick={onClick}
          content={text}
        />
      </Media>
    </MediaContextProvider>
  );
};

export const RequestCritiqueModalTrigger = (props) => {
  const text = i18next.t("Request changes");
  const icon = "exclamation circle";
  const color = "negative";
  return RequestBaseModalTrigger({ ...props, text, icon, color });
};

export const RequestResubmitModalTrigger = (props) => {
  const text = i18next.t("Resubmit for review");
  const icon = "paper hand outline";
  const color = "neutral";
  return RequestBaseModalTrigger({ ...props, text, icon, color });
};

export const RequestReviewModalTrigger = (props) => {
  const text = i18next.t("Start review");
  const icon = "eye";
  const color = "neutral";
  return RequestBaseModalTrigger({ ...props, text, icon, color });
};

for (const component of [
  RequestCritiqueModalTrigger,
  RequestResubmitModalTrigger,
  RequestReviewModalTrigger,
]) {
  component.propTypes = {
    onClick: PropTypes.func.isRequired,
    loading: PropTypes.bool,
    ariaAttributes: PropTypes.object,
    size: PropTypes.string,
    className: PropTypes.string,
  };

  component.defaultProps = {
    size: "mini",
    className: "ml-5",
  };
}
