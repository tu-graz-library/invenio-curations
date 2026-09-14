# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test curation services module."""

from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from flask_principal import Identity
from invenio_access.permissions import system_identity
from invenio_rdm_records.proxies import current_rdm_records
from invenio_rdm_records.requests import CommunitySubmission
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_requests import current_request_type_registry, current_requests_service
from invenio_requests.errors import CannotExecuteActionError

from invenio_curations import current_curations_service
from invenio_curations.services.errors import CurationRequestNotAcceptedError


def test_create_curation_request(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    basic_record_data,
):
    """Test the creation of a curation request."""
    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )

    res = current_curations_service.create(
        identity=simple_identity,
        data={"topic": {"record": draft.id}},
    )

    assert res.id
    assert res.data["title"] == "RDM Curation: Test curation"
    assert res.data["type"] == "rdm-curation"


def test_curation_basic_flow(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    curator_identity,
    basic_record_data,
):
    """Test the whole basic flow of a curation request.

    Draft create -> CR submit -> CR request review ->
    CR accept -> Check CR accepted
    CR = curation request
    """
    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )

    req = current_curations_service.create(
        identity=simple_identity,
        data={"topic": {"record": draft.id}},
    )

    res = current_curations_service.get_curations_data(simple_identity)

    expected_res = {
        "is_privileged": False,
        "publishing_edits": False,
        "auto_publish_on_accept": False,
    }

    assert res == expected_res

    current_draft = current_rdm_records.records_service.draft_cls.pid.resolve(
        draft.id,  # type: ignore[index]
        registered_only=False,
    )
    assert not current_curations_service.accepted_record(
        identity=simple_identity,
        record=current_draft,
    )

    current_requests_service.execute_action(curator_identity, req.id, "review")
    current_requests_service.execute_action(curator_identity, req.id, "accept")

    assert current_curations_service.accepted_record(
        identity=simple_identity,
        record=current_draft,
    )


def test_curation_bypass_curation(
    app,
    db,
    curator_role,
    location,
    bypass_curation_identity,
    basic_record_data,
):
    """Test privileged user capabilities."""
    draft = current_rdm_records.records_service.create(
        identity=bypass_curation_identity,
        data=basic_record_data,
    )

    res = current_curations_service.get_curations_data(bypass_curation_identity)

    expected_res = {
        "is_privileged": True,
        "publishing_edits": False,
        "auto_publish_on_accept": False,
    }

    assert res == expected_res

    current_rdm_records.records_service.publish(
        bypass_curation_identity,
        draft.id,
    )


def test_curation_permissions_non_community(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    curator_identity,
    bypass_curation_identity,
    basic_record_data,
):
    """Test basic curation permissions."""
    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )

    req = current_curations_service.create(
        identity=simple_identity,
        data={"topic": {"record": draft.id}},
    )

    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(simple_identity, req.id, "review")

    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(simple_identity, req.id, "accept")

    current_requests_service.execute_action(curator_identity, req.id, "review")
    current_requests_service.execute_action(curator_identity, req.id, "critique")

    with pytest.raises(CannotExecuteActionError):
        current_requests_service.execute_action(simple_identity, req.id, "submit")

    current_requests_service.execute_action(simple_identity, req.id, "resubmit")

    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(
            bypass_curation_identity,
            req.id,
            "review",
        )

    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(
            bypass_curation_identity,
            req.id,
            "accept",
        )


def test_curation_permissions_community_w_curations(
    app,
    db,
    curator_role,
    location,
    curator_identity,
    basic_record_data,
    community_simple,
    com_owner_identity,
):
    """Test curation with community records.

    Test the flow and permission when a record is submitted inside a community
    and curation request is also created.
    """
    draft = current_rdm_records.records_service.create(
        identity=com_owner_identity,
        data=basic_record_data,
    )

    cur_req = current_curations_service.create(
        identity=com_owner_identity,
        data={"topic": {"record": draft.id}},
    )

    com_id = str(community_simple.id)

    receiver = {"community": com_id}

    community_submission = current_request_type_registry.lookup(
        CommunitySubmission.type_id,
    )

    com_req = current_requests_service.create(
        com_owner_identity,
        {},
        community_submission,
        receiver,
        topic={"record": draft.id},
    )

    current_requests_service.execute_action(com_owner_identity, com_req.id, "submit")

    with pytest.raises(PermissionDeniedError):
        current_requests_service.execute_action(
            com_owner_identity,
            com_req.id,
            "accept",
        )

    current_requests_service.execute_action(curator_identity, cur_req.id, "review")
    current_requests_service.execute_action(curator_identity, cur_req.id, "accept")

    current_requests_service.execute_action(com_owner_identity, com_req.id, "accept")


def test_curation_permissions_community_wo_curations(
    app,
    db,
    curator_role,
    location,
    basic_record_data,
    community_bypass,
    bypass_curation_identity,
):
    """Test community records without curation.

    Test the flow and permission when a record is submitted inside a community
    and curation request is not created. (aka privileged curation user submitted
    the record)
    """
    draft = current_rdm_records.records_service.create(
        identity=bypass_curation_identity,
        data=basic_record_data,
    )

    com_id = str(community_bypass.id)

    receiver = {"community": com_id}

    community_submission = current_request_type_registry.lookup(
        CommunitySubmission.type_id,
    )

    com_req = current_requests_service.create(
        bypass_curation_identity,
        {},
        community_submission,
        receiver,
        topic={"record": draft.id},
    )

    current_requests_service.execute_action(
        bypass_curation_identity,
        com_req.id,
        "submit",
    )
    current_requests_service.execute_action(
        bypass_curation_identity,
        com_req.id,
        "accept",
    )


def test_get_review_cache_isolates_kwargs():
    """get_review cache must use separate entries for different kwargs.

    A call with expand=True must not reuse the cached result from a prior call
    without expand, which would return unexpanded data to the caller.
    """
    from invenio_curations.services.service import CurationRequestService

    identity = Identity("test-user")
    draft = MagicMock()

    mock_results = MagicMock()
    mock_results.total = 0
    mock_results.hits = iter([])

    service = CurationRequestService.__new__(CurationRequestService)
    service.requests_service = MagicMock()
    service.requests_service.search.return_value = mock_results
    mock_type = MagicMock()
    mock_type.type_id = "rdm-curation"
    service._request_type_registry = MagicMock()  # noqa: SLF001
    service._request_type_registry.lookup.return_value = mock_type  # noqa: SLF001

    with Flask(__name__).test_request_context(), patch(
        "invenio_curations.services.service.ResolverRegistry",
    ) as mock_registry:
        mock_registry.reference_entity.return_value = {"record": "test-draft-id"}
        service.get_review(identity, draft)
        service.get_review(identity, draft, expand=True)

    assert (
        service.requests_service.search.call_count == 2  # noqa: PLR2004
    ), (
        "different kwargs must produce separate cache entries and trigger two searches"
    )


def test_block_edit_during_review(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    curator_identity,
    basic_record_data,
):
    """CURATIONS_BLOCK_EDIT_DURING_REVIEW prevents draft updates while under active review."""
    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )
    req = current_curations_service.create(
        identity=simple_identity,
        data={"topic": {"record": draft.id}},
    )
    current_requests_service.execute_action(curator_identity, req.id, "review")

    app.config["CURATIONS_BLOCK_EDIT_DURING_REVIEW"] = True
    try:
        with pytest.raises(PermissionDeniedError):
            current_rdm_records.records_service.update_draft(
                identity=simple_identity,
                id_=draft.id,
                data=basic_record_data,
            )
    finally:
        app.config["CURATIONS_BLOCK_EDIT_DURING_REVIEW"] = False

    # Flag off: update succeeds
    current_rdm_records.records_service.update_draft(
        identity=simple_identity,
        id_=draft.id,
        data=basic_record_data,
    )


def test_allow_publishing_edits(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    basic_record_data,
):
    """CURATIONS_ALLOW_PUBLISHING_EDITS lets owners re-publish edits without curation.

    Scenario: record published by system (no curation request exists).
    Without flag, re-publishing an edit fails. With flag, it succeeds.
    """
    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )
    current_rdm_records.records_service.publish(system_identity, draft.id)

    edit_draft = current_rdm_records.records_service.edit(
        identity=simple_identity,
        id_=draft.id,
    )

    with pytest.raises(CurationRequestNotAcceptedError):
        current_rdm_records.records_service.publish(simple_identity, edit_draft.id)

    app.config["CURATIONS_ALLOW_PUBLISHING_EDITS"] = True
    try:
        current_rdm_records.records_service.publish(simple_identity, edit_draft.id)
    finally:
        app.config["CURATIONS_ALLOW_PUBLISHING_EDITS"] = False
