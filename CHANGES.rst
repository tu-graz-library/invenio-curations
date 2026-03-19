..
    Copyright (C) 2024-2026 Graz University of Technology.

    Invenio-Curations is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v0.8.2 (released 2026-03-19)

- fix(actions): allow cancel and delete from pending_resubmission
- fix: pending_resubmission is not always on published records
- fix: editing after Accept triggered View request
- fix(translations): add missing de translations
- fix(ui): add two request.status
- fix(ui): wrong request.status used

Version v0.8.1 (released 2026-03-13)

- fix(assets): import path

Version v0.8.0 (released 2026-03-13)

- translations: add translations for German language
- fix: handle anonymous user
- feat: add select reviewer feature to sidebar
- fix: anonymous user handling
- fix: filter system comments from backend
- feat: add new reply permission
- fix: apply new links creation
- fix: use relative URLs for reverse proxy and add doc config
- fix(ui): show all curation status states in despot form
- fix(compatibility): invenio-requests>=12.3.0
- fix(ui): permanent redirect not necessary
- chore: update js file formatting
- fix(ui): get only record.id from redux state
- fix: exit when reviewrs feature enabled

Version v0.7.0 (released 2026-02-10)

- chore(setup): bump dependencies
- fix: update required packages versions
- feat: edit RequestFeed component
- feat: adapt RequestFeed to invenio-requests>=11.0.0

Version v0.6.0 (released 2026-02-04)

- refactor: reduce one permission condition level
- fix: improve generators readability
- fix: black formatting
- tests: add curation unit tests
- fix: update permission docs
- fix(communities): show accept button for owners * fix requests permission policy to handle the case where records are created by curation privileged users so curation request is missing

Version v0.5.0 (released 2026-01-08)

- fix(tests): ignore mypy untyped decorator
- refactor: rename curations api
- refactor: rename key returned by get-publish-data api
- feat(ui): hide system comments from regular users
- feat(ui): override TimelineFeed component from invenioRDM v13

Version v0.4.0 (released 2025-12-02)

- fix: send only patched title
- types: change classVar to final
- feat: integrate new 'pending_resubmission' status
- feat: new get_publishing_data endpoint

Version v0.3.1 (release 2025-10-22)

- fix: readme markup


Version v0.3.0 (release 2025-10-22)

- fix: ruff
- global: admins to bypass curation workflow
- feature: create and update comments in curation requests


Version v0.2.0 (release 2025-07-28)

- fix: ruff PLC0415
- fix: setuptools require underscores instead of dashes
- setup: update deps
- global: update dep rdm-records
- global: use ruff
- mypy: add strict=true
- type-hints: complete type-hints in package
- feat: add Python 3.12 type hints to notifications and requests modules
- ui: fix link to unpublished record
- fix: community requests submit button
- ui-change: replace warning top message with custom-field
- fix: start publication button enabled with warnings
- ui: improve c workflow tooltips and status display
- fix: add fallback for full_name and email missing
- templates: replace username with full name and email
- chore: remove references to lastFormikUpdatedAt
- deposit form: use record.updated to determine necessity of re-fetch


Version 0.1.0 (released 2024-10-17)

- initial release
