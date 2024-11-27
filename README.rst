..
    Copyright (C) 2021 CERN.
    Copyright (C) 2024 Graz University of Technology.
    Copyright (C) 2024 TU Wien.

    Invenio-Curations is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Invenio-Curations
=================

.. image:: https://github.com/tu-graz-library/invenio-curations/workflows/CI/badge.svg
        :target: https://github.com/tu-graz-library/invenio-curations/actions?query=workflow%3ACI

.. image:: https://img.shields.io/github/tag/tu-graz-library/invenio-curations.svg
        :target: https://github.com/tu-graz-library/invenio-curations/releases

.. image:: https://img.shields.io/pypi/dm/invenio-curations.svg
        :target: https://pypi.python.org/pypi/invenio-curations

.. image:: https://img.shields.io/github/license/tu-graz-library/invenio-curations.svg
        :target: https://github.com/tu-graz-library/invenio-curations/blob/master/LICENSE


What *is* `Invenio-Curations`?
------------------------------

`Invenio-Curations` is an Invenio package that adds curation reviews to InvenioRDM.

The primary purpose of this package is to satisfy the need of some institutions to restrict the possibility for users to self-publish unreviewed records.
One of the reasons why institutions may want this is if they are pursuing a `Core Trust Seal <https://www.coretrustseal.org/>`_ or similar certification for their (InvenioRDM-based) repository.


Aren't there community reviews already?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Out of the box, InvenioRDM already provides reviews for records as part of the submission or inclusion into communities.
However, there is no requirement per default for records to be part of any community at all.
Thus, it is generally easy for users to self-publish records in standard InvenioRDM without any further review.

Further, the set of reviewers for community submission/inclusion requests depends on the target community in question.
In contrast, `Invenio-Curations` defines a fixed group of users to act as reviewers for all records in the system.


Requirements
------------

Requires InvenioRDM v12 or higher (``invenio-app-rdm >= 12.0.7``).


How to set up
-------------

After the successful installation of `Invenio-Curations`, it still needs to be configured properly to work.
The following sections should guide you through the required adaptations.


Update ``invenio.cfg``
~~~~~~~~~~~~~~~~~~~~~~

Add `notification builders` for `groups`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, requests can only be sent to a single `receiver`.
However, curation reviews are typically performed by a `group` of people rather than one single fixed `user`.
Thus, the curation requests are sent to a `group` rather than a single `user` in the system so that all users with a certain `role` can receive and act on curation requests.

Additionally, notification builders have to be configured so that notifications are sent out to the involved users whenever something's happening in the curation review.

.. code-block:: python

    from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS
    from invenio_curations.config import CURATIONS_NOTIFICATIONS_BUILDERS

    # enable sending of notifications when something's happening in the review
    NOTIFICATIONS_BUILDERS = {
        **NOTIFICATIONS_BUILDERS,
        # Curation request
        **CURATIONS_NOTIFICATIONS_BUILDERS
    }


Add service component
^^^^^^^^^^^^^^^^^^^^^

In order to require an accepted curation request before publishing a record, the component has to be appended to the RDM record service:

.. code-block:: python

    from invenio_curations.services.components import CurationComponent
    from invenio_rdm_records.services.components import DefaultRecordsComponents

    # NOTE: the curation component should be added at the end
    RDM_RECORDS_SERVICE_COMPONENTS = DefaultRecordsComponents + [
        CurationComponent,
    ]


Set the search facets
^^^^^^^^^^^^^^^^^^^^^

To show friendlier names than the internal identifiers for the new request type and its status values in the search facets, you need to set the following configuration:

.. code-block:: python

   from invenio_curations.services import facets as curations_facets

    REQUESTS_FACETS = {
        "type": {
            "facet": curations_facets.type,
            "ui": {
                "field": "type",
            },
        },
        "status": {
            "facet": curations_facets.status,
            "ui": {
                "field": "status",
            },
        },
    }


Set requests permission policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting the requests permission is done due to the following reasons:

Additional actions have to be specified.

Reading a request and creating comments depends on the state. Since new states are added, these states have to be included for these two permissions.

In the default InvenioRDM implementation, a user can submit an unpublished record to a community. Doing so will result in a `CommunitySubmission` request.
If this request is accepted, the record would also get published. Our `CurationComponent` would already stop the publish action. However, in the UI, the button to accept and publish is still visible and pushing it will present the user with a generic error.
In order to prevent this, the request permissions can be adapted such that the button is not shown in the first place.
Since we only want to change the behaviour of these community submission requests, we first check the type and then check the associated record. If the record has been accepted, the general request permissions will be applied. Otherwise, no one can accept the community submission.

.. code-block:: python

    from invenio_rdm_records.requests import CommunitySubmission
    from invenio_rdm_records.services.permissions import RDMRequestsPermissionPolicy
    from invenio_requests.services.generators import Creator, Receiver

    from invenio_curations.requests.curation import CurationRequest
    from invenio_curations.services.generators import (
        IfCurationRequestAccepted,
        IfRequestTypes,
        TopicPermission,
    )


    class CurationRDMRequestsPermissionPolicy(RDMRequestsPermissionPolicy):
        """Customized permission policy for sane handling of curation requests."""

        curation_request_record_review = IfRequestTypes(
            [CurationRequest],
            then_=[TopicPermission(permission_name="can_review")],
            else_=[],
        )

        # Only allow community-submission requests to be accepted after the rdm-curation request has been accepted
        can_action_accept = [
            IfRequestTypes(
                request_types=[CommunitySubmission],
                then_=[
                    IfCurationRequestAccepted(
                        then_=RDMRequestsPermissionPolicy.can_action_accept, else_=[]
                    )
                ],
                else_=RDMRequestsPermissionPolicy.can_action_accept,
            )
        ]

        # Update can read and can comment with new states
        can_read = [
            # Have to explicitly check the request type and circumvent using status, as creator/receiver will add a query filter where one entity must be the user.
            IfRequestTypes(
                [CurationRequest],
                then_=[
                    Creator(),
                    Receiver(),
                    TopicPermission(permission_name="can_review"),
                ],
                else_=RDMRequestsPermissionPolicy.can_read,
            )
        ]

        can_create_comment = can_read

        # Update submit to also allow record reviewers/managers for curation requests
        can_action_submit = RDMRequestsPermissionPolicy.can_action_submit + [
            curation_request_record_review
        ]
        # Add new actions
        can_action_review = RDMRequestsPermissionPolicy.can_action_accept
        can_action_critique = RDMRequestsPermissionPolicy.can_action_accept

        can_action_resubmit = can_action_submit

    REQUESTS_PERMISSION_POLICY = CurationRDMRequestsPermissionPolicy


Permit the moderators to view the draft under review
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For curation reviews to make sense, it is of course vital for the moderators to be able to view the drafts in question.

`Invenio-Curations` offers two permission generators that can come in handy for this purpose: ``CurationModerators`` and ``IfCurationRequestExists``.
The former creates ``RoleNeed`` for the configured ``CURATIONS_MODERATION_ROLE``.
It is intended to be used together with the latter, which checks if an ``rdm-curation`` request exists for the given record/draft.

However, please note that overriding the permission policy for records is significantly more complex than overriding the one for requests!
In fact, it's out of scope for this README - or is it?


Set RDM permission policy
^^^^^^^^^^^^^^^^^^^^^^^^^

Reasons to not rely on access grants:
- They can be completely disabled for an instance
- They can be managed by users which means they can just remove access for the moderators

Thus, we provide a very basic adaptation of the RDM record permission policy used in a vanilla instance. This adapted policy should serve as
an easy way to test the package as well as provide a starting point to understand which permissions have to be adapted for this module to work as expected.

.. code-block:: python

    from invenio_curations.services.permissions import CurationRDMRecordPermissionPolicy
    RDM_PERMISSION_POLICY = CurationRDMRecordPermissionPolicy


Make the new workflow available through the UI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The changes so far have dealt with setting up the mechanism for the curation workflow in the backend.
To also make the workflow accessible for users through the UI, some frontend components have to be updated as well.

`Invenio-Curations` provides a few `component overrides <https://inveniordm.docs.cern.ch/develop/howtos/override_components/>`_.
These overrides need to be registered in the overridable registry (i.e. in your instance's ``assets/js/invenio_app_rdm/overridableRegistry/mapping.js``):

.. code-block:: javascript

    import { curationComponentOverrides } from "@js/invenio_curations/requests";
    import { DepositBox } from "@js/invenio_curations/deposit/DepositBox";

    export const overriddenComponents = {
        // ... after your other overrides ...
        ...curationComponentOverrides,
        "InvenioAppRdm.Deposit.CardDepositStatusBox.container": DepositBox,
    };

The ``DepositBox`` overrides the record's lifecycle management box on the deposit form.
It takes care of rendering the "publish" button only when appropriate in the curation workflow.
The other ``curationComponentOverrides`` provide better rendering for the new elements (e.g. event types) in the request page.


Create curator role
~~~~~~~~~~~~~~~~~~~

The permission to manage curation requests is controlled by a specific role in the system.
The name of this role can be specified via a configuration variable ``CURATIONS_MODERATION_ROLE``.

The following ``invenio roles`` command can be used to create the role if it doesn't exist yet: ``invenio roles create <name-of-curation-role>``.

After the role has been created, it can be assigned to users via: ``invenio roles add <user-email-address> <name-of-curation-role>``.
