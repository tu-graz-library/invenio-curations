// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
// Copyright (C) 2024-2026 Graz University of Technology.
// Copyright (C) 2024 KTH Royal Institute of Technology.

// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Divider, Header } from "semantic-ui-react";
import { toRelativeTime } from "react-invenio-forms";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import { RequestReviewers } from "@js/invenio_requests/request/reviewers/RequestReviewers";
import {
  EntityDetails,
  DeletedResource,
} from "@js/invenio_requests/request/RequestMetadata";

// This component overrides the request metadata layout from InvenioApp RDM v13
// Because the "original" request workflow from community-submission has the final
// approval as *Accept and publish*, the record is automatically published and having
// a new section in the request metadata with a link to the published record makes
// sense.
// In the curation workflow, the user/author has to publish the record after the accept
// action, but this accept action would pop up the "not yet" published record, which leads
// to an error.
// This override checks whether the link to the published record returns a positive status
// and sets the state accordingly to be used in the rendering of the respective section.
//
// Apart from ATTENTION BLOCKs, the rest of the component is copy-pasted.
// https://github.com/inveniosoftware/invenio-requests/blob/3596f4c2acd22c439a030fb9bab8d87e98c12a2e/invenio_requests/assets/semantic-ui/js/invenio_requests/request/RequestMetadata.js#L162C24-L162C61
// it has been updated to include the RequestReviewers feature
export class RequestMetadataComponent extends Component {
  constructor(props) {
    super(props);

    // ATTENTION BLOCK state added for overridden component START
    this.state = {
      linkIsValid: false,
    };
    // BLOCK END
  }

  // ATTENTION BLOCK method was added to the component START
  componentDidMount() {
    const { request } = this.props;

    if (request.status === "accepted" && request.topic?.record) {
      // Even if the request is accepted, the publishing is the responsibility of the record's
      // author. display the Record section only if the record was actually published.
      const url = `/records/${request.topic.record}`;

      fetch(url, { method: "HEAD" })
        .then((response) => {
          if (response.status === 200) {
            this.setState({ linkIsValid: true });
          }
        })
        .catch((error) => {
          console.warn("Link check failed:", error);
        });
    }
  }
  // BLOCK END

  isResourceDeleted = (details) => details.is_ghost === true;

  render() {
    const { request, config, permissions } = this.props;
    const { enableReviewers, allowGroupReviewers, maxReviewers } = config;

    // ATTENTION BLOCK state: extra for overridden component START
    const { linkIsValid } = this.state;
    // BLOCK END

    const expandedCreatedBy = request.expanded?.created_by;
    const expandedReceiver = request.expanded?.receiver;
    return (
      <>
        {enableReviewers && (
          <>
            <RequestReviewers
              request={request}
              permissions={permissions}
              allowGroupReviewers={allowGroupReviewers}
              maxReviewers={maxReviewers}
            />
            <Divider />
          </>
        )}

        {expandedCreatedBy !== undefined && (
          <>
            <Header as="h3" size="tiny">
              {i18next.t("Creator")}
            </Header>
            {this.isResourceDeleted(expandedCreatedBy) ? (
              <DeletedResource details={expandedCreatedBy} />
            ) : (
              <EntityDetails
                userData={request.created_by}
                details={request.expanded?.created_by}
              />
            )}
            <Divider />
          </>
        )}

        <Header as="h3" size="tiny">
          {i18next.t("Receiver")}
        </Header>
        {this.isResourceDeleted(expandedReceiver) ? (
          <DeletedResource details={expandedReceiver} />
        ) : (
          <EntityDetails
            userData={request.receiver}
            details={request.expanded?.receiver}
          />
        )}
        <Divider />

        <Header as="h3" size="tiny">
          {i18next.t("Request type")}
        </Header>
        <RequestTypeLabel type={request.type} />
        <Divider />

        <Header as="h3" size="tiny">
          {i18next.t("Status")}
        </Header>
        <RequestStatus status={request.status} />
        <Divider />

        <Header as="h3" size="tiny">
          {i18next.t("Created")}
        </Header>
        {toRelativeTime(request.created, i18next.language)}

        {request.expires_at && (
          <>
            <Divider />
            <Header as="h3" size="tiny">
              {i18next.t("Expires")}
            </Header>
            {toRelativeTime(request.expires_at, i18next.language)}
          </>
        )}

        {/* ATTENTION BLOCK state check: extra for overridden component START*/}
        {linkIsValid && (
          <>
            <Divider />
            <Header as="h3" size="tiny">
              {i18next.t("Record")}
            </Header>
            <a href={`/records/${request.topic.record}`}>{request.title}</a>
          </>
        )}
        {/* BLOCK END */}
      </>
    );
  }
}

RequestMetadataComponent.propTypes = {
  request: PropTypes.object.isRequired,
  config: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
};

RequestMetadataComponent.defaultProps = {};

export const RequestMetadata = RequestMetadataComponent;
