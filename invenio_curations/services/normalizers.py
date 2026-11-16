# -*- coding: utf-8 -*-
#
# Copyright (C) 2026 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Normalizers."""

from copy import deepcopy


class DataNormalizer:
    """Base class for data normalizers."""

    def __init__(self, data: dict) -> None:
        """Construct."""
        self.data = data

    def normalize(self) -> dict:
        """Base normalize method."""
        return self.data


class SubjectFieldNormalizer(DataNormalizer):
    """Normalize metadata subject field."""

    def normalize(self) -> dict:
        """Normalize subject field.

        Keep only subject ID. Draft data from deposit form can contain other
        fields like subject description which can affect the diff computing
        between the new deposit draft and the current saved one.
        """
        keep_sub_list = []
        norm_data = deepcopy(self.data)
        if "subjects" in self.data["metadata"]:
            for sub in self.data["metadata"]["subjects"]:
                keep_sub = {"id": sub["id"]}
                keep_sub_list.append(keep_sub)
        norm_data["metadata"]["subjects"] = keep_sub_list
        return norm_data


CURATIONS_COMMENTS_DATA_DIFF_NORMALIZERS = [SubjectFieldNormalizer]
