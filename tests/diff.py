from invenio_curations.services.diff import DiffElement


def test_diff_element():
    expected_content_object = ("change", "test_key", ("old", "new"))
    actual_diff = DiffElement().from_base_content_object(str(expected_content_object))
    assert actual_diff == expected_content_object
