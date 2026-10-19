import pathlib
import shutil
import unittest

from tests.helpers import LinkCollector, build_to_tmp
from build import format_warnings, placeholder_report
from sitegen.content import UNCONFIRMED, NEWS


def collect(path: pathlib.Path) -> LinkCollector:
    c = LinkCollector()
    c.feed(path.read_text(encoding="utf-8"))
    return c


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = build_to_tmp()
        cls.addClassCleanup(shutil.rmtree, cls.out, ignore_errors=True)

    def test_writes_all_pages(self):
        names = sorted(p.name for p in self.out.glob("*.html"))
        self.assertEqual(names, sorted(["index.html", "company.html", "business.html", "message.html",
                                        "news.html", "privacy.html", "contact.html", "404.html"]))

    def test_static_copied(self):
        self.assertTrue((self.out / "static/css/style.css").exists())
        self.assertTrue((self.out / "static/img/tokyo-skyline.svg").exists())

    def test_no_root_relative_urls(self):
        for page in self.out.glob("*.html"):
            for link in collect(page).links:
                self.assertFalse(link.startswith("/"), f"{page.name}: {link}")

    def test_all_internal_links_resolve(self):
        for page in self.out.glob("*.html"):
            for link in collect(page).links:
                if link.startswith(("http", "mailto:", "#")):
                    continue
                path, _, frag = link.partition("#")
                target = self.out / path
                self.assertTrue(target.exists(), f"{page.name}: {link}")
                if frag:
                    self.assertIn(f'id="{frag}"', target.read_text(encoding="utf-8"), f"{page.name}: {link}")

    def test_no_javascript_anywhere(self):
        for page in self.out.glob("*.html"):
            self.assertEqual(collect(page).scripts, 0, page.name)
        self.assertEqual(list(self.out.rglob("*.js")), [])

    def test_only_free_external_hosts(self):
        for page in self.out.glob("*.html"):
            for link in collect(page).links:
                if link.startswith("http"):
                    self.assertRegex(link, r"^https://fonts\.(googleapis|gstatic)\.com(/|$)")

    def test_unique_titles(self):
        titles = [collect(p).title for p in self.out.glob("*.html")]
        self.assertEqual(len(titles), len(set(titles)))

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
        self.assertNotIn((1, 1), {(n.date.month, n.date.day) for n in NEWS})


if __name__ == "__main__":
    unittest.main()
