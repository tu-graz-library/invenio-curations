// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
// Copyright (C) 2024-2025 Graz University of Technology.
// Copyright (C) 2024 KTH Royal Institute of Technology.

// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Divider, Header, Icon, Message } from "semantic-ui-react";
import { toRelativeTime } from "react-invenio-forms";
import RequestStatus from "@js/invenio_requests/request/RequestStatus";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import { connect } from "react-redux";
import { connect as connectFormik } from "formik";

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
  user: PropTypes.shape({
    links: PropTypes.shape({
      avatar: PropTypes.string.isRequired,
    }).isRequired,
    profile: PropTypes.shape({
      full_name: PropTypes.string,
    }),
    username: PropTypes.string,
    email: PropTypes.string,
  }).isRequired,
};

const Community = ({ community }) => (
  <div className="flex">
    <Image src={community.links.logo} avatar size="tiny" className="mr-5" ui={false} />
    <a href={`/communities/${community.slug}`}>{community.metadata.title}</a>
  </div>
);

Community.propTypes = {
  community: PropTypes.shape({
    links: PropTypes.shape({
      logo: PropTypes.string.isRequired,
    }).isRequired,
    slug: PropTypes.string.isRequired,
    metadata: PropTypes.shape({
      title: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
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
  email: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
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
  group: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }).isRequired,
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
  details: PropTypes.oneOfType([
    PropTypes.shape({
      links: PropTypes.shape({
        avatar: PropTypes.string,
        logo: PropTypes.string,
      }),
      profile: PropTypes.shape({
        full_name: PropTypes.string,
      }),
      username: PropTypes.string,
      email: PropTypes.string,
      slug: PropTypes.string,
      metadata: PropTypes.shape({
        title: PropTypes.string,
      }),
      id: PropTypes.string,
      name: PropTypes.string,
    }),
    PropTypes.object,
  ]).isRequired,
};

const DeletedResource = ({ details }) => (
  <Message negative>{details.metadata.title}</Message>
);

DeletedResource.propTypes = {
  details: PropTypes.shape({
    metadata: PropTypes.shape({
      title: PropTypes.string.isRequired,
    }).isRequired,
  }).isRequired,
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
//
// Apart from ATTENTION BLOCKs, the rest of the component is copy-pasted.
// https://github.com/inveniosoftware/invenio-requests/blob/3596f4c2acd22c439a030fb9bab8d87e98c12a2e/invenio_requests/assets/semantic-ui/js/invenio_requests/request/RequestMetadata.js#L162C24-L162C61
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
    const { request } = this.props;
    // ATTENTION BLOCK state: extra for overridden component START
    const { linkIsValid } = this.state;
    // BLOCK END
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
};

RequestMetadataComponent.defaultProps = {};

export const RequestMetadata = RequestMetadataComponent;
