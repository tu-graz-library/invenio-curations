from html.parser import HTMLParser
from io import StringIO


class HTMLParseException(Exception):
    pass


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


def cleanup_html_tags(text):
    if not isinstance(text, str):
        raise HTMLParseException("Could not parse html input")

    if "<" not in text and ">" not in text:
        return text

    try:
        s = TagStripper()
        s.feed(text)

        return s.get_data()
    except Exception:
        raise HTMLParseException("Could not parse html input")
