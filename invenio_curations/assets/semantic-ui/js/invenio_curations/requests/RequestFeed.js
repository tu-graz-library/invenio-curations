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
import { http } from "react-invenio-forms";

class CurationsTimelineFeedComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      modalAction: null,
      // ATTENTION BLOCK states added for overridden component START
      canSeeAllComments: false,
      loading: false,
      // BLOCK END
    };
  }

  // ATTENTION BLOCK functions added for overridden component START
  componentDidMount() {
    this.fetchPublishingData();
  }

  // get isPrivileged from API
  fetchPublishingData = async () => {
    this.loading = true;
    try {
      let data = await http.get("/api/curations/publishing-data");
      let isPrivileged = data.data.is_privileged;
      this.setState({ canSeeAllComments: isPrivileged });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };
  // BLOCK END

  onOpenModal = (action) => {
    this.setState({ modalOpen: true, modalAction: action });
  };

  // This component overrides the TimelineFeed layout from InvenioApp RDM v13
  // Because we need to hide the system generated comments based on privileges
  // there is a need to call the api to get the privilege status of the current
  // user, then use that to display only user-created comments or all comments
  // in the timeline feed.
  // See: https://github.com/inveniosoftware/invenio-requests/blob/23f001055a791499c34bf0289155512bbcae5462/invenio_requests/assets/semantic-ui/js/invenio_requests/timeline/TimelineFeed.js#L22
  //
  // Apart from ATTENTION BLOCKs, the rest of the component is copy-pasted.
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
    // ATTENTION BLOCK get isPrivileged from state added for overridden component START
    const { modalOpen, modalAction, canSeeAllComments } = this.state;
    // BLOCK END

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
              {/* ATTENTION BLOCK new filter for overridden component START */}
                {timeline.hits?.hits.filter((event) => (
                  event.created_by?.user != "system" || canSeeAllComments
              //  BLOCK END
                )).map((event) => (
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
