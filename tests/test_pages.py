import datetime
import unittest
from pathlib import Path

from tests.helpers import ROOT
from sitegen.content import BUSINESSES, NEWS, NewsItem
from sitegen.pages import PAGES, body_index, news_anchor, news_list_html


class IndexPageTests(unittest.TestCase):
    def test_index_first_and_titled(self):
        self.assertEqual(PAGES[0].filename, "index.html")
        self.assertEqual(PAGES[0].title, "Lead Japan 合同会社 | 日本を導き、世界へ。")

    def test_index_hero(self):
        b = body_index()
        self.assertIn("<h1>日本を導き、世界へ。</h1>", b)
        self.assertIn('src="static/img/tokyo-skyline.svg"', b)
        self.assertIn('alt="東京タワーと東京の街並み"', b)
        self.assertIn("Lead Japan — Tokyo, Japan", b)

    def test_index_links_all_businesses(self):
        b = body_index()
        for biz in BUSINESSES:
            self.assertIn(f'href="business.html#{biz.slug}"', b)

    def test_index_shows_latest_three_news(self):
        self.assertEqual(body_index().count("<li><time"), min(3, len(NEWS)))

    def test_index_has_reveal_blocks(self):
        self.assertGreaterEqual(body_index().count("reveal"), 5)

    def test_index_links_sections(self):
        b = body_index()
        for href in ("company.html", "message.html", "news.html", "contact.html"):
            self.assertIn(f'href="{href}"', b)

    def test_skyline_svg_has_tower_and_no_script(self):
        svg = (ROOT / Path("static/img/tokyo-skyline.svg")).read_text(encoding="utf-8")
        self.assertIn('id="beacon"', svg)
        self.assertNotIn("<script", svg)
        self.assertIn("#e8380d", svg.lower())
        self.assertIn('viewBox="0 0 1600 600"', svg)
        self.assertLess(len(svg.encode("utf-8")), 60 * 1024)


class NewsListTests(unittest.TestCase):
    def test_news_anchor(self):
        item = NewsItem(datetime.date(2026, 1, 5), "c", "t", "b")
        self.assertEqual(news_anchor(item, 2), "news-20260105-2")

    def test_news_list_markup_and_escaping(self):
        item = NewsItem(datetime.date(2026, 1, 5), "A&B", "<x>", "b")
        out = news_list_html([item])
        self.assertIn('<ul class="news-list">', out)
        self.assertIn('<li><time datetime="2026-01-05">2026.01.05</time>', out)
        self.assertIn('<span class="news-cat">A&amp;B</span>', out)
        self.assertIn('<a href="news.html#news-20260105-0">&lt;x&gt;</a>', out)
        self.assertNotIn("<x>", out)


if __name__ == "__main__":
    unittest.main()
