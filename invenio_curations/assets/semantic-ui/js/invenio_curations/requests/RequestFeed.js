// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { DeleteConfirmationModal } from "@js/invenio_requests/components/modals/DeleteConfirmationModal";
import { Pagination } from "@js/invenio_requests/components/Pagination";
import RequestsFeed from "@js/invenio_requests/components/RequestsFeed";
import { TimelineCommentEditor } from "@js/invenio_requests/timelineCommentEditor";
import { TimelineCommentEventControlled } from "@js/invenio_requests/timelineCommentEventControlled";
import React, { Component } from "react";
import Overridable from "react-overridable";
import { Container, Divider, Message, Icon } from "semantic-ui-react";
import Error from "@js/invenio_requests/components/Error";
import Loader from "@js/invenio_requests/components/Loader";
import PropTypes from "prop-types";

class CurationsTimelineFeedComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      modalAction: null,
    };
  }

  onOpenModal = (action) => {
    this.setState({ modalOpen: true, modalAction: action });
  };

  render() {
    const {
      timeline,
      loading,
      error,
      setPage,
      size,
      page,
      userAvatar,
      request,
      permissions,
      warning,
    } = this.props;
    const { modalOpen, modalAction } = this.state;

    return (
      <Loader isLoading={loading}>
        <Error error={error}>
          {warning && (
            <Message visible warning>
              <p>
                <Icon name="warning sign" />
                {warning}
              </p>
            </Message>
          )}

          <>
            <Container id="requests-timeline" className="ml-0-mobile mr-0-mobile">
              <Overridable
                id="TimelineFeed.header"
                request={request}
                permissions={permissions}
              />
              <RequestsFeed>
                {timeline.hits?.hits
                .map((event) => (
                  <TimelineCommentEventControlled
                    key={event.id}
                    event={event}
                    openConfirmModal={this.onOpenModal}
                  />
                ))}
              </RequestsFeed>
              <Divider fitted />
              <Container textAlign="center" className="mb-15 mt-15">
                <Pagination
                  page={page}
                  size={size}
                  setPage={setPage}
                  totalLength={timeline.hits?.total}
                />
              </Container>
              <TimelineCommentEditor userAvatar={userAvatar} />
              <DeleteConfirmationModal
                open={modalOpen}
                action={modalAction}
                onOpen={() => this.setState({ modalOpen: true })}
                onClose={() => this.setState({ modalOpen: false })}
              />
            </Container>
          </>
        </Error>
      </Loader>
    );
  }
}

CurationsTimelineFeedComponent.propTypes = {
  getTimelineWithRefresh: PropTypes.func.isRequired,
  timelineStopRefresh: PropTypes.func.isRequired,
  timeline: PropTypes.object,
  error: PropTypes.object,
  isSubmitting: PropTypes.bool,
  setPage: PropTypes.func.isRequired,
  page: PropTypes.number,
  size: PropTypes.number,
  userAvatar: PropTypes.string,
  request: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
  loading: PropTypes.bool.isRequired,
  warning: PropTypes.string,
};

CurationsTimelineFeedComponent.defaultProps = {
  timeline: null,
  error: null,
  isSubmitting: false,
  page: 1,
  size: 10,
  userAvatar: "",
  warning: null,
};

export const CurationsTimelineFeed = CurationsTimelineFeedComponent;
