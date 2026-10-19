import pathlib
import shutil
import unittest

from tests.helpers import LinkCollector, build_to_tmp
from build import placeholder_report


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


if __name__ == "__main__":
    unittest.main()
