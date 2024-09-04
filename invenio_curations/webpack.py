# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2021 CERN.
# Copyright (C)      2024 Graz University of Technology.
# Copyright (C)      2024 TU Wien.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for curations.

You include one of the bundles in a page like the example below (using
``comunities`` bundle as an example):

.. code-block:: html

    {{ webpack['invenio-curations.js'] }}

"""

from invenio_assets.webpack import WebpackThemeBundle

curations = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-curations-deposit": "./js/invenio_curations/deposit/index.js",
            },
            dependencies={},
            aliases={
                "@translations/invenio_curations": "translations/invenio_curations",
                "@js/invenio_curations": "js/invenio_curations",
            },
        ),
    },
)
