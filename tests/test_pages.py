import datetime
import unittest
from pathlib import Path

from tests.helpers import ROOT
from unittest import mock

from sitegen.content import BUSINESSES, NEWS, PLACEHOLDER, PRIVACY, SITE, NewsItem
from sitegen.pages import (PAGES, body_business, body_company, body_contact, body_index,
                           body_message, body_news, body_privacy, news_anchor,
                           news_list_html, page_hero)


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


class SubPageTests(unittest.TestCase):
    def test_company_table_rows(self):
        b = body_company()
        for th in ("商号", "英文社名", "設立", "代表者", "所在地", "事業内容"):
            self.assertIn(f'<th scope="row">{th}</th>', b)
        self.assertIn("Lead Japan 合同会社", b)

    def test_business_sections_have_ids(self):
        b = body_business()
        for biz in BUSINESSES:
            self.assertIn(f'id="{biz.slug}"', b)
        self.assertIn("スタートアップ向け業務システムの開発", b)

    def test_business_text_is_escaped(self):
        from unittest import mock
        evil = BUSINESSES[0].__class__("ai", "01", "<b>X</b>", "E", "s&t", ("d",))
        with mock.patch("sitegen.pages.BUSINESSES", (evil,)):
            b = body_business()
        self.assertIn("&lt;b&gt;X&lt;/b&gt;", b)
        self.assertIn("s&amp;t", b)

    def test_message_has_signature(self):
        self.assertIn("代表社員", body_message())

    def test_subpages_have_breadcrumb(self):
        for fn in (body_company, body_business, body_message):
            self.assertIn('aria-label="パンくずリスト"', fn())

    def test_pages_registered_in_order(self):
        self.assertEqual([p.filename for p in PAGES[:4]],
                         ["index.html", "company.html", "business.html", "message.html"])
        self.assertEqual(PAGES[1].title, "会社紹介 | Lead Japan 合同会社")

    def test_page_hero_escapes(self):
        self.assertIn("&lt;", page_hero("<", "X"))


class NewsPrivacyContactTests(unittest.TestCase):
    def test_news_anchors_match_list_links(self):
        b = body_news()
        for i, item in enumerate(NEWS):
            a = news_anchor(item, i)
            self.assertIn(f'id="{a}"', b)
            self.assertIn(f'href="news.html#{a}"', b)

    def test_privacy_sections(self):
        b = body_privacy()
        for heading, _ in PRIVACY:
            self.assertIn(heading, b)
        self.assertIn("制定日：2026年10月19日", b)

    def test_privacy_enactment_date_once(self):
        self.assertEqual(body_privacy().count("制定日"), 1)

    def test_privacy_contact_section_names_operator(self):
        text = " ".join(dict(PRIVACY)["お問い合わせ窓口"])
        for key in ("name", "address", "representative", "email"):
            self.assertIn(SITE[key], text)
        self.assertIn("お問い合わせページ", text)

    def test_contact_note_matches_privacy_purpose(self):
        self.assertIn("プライバシーポリシーに定める利用目的の範囲内で", body_contact())

    def test_contact_no_form_post(self):
        b = body_contact()
        self.assertNotIn("<form", b)
        self.assertIn('href="privacy.html"', b)

    def test_contact_placeholder_email_not_mailto(self):
        with mock.patch.dict("sitegen.pages.SITE", {"email": PLACEHOLDER}):
            self.assertNotIn("mailto:", body_contact())
        with mock.patch.dict("sitegen.pages.SITE", {"email": "info@example.jp"}):
            self.assertIn('href="mailto:info@example.jp"', body_contact())

    def test_all_pages_registered(self):
        self.assertEqual([p.filename for p in PAGES],
                         ["index.html", "company.html", "business.html", "message.html",
                          "news.html", "privacy.html", "contact.html", "404.html"])


if __name__ == "__main__":
    unittest.main()
