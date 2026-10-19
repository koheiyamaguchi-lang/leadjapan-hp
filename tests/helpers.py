"""Shared test helpers."""
from __future__ import annotations

import html.parser
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class LinkCollector(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.scripts = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            self.scripts += 1
        if tag == "title":
            self._in_title = True
        for key in ("href", "src"):
            if a.get(key) is not None:
                self.links.append(a[key])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def build_to_tmp() -> pathlib.Path:
    from build import build
    out = pathlib.Path(tempfile.mkdtemp())
    build(out)
    return out
