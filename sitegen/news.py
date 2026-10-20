"""News data: NewsItem model and JSON load/dump (stdlib only)."""
from __future__ import annotations

import datetime
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

CATEGORIES: tuple[str, ...] = ("プレスリリース", "お知らせ", "出版", "事業")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NEWS_JSON = Path(__file__).resolve().parents[1] / "content" / "news.json"

_REQUIRED = ("slug", "date", "category", "title", "summary", "body_md", "body_html", "image", "image_alt")


@dataclass(frozen=True)
class NewsItem:
    slug: str
    date: datetime.date
    category: str
    title: str
    summary: str
    body_html: str
    body_md: str = ""
    image: str | None = None
    image_alt: str = ""


class NewsDataError(ValueError):
    pass


def _parse(path: Path, raw: object, index: int, seen: set[str]) -> NewsItem:
    slug = raw.get("slug") if isinstance(raw, dict) else None
    label = f"{path}: item {slug!r}" if isinstance(slug, str) and slug else f"{path}: item #{index}"

    def fail(msg: str) -> NewsDataError:
        return NewsDataError(f"{label}: {msg}")

    if not isinstance(raw, dict):
        raise fail("must be an object")
    missing = [k for k in _REQUIRED if k not in raw]
    if missing:
        raise fail(f"missing keys {missing}")
    for k in ("slug", "category", "title", "summary", "body_md", "body_html", "image_alt"):
        if not isinstance(raw[k], str):
            raise fail(f"{k} must be a string")
    if not SLUG_RE.match(raw["slug"]):
        raise fail(f"invalid slug {raw['slug']!r}")
    if raw["slug"] in seen:
        raise fail("duplicate slug")
    if raw["category"] not in CATEGORIES:
        raise fail(f"invalid category {raw['category']!r}")
    if not raw["title"].strip():
        raise fail("title is empty")
    if not isinstance(raw["date"], str):
        raise fail("date must be a YYYY-MM-DD string")
    try:
        date = datetime.date.fromisoformat(raw["date"])
    except ValueError:
        raise fail(f"invalid date {raw['date']!r}") from None
    image = raw["image"]
    if image is not None and not (isinstance(image, str) and image):
        raise fail("image must be null or a non-empty string")
    seen.add(raw["slug"])
    return NewsItem(raw["slug"], date, raw["category"], raw["title"], raw["summary"],
                    raw["body_html"], raw["body_md"], image, raw["image_alt"])


def _sorted(items: Sequence[NewsItem]) -> list[NewsItem]:
    by_slug = sorted(items, key=lambda n: n.slug)
    return sorted(by_slug, key=lambda n: n.date, reverse=True)


def load_news(path: Path = NEWS_JSON) -> tuple[NewsItem, ...]:
    if not path.exists():
        return ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise NewsDataError(f"{path}: cannot read: {e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise NewsDataError(f"{path}: expected an object with an 'items' list")
    seen: set[str] = set()
    items = [_parse(path, raw, i, seen) for i, raw in enumerate(data["items"])]
    return tuple(_sorted(items))


def news_to_json(items: Sequence[NewsItem]) -> str:
    out = [{"slug": n.slug, "date": n.date.isoformat(), "category": n.category, "title": n.title,
            "summary": n.summary, "body_md": n.body_md, "body_html": n.body_html,
            "image": n.image, "image_alt": n.image_alt} for n in _sorted(items)]
    return json.dumps({"version": 1, "items": out}, ensure_ascii=False, indent=2) + "\n"
