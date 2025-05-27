// This file is part of InvenioRDM
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { i18next } from "@translations/invenio_curations/i18next";

/**
 * HOC that adds curation status information to a component
 * @param {React.Component} WrappedComponent
 * @returns {React.Component}
 */
export const withCurationStatus = (WrappedComponent) => {
  const WithCurationStatus = ({ record, request, ...props }) => {
    const getStatusInfo = () => {
      const isDraft = record?.status === 'draft_with_review';
      const isPublished = record?.is_published;

      const hasValidationErrors = record?.ui?.validationErrors ||
        record?.errors?.length > 0 ||
        (record?.files?.enabled && record?.files?.count === 0);

      let statusInfo = {
        icon: "circle",
        color: "grey",
        text: i18next.t("Draft"),
        tooltip: hasValidationErrors
          ? i18next.t("Please fill in all required fields before submitting for review.")
          : i18next.t("Once your upload is complete, you can submit it for review to the global repository curators."),
      };
      if (isPublished) {
        statusInfo = {
          icon: "check circle",
          color: "green",
          text: i18next.t("Published"),
          tooltip: i18next.t("This record is published."),
        };
      } else if (isDraft && request) {
        if (!hasValidationErrors) {
          switch (request.status) {
            case "created":
              statusInfo = {
                icon: "clock",
                color: "blue",
                text: i18next.t("Ready for Review"),
                tooltip: i18next.t("Your record is ready to be submitted for review."),
              };
              break;
            case "submitted":
              statusInfo = {
                icon: "clock",
                color: "yellow",
                text: i18next.t("Under Review"),
                tooltip: i18next.t("This record is being reviewed by curators."),
              };
              break;
            case "accepted":
              statusInfo = {
                icon: "check",
                color: "green",
                text: i18next.t("Ready to Publish"),
                tooltip: i18next.t("Once accepted, you can publish the record yourself."),
              };
              break;
            case "declined":
              statusInfo = {
                icon: "times",
                color: "red",
                text: i18next.t("Declined"),
                tooltip: i18next.t("This record has been declined. Please check the curation request for details."),
              };
              break;
            case "critiqued":
              statusInfo = {
                icon: "exclamation",
                color: "orange",
                text: i18next.t("Needs revision"),
                tooltip: i18next.t("This record needs revision. Please check the curation request for details."),
              };
              break;
          }
        }
      }
      return statusInfo;
    };

    const statusInfo = getStatusInfo();
    return <WrappedComponent {...props} statusInfo={statusInfo} />;
  };

  WithCurationStatus.displayName = `WithCurationStatus(${getDisplayName(WrappedComponent)})`;
  return WithCurationStatus;
};

// helper function to get a component's display name
function getDisplayName(WrappedComponent) {
  return WrappedComponent.displayName || WrappedComponent.name || "Component";
}