# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Diff handling module."""

from abc import ABC, abstractmethod

from flask import current_app, render_template
from invenio_i18n import lazy_gettext as _

from .utils import HTMLParseException, cleanup_html_tags


class DiffException(Exception):
    """Custom exception for diff exceptions."""


class DiffBase(ABC):
    """Interface for classes that process diffs in context of comment creation/update."""

    @abstractmethod
    def validate_and_cleanup(self):
        """Validate the current diff, and remove unwanted data."""
        ...

    @abstractmethod
    def to_html(self, *args):
        """Represent the inner state in HTML."""
        ...


class DiffElement(DiffBase):
    """Wrapper class for a diff tuple."""

    def __init__(self, diff=None):
        """Constructs."""
        self._diff = diff

    @property
    def diff(self):
        """Returns current diff."""
        return self._diff

    def match_diff_key(self, diff):
        """Check if the given ``diff`` matches this diff processor.

        Note: The ``diff`` is expected to be a tuple from ``dictdiffer.diff()``.
        """
        return isinstance(diff, tuple)

    def to_html(self):
        """Base implementation for the representation of a diff in html."""
        update, key, result = self._diff
        if update != "change":
            return str({" ".join(key.split(".")): result})
        else:
            old, new = result
            return str({" ".join(key.split(".")): {"old": old, "new": new}})

    def validate_and_cleanup(self):
        """Try to validate only dictdiffer.diff tuples."""
        update, key, result = self._diff
        condition = (
            isinstance(update, str)
            and isinstance(key, str)
            and ((isinstance(result, list)) or isinstance(result, tuple))
        )
        if not condition:
            current_app.logger.error(
                f"Could not evaluate diff element {self._diff} of class {self.__class__.__name__}"
            )
        return condition


class DiffDescription(DiffElement):
    """Wrapper for the description field diffs of the metadata."""

    key_name = "metadata.description"

    def match_diff_key(self, diff):
        """Override match_diff_key method.

        Match the possible diffs that contain description changes.
        """
        if not super().match_diff_key(diff):
            return False
        _, key, result = diff
        if isinstance(key, str) and key == self.key_name:
            return True
        elif (
            isinstance(key, str)
            and isinstance(result, list)
            and len(result) == 1
            and isinstance(result[0], tuple)
        ):
            name, _ = result[0]
            return f"{key}.{name}" == self.key_name

        return False

    def validate_and_cleanup(self):
        """Override validate_and_cleanup method to strip HTML tags which are found in description diffs."""
        update, key, result = self._diff
        try:
            if isinstance(result, list) and len(result) == 1:
                field, val = result[0]
                new_val = cleanup_html_tags(val).strip()
                self._diff = (update, key, [(field, new_val)])
                return True
            elif isinstance(result, tuple):
                old, new = result
                new_old = cleanup_html_tags(old).strip()
                new_new = cleanup_html_tags(new).strip()
                self._diff = (update, key, (new_old, new_new))
                return True
            else:
                # not supported yet
                current_app.logger.error(
                    f"Could not evaluate diff element {self._diff} of class {self.__class__.__name__}"
                )
                return False
        except HTMLParseException as e:
            current_app.logger.error(
                f"Could not parse HTML for diff {self._diff} and class {self.__class__.__name__}"
            )
            return False


class DiffProcessor(DiffBase):
    """DiffProcessor class.

    Used in context of requests comments processing.
    Manages the rendering of a list of diffs (which is the data of a comment).


    :ivar _diffs: A list of diff tuples.
    :type _diffs: list

    :ivar _configured_elements: Wrapper classes for specific diffs.
    :type _configured_elements: list

    :ivar _comment_template_file: HTML template filename used to render the comment.
    :type _comment_template_file: str
    """

    _diffs = None
    _configured_elements = None
    _comment_template_file = None

    _known_actions = {
        "resubmit": _("Record was resubmitted for review with the following changes:"),
        "update_while_critiqued": _("Record was updated after changes were requested!"),
        "update_while_review": _(
            "Record was updated! Please check the latest changes."
        ),
        "default": _("Action triggered comment update"),
    }

    def __init__(
        self, diffs=None, configured_elements=None, comment_template_file=None
    ):
        """Constructs."""
        self._diffs = diffs
        self._configured_elements = configured_elements
        self._comment_template_file = comment_template_file

    def _map_one_diff(self, raw_diff):
        """Return the class of a specific diff.

        :param raw_diff: This should be a tuple resulting from a dictdiffer.diff operation.
        :type raw_diff: tuple

        :returns: The wrapper class of the given diff.
        :rtype: class
        """
        for element in self._configured_elements:
            if element().match_diff_key(raw_diff):
                return element

        return DiffElement

    def map_and_build_diffs(self, raw_diffs):
        """Maps the diffs to their specific wrapper class, instantiates them and adds them to the list.

        :param raw_diffs: This should be a list of tuples resulted from a dictdiffer.diff operation
        :type raw_diffs: list
        """
        if not isinstance(raw_diffs, list):
            raise DiffException()

        self._diffs = []
        for raw_diff in raw_diffs:
            self._diffs.append(self._map_one_diff(raw_diff)(raw_diff))

    def validate_and_cleanup(self):
        """Removes structures that shouldn't be in diffs list."""
        to_remove = []

        for diff in self._diffs:
            if not diff.validate_and_cleanup():
                to_remove.append(diff)

        for remove in to_remove:
            self._diffs.remove(remove)

    def to_html(self, action):
        """Renders the diffs using the configured template.

        :param action: Action is used to get the title of the comment.
        :type action: str

        :returns: The rendered comment.
        :rtype: str
        """
        if action not in self._known_actions:
            action = "default"

        adds = []
        changes = []
        removes = []

        self.validate_and_cleanup()
        for diff in self._diffs:
            update, _, _ = diff.diff
            if update == "add":
                adds.append(diff.to_html())
            elif update == "change":
                changes.append(diff.to_html())
            elif update == "remove":
                removes.append(diff.to_html())

        try:
            return render_template(
                self._comment_template_file,
                adds=adds,
                changes=changes,
                removes=removes,
                header=self._known_actions[action],
            )
        except Exception:
            raise DiffException()
