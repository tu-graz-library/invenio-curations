// -*- coding: utf-8 -*-
//
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { i18next } from "@translations/invenio_curations/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { http, FieldLabel } from "react-invenio-forms";
import Overridable from "react-overridable";
import { Button, Card, Grid, GridColumn, Icon, Popup } from "semantic-ui-react";

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
      if (this.record.id !== undefined && this.record.id !== null) {
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
      const urlParts = document.URL.split("uploads/");
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
      const request = await http.get("/api/curations", {
        params: {
          expand: 1,
          topic: `record:${this.record.id}`,
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

    const payload = {
      topic: {
        record: this.record.id,
      },
    };
    try {
      const request = await http.post("/api/curations", payload, {
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
    const { latestRequest, record } = this.state;
    const recordIdAvailable = record.id !== undefined && record.id !== null;
    const recordCurationLabel = (
      <span className="ml-5 mr-10">{i18next.t("Curation request")}</span>
    );

    return (
      <Overridable id="InvenioCurations.Deposit.CurationsBox.Container">
        <Card fluid>
          <Card.Content>
            <Card.Content>
              <Grid verticalAlign="top" columns={2}>
                <GridColumn>
                  <FieldLabel label={recordCurationLabel} icon="eye" />

                  {latestRequest ? (
                    <RequestStatusLabel status={latestRequest.status} />
                  ) : (
                    <span className="ui label">
                      {i18next.t("No open request for this record exists.")}
                    </span>
                  )}
                </GridColumn>

                <GridColumn textAlign="right">
                  {latestRequest ? (
                    <Button
                      as="a"
                      href={`/me/requests/${latestRequest.id}`}
                      icon
                      labelPosition="right"
                      size="tiny"
                    >
                      {i18next.t("View request")}
                      <Icon name="right arrow" />
                    </Button>
                  ) : (
                    <Popup
                      disabled={recordIdAvailable}
                      content={i18next.t(
                        "Before creating a curation request, the draft has to be saved."
                      )}
                      trigger={
                        <span>
                          <Button
                            onClick={async () => {
                              await this.fetchCurationRequest();
                              await this.createCurationRequest();
                            }}
                            loading={this.loading}
                            primary
                            size="tiny"
                            type="button"
                            disabled={!recordIdAvailable}
                          >
                            {i18next.t("Create curation request")}
                          </Button>
                        </span>
                      }
                    />
                  )}
                </GridColumn>
              </Grid>
            </Card.Content>
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
