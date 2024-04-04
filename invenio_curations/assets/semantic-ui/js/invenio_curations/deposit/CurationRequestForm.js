// -*- coding: utf-8 -*-
//
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React, { Component } from "react";
import { http } from "react-invenio-forms";

import { RequestMetadata } from "@js/invenio_requests";
import { Button, Card, Header } from "semantic-ui-react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import {
  CustomFields,
  FieldLabel,
  RadioField,
  TextField,
  withCancel,
} from "react-invenio-forms";

function wait(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

export class CurationsContainer extends Component {
  constructor(props) {
    super(props);
    this.config = props.config || {};
    this.state = {
      loading: false,
      latestRequest: null,
    };
  }

  get record() {
    return this.props.record;
  }

  fetchLatestCurationRequest = async () => {
    this.loading = true;

    try {
      let request = await http.get(`/api/curations`, {
        params: {
          expand: 1,
          topic: `record:${this.record["id"]}`,
          is_open: true,
        },
      });

      this.setState({
        latestRequest:
          request.data.hits.total > 0 ? request.data.hits.hits[0] : null,
      });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };

  createCurationRequest = async () => {
    this.loading = true;

    let payload = {
      topic: {
        record: this.record["id"],
      },
    };
    try {
      let request = await http.post(`/api/curations`, payload, {
        params: {
          expand: 1,
        },
      });

      this.setState({
        latestRequest: request.data,
      });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };

  set loading(v) {
    this.setState({
      loading: v,
    });
  }

  get loading() {
    return this.state.loading;
  }

  componentDidMount() {
    this.fetchLatestCurationRequest();
  }

  render() {
    let { latestRequest } = this.state;

    return (
      <Overridable id="InvenioCurations.Deposit.CardCurationsBox.container">
        <Card>
          <Card.Content>
            <Card.Header>
              <FieldLabel
                label={i18next.t("Curation")}
                icon={"list"}
              ></FieldLabel>
            </Card.Header>
          </Card.Content>
          <Card.Content>
            <Button
              fluid
              onClick={this.fetchLatestCurationRequest}
              loading={this.loading}
              primary
              size="medium"
              icon
              labelPosition="left"
              type="button"
            >
              {i18next.t("Fetch latest request")}
            </Button>
            {latestRequest && (
              <RequestMetadata request={latestRequest}></RequestMetadata>
            )}
          </Card.Content>
          <Card.Content>
            {!latestRequest && (
              <div>
                <p>{i18next.t("No open request for this record exists.")}</p>
                <Button
                  fluid
                  onClick={this.createCurationRequest}
                  loading={this.loading}
                  primary
                  size="medium"
                  icon
                  labelPosition="left"
                  type="button"
                >
                  {i18next.t("Create curation request")}
                </Button>
              </div>
            )}
          </Card.Content>
        </Card>
      </Overridable>
    );
  }
}

CurationsContainer.propTypes = {
  config: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object,
};

CurationsContainer.defaultProps = {
  permissions: null,
};
