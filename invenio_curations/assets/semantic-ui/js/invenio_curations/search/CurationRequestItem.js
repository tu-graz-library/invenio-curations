// This file is part of InvenioRDM
// Copyright (C) 2026 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Icon, Item, Label } from "semantic-ui-react";

import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import { Trans } from "react-i18next";
import { i18next } from "@translations/invenio_curations/i18next";
import { toRelativeTime } from "react-invenio-forms";

const getCreatorName = (result) => {
  const isCreatorUser = "user" in result.created_by;
  const isCreatorCommunity = "community" in result.created_by;
  const isCreatorGuest = "email" in result.created_by;

  if (isCreatorUser) {
    return (
      result.expanded?.created_by.profile?.full_name ||
      result.expanded?.created_by.username ||
      result.created_by.user
    );
  } else if (isCreatorCommunity) {
    return (
      result.expanded?.created_by.metadata?.title || result.created_by.community
    );
  } else if (isCreatorGuest) {
    return result.created_by.email;
  }
  return "";
};

const statusLabels = {
  submitted: i18next.t("Submitted"),
  resubmitted: i18next.t("Resubmitted"),
  review: i18next.t("Under review"),
  critiqued: i18next.t("Changes requested"),
  accepted: i18next.t("Accepted"),
  declined: i18next.t("Declined"),
  cancelled: i18next.t("Cancelled"),
  pending_resubmission: i18next.t("Pending resubmission"),
  created: i18next.t("Created"),
};

const LastStatusChange = ({ result }) => {
  // Use updated timestamp as the last status change time
  const status = result.status;
  const updatedDate = result.updated;
  const creatorName = getCreatorName(result);

  if (!updatedDate || !status || status === "created") return null;

  const label = statusLabels[status] || status;

  return (
    <small className="mt-5" style={{ display: "block" }}>
      <Label size="tiny" color="yellow">
        {label} {toRelativeTime(updatedDate, i18next.language)}
        {creatorName && ` ${i18next.t("by")} ${creatorName}`}
      </Label>
    </small>
  );
};

LastStatusChange.propTypes = {
  result: PropTypes.object.isRequired,
};

export const CurationRequestItem = ({
  result,
  updateQueryState,
  currentQueryState,
  detailsURL,
}) => {
  const createdDate = new Date(result.created);
  const creatorName = getCreatorName(result);

  const getUserIcon = (receiver) => {
    return receiver?.is_ghost ? "user secret" : "users";
  };

  return (
    <Item key={result.id} className="computer tablet only flex">
      <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <Item.Extra>
            <RequestTypeIcon type={result.type} />
          </Item.Extra>
        </Item.Content>
      </div>
      <Item.Content>
        <Item.Extra>
          {result.type && <RequestTypeLabel type={result.type} />}
          <RequestStatusLabel status={result.status} />
          <div className="right floated">
            <RequestActionController
              request={result}
              actionSuccessCallback={() => updateQueryState(currentQueryState)}
            />
          </div>
        </Item.Extra>
        <Item.Header
          className={`truncate-lines-2 theme-primary-text ${
            result.is_closed && "mt-5"
          }`}
        >
          <a className="header-link" href={detailsURL}>
            {result.title}
          </a>
        </Item.Header>
        <Item.Meta>
          <small>
            <Trans
              defaults="Opened {{relativeTime}} by"
              values={{
                relativeTime: toRelativeTime(
                  createdDate.toISOString(),
                  i18next.language
                ),
              }}
            />{" "}
            {creatorName}
          </small>
          <LastStatusChange result={result} />
          <small className="right floated">
            {result.receiver.community &&
              result.expanded?.receiver.metadata.title && (
                <>
                  <Icon
                    className="default-margin"
                    name={getUserIcon(result.expanded?.receiver)}
                  />
                  <span className="ml-5">
                    {result.expanded?.receiver.metadata.title}
                  </span>
                  {result.expires_at && " - "}
                </>
              )}
            {result.expires_at && (
              <span>
                {i18next.t("Expires at: {{- expiringDate}}", {
                  expiringDate: DateTime.fromISO(result.expires_at).toLocaleString(
                    i18next.language
                  ),
                })}
              </span>
            )}
          </small>
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};

CurationRequestItem.propTypes = {
  result: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};
