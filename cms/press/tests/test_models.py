import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from sitegen.news import CATEGORIES

from press.models import Article, suggest_slug


def make_article(**kw):
    data = dict(
        title="タイトル",
        slug="a-1",
        published_on=datetime.date(2026, 10, 20),
        category="お知らせ",
        summary="概要",
        body_md="本文",
    )
    data.update(kw)
    return Article(**data)


class ArticleModelTests(TestCase):
    def test_slug_rejects_invalid_and_duplicate(self):
        for bad in ("日本語", "Has Space", "UPPER", "-lead", "a--b"):
            with self.assertRaises(ValidationError):
                make_article(slug=bad).full_clean()
        make_article(slug="ok-1").save()
        with self.assertRaises(ValidationError):
            make_article(slug="ok-1", title="別").full_clean()

    def test_title_unique(self):
        make_article(slug="t-1").save()
        with self.assertRaises(ValidationError):
            make_article(slug="t-2").full_clean()

    def test_category_choices_match_site(self):
        self.assertEqual([c for c, _ in Article._meta.get_field("category").choices], list(CATEGORIES))

    def test_default_status_is_draft(self):
        self.assertEqual(make_article().status, "draft")

    def test_image_requires_alt(self):
        a = make_article(image=SimpleUploadedFile("x.png", b"x"), image_alt="")
        with self.assertRaises(ValidationError) as cm:
            a.clean()
        self.assertIn("image_alt", cm.exception.message_dict)

    def test_image_over_5mb_rejected(self):
        a = make_article(image=SimpleUploadedFile("x.png", b"x" * (5 * 1024 * 1024 + 1)), image_alt="alt")
        with self.assertRaises(ValidationError) as cm:
            a.clean()
        self.assertIn("image", cm.exception.message_dict)

    def test_image_format_validated_on_full_clean(self):
        a = make_article(image=SimpleUploadedFile("x.gif", b"x"), image_alt="alt")
        with self.assertRaises(ValidationError) as cm:
            a.full_clean()
        self.assertIn("image", cm.exception.message_dict)
        for ext in ("jpg", "JPEG", "png", "webp"):
            a = make_article(image=SimpleUploadedFile(f"x.{ext}", b"x"), image_alt="alt")
            try:
                a.full_clean()
            except ValidationError as e:
                self.assertNotIn("image", e.message_dict)

    def test_title_colliding_with_fixed_page_title_rejected(self):
        # page title "<title> | Lead Japan 合同会社" equals the company page's title
        a = make_article(title="会社紹介")
        with self.assertRaises(ValidationError) as cm:
            a.clean()
        self.assertIn("title", cm.exception.message_dict)
        make_article(title="会社紹介について").clean()

    def test_suggest_slug(self):
        d = datetime.date(2026, 10, 20)
        self.assertEqual(suggest_slug(d), "2026-10-20")
        make_article(slug="2026-10-20").save()
        self.assertEqual(suggest_slug(d), "2026-10-20-2")
        make_article(slug="2026-10-20-2", title="別").save()
        self.assertEqual(suggest_slug(d), "2026-10-20-3")

    def test_allowed_hosts_local_only(self):
        # The test runner appends "testserver" to the live setting, so read the module itself.
        from cms_site import settings as site_settings

        self.assertEqual(site_settings.ALLOWED_HOSTS, ["127.0.0.1", "localhost"])

    def test_admin_changelist_loads(self):
        user = get_user_model().objects.create_superuser("admin", "a@example.com", "pw")
        self.client.force_login(user)
        resp = self.client.get(reverse("admin:press_article_changelist"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "記事")
