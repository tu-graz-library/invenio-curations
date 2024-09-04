// This file is part of InvenioRDM
// Copyright (C) 2024 TU Wien.
// Copyright (C) 2024 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { http } from "react-invenio-forms";
import { Card, Form, Grid } from "semantic-ui-react";
import PropTypes from "prop-types";
import { DepositStatusBox, SaveButton, PreviewButton } from "@js/invenio_rdm_records";
import { ShareDraftButton } from "@js/invenio_app_rdm/deposit/ShareDraftButton";
import { RequestOrPublishButton } from "./RequestOrPublishButton";
import { connect } from "react-redux";
import { connect as connectFormik } from "formik";

// this component overrides the deposit status box from Invenio-App-RDM v12:
// https://github.com/inveniosoftware/invenio-app-rdm/blob/maint-v12.x/invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/deposit/RDMDepositForm.js#L607-L651
export class DepositBoxComponent extends React.Component {
  constructor(props) {
    super(props);
    let { permissions, groupsEnabled } = props;

    this.recordFetchInterval = null;
    this.state = {
      latestRequest: null,
      loading: false,
      permissions: permissions,
      groupsEnabled: groupsEnabled,
    };
  }

  componentDidMount() {
    this.fetchCurationRequest();
  }

  componentWillUnmount() {
    clearInterval(this.recordFetchInterval);
  }

  get record() {
    const { record } = this.props;
    return record;
  }

  set loading(val) {
    this.setState({ loading: val });
  }

  get loading() {
    const { loading } = this.state;
    return loading;
  }

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
    const { latestRequest, groupsEnabled, permissions } = this.state;
    const { record } = this.props;

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

DepositBoxComponent.propTypes = {
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object,
  groupsEnabled: PropTypes.bool,
};

DepositBoxComponent.defaultProps = {
  permissions: null,
  groupsEnabled: false,
};

const mapStateToProps = (state) => ({
  record: state.deposit.record,
});

export const DepositBox = connect(
  mapStateToProps,
  null
)(connectFormik(DepositBoxComponent));
