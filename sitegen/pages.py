"""Page registry. PAGES is filled by later tasks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from sitegen.content import BUSINESSES, MESSAGE, NEWS, SITE, NewsItem
from sitegen.render import esc


@dataclass(frozen=True)
class Page:
    filename: str
    title: str
    description: str
    body: Callable[[], str]


def news_anchor(item: NewsItem, index: int) -> str:
    """Anchor id for a news item; index is its position in the (newest-first) list."""
    return f"news-{item.date:%Y%m%d}-{index}"


def news_list_html(items: Sequence[NewsItem]) -> str:
    rows = []
    for i, item in enumerate(items):
        rows.append(
            f'<li><time datetime="{item.date:%Y-%m-%d}">{item.date:%Y.%m.%d}</time>'
            f'<span class="news-cat">{esc(item.category)}</span>'
            f'<a href="news.html#{esc(news_anchor(item, i))}">{esc(item.title)}</a></li>'
        )
    return '<ul class="news-list">\n' + "\n".join(rows) + "\n</ul>"


def _section_head(label: str, title: str, extra: str = "") -> str:
    return (
        f'<div class="section-head reveal{extra}">'
        f'<span class="section-label">{esc(label)}</span>'
        f'<h2 class="section-title">{esc(title)}</h2>'
        "</div>"
    )


def body_index() -> str:
    cards = "\n".join(
        f'<a class="card biz-card reveal" style="--d: {i}" href="business.html#{esc(b.slug)}">'
        f'<span class="biz-num">{esc(b.number)}</span>'
        f'<h3 class="biz-title">{esc(b.title)}</h3>'
        f'<span class="biz-en">{esc(b.title_en)}</span>'
        f'<p class="biz-summary">{esc(b.summary)}</p>'
        f'<span class="biz-more">詳しく見る</span>'
        "</a>"
        for i, b in enumerate(BUSINESSES)
    )
    return f"""<section class="section hero">
<div class="hero-sky" aria-hidden="true"></div>
<img class="hero-skyline" src="static/img/tokyo-skyline.svg" alt="東京タワーと東京の街並み" width="1600" height="600">
<div class="container hero-inner">
<p class="hero-kicker reveal">{esc(SITE["name_en"])}</p>
<h1>{esc(SITE["tagline"])}</h1>
<p class="hero-sub reveal" style="--d: 1">Lead Japan — Tokyo, Japan</p>
</div>
<a class="scroll-cue" href="#about" aria-label="下へスクロール"><span>SCROLL</span></a>
</section>

<section class="section top-about" id="about">
<div class="container about-grid">
{_section_head("About", "会社紹介", " reveal--left")}
<div class="about-body reveal" style="--d: 1">
<p class="lead-text">{esc(SITE["philosophy"])}</p>
<a class="btn" href="company.html">会社紹介を見る</a>
</div>
</div>
</section>

<section class="section alt top-business" id="business">
<div class="container">
{_section_head("Business", "事業概要")}
<div class="biz-grid">
{cards}
</div>
</div>
</section>

<section class="section top-message" id="message">
<div class="container message-inner">
{_section_head("Message", "代表挨拶")}
<blockquote class="message-excerpt reveal reveal--zoom" style="--d: 1"><p>{esc(MESSAGE[0])}</p></blockquote>
<a class="btn reveal" style="--d: 2" href="message.html">代表挨拶を読む</a>
</div>
</section>

<section class="section alt top-news" id="news">
<div class="container news-grid">
{_section_head("News", "ニュースルーム", " reveal--left")}
<div class="news-body reveal reveal--right" style="--d: 1">
{news_list_html(NEWS[:3])}
<a class="btn" href="news.html">ニュース一覧へ</a>
</div>
</div>
</section>

<section class="section cta-band" id="contact">
<div class="container cta-inner reveal">
<span class="section-label">Contact</span>
<a class="cta-link" href="contact.html">お問い合わせはこちら</a>
</div>
</section>"""


PAGES: list[Page] = [
    Page(
        filename="index.html",
        title="Lead Japan 合同会社 | 日本を導き、世界へ。",
        description=(
            "Lead Japan 合同会社（東京都）の公式サイト。AIソリューションの展開、"
            "コンサルティング、システム開発、出版を通じて、日本の成長に寄与します。"
        ),
        body=body_index,
    ),
]
