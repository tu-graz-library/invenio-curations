import json
from abc import abstractmethod
from typing import ClassVar

from jinja2 import Template

from .utils import TagStripper, cleanup_html_tags, HTMLParseException
import ast

class DiffBase:

    @abstractmethod
    def validate_and_cleanup(self):...

    @abstractmethod
    def compare(self, other):...

    @abstractmethod
    def from_html(self, *args):...

    @abstractmethod
    def to_html(self, *args):...


class DiffElement(DiffBase):

    def __init__(self, diff=None):
        self._diff = diff

    def __eq__(self, other):
        if not isinstance(other, DiffElement):
            return False
        update_this, key_this, result_this = self._diff
        update_other, key_other, result_other = other.get_diff()

        return (update_this == update_other and
                key_this == key_other and
                set(json.dumps(result_this)) == set(json.dumps(result_other)))

    def get_diff(self):
        return self._diff

    def build_diff(self, df):
        update, key, result = df
        if update == "change":
            old, new = result["old"], result["new"]
            self._diff = update, key, (old, new)
        else:
            self._diff = update, key, result
        return self

    def match_diff_key(self, diff):
        return True

    def compare(self, other):
        """
            Compare method used to compare 2 diffs used to keep the old reference.
        """
        update_this, key_this, result_this = self._diff
        update_other, key_other, result_other = other.get_diff()

        if key_this != key_other:
            return None

        if (set(json.dumps(result_this)) == set(json.dumps(result_other))
                and update_this != update_other
                and update_this.lower() != "change"
                and update_other.lower() != "change"):

            # something was reverted
            return False

        elif (update_this.lower() == "change"
              and update_other.lower() == "change"
              and key_this == key_other):
            # make sure to set the 'old' values from other
            old_other, _ = result_other
            _, new_this = result_this

            if old_other == new_this:
                # field back to original value, remove from comment
                return False

            result_this = (old_other, new_this)
            self._diff = (update_this, key_this, result_this)
            return True

        elif self._diff == other:
           return False

        else:
            return True

    def from_html(self, text):
        return ast.literal_eval(text)

    def to_html(self):
        update, key, result = self._diff
        if update != "change":
            return str({" ".join(key.split(".")): result})
        else:
            old, new = result
            return str({" ".join(key.split(".")): {"old": old, "new": new}})

    def validate_and_cleanup(self):
        _, key, result = self._diff

        return (isinstance(key, str) and
                ((isinstance(result, list) and len(result) == 1) or isinstance(result, tuple)))


class DiffDescription(DiffElement):

    _name = "metadata.description"

    def match_diff_key(self, diff):
        _, key, result = diff
        if isinstance(key, str) and key == self._name:
            return True
        elif (isinstance(key, str) and
              isinstance(result, list) and
              len(result) == 1 and
              isinstance(result[0], dict)
        ):
            return key + "." + result[0].keys().next() == self._name

    def validate_and_cleanup(self):
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
                # not supported yet, don't publish in the comment
                # to not interfere with future diffs
                return False
        except HTMLParseException:
            return False


class DiffProcessor(DiffBase):
    """
    DiffProcessor class.
    """
    _diffs = None
    _configured_elements = None

    _known_actions = {
        "resubmit": "Record was resubmitted for review with the following changes:",
        "update_while_critiqued": "Record started being updated, work in progress...",
        "update_while_review": "Record was updated! Please check the latest changes.",
        "default": "Action triggered comment update",
    }
    _added = "Added:"
    _changed = "Changed:"
    _removed = "Removed:"

    def __init__(self, diffs=None, configured_elements=None):
        self._diffs = diffs
        self._configured_elements = configured_elements

    def _map_one_diff(self, raw_diff):
        for element in self._configured_elements:
            if element().match_diff_key(raw_diff):
                return element

        return DiffElement

    def map_and_build_diffs(self, raw_diffs):
        self._diffs = []
        for raw_diff in raw_diffs:
            self._diffs.append(self._map_one_diff(raw_diff)(raw_diff))

    def validate_and_cleanup(self):
        to_remove = []

        for diff in self._diffs:
            if not diff.validate_and_cleanup():
                to_remove.append(diff)

        for remove in to_remove:
            self._diffs.remove(remove)

    def from_html(self, html):
        # parse html into a DiffProcessor object
        # beware: tightly coupled with to_html() method!!
        html_free_text = cleanup_html_tags(html)
        list_of_updates = [st.strip() for st in html_free_text.split("\n") if len(st.strip()) > 0]

        added_zone, change_zone, remove_zone = False, False, False
        result_diffs = []
        for update in list_of_updates[1:]:
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

            d = {}
            for element in self._configured_elements:
                try:
                    d = element().from_html(update)
                    break
                except Exception:
                    continue

            if len(d.keys()) == 0:
                raise HTMLParseException()

            if change_zone:
                for key in d:
                    new_key = ".".join(key.split(" "))
                    df = ("change", new_key, d[key])
                    result_diffs.append(self._map_one_diff(df)().build_diff(df))

            if added_zone or remove_zone:
                for key in d:
                    new_key = ".".join(key.split(" "))
                    df = ("add" if added_zone else "remove", new_key, d[key])
                    result_diffs.append(self._map_one_diff(df)().build_diff(df))

        return DiffProcessor(result_diffs, self._configured_elements)

    def to_html(self, action):
        if action not in self._known_actions:
            action = "default"
        template_string = """
<body>
    <h3> {{header}} </h3>

    {% if adds|length > 0 %}
    <h3>{{added_msg}}</h3>
    <ul>
    {% for add in adds %}
        <li>{{add}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    {% if changes|length > 0 %}
    <h3>{{changed_msg}}</h3>
    <ul>
    {% for change in changes %}
        <li>{{change}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    {% if removes|length > 0 %}
    <h3>{{removed_msg}}</h3>
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

        self.validate_and_cleanup()
        for diff in self._diffs:
            update, _, _ = diff.get_diff()
            if update == "add":
                adds.append(diff.to_html())
            elif update == "change":
                changes.append(diff.to_html())
            elif update == "remove":
                removes.append(diff.to_html())

        return Template(template_string).render(
            adds=adds,
            changes=changes,
            removes=removes,
            header=self._known_actions[action],
            added_msg=self._added,
            changed_msg=self._changed,
            removed_msg=self._removed,
        )

    def _get_joined_update(self, update):
        update_name, update_key, result = update.get_diff()

        return "|".join([str(update_name), str(update_key), str(result)])

    def _get_split_update(self, joined_update):
        update_split = joined_update.split("|")
        update_name, update_key = update_split[0], update_split[1]
        update_dict = ast.literal_eval(update_split[2])

        return DiffElement((update_name, update_key, update_dict))

    def compare(self, other):
        # the purpose of this comparing method is to modify this instance's diff list
        # by keeping the received object as a base of comparing
        to_add = set()
        to_remove = set()
        skip_second_loop = set()

        self.validate_and_cleanup()
        for diff_this in self._diffs:
            for other_diff in other.get_diffs():
                result = diff_this.compare(other_diff)
                if result is None:
                    continue
                elif not result:
                    to_remove.add(self._get_joined_update(diff_this))
                skip_second_loop.add(self._get_joined_update(other_diff))

        for other_diff in other.get_diffs():
            if self._get_joined_update(other_diff) not in skip_second_loop:
                # keep all operations that were not touched in the previous loop
                to_add.add(self._get_joined_update(other_diff))

        for update in to_add:
            self._diffs.append(self._get_split_update(update))
        for update in to_remove:
            self._diffs.remove(self._get_split_update(update))

        return self

    def get_diffs(self):
        return self._diffs
