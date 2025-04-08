from jinja2 import Template

from .utils import TagStripper, standardize_diff
import ast

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

    def _cleanup_html_tags(self):
        idx = 0
        for update, key, result in self._diffs:
            s = TagStripper()
            if isinstance(result, list) and len(result) == 1:
                field, val = result[0]
                if "<" in val:
                    s.feed(val)
                    self._diffs[idx] =(update, key, [(field, s.get_data().strip())])
            elif isinstance(result, tuple):
                old, new = result
                s.feed(old)
                new_old = s.get_data().strip()

                s_new = TagStripper()
                s_new.feed(new)
                new_new = s_new.get_data().strip()
                self._diffs[idx] =(update, key, (new_old, new_new))
            else:
                # not supported yet
                continue
            idx += 1

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

        self._cleanup_html_tags()
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
        update_name, update_key, result = update

        return "|".join([str(update_name), str(update_key), str(result)])

    def _get_split_update(self, joined_update):
        update_split = joined_update.split("|")
        update_name, update_key = update_split[0], update_split[1]
        update_dict = ast.literal_eval(update_split[2])

        return update_name, update_key, update_dict

    def compare(self, other):
        # the purpose of this comparing method is to modify this instance's diff list
        # by keeping the received object as a base of comparing
        to_add = set()
        to_remove = set()
        skip_second_loop = set()
        idx = 0

        self._cleanup_html_tags()
        for update_this, key_this, result_this in self._diffs:
            for update_other, key_other, result_other in other.get_diffs():
                if (key_this == key_other
                        and set(result_this) == set(result_other)
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
                        # field back to original value, remove from comment
                        to_remove.add(self._get_joined_update((update_this, key_this, result_this)))
                        skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                        break

                    result_this = (old_other, new_this)
                    skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                    self._diffs[idx] = (update_this, key_this, result_this)
                    break

                elif (update_this.lower() == update_other.lower()
                      and key_this == key_other
                    and result_this == result_other):
                    skip_second_loop.add(self._get_joined_update((update_other, key_other, result_other)))
                    pass
            idx += 1

        for update_other, key_other, result_other in other.get_diffs():
            if (update_other.lower() != "change"
                    and self._get_joined_update((update_other, key_other, result_other)) not in skip_second_loop):
                # keep all operations that were not touched in the previous loop
                to_add.add(self._get_joined_update((update_other, key_other, result_other)))

        for update in to_add:
            self._diffs.append(self._get_split_update(update))
        for update in to_remove:
            self._diffs.remove(self._get_split_update(update))

        return self

    def get_diffs(self):
        return self._diffs
