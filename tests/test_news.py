import datetime
import json
import tempfile
import unittest
from pathlib import Path

from sitegen.news import CATEGORIES, NewsDataError, NewsItem, load_news, news_to_json


def valid(**over):
    d = {"slug": "a-one", "date": "2026-01-05", "category": "お知らせ", "title": "題",
         "summary": "概要", "body_md": "本文", "body_html": "<p>本文</p>",
         "image": None, "image_alt": ""}
    d.update(over)
    return d


class NewsTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def write(self, items):
        p = self.tmp / "news.json"
        p.write_text(json.dumps({"version": 1, "items": items}, ensure_ascii=False), encoding="utf-8")
        return p

    def test_categories(self):
        self.assertEqual(CATEGORIES, ("プレスリリース", "お知らせ", "出版", "事業"))

    def test_roundtrip(self):
        items = (
            NewsItem("b-two", datetime.date(2026, 1, 5), "出版", "t2", "s", "<p>s</p>", "s", "static/img/news/x.jpg", "alt"),
            NewsItem("a-one", datetime.date(2026, 1, 5), "お知らせ", "t1", "s", "<p>s</p>"),
            NewsItem("c-old", datetime.date(2025, 1, 1), "事業", "t3", "s", "<p>s</p>"),
        )
        p = self.tmp / "news.json"
        text = news_to_json(items)
        self.assertTrue(text.endswith("\n"))
        self.assertIn("2026-01-05", text)
        p.write_text(text, encoding="utf-8")
        loaded = load_news(p)
        self.assertEqual([n.slug for n in loaded], ["a-one", "b-two", "c-old"])
        self.assertEqual(set(loaded), set(items))

    def test_missing_file_is_empty(self):
        self.assertEqual(load_news(self.tmp / "nope.json"), ())

    def test_load_news_rejects_invalid_entries(self):
        missing = valid()
        del missing["summary"]
        cases = [
            (valid(slug="Bad Slug"), "Bad Slug"),
            (valid(category="広告"), "a-one"),
            (valid(date="2026-13-01"), "a-one"),
            (valid(title=""), "a-one"),
            (missing, "a-one"),
        ]
        for bad, expect in cases:
            with self.subTest(bad=bad):
                p = self.write([bad])
                with self.assertRaises(NewsDataError) as cm:
                    load_news(p)
                self.assertIn(str(p), str(cm.exception))
                self.assertIn(expect, str(cm.exception))

    def test_duplicate_slug_rejected(self):
        p = self.write([valid(), valid(title="別")])
        with self.assertRaises(NewsDataError) as cm:
            load_news(p)
        self.assertIn(str(p), str(cm.exception))
        self.assertIn("a-one", str(cm.exception))

    def test_entry_without_slug_names_index(self):
        bad = valid()
        del bad["slug"]
        p = self.write([valid(slug="ok-one"), bad])
        with self.assertRaises(NewsDataError) as cm:
            load_news(p)
        self.assertIn("1", str(cm.exception))

    def test_repo_news_json_has_migrated_items(self):
        items = load_news()  # must load without NewsDataError
        slugs = [n.slug for n in items]
        self.assertEqual(len(slugs), len(set(slugs)))
        for n in items:
            self.assertTrue(n.title.strip(), n.slug)
            self.assertTrue(n.summary.strip(), n.slug)
            self.assertTrue(n.body_html.strip(), n.slug)


if __name__ == "__main__":
    unittest.main()
