import pathlib
import shutil
import tempfile
import unittest
from unittest import mock

from tests.helpers import (LinkCollector, build_to_tmp, check_internal_links_resolve, check_no_javascript,
                           check_only_free_external_hosts, check_unique_titles, collect)
from build import build, format_warnings, placeholder_report
from sitegen.content import UNCONFIRMED, NEWS
from sitegen.pages import PAGES, article_pages, news_page_filename


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = build_to_tmp()
        cls.addClassCleanup(shutil.rmtree, cls.out, ignore_errors=True)

    def test_writes_all_pages(self):
        names = sorted(p.name for p in self.out.glob("*.html"))
        self.assertEqual(names, sorted(["index.html", "company.html", "business.html", "message.html",
                                        "news.html", "privacy.html", "contact.html", "404.html"]
                                       + [news_page_filename(n) for n in NEWS]))

    def test_article_pages_written_and_linked(self):
        index = (self.out / "index.html").read_text(encoding="utf-8")
        latest = {news_page_filename(n) for n in NEWS[:3]}  # the home page shows only the latest three
        for item in NEWS:
            name = news_page_filename(item)
            self.assertTrue((self.out / name).exists(), name)
            self.assertIn(f'href="{name}"', (self.out / "news.html").read_text(encoding="utf-8"))
            if name in latest:
                self.assertIn(f'href="{name}"', index)
            page = (self.out / name).read_text(encoding="utf-8")
            self.assertIn('<a href="news.html" aria-current="page">', page)
            self.assertEqual(page.count('aria-current="page"'), 1)
            self.assertIn('property="og:title"', page)

    def test_unpublished_article_has_no_page_or_link(self):
        if len(NEWS) < 2:
            self.skipTest("needs at least two articles")
        kept, dropped = NEWS[:-1], news_page_filename(NEWS[-1])
        pages = [p for p in PAGES if not p.filename.startswith("news-")] + article_pages(kept)
        out = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, out, ignore_errors=True)
        with mock.patch("sitegen.pages.NEWS", kept):
            build(out, pages)
        self.assertFalse((out / dropped).exists())
        for page in out.glob("*.html"):
            self.assertNotIn(f'href="{dropped}"', page.read_text(encoding="utf-8"), page.name)

    def test_static_copied(self):
        self.assertTrue((self.out / "static/css/style.css").exists())
        self.assertTrue((self.out / "static/img/tokyo-skyline.svg").exists())

    def test_no_root_relative_urls(self):
        for page in self.out.glob("*.html"):
            for link in collect(page).links:
                self.assertFalse(link.startswith("/"), f"{page.name}: {link}")

    def test_all_internal_links_resolve(self):
        check_internal_links_resolve(self, self.out)

    def test_no_javascript_anywhere(self):
        check_no_javascript(self, self.out)

    def test_only_free_external_hosts(self):
        check_only_free_external_hosts(self, self.out)

    def test_unique_titles(self):
        check_unique_titles(self, self.out)

    def test_404_content(self):
        text = (self.out / "404.html").read_text(encoding="utf-8")
        self.assertIn("ページが見つかりません", text)
        self.assertIn('href="index.html"', text)

    def test_placeholder_report(self):
        report = placeholder_report(list(self.out.glob("*.html")))
        self.assertTrue(report)
        self.assertTrue(all(v > 0 for v in report.values()))
        self.assertIn("company.html", report)

    def test_format_warnings_lists_unconfirmed(self):
        out = format_warnings({"company.html": 2})
        self.assertIn("警告: 【要入力】 が 2 箇所", out)
        lines = out.splitlines()
        confirm = [l for l in lines if l.startswith("要確認: ")]
        self.assertEqual(len(confirm), len(UNCONFIRMED))
        for item in UNCONFIRMED:
            self.assertIn(f"要確認: {item}", lines)
        self.assertLess(lines.index(next(l for l in lines if l.startswith("警告"))), lines.index(confirm[0]))

    def test_unconfirmed_not_rendered(self):
        for page in self.out.glob("*.html"):
            self.assertNotIn("要確認", page.read_text(encoding="utf-8"), page.name)

    def test_founding_news_placeholder_not_new_year(self):
        founding = [n for n in NEWS if n.slug == "founding"]  # tolerant: only checked if it exists
        for n in founding:
            self.assertNotEqual((n.date.month, n.date.day), (1, 1))


if __name__ == "__main__":
    unittest.main()
