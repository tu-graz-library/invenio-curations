# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
# Copyright (C) 2024 TU Wien.
#
# Invenio-Curations is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Component for checking curations."""
import json
import re
from abc import ABC

import dictdiffer
import pprint
import ast
from invenio_access.permissions import system_identity
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_i18n import lazy_gettext as _
from invenio_pidstore.models import PIDStatus
from invenio_requests.customizations import CommentEventType
from invenio_requests.proxies import current_requests_service, current_events_service
from flask import current_app
from jinja2 import Template
from io import StringIO
from html.parser import HTMLParser

from ..proxies import current_curations_service
from .errors import CurationRequestNotAccepted


class TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


class DiffProcessor:
    """
    DiffProcessor class.
    """
    _diffs = None
    _known_actions = {
        "resubmit": "Record was resubmitted for review with the following changes:",
        "update_while_critiqued": "Record started being updated, work in progress...",
        "default": "Action triggered comment update"
    }
    _added = "Added:"
    _changed = "Changed:"
    _removed = "Removed:"

    def __init__(self, diffs=None):
        self._diffs = diffs

    def from_html(self, html):
        # parse html into a DiffProcessor object
        # beware: tightly coupled with to_html() method!!
        s = TagStripper()
        s.feed(html)
        list_of_updates = [st.strip() for st in s.get_data().split("\n") if len(st.strip()) > 0]

        added_zone, change_zone, remove_zone = False, False, False
        result_diffs = []
        for update in list_of_updates:
            if update == self._added:
                added_zone = True
                change_zone = False
                remove_zone = False
                continue
            if update == self._changed:
                change_zone = True
                added_zone = False
                remove_zone = False
                continue
            if update == self._removed:
                remove_zone = True
                change_zone = False
                added_zone = False
                continue

            if change_zone:
                d = ast.literal_eval(update)
                for key in d:
                    new_key = ".".join(key.split(" "))
                    old, new = d[key]["old"], d[key]["new"]
                    result_diffs.append(('change', new_key, (old, new)))

            if added_zone or remove_zone:
                d = ast.literal_eval(update)
                for key in d:
                    new_key = ".".join(key.split(" "))
                    result_diffs.append(('add' if added_zone else 'remove', new_key, d[key]))

        return DiffProcessor(result_diffs)

    def to_html(self, action):
        if action not in self._known_actions:
            action = "default"
        template_string = """
<body>
    <h3> {{header}} </h3>

    {% if adds|length > 0 %}
    <h3>Added:</h3>
    <ul>
    {% for add in adds %}
        <li>{{add}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    {% if changes|length > 0 %}
    <h3>Changed:</h3>
    <ul>
    {% for change in changes %}
        <li>{{change}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    {% if removes|length > 0 %}
    <h3>Removed:</h3>
    <ul>
    {% for remove in removes %}
        <li>{{remove}}</li>
    {% endfor %}
    </ul>
    {% endif %}
</body>
        """

        adds = []
        changes = []
        removes = []

        print(self._diffs)
        for update, key, result in self._diffs:
            if update.lower() == "add":
                result = {" ".join(key.split(".")): result}
                adds.append(str(result))
            elif update.lower() == "change":
                old, new = result
                result = {" ".join(key.split(".")): {"old": old, "new": new}}
                changes.append(str(result))
            elif update.lower() == "remove":
                result = {" ".join(key.split(".")): result}
                removes.append(str(result))

        return Template(template_string).render(adds=adds, changes=changes, removes=removes,
                                                header=self._known_actions[action])

    def _get_joined_update(self, update):
        update_name, update_key, result = update

        return "|".join([str(update_name), str(update_key), str(result)])

    def compare(self, other):
        # the purpose of this comparing method is to modify this instance's diff list
        # taking the received object as a base of comparing
        to_add = set()
        to_remove = set()
        skip_second_loop = set()
        idx = 0
        for update_this, key_this, result_this in self._diffs:
            for update_other, key_other, result_other in other.get_diffs():
                if (key_this == key_other
                        and result_this == result_other
                        and update_this != update_other
                        and update_this.lower() != "change"
                        and update_other.lower() != "change"):
                    # something was reverted
                    to_remove.add(self._get_joined_update((update_this, key_this, result_this)))
                    skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                    break

                elif (update_this.lower() == "change"
                      and update_other.lower() == "change"
                      and key_this == key_other):
                    # make sure to set the 'old' values from other
                    old_other, _ = result_other
                    _, new_this = result_this

                    if old_other == new_this:
                        to_remove.add(self._get_joined_update((update_this, key_this, result_this)))
                        skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                        break
                    result_this = (old_other, new_this)
                    skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                    self._diffs[idx] = (update_this, key_this, result_this)
            idx += 1

        for update_other, key_other, result_other in other.get_diffs():
            if (update_other.lower() != "change"
                    and self._get_joined_update((update_other, key_other, result_other)) not in to_remove
                    and self._get_joined_update((update_other, key_other, result_other)) not in skip_second_loop):
                # bring all add/remove that were not reverted
                to_add.add(self._get_joined_update((update_other, key_other, result_other)))

            elif (update_other.lower() == "change" and
                  self._get_joined_update((update_other, key_other, result_other)) not in to_remove and
                  self._get_joined_update((update_other, key_other, result_other)) not in skip_second_loop):
                to_add.add(self._get_joined_update((update_other, key_other, result_other)))

        for update in to_add:
            update_split = update.split("|")
            update_name, update_key = update_split[0], update_split[1]
            update_dict = ast.literal_eval(update_split[2])
            self._diffs.append((update_name, update_key, update_dict))
        for update in to_remove:
            update_split = update.split("|")
            update_name, update_key = update_split[0], update_split[1]
            update_dict = ast.literal_eval(update_split[2])
            self._diffs.remove((update_name, update_key, update_dict))

        return self

    def get_diffs(self):
        return self._diffs


class CurationComponent(ServiceComponent, ABC):
    """Service component for access integration."""

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Check if record curation request has been accepted."""
        # The `PIDComponent` takes care of calling `record.register()` which sets the
        # status for `record.pid.status` to "R", but the draft's dictionary data
        # only gets updated via `record.commit()` (which is performed by the `uow`).
        # Thus, if we spot a discrepancy here we can deduce that this is the first time
        # the record gets published.
        has_been_published = (
                draft.pid.status == draft["pid"]["status"] == PIDStatus.REGISTERED
        )
        if has_been_published and current_curations_service.allow_publishing_edits:
            return

        review_accepted = current_curations_service.accepted_record(
            system_identity,
            draft,
        )

        if not review_accepted:
            raise CurationRequestNotAccepted()

    def delete_draft(self, identity, draft=None, record=None, force=False):
        """Delete a draft."""
        request = current_curations_service.get_review(
            system_identity,
            draft,
            expand=True,
        )

        # No open request. Nothing to do.
        if request is None:
            return

        # New record or new version -> request can be removed.
        if record is None:
            current_requests_service.delete(
                system_identity, request["id"], uow=self.uow
            )
            return

        # Delete draft for a published record.
        # Since only one request per record should exist, it is not deleted. Instead, put it back to accepted.
        current_requests_service.execute_action(
            system_identity, request["id"], "cancel", uow=self.uow
        )

    def _check_update_request(
            self, identity, request, data=None, record=None, errors=None
    ):
        """Update request title if record title has changed."""
        updated_draft_title = (data or {}).get("metadata", {}).get("title")
        current_draft_title = (record or {}).get("metadata", {}).get("title")
        if current_draft_title != updated_draft_title:
            request["title"] = "RDM Curation: {title}".format(
                title=updated_draft_title or record["id"]
            )
            # Using system identity, to not have to update the default request can_update permission.
            # Data will be checked in the requests service.
            current_requests_service.update(
                system_identity, request["id"], request, uow=self.uow
            )

    def _prepare_data(self, data, current_draft):
        supported_fields = ["metadata", "custom_fields"]
        new_data = {}
        new_crt_draft = {}
        for field in supported_fields:
            new_data[field] = data[field]
            new_crt_draft[field] = current_draft[field]

        return new_data, new_crt_draft

    def _create_new_comment(self, request, content):

        payload = {
            "payload": {
                "content": content
            }
        }

        try:
            current_events_service.create(system_identity, request["id"], payload, CommentEventType())
        except Exception:
            return {
                "field": "custom_fields.rdm-curation",
                "messages": [
                    _(
                        "Record saved successfully, but request comment failed to create."
                    )
                ],
            }

    def _update_existing_comment(self, new_data, crt_comment_event):
        if crt_comment_event is None:
            # TODO add error
            return

        payload = {
            "payload": {
                "content": new_data
            }
        }

        try:
            current_events_service.update(system_identity, crt_comment_event.get("id"), payload,
                                          revision_id=crt_comment_event.get("revision_id"))
        except Exception:
            return {
                "field": "custom_fields.rdm-curation",
                "messages": [
                    _(
                        "Record saved successfully, but failed to update request comment."
                    )
                ],
            }

    def update_draft(self, identity, data=None, record=None, errors=None):
        """Update draft handler."""
        has_published_record = record is not None and record.is_published
        if has_published_record and current_curations_service.allow_publishing_edits:
            return

        request = current_curations_service.get_review(
            system_identity,
            record,
            expand=True,
        )

        # Inform user to create a curation request
        if not request:
            errors.append(
                {
                    "field": "custom_fields.rdm-curation",
                    "messages": [
                        _(
                            "Missing curation request. Please create a curation request, if the record is ready to be published."
                        )
                    ],
                }
            )
            return

        current_draft = self.service.draft_cls.pid.resolve(
            record["id"], registered_only=False
        )

        self._check_update_request(
            identity, request, data=data, record=current_draft, errors=errors
        )

        prepared_current_draft, prepared_data = self._prepare_data(data, current_draft)
        diff = dictdiffer.diff(prepared_data, prepared_current_draft)
        diff_list = list(diff)
        diff_processor = DiffProcessor(diff_list)

        # TODO: Should updates be disallowed if the record/request is currently being reviewed?
        # It could be possible that the record gets updated while a curator performs a review. The curator would be looking at an outdated record and the review might not be correct.

        # If a request is open, it still has to be reviewed eventually.

        if request["is_open"] and request["status"] == "resubmitted":
            # if the user resubmits the record for review, we should add a comment that describes
            # what was changed from the previous attempt (creation/other resubmission)

            # TODO add extra comment validation for auto-generated
            last_request_log_event = None
            last_created_comment = None
            for hit in list(current_events_service.search(system_identity, request["id"]).hits):
                if hit.get("type") == "C":
                    # saved record while critiqued, store this
                    last_created_comment = hit
                    continue

                if hit.get("type") == "L":
                    last_request_log_event = hit.get("payload").get("event")

            if (last_request_log_event in ["resubmitted", "critiqued"] and
                    last_created_comment is None):
                # happy path: critiqued - resubmitted, no intermediate saves
                errors.append(self._create_new_comment(request, diff_processor.to_html("resubmit")))
            else:
                # if there were draft saves between critiqued - resubmitted, be sure to capture
                # the diff between these 2 statuses, not between draft saves.
                last_diff = DiffProcessor().from_html(last_created_comment.get("payload").get("content"))
                errors.append(self._update_existing_comment(diff_processor.compare(last_diff).to_html("resubmit"),
                                                            last_created_comment))

            return

        elif request["is_open"] and request["status"] == "critiqued" and len(diff_processor.get_diffs()) > 0:
            # update draft while critiqued without resubmitting immediately, create comment and
            # then update the same comment if new updates of this sort come
            last_event = list(current_events_service.search(system_identity, request["id"]).hits)[-1]

            if last_event.get("type") == "L":
                errors.append(self._create_new_comment(request, diff_processor.to_html("update_while_critiqued")))
            elif last_event.get("type") == "C":
                last_diff = DiffProcessor().from_html(last_event.get("payload").get("content"))
                errors.append(
                    self._update_existing_comment(diff_processor.compare(last_diff).to_html("update_while_critiqued"),
                                                  last_event))

            return

        # TODO decide what to do on review status
        elif request["is_open"]:
            return

        # Compare metadata of current draft and updated draft.

        # Sometimes the metadata differs between the passed `record` and resolved
        # `current_draft` in references (e.g. in the `record` object, the creator's
        # affiliation has an ID & name, but in the `current_draft` it's only the ID)
        # this discrepancy can be removed by resolving or cleaning the relations
        current_draft.relations.clean()
        record.relations.clean()

        current_data = self.service.schema.dump(
            current_draft,
            context=dict(
                identity=identity,
                pid=current_draft.pid,
                record=current_draft,
            ),
        )
        # Load updated data with service schema
        updated_data = self.service.schema.dump(
            record,
            context=dict(
                identity=identity,
                pid=record.pid,
                record=record,
            ),
        )
        # TODO: File updates are not picked up. File actions are handled in dedicated files service.
        #       Files service is not configurable per default and we can not add a component there.
        diff = dictdiffer.diff(current_data, updated_data)
        diff_list = list(diff)

        # Request is closed but draft was updated with new data. Put back for review
        if diff_list:
            current_requests_service.execute_action(
                identity, request["id"], "resubmit", uow=self.uow
            )
