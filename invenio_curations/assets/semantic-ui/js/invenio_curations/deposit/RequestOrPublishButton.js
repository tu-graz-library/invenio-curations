// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Button, Icon, Popup } from "semantic-ui-react";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { PublishButton } from "@js/invenio_rdm_records";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_curations/i18next";

export const RequestOrPublishButton = (props) => {
  const { request, record, handleCreateRequest, handleResubmitRequest, loading } =
    props;
  const recordIdAvailable = record?.id != null;
  let elem = null;

  if (request) {
    switch (request.status) {
      case "accepted":
        elem = <PublishButton fluid />;
        break;

      case "critiqued":
        elem = (
          <Button
            onClick={handleResubmitRequest}
            loading={loading}
            primary
            size="medium"
            type="button"
            disabled={!recordIdAvailable}
            positive
            icon
            labelPosition="left"
            fluid
          >
            <Icon name="paper hand outline" />
            {i18next.t("Resubmit updated record")}
          </Button>
        );
        break;

      default:
        elem = (
          <span style={{ display: "flex", gap: "0.25em" }}>
            <Button
              as="a"
              href={`/me/requests/${request.id}`}
              icon
              labelPosition="left"
              size="medium"
              positive
              fluid
            >
              {i18next.t("View request")}
              <Icon name="right arrow" />
            </Button>
            <RequestStatusLabel status={request.status} />
          </span>
        );
    }
  } else {
    elem = (
      <Popup
        disabled={recordIdAvailable}
        content={i18next.t(
          "Before creating a curation request, the draft has to be saved."
        )}
        position="top center"
        trigger={
          <span>
            <Button
              onClick={handleCreateRequest}
              loading={loading}
              primary
              size="medium"
              type="button"
              disabled={!recordIdAvailable}
              positive
              icon
              labelPosition="left"
              fluid
            >
              <Icon name="paper hand outline" />
              {i18next.t("Start publication process")}
            </Button>
          </span>
        }
      />
    );
  }

  return elem;
};

RequestOrPublishButton.propTypes = {
  request: PropTypes.object,
  record: PropTypes.object,
  handleCreateRequest: PropTypes.func.isRequired,
  handleResubmitRequest: PropTypes.func.isRequired,
  loading: PropTypes.bool,
};

RequestOrPublishButton.defaultProps = {
  request: null,
  record: null,
  loading: false,
};
