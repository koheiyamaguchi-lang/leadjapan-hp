import unittest

from tests.helpers import LinkCollector
from sitegen.render import render_layout, find_placeholders


class RenderTests(unittest.TestCase):
    def test_layout_basics(self):
        html = render_layout(title="会社紹介 | Lead Japan 合同会社", description="d", body="<p>x</p>", current="company.html")
        self.assertIn('<html lang="ja">', html)
        self.assertIn('<meta charset="utf-8">', html)
        self.assertIn('name="viewport"', html)
        self.assertIn('<a href="company.html" aria-current="page">会社紹介</a>', html)
        self.assertEqual(html.count('aria-current="page"'), 1)
        self.assertIn('href="privacy.html"', html)
        self.assertIn("© 2026 Lead Japan LLC", html)

    def test_layout_escapes_title_and_description(self):
        html = render_layout(title='A<b>&"', description='<x>', body="", current="index.html")
        self.assertIn("<title>A&lt;b&gt;&amp;&quot;</title>", html)
        self.assertNotIn("<x>", html)

    def test_mobile_nav_toggle_markup(self):
        html = render_layout(title="t", description="d", body="", current="index.html")
        self.assertIn('id="nav-toggle"', html)
        self.assertIn('for="nav-toggle"', html)

    def test_no_scripts(self):
        p = LinkCollector()
        p.feed(render_layout(title="t", description="d", body="", current="index.html"))
        self.assertEqual(p.scripts, 0)

    def test_find_placeholders(self):
        self.assertEqual(find_placeholders("a【要入力】b【要入力】"), 2)


if __name__ == "__main__":
    unittest.main()
