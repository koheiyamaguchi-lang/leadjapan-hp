"""HTML layout rendering (standard library only, no JavaScript)."""
from __future__ import annotations

import html

from sitegen.content import COPYRIGHT, NAV, PLACEHOLDER, SITE

FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Noto+Sans+JP:wght@400;500;700&"
    "family=Noto+Serif+JP:wght@600;700&display=swap"
)


def esc(s: object) -> str:
    return html.escape(str(s), quote=True)


def find_placeholders(text: str) -> int:
    return text.count(PLACEHOLDER)


def _nav_links(current: str | None) -> str:
    items = []
    for filename, label in NAV:
        attr = ' aria-current="page"' if filename == current else ""
        items.append(f'<a href="{esc(filename)}"{attr}>{esc(label)}</a>')
    return "\n".join(items)


def render_layout(*, title: str, description: str, body: str, current: str) -> str:
    nav = _nav_links(current)
    footer_links = "\n".join(
        f'<a href="{esc(f)}">{esc(label)}</a>' for f, label in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" type="image/svg+xml" href="static/img/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS_URL}">
<link rel="stylesheet" href="static/css/style.css">
<link rel="stylesheet" href="static/css/motion.css">
</head>
<body>
<a class="skip-link" href="#main">本文へスキップ</a>
<header class="site-header">
<div class="container header-inner">
<a class="logo" href="index.html">Lead Japan <small>合同会社</small></a>
<input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="メニュー">
<label for="nav-toggle" class="nav-toggle-label"><span class="visually-hidden">メニュー</span><span></span></label>
<nav class="global-nav" aria-label="グローバルナビゲーション">
{nav}
</nav>
</div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
<div class="container footer-inner">
<div class="footer-company">
<p class="footer-name">{esc(SITE["name"])}</p>
<p>{esc(SITE["location"])}</p>
</div>
<nav class="footer-nav" aria-label="フッターナビゲーション">
{footer_links}
<a href="privacy.html">プライバシーポリシー</a>
</nav>
</div>
<p class="copyright container">{esc(COPYRIGHT)}</p>
</footer>
</body>
</html>
"""
