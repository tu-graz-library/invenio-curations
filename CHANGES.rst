..
    Copyright (C) 2024-2026 Graz University of Technology.

    Invenio-Curations is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

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
