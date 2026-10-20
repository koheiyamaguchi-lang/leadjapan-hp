from __future__ import annotations

from pathlib import Path

from sitegen.news import NewsItem, news_to_json

from .models import Article
from .rendering import render_markdown

IMAGE_DIR = "static/img/news"
ALLOWED_EXTS = (".jpg", ".jpeg", ".png", ".webp")


class ExportError(Exception):
    pass


def image_target(article: Article) -> str | None:
    if not article.image:
        return None
    ext = Path(article.image.name).suffix.lower()
    if ext not in ALLOWED_EXTS:
        raise ExportError(f"{article.slug}: 画像の拡張子 {ext!r} は使用できません ({', '.join(ALLOWED_EXTS)})")
    return f"{IMAGE_DIR}/{article.slug}{ext}"


def article_to_newsitem(article: Article, *, image: str | None = ...) -> NewsItem:
    if image is ...:
        image = image_target(article)
    return NewsItem(
        slug=article.slug,
        date=article.published_on,
        category=article.category,
        title=article.title,
        summary=article.summary,
        body_html=render_markdown(article.body_md),
        body_md=article.body_md,
        image=image,
        image_alt=article.image_alt if image else "",
    )


def export_published(repo_root: Path) -> list[str]:
    repo_root = Path(repo_root)
    articles = list(Article.objects.filter(status="published"))

    # Validate everything first so a failure leaves the repo untouched.
    plan = []
    for a in articles:
        target = image_target(a)
        if target and not a.image.storage.exists(a.image.name):
            raise ExportError(f"{a.slug}: 画像ファイルが見つかりません ({a.image.name})")
        plan.append((a, target))

    changed: list[str] = []
    (repo_root / "content").mkdir(parents=True, exist_ok=True)
    img_dir = repo_root / IMAGE_DIR
    img_dir.mkdir(parents=True, exist_ok=True)

    referenced = set()
    for a, target in plan:
        if not target:
            continue
        referenced.add(target)
        with a.image.storage.open(a.image.name, "rb") as src:
            (repo_root / target).write_bytes(src.read())
        changed.append(target)

    for f in sorted(img_dir.iterdir()):
        rel = f"{IMAGE_DIR}/{f.name}"
        if f.is_file() and not f.name.startswith(".") and rel not in referenced:
            f.unlink()
            changed.append(rel)

    items = [article_to_newsitem(a, image=t) for a, t in plan]
    (repo_root / "content/news.json").write_text(news_to_json(items), encoding="utf-8")
    changed.append("content/news.json")
    return changed
