// This file is part of InvenioRDM
// Copyright (C) 2025 Graz University of Technology.
//
// Invenio-Curations is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// NOTE: This entry point replaces invenio-app-rdm-user-requests.js for the
// curation overview page. It mirrors the default search app setup from
// invenio-app-rdm/user_dashboard/requests.js but uses a custom ResultsList.item.
// When upgrading invenio-app-rdm or invenio-requests, check if the original
// requests.js has added new default components or changed its setup.
// See: invenio_app_rdm/theme/assets/semantic-ui/js/invenio_app_rdm/user_dashboard/requests.js

import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  ContribBucketAggregationElement,
  ContribBucketAggregationValuesElement,
  ContribSearchAppFacets,
} from "@js/invenio_search_ui/components";
import React from "react";
import { overrideStore, parametrize } from "react-overridable";
import { withState } from "react-searchkit";
import { defaultContribComponents } from "@js/invenio_requests/contrib";
import { RDMRecordSearchBarElement } from "@js/invenio_app_rdm/search/components";
import {
  MobileRequestItem,
  RequestsSearchLayout,
  RequestsEmptyResultsWithState,
  RequestsResults,
} from "@js/invenio_requests/search";
import { CurationRequestItem } from "./CurationRequestItem";
import { curationComponentOverrides } from "../requests";
import PropTypes from "prop-types";

const appName = "InvenioAppRdm.DashboardRequests";

function CurationRequestsItemTemplate({ result }) {
  const CurationRequestItemWithState = withState(CurationRequestItem);
  const MobileRequestsItemWithState = withState(MobileRequestItem);
  const detailsURL = `/me/requests/${result.id}`;
  return (
    <>
      <CurationRequestItemWithState result={result} detailsURL={detailsURL} />
      <MobileRequestsItemWithState result={result} detailsURL={detailsURL} />
    </>
  );
}

CurationRequestsItemTemplate.propTypes = {
  result: PropTypes.object.isRequired,
};

const RequestsSearchLayoutWithApp = parametrize(RequestsSearchLayout, {
  appName: appName,
  showSharedFilters: true,
});

const defaultComponents = {
  [`${appName}.BucketAggregation.element`]: ContribBucketAggregationElement,
  [`${appName}.BucketAggregationValues.element`]: ContribBucketAggregationValuesElement,
  [`${appName}.SearchApp.facets`]: ContribSearchAppFacets,
  [`${appName}.ResultsList.item`]: CurationRequestsItemTemplate,
  [`${appName}.ResultsGrid.item`]: () => null,
  [`${appName}.SearchApp.layout`]: RequestsSearchLayoutWithApp,
  [`${appName}.SearchApp.results`]: RequestsResults,
  [`${appName}.SearchBar.element`]: RDMRecordSearchBarElement,
  [`${appName}.EmptyResults.element`]: RequestsEmptyResultsWithState,
  ...defaultContribComponents,
  ...curationComponentOverrides,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...defaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true
);
