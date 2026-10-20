"""Regression: owner-written press-release content must never break the whole-site checks."""
import datetime
import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

from build import build
from sitegen.news import NewsItem
from sitegen.pages import PAGES, article_pages
from tests.helpers import check_whole_site


class RealisticNewsTest(unittest.TestCase):
    def test_site_with_realistic_press_release_passes_all_checks(self):
        body = ('<p>月額5万円から利用できます。売上高の拡大を目指します。</p>'
                '<p><a href="https://example.com">詳細はこちら</a></p>')
        items = (
            NewsItem("new-service", datetime.date(2026, 11, 1), "プレスリリース", "新サービス開始のお知らせ",
                     "月額5万円で提供開始", body, "md"),
        )
        pages = [p for p in PAGES if not p.filename.startswith("news-")] + article_pages(items)
        out = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out, ignore_errors=True)
        with mock.patch("sitegen.pages.NEWS", items):
            build(out, pages)
        self.assertIn("月額5万円", (out / "news-new-service.html").read_text(encoding="utf-8"))
        self.assertIn('href="https://example.com"', (out / "news-new-service.html").read_text(encoding="utf-8"))
        check_whole_site(self, out)


if __name__ == "__main__":
    unittest.main()
