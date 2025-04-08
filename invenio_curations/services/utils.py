from io import StringIO
from html.parser import HTMLParser

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

def standardize_diff(diff_list):
    # TODO
    result_diffs = []
    for diff in diff_list:
        update_name, key, result = diff
        if update_name == "change":
            result_diffs.append(diff)
            continue
        field_name, field_value = result
        new_key = ".".join((key, field_name))
        result_diffs.append((update_name, new_key, field_value))
    return result_diffs