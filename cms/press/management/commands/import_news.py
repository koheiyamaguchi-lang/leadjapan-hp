from django.core.management.base import BaseCommand, CommandError

from sitegen.news import NEWS_JSON, NewsDataError, load_news

from press.models import Article


class Command(BaseCommand):
    help = "content/news.json から記事を取り込む (スラッグで作成/更新、画像は変更しない)"

    def add_arguments(self, parser):
        parser.add_argument("--path", default=str(NEWS_JSON))

    def handle(self, *args, **opts):
        from pathlib import Path

        try:
            items = load_news(Path(opts["path"]))
        except NewsDataError as e:
            raise CommandError(str(e)) from e
        for n in items:
            _, created = Article.objects.update_or_create(
                slug=n.slug,
                defaults=dict(
                    title=n.title, published_on=n.date, category=n.category, summary=n.summary,
                    body_md=n.body_md, status="published",
                ),
            )
            self.stdout.write(f"{'created' if created else 'updated'}: {n.slug}")
