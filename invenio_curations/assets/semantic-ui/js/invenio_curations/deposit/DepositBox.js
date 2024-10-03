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

    this.recordFetchInterval = null;
    this.state = {
      latestRequest: null,
      loading: false,
      lastFetchedAt: null,
    };
  }

  componentDidMount() {
    this.fetchCurationRequest();
    this._setInterval();
  }

  componentWillUnmount() {
    this._clearInterval();
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
    this.setState({ lastFetchedAt: Date.now() });
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

  _clearInterval = () => {
    this.recordFetchInterval = window.clearInterval(this.recordFetchInterval);
  };

  _setInterval = () => {
    // Fetch request every 10 seconds to get updates without manual refresh
    // make sure to clear old interval
    this.recordFetchInterval ??= window.setInterval(
      this.fetchCurationRequest,
      1000 * 10
    );
  };

  resetInterval = () => {
    this._clearInterval();
    this._setInterval();
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

  handleSave = () => {
    this.loading = true;
    try {
      // We assume there is exactly one button named `save` which is the save draft button.
      // Another approach would be to get the redux context from the deposit form and perform the same actions the `SaveButton` performs.
      // However, the context is not exported from invenio-rdm-records at the moment. This implementation can be adapted if this changes.

      // see
      //  - SaveButton action: https://github.com/inveniosoftware/invenio-rdm-records/blob/a4fbec8dbde537244a58d905495fb6919029abaa/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records/src/deposit/controls/SaveButton/SaveButton.js#L25-L33
      //  - DepositFormSubmitContext: https://github.com/inveniosoftware/invenio-rdm-records/blob/a4fbec8dbde537244a58d905495fb6919029abaa/invenio_rdm_records/assets/semantic-ui/js/invenio_rdm_records/src/deposit/api/DepositFormSubmitContext.js
      let saveButton = document.getElementsByName("save")[0];
      saveButton.click();
    } catch (error) {
      console.error("Error when trying to save the draft", error);
    }
    this.loading = false;
  };

  checkShouldFetchCurationRequest = async () => {
    // Fetch curation request instantly when record was updated from an external component
    const { lastFetchedAt } = this.state;
    const { lastFormikUpdatedAt } = this.props;

    // Checking lastFormikUpdatedAt as `record.updated` is not deserialized from the backend response.
    // If the relevant PR is merged or this change is added somewhere else, lastFormikUpdatedAt can be removed completely.
    // PR: https://github.com/inveniosoftware/invenio-rdm-records/pull/1838
    if (lastFetchedAt < lastFormikUpdatedAt) {
      this.resetInterval();
      this.fetchCurationRequest();
    }
  };

  render() {
    const { latestRequest } = this.state;
    const { record, permissions, groupsEnabled } = this.props;

    this.checkShouldFetchCurationRequest();

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
                  handleCreateRequest={async (event) => {
                    this.handleSave(event);
                    await this.fetchCurationRequest();
                    await this.createCurationRequest();
                  }}
                  handleResubmitRequest={async (event) => {
                    this.handleSave(event);
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
  lastFormikUpdatedAt: PropTypes.object,
};

DepositBoxComponent.defaultProps = {
  permissions: null,
  groupsEnabled: false,
  lastFormikUpdatedAt: Date.now(),
};

// In order to create the rdm-curation request, we need the `record.id` in the `DepositBox`, so we
// can't wire up the `RequestOrPublishButton` with the Formik state like the `ShareDraftButton` does.
// However, the `state.deposit.record` coming from Formik may not have the `record.parent` property
// which is expected by the `ShareDraftButton` (and passed to it as prop from the `DepositBox`).
// Thus, we merge the incoming record with the one from the original props.
const mapStateToProps = (state, ownProps) => ({
  record: { ...ownProps.record, ...state.deposit.record },
  lastFormikUpdatedAt: Date.now(),
});

export const DepositBox = connect(
  mapStateToProps,
  null
)(connectFormik(DepositBoxComponent));
