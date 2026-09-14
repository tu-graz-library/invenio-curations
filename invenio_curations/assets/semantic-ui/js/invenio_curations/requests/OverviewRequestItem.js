// This file is part of InvenioRDM
// Copyright (C) 2026 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_curations/i18next";
import { default as RequestTypeIcon } from "@js/invenio_requests/components/RequestTypeIcon";
import { Trans } from "react-i18next";
import React from "react";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import { withState } from "react-searchkit";
import { Icon, Item } from "semantic-ui-react";
import PropTypes from "prop-types";
import { toRelativeTime } from "react-invenio-forms";
import { DateTime } from "luxon";

// This file overrides the request result list item from InvenioAppRdm's user
// dashboard, in order to show - for `rdm-curation` requests - who last started the
// curation review, and when. Unlike the rest of the timeline (which can show relative
// times), this line always shows an absolute date, so it stays meaningful when
// re-visiting the overview later.
//
// The two "*RequestItem" components don't expose a slot for extra metadata, so -
// following the precedent set in RequestMetadataLayout.js - they are copy-pasted here
// from invenio-requests, with the review-started line added to their existing
// Item.Meta block (marked with ATTENTION).
// https://github.com/inveniosoftware/invenio-requests/blob/master/invenio_requests/assets/semantic-ui/js/invenio_requests/search/ComputerTabletRequestItem.js
// https://github.com/inveniosoftware/invenio-requests/blob/master/invenio_requests/assets/semantic-ui/js/invenio_requests/search/MobileRequestItem.js

const ReviewStartedInfo = ({ result }) => {
  const { review_started_by: reviewer, review_started_at: startedAt } =
    result.payload || {};

  if (result.type !== "rdm-curation" || !reviewer || !startedAt) {
    return null;
  }

  return (
    <small className="block rel-mt-1">
      {i18next.t("Curation review started by {{- reviewer}} on {{- date}}", {
        reviewer,
        date: DateTime.fromISO(startedAt).toLocaleString(DateTime.DATETIME_MED),
      })}
    </small>
  );
};

ReviewStartedInfo.propTypes = {
  result: PropTypes.object.isRequired,
};

const CurationComputerTabletRequestItem = ({
  result,
  updateQueryState,
  currentQueryState,
  detailsURL,
}) => {
  const createdDate = new Date(result.created);
  let creatorName = "";
  const isCreatorUser = "user" in result.created_by;
  const isCreatorCommunity = "community" in result.created_by;
  const isCreatorGuest = "email" in result.created_by;
  if (isCreatorUser) {
    creatorName =
      result.expanded?.created_by.profile?.full_name ||
      result.expanded?.created_by.username ||
      result.created_by.user;
  } else if (isCreatorCommunity) {
    creatorName =
      result.expanded?.created_by.metadata?.title || result.created_by.community;
  } else if (isCreatorGuest) {
    creatorName = result.created_by.email;
  }

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
          {result.status && result.is_closed && (
            <RequestStatusLabel status={result.status} />
          )}
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
          <a className="header-link " href={detailsURL}>
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
          <small className="right floated">
            {result.receiver?.community &&
              result.expanded?.receiver?.metadata.title && (
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
          {/* ATTENTION: extra line showing who started the curation review */}
          <ReviewStartedInfo result={result} />
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};

CurationComputerTabletRequestItem.propTypes = {
  result: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};

const CurationMobileRequestItem = ({
  result,
  updateQueryState,
  currentQueryState,
  detailsURL,
}) => {
  const createdDate = new Date(result.created);
  let creatorName = "";
  const isCreatorUser = "user" in result.created_by;
  const isCreatorCommunity = "community" in result.created_by;
  if (isCreatorUser) {
    creatorName =
      result.expanded?.created_by.profile?.full_name ||
      result.expanded?.created_by.username ||
      result.created_by.user;
  } else if (isCreatorCommunity) {
    creatorName =
      result.expanded?.created_by.metadata?.title || result.created_by.community;
  }

  const getUserIcon = (receiver) => {
    return receiver?.is_ghost ? "user secret" : "users";
  };
  const getTypeIcon = (type) => {
    if (type === "community-invitation") return "user plus";
    else return "plus";
  };

  return (
    <Item key={result.id} className="mobile only flex">
      <Item.Content className="centered">
        <Item.Extra>
          {result.type && <RequestTypeLabel type={result.type} />}
          {result.status && result.is_closed && (
            <RequestStatusLabel status={result.status} />
          )}
        </Item.Extra>
        <Item.Header className="truncate-lines-2 rel-mt-1">
          <a className="header-link p-0" href={detailsURL}>
            <Icon
              size="small"
              name={getTypeIcon(result.type)}
              className="neutral mr-5"
            />
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
          <small className="block rel-mt-1">
            {result.receiver?.community &&
              result.expanded?.receiver?.metadata.title && (
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
          {/* ATTENTION: extra line showing who started the curation review */}
          <ReviewStartedInfo result={result} />
          {!result.is_closed && (
            <div className="block rel-mt-1">
              <RequestActionController
                request={result}
                actionSuccessCallback={() => updateQueryState(currentQueryState)}
              />
            </div>
          )}
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};

CurationMobileRequestItem.propTypes = {
  result: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  detailsURL: PropTypes.string.isRequired,
};

export function CurationRequestsResultsItemTemplateDashboard({ result }) {
  const ComputerTabletRequestsItemWithState = withState(
    CurationComputerTabletRequestItem
  );
  const MobileRequestsItemWithState = withState(CurationMobileRequestItem);
  const detailsURL = `/me/requests/${result.id}`;
  return (
    <>
      <ComputerTabletRequestsItemWithState result={result} detailsURL={detailsURL} />
      <MobileRequestsItemWithState result={result} detailsURL={detailsURL} />
    </>
  );
}

CurationRequestsResultsItemTemplateDashboard.propTypes = {
  result: PropTypes.object.isRequired,
};
