# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Diff handling module."""

import typing
from abc import ABC, abstractmethod
from typing import Any, Final

from flask import current_app, render_template
from invenio_i18n import lazy_gettext as _

from .utils import HTMLParseError, cleanup_html_tags

"""Supported dictdiffer.diff() types for comment rendering."""
type DIFF_TYPE = tuple[str, str, list | tuple]


class DiffError(Exception):
    """Custom exception for diff exceptions."""


class DiffProcessorBase(ABC):
    """Interface for classes that process diffs in context of comment creation/update."""

    @abstractmethod
    def map_and_build_diffs(self, raw_diffs: list[tuple]) -> None:
        """Maps the raw diffs resulted from dictdiffer.diff to specific structures."""

    @abstractmethod
    def to_html(self, *args: Any) -> str:
        """Represent the inner state in HTML."""


class DiffElement:
    """Wrapper class for a diff tuple."""

    def __init__(self, diff: DIFF_TYPE | None = None) -> None:
        """Constructs."""
        self._diff = diff

    def __repr__(self) -> str:
        """Represent the diff."""
        if self._diff is None:
            raise DiffError
        update, key, result = self._diff
        if update != "change":
            return str({key: result})
        old, new = result
        return str({key: {"old": old, "new": new}})

    @property
    def diff(self) -> DIFF_TYPE | None:
        """Returns current diff."""
        return self._diff

    def match_diff_key(self, diff: DIFF_TYPE) -> bool:  # noqa: ARG002
        """Check if the given ``diff`` matches this diff processor.

        Note: The ``diff`` is expected to be a tuple from ``dictdiffer.diff()``.
        """
        return True

    def cleanup(self) -> typing.Self:
        """Cleanup the current diff with changing or removing unwanted data."""
        return self

    def validate(self) -> bool:
        """Validate the current diff. For the base method means just a sanity check."""
        if self._diff is None:
            raise DiffError

        return True


class DiffDescription(DiffElement):
    """Wrapper for the description field diffs of the metadata."""

    key_name = "metadata.description"

    def match_diff_key(self, diff: DIFF_TYPE) -> bool:
        """Override match_diff_key method.

        Match the possible diffs that contain description changes.
        """
        if not super().match_diff_key(diff):
            return False
        _, key, result = diff
        if key == self.key_name:
            return True
        try:
            name, _ = result[0]
        except Exception:  # noqa: BLE001
            return False
        else:
            return f"{key}.{name}" == self.key_name

    def cleanup(self) -> typing.Self:
        """Override cleanup method to strip HTML tags which are found in description diffs."""
        if self._diff is None:
            raise DiffError
        update, key, result = self._diff
        try:
            if isinstance(result, list) and len(result) == 1:
                field, val = result[0]
                new_val = cleanup_html_tags(val).strip()
                self._diff = (update, key, [(field, new_val)])
                return self
            if isinstance(result, tuple):
                old, new = result
                new_old = cleanup_html_tags(old).strip()
                new_new = cleanup_html_tags(new).strip()
                self._diff = (update, key, (new_old, new_new))
                return self
            current_app.logger.error(
                "Could not evaluate diff element %s of class %s",
                self._diff,
                self.__class__.__name__,
            )
        except HTMLParseError as err:
            current_app.logger.error(
                "Could not parse HTML for diff %s and class %s",
                self._diff,
                self.__class__.__name__,
            )
            raise DiffError from err
        else:
            raise DiffError

    def validate(self) -> bool:
        """Validate the description diff for expected structure."""
        _, _, result = self._diff
        return (isinstance(result, list) and len(result) == 1) or isinstance(
            result,
            tuple,
        )


class DiffProcessor(DiffProcessorBase):
    """DiffProcessor class.

    Used in context of requests comments processing.
    Manages the rendering of a list of diffs (which is the data of a comment).


    :ivar _diffs: A list of diff tuples.
    :ivar _configured_elements: Wrapper classes for specific diffs.
    :ivar _comment_template_file: HTML template filename used to render the comment.
    """

    _known_actions: Final[dict] = {
        "resubmit": _("Record was resubmitted for review with the following changes:"),
        "update_while_critiqued": _("Record was updated after changes were requested!"),
        "update_while_review": _(
            "Record was updated! Please check the latest changes.",
        ),
        "default": _("Action triggered comment update"),
    }

    def __init__(
        self,
        diffs: list[DiffElement] | None = None,
        configured_elements: list[type[DiffElement]] | None = None,
        comment_template_file: str | None = None,
    ) -> None:
        """Constructs."""
        self._diffs = diffs
        self._configured_elements = configured_elements
        self._comment_template_file = comment_template_file

    @property
    def diffs(self) -> list[DiffElement] | None:
        """Returns current diff list."""
        return self._diffs

    def _map_one_diff(self, raw_diff: DIFF_TYPE) -> DiffElement:
        """Return the class of a specific diff.

        :param raw_diff: This should be a tuple resulting from a dictdiffer.diff operation.

        :returns: The wrapper class of the given diff.
        """
        if self._configured_elements is None:
            raise DiffError

        for element in self._configured_elements:
            if element().match_diff_key(raw_diff):
                return element(raw_diff)

        return DiffElement(raw_diff)

    def map_and_build_diffs(self, raw_diffs: list[DIFF_TYPE]) -> None:
        """Maps the diffs to their specific wrapper class, instantiates them and adds them to the list.

        :param raw_diffs: This should be a list of tuples resulted from a dictdiffer.diff operation
        """
        self._diffs = []
        for raw_diff in raw_diffs:
            self._diffs.append(self._map_one_diff(raw_diff))

    def _prepare_content(self) -> None:
        """Removes structures that shouldn't be in diffs list."""
        if self._diffs is None:
            raise DiffError

        to_remove = [diff for diff in self._diffs if not diff.validate()]

        for remove in to_remove:
            self._diffs.remove(remove)

    def to_html(self, action: str) -> str:
        """Renders the diffs using the configured template.

        :param action: Action is used to get the title of the comment.

        :returns: The rendered comment.
        """
        if self._diffs is None or self._comment_template_file is None:
            raise DiffError

        if action not in self._known_actions:
            action = "default"

        adds = []
        changes = []
        removes = []

        self._prepare_content()
        for diff in self._diffs:
            # we shouldn't have None returned here after prepare_content
            update, _, _ = diff.cleanup().diff
            if update == "add":
                adds.append(diff)
            elif update == "change":
                changes.append(diff)
            elif update == "remove":
                removes.append(diff)

        try:
            return render_template(
                self._comment_template_file,
                adds=adds,
                changes=changes,
                removes=removes,
                header=self._known_actions[action],
            )
        except Exception as e:
            raise DiffError from e
