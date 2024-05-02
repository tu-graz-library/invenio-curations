..
    Copyright (C) 2021 CERN.

    Invenio-curations is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

==================
 Invenio-curations
==================

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



## Update invenio.cfg
### Add notification builders and entity resolver for groups

from invenio_curations.notifications.builders import (
    CurationRequestAcceptNotificationBuilder,
    CurationRequestSubmitNotificationBuilder,
)

from invenio_records_resources.references.entity_resolvers import ServiceResultResolver

from invenio_app_rdm.config import NOTIFICATIONS_BUILDERS, NOTIFICATIONS_ENTITY_RESOLVERS
NOTIFICATIONS_BUILDERS = {
    **NOTIFICATIONS_BUILDERS,
    # Curation request
    CurationRequestAcceptNotificationBuilder.type: CurationRequestAcceptNotificationBuilder,
    CurationRequestSubmitNotificationBuilder.type: CurationRequestSubmitNotificationBuilder,
}

NOTIFICATIONS_ENTITY_RESOLVERS = NOTIFICATIONS_ENTITY_RESOLVERS + [ServiceResultResolver(service_id="groups", type_key="group")]


### Add service component
In order to require an accepted curation request before publishing a record, the component has to be added to the RDM record service
```py
from invenio_curations.services.components import CurationComponent
from invenio_rdm_records.services.components import DefaultRecordsComponents
RDM_RECORDS_SERVICE_COMPONENTS = DefaultRecordsComponents + [
    CurationComponent,
]
```

## Overwrite deposit view
The deposit view has to be updated to include the curation section. Most importantly, the curation specific javascript has to be included in the javascript block:
`{{ webpack['invenio-curations-deposit.js'] }}`

This can be achieved by providing a custom template. Make sure to copy the current template from `invenio_app_rdm/records_ui/templates/semantic-ui/invenio_app_rdm/records/deposit.html`.
In order to override this, place it into your instances `templates/semantic-ui/invenio_app_rdm/records/deposit.html` folder.
Then add the afore mentioned line to the javascript block in the template
```
{%- block javascript %}
  {{ super() }}
  ...

  {# This line right here #}
  {{ webpack['invenio-curations-deposit.js'] }}
{%- endblock %}

```

## Create curator role
A curator role is used to ensure a user has the permission to manage curation requests. Its name is specified via a config variable `CURATIONS_MODERATION_ROLE`.
In order to create this role, the following command can be run inside an instance: `invenio roles create <name-of-curation-role>`
Adding a role to a user can be achieved by running: `invenio roles add <user-email-address> <name-of-curation-role>`
