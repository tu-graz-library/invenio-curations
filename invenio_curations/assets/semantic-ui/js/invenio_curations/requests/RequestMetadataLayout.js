// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
// Copyright (C) 2024-2026 Graz University of Technology.
// Copyright (C) 2024 KTH Royal Institute of Technology.

// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import { Divider, Header, Icon, Message } from "semantic-ui-react";
import { toRelativeTime } from "react-invenio-forms";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";

// Sub-components for entity display (inlined for v13 compatibility — not exported by invenio-requests v13)
const User = ({ user }) => (
  <div className="flex">
    <Image
      src={user.links.avatar}
      avatar
      size="tiny"
      className="mr-5"
      ui={false}
      rounded
    />
    <span>
      {user.profile?.full_name ||
        user?.username ||
        user?.email ||
        i18next.t("Anonymous user")}
    </span>
  </div>
);

User.propTypes = {
  user: PropTypes.object.isRequired,
};

const Community = ({ community }) => (
  <div className="flex">
    <Image src={community.links.logo} avatar size="tiny" className="mr-5" ui={false} />
    <a href={`/communities/${community.slug}`}>{community.metadata.title}</a>
  </div>
);

Community.propTypes = {
  community: PropTypes.object.isRequired,
};

const ExternalEmail = ({ email }) => (
  <div className="flex">
    <Icon name="mail" className="mr-5" />
    <span>
      {i18next.t("Email")}: {email.id}
    </span>
  </div>
);

ExternalEmail.propTypes = {
  email: PropTypes.object.isRequired,
};

const Group = ({ group }) => (
  <div className="flex">
    <Icon name="group" className="mr-5" />
    <span>
      {i18next.t("Group")}: {group?.name}
    </span>
  </div>
);

Group.propTypes = {
  group: PropTypes.object.isRequired,
};

const EntityDetails = ({ userData, details }) => {
  const isUser = "user" in userData;
  const isCommunity = "community" in userData;
  const isExternalEmail = "email" in userData;
  const isGroup = "group" in userData;

  if (isUser) {
    return <User user={details} />;
  } else if (isCommunity) {
    return <Community community={details} />;
  } else if (isExternalEmail) {
    return <ExternalEmail email={details} />;
  } else if (isGroup) {
    return <Group group={details} />;
  }
  return null;
};

EntityDetails.propTypes = {
  userData: PropTypes.object.isRequired,
  details: PropTypes.object.isRequired,
};

const DeletedResource = ({ details }) => (
  <Message negative>{details.metadata.title}</Message>
);

DeletedResource.propTypes = {
  details: PropTypes.object.isRequired,
};

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
export class RequestMetadataComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      linkIsValid: false,
    };
  }

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

  isResourceDeleted = (details) => details.is_ghost === true;

  render() {
    const { request } = this.props;
    const { linkIsValid } = this.state;

    const expandedCreatedBy = request.expanded?.created_by;
    const expandedReceiver = request.expanded?.receiver;
    return (
      <>
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

        {expandedReceiver !== undefined && (
          <>
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
          </>
        )}

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

        {linkIsValid && (
          <>
            <Divider />
            <Header as="h3" size="tiny">
              {i18next.t("Record")}
            </Header>
            <a href={`/records/${request.topic.record}`}>{request.title}</a>
          </>
        )}
      </>
    );
  }
}

RequestMetadataComponent.propTypes = {
  request: PropTypes.object.isRequired,
  config: PropTypes.object,
  permissions: PropTypes.object,
};

RequestMetadataComponent.defaultProps = {
  config: {},
  permissions: {},
};

export const RequestMetadata = RequestMetadataComponent;
