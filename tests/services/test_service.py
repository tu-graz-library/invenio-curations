# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test curation services module."""

import copy

import pytest
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


@pytest.mark.parametrize("allow_changes", [True, False])
def test_curations_allow_changes_after_accept(
    app,
    db,
    curator_role,
    location,
    simple_identity,
    curator_identity,
    basic_record_data,
    monkeypatch,
    allow_changes,
):
    """Test CURATIONS_ALLOW_CHANGES_AFTER_ACCEPT configuration."""
    monkeypatch.setitem(
        app.config,
        "CURATIONS_ALLOW_CHANGES_AFTER_ACCEPT",
        allow_changes,
    )

    draft = current_rdm_records.records_service.create(
        identity=simple_identity,
        data=basic_record_data,
    )

    req = current_curations_service.create(
        identity=simple_identity,
        data={"topic": {"record": draft.id}},
    )

    current_requests_service.execute_action(curator_identity, req.id, "review")
    current_requests_service.execute_action(curator_identity, req.id, "accept")

    req_accepted = current_requests_service.read(simple_identity, req.id)
    assert req_accepted.data["status"] == "accepted"

    current_draft = current_rdm_records.records_service.draft_cls.pid.resolve(
        draft.id,
        registered_only=False,
    )
    assert current_curations_service.accepted_record(
        identity=simple_identity,
        record=current_draft,
    )

    # Updating without modifications should keep request accepted regardless of config
    current_rdm_records.records_service.update_draft(
        identity=simple_identity,
        id_=draft.id,
        data=basic_record_data,
    )
    req_unchanged = current_requests_service.read(simple_identity, req.id)
    assert req_unchanged.data["status"] == "accepted"

    # Modify draft metadata after acceptance
    updated_data = copy.deepcopy(basic_record_data)
    updated_data["metadata"]["title"] = "Updated title after accept"

    current_rdm_records.records_service.update_draft(
        identity=simple_identity,
        id_=draft.id,
        data=updated_data,
    )

    req_after_update = current_requests_service.read(simple_identity, req.id)
    current_draft = current_rdm_records.records_service.draft_cls.pid.resolve(
        draft.id,
        registered_only=False,
    )

    if allow_changes:
        assert req_after_update.data["status"] == "accepted"
        assert current_curations_service.accepted_record(
            identity=simple_identity,
            record=current_draft,
        )

        published = current_rdm_records.records_service.publish(
            identity=simple_identity,
            id_=draft.id,
        )
        assert published.id == draft.id
    else:
        assert req_after_update.data["status"] == "pending_resubmission"
        assert not current_curations_service.accepted_record(
            identity=simple_identity,
            record=current_draft,
        )

        with pytest.raises(CurationRequestNotAcceptedError):
            current_rdm_records.records_service.publish(
                identity=simple_identity,
                id_=draft.id,
            )

        # Ensure user can resubmit and proceed after re-acceptance
        current_requests_service.execute_action(simple_identity, req.id, "resubmit")
        req_resubmitted = current_requests_service.read(simple_identity, req.id)
        assert req_resubmitted.data["status"] == "resubmitted"

        current_requests_service.execute_action(curator_identity, req.id, "review")
        current_requests_service.execute_action(curator_identity, req.id, "accept")

        req_accepted_again = current_requests_service.read(simple_identity, req.id)
        assert req_accepted_again.data["status"] == "accepted"

        published = current_rdm_records.records_service.publish(
            identity=simple_identity,
            id_=draft.id,
        )
        assert published.id == draft.id
