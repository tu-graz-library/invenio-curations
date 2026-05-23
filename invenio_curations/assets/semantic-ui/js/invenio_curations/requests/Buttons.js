/*
 * SPDX-FileCopyrightText: 2024 TU Wien.
 * SPDX-FileCopyrightText: 2024 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_curations/i18next";
import React from "react";
import { Button } from "semantic-ui-react";

class RequestBaseButton extends React.Component {
  render() {
    const { onClick, loading, ariaAttributes, size, content, className, icon, color } =
      this.props;

    return (
      <Button
        icon={icon}
        labelPosition="left"
        content={content}
        onClick={onClick}
        negative={color === "negative"}
        positive={color === "positive"}
        loading={loading}
        disabled={loading}
        size={size}
        className={className}
        {...ariaAttributes}
      />
    );
  }
}

export const RequestCritiqueButton = (props) => {
  return (
    <RequestBaseButton
      icon="exclamation circle"
      color="negative"
      content={i18next.t("Request changes")}
      {...props}
    />
  );
};

export const RequestResubmitButton = (props) => {
  return (
    <RequestBaseButton
      icon="paper hand outline"
      color="neutral"
      content={i18next.t("Resubmit for review")}
      {...props}
    />
  );
};

export const RequestReviewButton = (props) => {
  return (
    <RequestBaseButton
      icon="eye"
      color="neutral"
      content={i18next.t("Start review")}
      {...props}
    />
  );
};
