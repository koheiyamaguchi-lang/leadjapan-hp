import unittest

from sitegen import content as c


class ContentTest(unittest.TestCase):
    def test_company_name(self):
        self.assertEqual(c.SITE["name"], "Lead Japan 合同会社")

    def test_four_businesses_in_order(self):
        self.assertEqual([b.title for b in c.BUSINESSES],
                         ["AIソリューションの展開", "コンサルティング", "システム開発", "出版"])

    def test_system_dev_details(self):
        d = c.BUSINESSES[2].details
        self.assertIn("プロジェクトマネジメント関連", " ".join(d))
        self.assertIn("スタートアップ向け業務システムの開発", " ".join(d))

    def test_book_title_in_publishing_and_news(self):
        self.assertIn("外資系PM1年目の教科書", " ".join(c.BUSINESSES[3].details) + c.BUSINESSES[3].summary)
        self.assertTrue(any("外資系PM1年目の教科書" in n.title for n in c.NEWS))

    def test_news_sorted_newest_first(self):
        dates = [n.date for n in c.NEWS]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_news_categories(self):
        self.assertTrue({n.category for n in c.NEWS} <= {"お知らせ", "出版", "事業"})

    def test_no_revenue_claims(self):
        blob = repr(c.__dict__)
        for word in ("売上高", "億円", "万円"):
            self.assertNotIn(word, blob)

    def test_nav_targets(self):
        self.assertEqual([f for f, _ in c.NAV],
                         ["company.html", "business.html", "message.html", "news.html", "contact.html"])


if __name__ == "__main__":
    unittest.main()
