import pytest

from invenio_curations.services.diff import DiffElement


def test_diff_element_from_base_content_object():
    expected_content_object = ("change", "test_key", ("old", "new"))
    actual_diff = DiffElement().from_base_content_object(str(expected_content_object))
    assert actual_diff == expected_content_object

    expected_content_object = ("change2", "test_key_2", [{"test_title": ("test_subtitle", "new")}])
    actual_diff = DiffElement().from_base_content_object(str(expected_content_object))
    assert actual_diff == expected_content_object

    with pytest.raises(Exception) as e:
        DiffElement().from_base_content_object("malformed object: test")

    assert e.type is SyntaxError

def test_diff_element_get_base_content_object():
    pass

def test_diff_element_to_html():
    pass

def test_diff_element_validate_and_cleanup():
    pass

def test_diff_element_compare():
    pass






