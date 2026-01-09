// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { DeleteConfirmationModal } from "@js/invenio_requests/components/modals/DeleteConfirmationModal";
import RequestsFeed from "@js/invenio_requests/components/RequestsFeed";
import { TimelineCommentEditor } from "@js/invenio_requests/timelineCommentEditor";
import { TimelineCommentEventControlled } from "@js/invenio_requests/timelineCommentEventControlled";
import { getEventIdFromUrl } from "@js/invenio_requests/timelineEvents/utils";
import React, { Component } from "react";
import Overridable from "react-overridable";
import { Container, Message, Icon } from "semantic-ui-react";
import Error from "@js/invenio_requests/components/Error";
import Loader from "@js/invenio_requests/components/Loader";
import TimelineEventPlaceholder from "@js/invenio_requests/components/TimelineEventPlaceholder";
import LoadMore from "@js/invenio_requests/timeline/LoadMore";
import PropTypes from "prop-types";

class CurationsTimelineFeedComponent extends Component {
  constructor(props) {
    super(props);

    this.state = {
      modalOpen: false,
      modalAction: null,
    };
  }

  loadNextAppendedPage = () => {
    const { fetchNextTimelinePage } = this.props;
    fetchNextTimelinePage("first");
  };

  loadNextPageAfterFocused = () => {
    const { fetchNextTimelinePage } = this.props;
    fetchNextTimelinePage("focused");
  };

  onOpenModal = (action) => {
    this.setState({ modalOpen: true, modalAction: action });
  };

  renderHitList = (hits) => {
    const { userAvatar, permissions } = this.props;

    return (
      <>
        {hits.map((event) => (
          <TimelineCommentEventControlled
            key={event.id}
            event={event}
            openConfirmModal={this.onOpenModal}
            userAvatar={userAvatar}
            allowQuote={false}
            allowReply={permissions.can_reply_comment}
          />
        ))}
      </>
    );
  };

  render() {
    const {
      timeline,
      initialLoading,
      error,
      userAvatar,
      request,
      permissions,
      warning,
      size,
    } = this.props;
    const { modalOpen, modalAction } = this.state;
    const {
      firstPageHits,
      lastPageHits,
      focusedPageHits,
      afterFirstPageHits,
      afterFocusedPageHits,
      focusedPage,
      pageAfterFocused,
      lastPage,
      totalHits,
      loadingAfterFirstPage,
      loadingAfterFocusedPage,
    } = timeline;

    let remainingBeforeFocused = 0;
    let remainingAfterFocused = 0;

    if (focusedPage && focusedPage !== lastPage) {
      remainingBeforeFocused =
        (focusedPage - 1) * size - (firstPageHits.length + afterFirstPageHits.length);
      remainingAfterFocused =
        totalHits - (pageAfterFocused * size + lastPageHits.length);
    } else {
      remainingBeforeFocused =
        totalHits -
        (firstPageHits.length + afterFirstPageHits.length + lastPageHits.length);
    }

    const firstFeedClassName = remainingBeforeFocused > 0 ? "gradient-feed" : null;
    const lastFeedClassName =
      remainingAfterFocused > 0 || (remainingBeforeFocused > 0 && focusedPage === null)
        ? "stretched-feed gradient-feed"
        : null;
    const focusedFeedClassName =
      (focusedPage !== null && remainingBeforeFocused > 0 ? "stretched-feed" : "") +
      (remainingAfterFocused > 0 ? " gradient-feed" : "");

    return (
      <Loader isLoading={initialLoading}>
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

              {/* First Feed before focused page (oldest comments) */}
              <RequestsFeed className={firstFeedClassName}>
                {this.renderHitList(firstPageHits)}

                {/* Events before focused page */}
                {afterFirstPageHits && this.renderHitList(afterFirstPageHits)}
                {loadingAfterFirstPage && <TimelineEventPlaceholder />}
              </RequestsFeed>

              {/* LoadMore button for events before focused */}
              {remainingBeforeFocused > 0 && (
                <LoadMore
                  remaining={remainingBeforeFocused}
                  loading={loadingAfterFirstPage}
                  loadNextAppendedPage={this.loadNextAppendedPage}
                />
              )}

              {/* Focused Feed */}
              {focusedPageHits && (
                <>
                  <RequestsFeed className={focusedFeedClassName}>
                    {/* Events at focused page */}
                    {this.renderHitList(focusedPageHits)}

                    {/* Events after focused page */}
                    {this.renderHitList(afterFocusedPageHits)}
                    {loadingAfterFocusedPage && <TimelineEventPlaceholder />}
                  </RequestsFeed>

                  {/* LoadMore button for events after focused */}
                  {remainingAfterFocused > 0 && (
                    <LoadMore
                      remaining={remainingAfterFocused}
                      loading={loadingAfterFocusedPage}
                      loadNextAppendedPage={this.loadNextPageAfterFocused}
                    />
                  )}
                </>
              )}

              {/* Last Feed (newest comments) */}
              {lastPageHits.length > 0 && (
                <RequestsFeed className={lastFeedClassName}>
                  {this.renderHitList(lastPageHits)}
                </RequestsFeed>
              )}

              <TimelineCommentEditor
                userAvatar={userAvatar}
                canCreateComment={permissions.can_create_comment}
              />
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
