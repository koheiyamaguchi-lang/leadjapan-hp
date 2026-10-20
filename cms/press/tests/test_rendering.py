from django.test import SimpleTestCase

from press.rendering import render_markdown


class RenderMarkdownTests(SimpleTestCase):
    def test_render_markdown_basic(self):
        out = render_markdown("## 見出し\n\n**太字**\n\n- a")
        self.assertIn("<h2>見出し</h2>", out)
        self.assertIn("<strong>太字</strong>", out)
        self.assertIn("<li>a</li>", out)

    def test_render_markdown_escapes_html_and_unsafe_links(self):
        out = render_markdown(
            '<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n'
            "[x](javascript:alert(1)) [ok](https://a.jp) [m](mailto:a@b.jp) [r](contact.html)"
        )
        self.assertNotIn("<script", out)
        self.assertNotIn("<img", out)
        self.assertNotIn("javascript:", out)
        for href in ("https://a.jp", "mailto:a@b.jp", "contact.html"):
            self.assertIn(f'href="{href}"', out)
