// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
// Copyright (C) 2024-2025 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_requests/i18next";
import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Image, toRelativeTime } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Feed } from "semantic-ui-react";

const formatEventTime = (timestamp, language) =>
  window.CURATIONS_CONFIG?.absoluteDates
    ? DateTime.fromISO(timestamp).setLocale(language).toLocaleString(DateTime.DATETIME_MED)
    : toRelativeTime(timestamp, language);

// We use the original components but provide a fixed layout
import RequestsFeed from "@js/invenio_requests/components/RequestsFeed";
import TimelineEventBody from "@js/invenio_requests/components/TimelineEventBody";

class CurationTimelineActionEvent extends Component {
  render() {
    const { event, iconName, iconColor, eventContent } = this.props;

    const createdBy = event.created_by;
    const isUser = "user" in createdBy;
    const expandedCreatedBy = event.expanded?.created_by;

    let userAvatar,
      user = null;
    if (isUser && expandedCreatedBy) {
      userAvatar = (
        <Image
          src={expandedCreatedBy.links.avatar}
          avatar
          size="tiny"
          className="mr-5"
          ui={false}
        />
      );
      user = expandedCreatedBy.profile?.full_name || expandedCreatedBy.username;
    }

    return (
      <RequestsFeed.Item>
        <RequestsFeed.Content isEvent>
          <RequestsFeed.Icon name={iconName} size="large" color={iconColor} />
          <RequestsFeed.Event isActionEvent>
            <Feed.Content>
              <Feed.Summary className="flex">
                {userAvatar}
                <b>{user}</b>
                <Feed.Date>
                  <TimelineEventBody
                    payload={{
                      content: eventContent,
                      format: event?.payload?.format || "text",
                    }}
                  />{" "}
                  {formatEventTime(event.created, i18next.language)}
                </Feed.Date>
              </Feed.Summary>
            </Feed.Content>
          </RequestsFeed.Event>
        </RequestsFeed.Content>
      </RequestsFeed.Item>
    );
  }
}

CurationTimelineActionEvent.propTypes = {
  event: PropTypes.object.isRequired,
  iconName: PropTypes.string.isRequired,
  eventContent: PropTypes.string.isRequired,
  iconColor: PropTypes.string,
};

CurationTimelineActionEvent.defaultProps = {
  iconColor: "grey",
};

export default CurationTimelineActionEvent;
