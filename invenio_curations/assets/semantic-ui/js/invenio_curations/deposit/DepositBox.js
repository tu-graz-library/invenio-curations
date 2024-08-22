// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { http } from "react-invenio-forms";
import { Card, Form, Grid } from "semantic-ui-react";
import PropTypes from "prop-types";
import { getInputFromDOM } from "./utils";
import { DepositStatusBox, SaveButton, PreviewButton } from "@js/invenio_rdm_records";
import { ShareDraftButton } from "@js/invenio_app_rdm/deposit/ShareDraftButton";
import { RequestOrPublishButton } from "./RequestOrPublishButton";

// this component overrides the deposit status box from Invenio-App-RDM v12:
// https://github.com/inveniosoftware/invenio-app-rdm/blob/maint-v12.x/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/deposit/RDMDepositForm.js#L607-L651
export class DepositBox extends React.Component {
  constructor(props) {
    super(props);
    let { record, permissions, groupsEnabled } = props;

    this.recordFetchInterval = null;
    this.state = {
      latestRequest: null,
      loading: false,
      record: record || getInputFromDOM("deposits-record"),
      permissions: permissions,
      groupsEnabled: groupsEnabled,
    };
  }

  get record() {
    return this.state.record;
  }

  set loading(val) {
    this.setState({ loading: val });
  }

  get loading() {
    return this.state.loading;
  }

  componentDidMount() {
    this.fetchCurationRequest();

    this.recordFetchInterval = setInterval(() => {
      this.readLocalRecordId();
      if (this.record?.id != null) {
        clearInterval(this.recordFetchInterval);
      }
    }, 1000);
  }

  componentWillUnmount() {
    clearInterval(this.recordFetchInterval);
  }

  // try to fetch the record id from locally available information (like the URL)
  readLocalRecordId = () => {
    if (this.state.record?.id != null) {
      // if we already have a recid, there's no need to do anything
      return;
    }

    try {
      const urlParts = document.URL.split("uploads/");
      if (urlParts.length > 1) {
        const recid = urlParts[1];
        if (recid === "new") return;

        this.setState((prevState) => {
          return { record: { ...prevState.record, id: recid } };
        });
      }
    } catch (error) {
      console.error("Error while fetching local record:", error);
    }
  };

  // get the (latest) curation request for the current record
  fetchCurationRequest = async () => {
    this.loading = true;

    try {
      const request = await http.get("/api/curations", {
        params: { expand: 1, topic: `record:${this.record.id}` },
      });

      const hits = request.data.hits;
      this.setState({ latestRequest: hits.total > 0 ? hits.hits[0] : null });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };

  // create a new curation request for the record
  createCurationRequest = async () => {
    this.loading = true;

    const payload = { topic: { record: this.record.id } };
    try {
      const request = await http.post("/api/curations", payload, {
        params: { expand: 1 },
      });

      this.setState({ latestRequest: request.data });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };

  // resubmit the curation request
  resubmitCurationRequest = async () => {
    this.loading = true;
    try {
      const { latestRequest } = this.state;
      const request = await http.post(latestRequest.links.actions.resubmit);
      this.setState({ latestRequest: request.data });
    } catch (e) {
      console.error(e);
    }

    this.loading = false;
  };

  render() {
    const { latestRequest, record, groupsEnabled, permissions } = this.state;

    return (
      <Card className="access-right">
        <Form.Field required>
          <Card.Content>
            <DepositStatusBox />
          </Card.Content>

          <Card.Content>
            <Grid relaxed>
              <Grid.Column computer={8} mobile={16} className="pb-0 left-btn-col">
                <SaveButton fluid />
              </Grid.Column>

              <Grid.Column computer={8} mobile={16} className="pb-0 right-btn-col">
                <PreviewButton fluid />
              </Grid.Column>

              <Grid.Column width={16} className="pt-10 pb-10">
                <RequestOrPublishButton
                  request={latestRequest}
                  record={record}
                  loading={this.loading}
                  handleCreateRequest={async () => {
                    await this.fetchCurationRequest();
                    await this.createCurationRequest();
                  }}
                  handleResubmitRequest={async () => {
                    await this.resubmitCurationRequest();
                  }}
                />
              </Grid.Column>

              <Grid.Column width={16} className="pt-0">
                {(record.is_draft === null || permissions.can_manage) && (
                  <ShareDraftButton
                    record={record}
                    permissions={permissions}
                    groupsEnabled={groupsEnabled}
                  />
                )}
              </Grid.Column>
            </Grid>
          </Card.Content>
        </Form.Field>
      </Card>
    );
  }
}

DepositBox.propTypes = {
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object,
  groupsEnabled: PropTypes.bool,
};

DepositBox.defaultProps = {
  record: null,
  permissions: null,
  groupsEnabled: false,
};
