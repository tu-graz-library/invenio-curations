..
    Copyright (C) 2021 CERN.
    Copyright (C) 2024 Graz University of Technology.
    Copyright (C) 2024 TU Wien.

    Invenio-Curations is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

=================
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

Invenio module for generic and customizable curations.

TODO: Please provide feature overview of module

Further documentation is available on
https://invenio-curations.readthedocs.io/


Update ``invenio.cfg``
----------------------

Add `notification builders` and `entity resolver` for `groups`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently, requests can only be sent to a single `receiver`.
However, curation reviews are typically performed by a `group` of people rather than one single fixed `user`.
Thus, the curation requests are sent to a `group` rather than a single `user` in the system so that all users with a certain `role` can receive and act on curation requests.

To enable resolution of user groups, an `entity resolver` has to be added to the configuration.

Additionally, notification builders have to be configured so that notifications are sent out to the involved users whenever something's happening in the curation review.

.. code-block:: python

    from invenio_curations.notifications.builders import (
        CurationRequestAcceptNotificationBuilder,
        CurationRequestSubmitNotificationBuilder,
    )
    from invenio_records_resources.references.entity_resolvers import ServiceResultResolver
    from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS, NOTIFICATIONS_ENTITY_RESOLVERS

    # enable sending of notifications when something's happening in the review
    NOTIFICATIONS_BUILDERS = {
        **NOTIFICATIONS_BUILDERS,
        # Curation request
        CurationRequestAcceptNotificationBuilder.type: CurationRequestAcceptNotificationBuilder,
        CurationRequestSubmitNotificationBuilder.type: CurationRequestSubmitNotificationBuilder,
    }

    # enable requests to target groups of users (i.e. `roles`)
    NOTIFICATIONS_ENTITY_RESOLVERS = NOTIFICATIONS_ENTITY_RESOLVERS + [
        ServiceResultResolver(service_id="groups", type_key="group")
    ]


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


Set requests permission policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the default InvenioRDM implementation, a user can submit an unpublished record to a community. Doing so will result in a `CommunitySubmission` request.
If this request is accepted, the record would also get published. Our `CurationComponent` would already stop the publish action. However, in the UI, the button to accept and publish is still visible and pushing it will present the user with a generic error.
In order to prevent this, the request permissions can be adapted such that the button is not shown in the first place.
Since we only want to change the behaviour of these community submission requests, we first check the type and then check the associated record. If the record has been accepted, the general request permissions will be applied. Otherwise, no one can accept the community submission.

.. code-block:: python
    from invenio_rdm_records.requests import CommunityInclusion, CommunitySubmission
    from invenio_rdm_records.services.permissions import RDMRequestsPermissionPolicy
    from invenio_curations.services.generators import (
        IfCurationRequestAccepted,
        IfRequestTypes,
    )


    class CurationRDMRequestsPermissionPolicy(RDMRequestsPermissionPolicy):
        """."""

        can_action_accept = [
            IfRequestTypes(
                request_types=[
                    CommunitySubmission,
                ],
                then_=[
                    IfCurationRequestAccepted(
                        then_=RDMRequestsPermissionPolicy.can_action_accept, else_=[]
                    )
                ],
                else_=RDMRequestsPermissionPolicy.can_action_accept,
            )
        ]


    REQUESTS_PERMISSION_POLICY = CurationRDMRequestsPermissionPolicy




Overwrite deposit view template
-------------------------------

The deposit view has to be updated to include the curation section.
Most importantly, the curation specific JavaScript has to be included in the JavaScript block:
``{{ webpack['invenio-curations-deposit.js'] }}``

This can be achieved by providing a custom template, e.g. in your instance's ``templates/`` directory:

Copy the current template from ``invenio_app_rdm/records_ui/templates/semantic-ui/invenio_app_rdm/records/deposit.html`` (available e.g. `here <https://github.com/inveniosoftware/invenio-app-rdm/blob/master/invenio_app_rdm/records_ui/templates/semantic-ui/invenio_app_rdm/records/deposit.html>`_) into your instance's ``templates/`` directory (the last parts of the path have to match): ``templates/semantic-ui/invenio_app_rdm/records/deposit.html``.

Then add the aforementioned line to the JavaScript block in your template:

.. code-block:: jinja

    {%- block javascript %}
      {{ super() }}
      ...

      {# This line right here #}
      {{ webpack['invenio-curations-deposit.js'] }}
    {%- endblock %}


Create curator role
-------------------

The permission to manage curation requests is controlled by a specific role in the system.
The name of this role can be specified via a configuration variable ``CURATIONS_MODERATION_ROLE``.

The following ``invenio roles`` command can be used to create the role if it doesn't exist yet: ``invenio roles create <name-of-curation-role>``.

After the role has been created, it can be assigned to users via: ``invenio roles add <user-email-address> <name-of-curation-role>``.
