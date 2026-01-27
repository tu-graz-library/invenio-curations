# -*- coding: utf-8 -*-
#
# Copyright (C) 2024-2026 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import pytest
from flask_principal import Identity, Need, RoleNeed, UserNeed
from flask_security.utils import hash_password
from invenio_access.permissions import system_identity
from invenio_accounts.models import Role
from invenio_accounts.proxies import current_datastore
from invenio_app.factory import create_app as _create_app
from invenio_communities import current_communities
from invenio_communities.communities.records.api import Community
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_rdm_records import config
from invenio_rdm_records.services.components import DefaultRecordsComponents
from invenio_records_resources.services.records.results import RecordItem
from invenio_vocabularies.proxies import current_service as vocabulary_service

from invenio_curations.services.components import CurationComponent
from invenio_curations.services.permissions import (
    CurationRDMRecordPermissionPolicy,
    CurationRDMRequestsPermissionPolicy,
)


@pytest.fixture(scope="module")
def app_config(app_config):
    """Application config override."""
    # Generic configs
    app_config["THEME_FRONTPAGE"] = False
    app_config["REST_CSRF_ENABLED"] = False

    # Curation Specific configs
    app_config["CURATIONS_PRIVILEGED_ROLES"] = ["administration", "bypass-curation"]
    app_config["CURATIONS_MODERATION_ROLE"] = "administration-rdm-records-curation"
    app_config["REQUESTS_PERMISSION_POLICY"] = CurationRDMRequestsPermissionPolicy
    app_config["RDM_PERMISSION_POLICY"] = CurationRDMRecordPermissionPolicy

    # RDM Records configs
    supported_configurations = [
        "FILES_REST_PERMISSION_FACTORY",
        "PIDSTORE_RECID_FIELD",
        "RECORDS_PERMISSIONS_RECORD_POLICY",
        "RECORDS_REST_ENDPOINTS",
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    app_config["FILES_REST_STORAGE_CLASS_LIST"] = {
        "L": "Local",
    }
    app_config["FILES_REST_DEFAULT_STORAGE_CLASS"] = "L"

    app_config["RECORDS_REFRESOLVER_CLS"] = (
        "invenio_records.resolver.InvenioRefResolver"
    )
    app_config["RECORDS_REFRESOLVER_STORE"] = (
        "invenio_jsonschemas.proxies.current_refresolver_store"
    )
    app_config["RDM_RECORDS_SERVICE_COMPONENTS"] = DefaultRecordsComponents + [
        CurationComponent,
    ]
    app_config["RDM_COMMUNITY_REQUIRED_TO_PUBLISH"] = False

    return app_config


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return _create_app


@pytest.fixture
def users(app, db):
    """Create example users."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="curator@inveniosoftware.org",
            password=hash_password("curation"),
            active=True,
        )
        user3 = datastore.create_user(
            email="bypass@inveniosoftware.org",
            password=hash_password("bypasser"),
            active=True,
        )
        user4 = datastore.create_user(
            email="community@inveniosoftware.org",
            password=hash_password("communityboss"),
            active=True,
        )

    db.session.commit()
    return [user1, user2, user3, user4]


@pytest.fixture
def curator_role(db):
    """Create the curation moderation role."""
    r = Role()
    r.name = "administration-rdm-records-curation"
    db.session.add(r)
    db.session.commit()
    return r


@pytest.fixture
def simple_identity(users):
    """Basic user."""
    user = users[0]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture
def curator_identity(users, curator_role):
    """Curator user."""
    user = users[1]
    identity = Identity(user.id)
    identity.provides.add(UserNeed(user.id))
    curator_role = current_datastore.find_role("administration-rdm-records-curation")
    identity.provides.add(RoleNeed(curator_role.id))
    identity.provides.add(Need(method="system_role", value="authenticated_user"))
    return identity


@pytest.fixture
def bypass_curation_identity(app, db, users):
    """Bypass-curation identity."""
    user = users[2]
    i = Identity(user.id)

    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        role = datastore.find_or_create_role(name="bypass-curation")
        datastore.add_role_to_user(user, role)
        datastore.commit()
    i.provides.add(UserNeed(user.id))
    i.provides.add(RoleNeed("bypass-curation"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture
def com_owner_identity(users):
    """Community owner user."""
    user = users[3]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture
def basic_record_data(resource_type_type):
    """Basic RDM vocabulary and record data."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
                "marc21_type": "dataset",
                "marc21_subtype": "",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    },
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "publication_date": "2020-06-01",
            "publisher": "Acme Inc",
            "resource_type": {"id": "dataset"},
            "title": "Test curation",
        },
    }


@pytest.fixture
def minimal_community():
    """Data for a minimal community."""
    return {
        "slug": "blr",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Biodiversity Literature Repository",
        },
    }


def _community_get_or_create(community_dict: dict, identity: Identity) -> RecordItem:
    """Util to get or create community, to avoid duplicate error."""
    slug = community_dict["slug"]
    try:
        c = current_communities.service.record_cls.pid.resolve(slug)
    except PIDDoesNotExistError:
        c = current_communities.service.create(
            identity,
            community_dict,
        )
        Community.index.refresh()
    return c


@pytest.fixture
def community_simple(com_owner_identity, minimal_community):
    """Get a basic community."""
    return _community_get_or_create(minimal_community, com_owner_identity)


@pytest.fixture
def community_bypass(bypass_curation_identity, minimal_community):
    """Get the community with the bypass-curation owner."""
    return _community_get_or_create(minimal_community, bypass_curation_identity)
