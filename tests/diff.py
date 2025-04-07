# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

import pytest

from invenio_curations.services.diff import DiffDescription, DiffElement, DiffProcessor


def test_diff_element_to_html():
    """Test the final representation of a diff element."""
    diff_change = ("change", "test_key", ("old", "new"))
    diff_elem_change = DiffElement(diff_change)

    diff_add = ("add", "test_key_2", [{"test_title": ("test_subtitle", "new")}])
    diff_elem_add = DiffElement(diff_add)

    diff_remove = ("remove", "test_key_2", [{"test_title": ("test_subtitle", "new")}])
    diff_elem_remove = DiffElement(diff_remove)

    expected_html_diff_change = "{'test_key': {'old': 'old', 'new': 'new'}}"
    assert diff_elem_change.to_html() == expected_html_diff_change

    expected_html_diff_add_remove = (
        "{'test_key_2': [{'test_title': ('test_subtitle', 'new')}]}"
    )
    assert diff_elem_add.to_html() == expected_html_diff_add_remove
    assert diff_elem_remove.to_html() == expected_html_diff_add_remove


@pytest.mark.parametrize(
    "diff_input,expected",
    [
        (("change", "metadata.description", ("old", "new")), True),
        (("change", "metadata.other", ("old", "new")), False),
        (("add", "metadata", [("description", "bla")]), True),
        (("remove", "metadata", [("description", "bla")]), True),
        (("add", "metadata", [{"other": "field"}]), False),
        (("add", "metadata", [("other", "field")]), False),
    ],
)
def test_diff_element_description_match_key(diff_input, expected):
    """Test custom match key."""
    assert DiffDescription().match_diff_key(diff_input) == expected


def test_diff_element_description_strip_html():
    """Test HTML tag strip."""
    diff1 = DiffDescription(
        ("change", "metadata.description", ("<p>old</p>", "<p>new</p>"))
    )
    assert diff1.validate_and_cleanup()
    assert diff1.diff == ("change", "metadata.description", ("old", "new"))

    diff2 = DiffDescription(
        ("add", "metadata", [("description", "<div class='test'><h3>bla</h3></div>")])
    )
    assert diff2.validate_and_cleanup()
    assert diff2.diff == ("add", "metadata", [("description", "bla")])

    diff3 = DiffDescription(
        (
            "add",
            "metadata",
            [
                ("description", "<div class='test'><h3>bla</h3></div>"),
                ("other", "test"),
            ],
        )
    )
    assert not diff3.validate_and_cleanup()


def test_map_and_build_diffs():
    """Test wrapper class mapping."""
    diff1 = (
        "add",
        "metadata",
        [("description", "<div class='test'><h3>bla</h3></div>")],
    )
    diff2 = ("change", "metadata.other", ("old", "new"))
    diff3 = ("change", "metadata.description", ("old", "new"))
    diff4 = (
        "remove",
        "metadata",
        [("description", "<div class='test'><h3>bla</h3></div>")],
    )
    diff5 = ("remove", "metadata", [("other", "test")])

    diff_list = [diff1, diff2, diff3, diff4, diff5]
    configured_elements = [DiffDescription]
    dp = DiffProcessor(configured_elements=configured_elements)
    dp.map_and_build_diffs(diff_list)

    result_list = dp.get_diffs()
    assert len(result_list) == 5
    assert (
        isinstance(result_list[0], DiffDescription)
        and isinstance(result_list[1], DiffElement)
        and isinstance(result_list[2], DiffDescription)
        and isinstance(result_list[3], DiffDescription)
        and isinstance(result_list[4], DiffElement)
    )
