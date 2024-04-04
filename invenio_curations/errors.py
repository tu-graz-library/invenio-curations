# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-Curations is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom exceptions used in the Invenio-Requests module."""


class ActionError(Exception):
    """Exception indicating an error related to the action."""

    def __init__(self, action, reason):
        """Constructor.

        :param action: The name of the action in question.
        :param reason: Description of what went wrong.
        """
        self.action = action
        self.reason = reason

    def __str__(self):
        """Return str(self)."""
        return f"Error for action '{self.action}': {self.reason}"


class NoSuchActionError(ActionError):
    """There was no such action available."""

    def __init__(self, action, reason=None):
        """Constructor.

        :param action: The name of the action.
        """
        reason = reason or "No such action available"
        super().__init__(action, reason)


class CannotExecuteActionError(ActionError):
    """The selected action could not be executed."""

    def __init__(self, action, reason=None):
        """Constructor.

        :param action: The name of the action.
        """
        reason = reason or "Could not execute the action"
        super().__init__(action, reason)
