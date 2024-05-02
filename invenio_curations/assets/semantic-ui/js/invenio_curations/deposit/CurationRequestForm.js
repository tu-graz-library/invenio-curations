// -*- coding: utf-8 -*-
//
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React, { Component } from "react";
import { RequestMetadata } from "@js/invenio_requests";
import { Button, Card } from "semantic-ui-react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { http, FieldLabel } from "react-invenio-forms";

export class CurationsContainerComponent extends Component {
  constructor(props) {
    super(props);
    this.recordFetchInterval = null;
    this.state = {
      loading: false,
      latestRequest: null,
      record: props.record,
    };
  }

  componentDidMount() {
    this.fetchCurationRequest();

    this.recordFetchInterval = setInterval(() => {
      this.readLocalRecordId();
      if (this.record["id"] !== undefined && this.record["id"] !== null) {
        clearInterval(this.recordFetchInterval);
      }
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.recordFetchInterval);
  }

  get record() {
    const { record } = this.state;
    return record;
  }

  readLocalRecordId = () => {
    try {
      let recid = undefined;
      let urlParts = document.URL.split("uploads/");
      if (urlParts.length > 1) {
        recid = urlParts[1];
        if (recid === "new") return;

        this.setState((prevState) => {
          const record = prevState.record;
          return {
            record: { ...record, id: recid },
          };
        });
      }
    } catch (error) {
      console.error("Error during fetching local record:", error);
    }
  };

  fetchCurationRequest = async () => {
    this.loading = true;

    try {
      let request = await http.get(`/api/curations`, {
        params: {
          expand: 1,
          topic: `record:${this.record["id"]}`,
        },
      });

      this.setState({
        latestRequest: request.data.hits.total > 0 ? request.data.hits.hits[0] : null,
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
    const { loading } = this.state;
    return loading;
  }

  render() {
    let { latestRequest, record } = this.state;
    const recordIdAvailable = record["id"] !== undefined && record["id"] !== null;

    return (
      <Overridable id="InvenioCurations.Deposit.CardCurationsBox.container">
        <Card>
          <Card.Content>
            <Card.Header>
              <FieldLabel label={i18next.t("Curation")} icon="list" />
            </Card.Header>
          </Card.Content>
          <Card.Content>
            {latestRequest && <RequestMetadata request={latestRequest} />}
          </Card.Content>
          <Card.Content>
            {!latestRequest && (
              <div>
                <p>{i18next.t("No open request for this record exists.")}</p>
                {!recordIdAvailable && (
                  <p>
                    {i18next.t(
                      "Before creating a curation request, the draft has to be saved."
                    )}
                  </p>
                )}
                {recordIdAvailable && (
                  <Button
                    fluid
                    onClick={async () => {
                      await this.fetchCurationRequest();
                      await this.createCurationRequest();
                    }}
                    loading={this.loading}
                    primary
                    size="medium"
                    icon
                    labelPosition="left"
                    type="button"
                  >
                    {i18next.t("Create curation request")}
                  </Button>
                )}
              </div>
            )}
          </Card.Content>
        </Card>
      </Overridable>
    );
  }
}

CurationsContainerComponent.propTypes = {
  record: PropTypes.object.isRequired,
};

CurationsContainerComponent.defaultProps = {};

export const CurationsContainer = CurationsContainerComponent;
