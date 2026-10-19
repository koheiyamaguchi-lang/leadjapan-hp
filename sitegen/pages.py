"""Page registry. PAGES is filled by later tasks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from sitegen.content import BUSINESSES, MESSAGE, MESSAGE_TITLE, NEWS, PLACEHOLDER, PRIVACY, SITE, NewsItem
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


def page_hero(title: str, label_en: str) -> str:
    return (
        '<section class="page-hero"><div class="container">'
        f'<span class="section-label">{esc(label_en)}</span>'
        f'<h1>{esc(title)}</h1>'
        "</div></section>\n"
        '<div class="container"><nav class="breadcrumb" aria-label="パンくずリスト">'
        f'<a href="index.html">ホーム</a> / <span>{esc(title)}</span></nav></div>'
    )


_SVG = (
    '<svg class="biz-icon" viewBox="0 0 120 120" width="120" height="120" aria-hidden="true" '
    'fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
)

ICONS: dict[str, str] = {
    "ai": _SVG
    + '<circle cx="60" cy="22" r="9"/><circle cx="24" cy="60" r="9"/><circle cx="96" cy="60" r="9"/>'
    '<circle cx="42" cy="98" r="9"/><circle cx="78" cy="98" r="9"/><circle cx="60" cy="60" r="7"/>'
    '<path d="M54 29 29 52M66 29l25 23M33 60h20M67 60h20M56 66 46 90M64 66l10 24M51 98h18"/></svg>',
    "consulting": _SVG
    + '<circle cx="60" cy="60" r="44"/><circle cx="60" cy="60" r="4"/>'
    '<path d="m82 38-12 28-28 16 12-28z"/><path d="M60 10v8M60 102v8M10 60h8M102 60h8"/></svg>',
    "system": _SVG
    + '<rect x="14" y="14" width="64" height="46" rx="3"/><path d="M14 26h64"/>'
    '<rect x="34" y="40" width="64" height="46" rx="3"/><path d="M34 52h64"/>'
    '<rect x="54" y="66" width="52" height="40" rx="3"/><path d="M54 78h52"/></svg>',
    "publishing": _SVG
    + '<path d="M60 36C48 26 30 24 12 28v62c18-4 36-2 48 8 12-10 30-12 48-8V28c-18-4-36-2-48 8z"/>'
    '<path d="M60 36v62M24 46c10-2 22 0 28 5M24 62c10-2 22 0 28 5M96 46c-10-2-22 0-28 5M96 62c-10-2-22 0-28 5"/></svg>',
}


def body_company() -> str:
    biz_list = "<ul>" + "".join(f"<li>{esc(b.title)}</li>" for b in BUSINESSES) + "</ul>"
    rows = [
        ("商号", esc(SITE["name"])),
        ("英文社名", esc(SITE["name_en"])),
        ("設立", esc(SITE["founded"])),
        ("代表者", esc(SITE["representative"])),
        ("所在地", esc(SITE["address"])),
        ("事業内容", biz_list),
        ("現況", esc(SITE["status"])),
    ]
    table = "\n".join(f'<tr><th scope="row">{th}</th><td>{td}</td></tr>' for th, td in rows)
    return f"""{page_hero("会社紹介", "COMPANY")}
<section class="section">
<div class="container">
{_section_head("Philosophy", "企業理念")}
<blockquote class="philosophy reveal reveal--zoom"><p>{esc(SITE["philosophy"])}</p></blockquote>
</div>
</section>

<section class="section alt">
<div class="container name-origin">
{_section_head("Name", "社名の由来", " reveal--left")}
<div class="reveal reveal--right" style="--d: 1">
<p><strong>Lead</strong>は「導く」。<strong>Japan</strong>は私たちが拠って立つ国、日本です。</p>
<p>日本を導き、世界の中で日本の立ち位置を発展させていく。その思いを社名に込めました。</p>
<p>日本の成長に寄与するかどうか。それが、私たちのあらゆる判断の価値基準です。</p>
</div>
</div>
</section>

<section class="section">
<div class="container">
{_section_head("Profile", "会社概要")}
<table class="company-table reveal">
{table}
</table>
</div>
</section>"""


def body_business() -> str:
    items = []
    for i, b in enumerate(BUSINESSES):
        side = "reveal--left" if i % 2 == 0 else "reveal--right"
        details = "".join(f"<li>{esc(d)}</li>" for d in b.details)
        icon = ICONS.get(b.slug, "")
        items.append(
            f'<section id="{esc(b.slug)}" class="business-item reveal {side}">\n'
            f'<div class="business-visual">{icon}</div>\n'
            '<div class="business-text">'
            f'<span class="biz-num">{esc(b.number)}</span>'
            f'<h2>{esc(b.title)}</h2>'
            f'<span class="biz-en">{esc(b.title_en)}</span>'
            f'<p>{esc(b.summary)}</p>'
            f'<ul>{details}</ul>'
            "</div>\n</section>"
        )
    return f"""{page_hero("事業概要", "BUSINESS")}
<div class="container business-list">
{chr(10).join(items)}
</div>"""


def body_message() -> str:
    paras = "\n".join(f"<p>{esc(p)}</p>" for p in MESSAGE)
    return f"""{page_hero("代表挨拶", "MESSAGE")}
<section class="section">
<div class="container message-layout">
<aside class="message-side reveal reveal--left" aria-hidden="true">
<img src="static/img/tokyo-skyline.svg" alt="" width="1600" height="600">
</aside>
<article class="message-body reveal reveal--right" style="--d: 1">
<h2>{esc(MESSAGE_TITLE)}</h2>
{paras}
<p class="signature"><span>{esc(SITE["name"])}</span> 代表社員 <strong>{esc(SITE["representative"])}</strong></p>
</article>
</div>
</section>"""


def body_news() -> str:
    articles = []
    for i, item in enumerate(NEWS):
        articles.append(
            f'<article id="{esc(news_anchor(item, i))}" class="news-article reveal">\n'
            '<div class="news-meta">'
            f'<time datetime="{item.date:%Y-%m-%d}">{item.date:%Y.%m.%d}</time>'
            f'<span class="news-cat">{esc(item.category)}</span></div>\n'
            f'<h2>{esc(item.title)}</h2>\n'
            f'<p>{esc(item.body)}</p>\n'
            "</article>"
        )
    return f"""{page_hero("ニュースルーム", "NEWSROOM")}
<section class="section">
<div class="container">
{news_list_html(NEWS)}
</div>
</section>

<section class="section alt">
<div class="container news-articles">
{chr(10).join(articles)}
</div>
</section>"""


def body_privacy() -> str:
    sections = []
    for n, (heading, paras) in enumerate(PRIVACY, start=1):
        body = "".join(f"<p>{esc(p)}</p>" for p in paras)
        sections.append(f"<section>\n<h2>第{n}条　{esc(heading)}</h2>\n{body}\n</section>")
    return f"""{page_hero("プライバシーポリシー", "PRIVACY POLICY")}
<section class="section">
<div class="container policy reveal">
{chr(10).join(sections)}
<p class="policy-sign">制定日：2026年10月19日<br>{esc(SITE["name"])} 代表社員 {esc(SITE["representative"])}</p>
</div>
</section>"""


def body_contact() -> str:
    email = SITE["email"]
    if email == PLACEHOLDER:
        email_html = esc(email)
    else:
        email_html = f'<a href="mailto:{esc(email)}">{esc(email)}</a>'
    categories = "".join(
        f"<li>{esc(c)}</li>" for c in ("AIソリューション", "コンサルティング", "システム開発", "出版・取材")
    )
    btn = (
        f'<a class="btn" href="mailto:{esc(email)}">メールで問い合わせる</a>'
        if email != PLACEHOLDER
        else '<span class="btn is-disabled" aria-disabled="true">メールで問い合わせる</span>'
    )
    return f"""{page_hero("お問い合わせ", "CONTACT")}
<section class="section">
<div class="container contact reveal">
<p>事業に関するご相談、取材・出版に関するお問い合わせは、下記のメールアドレスまでご連絡ください。内容を確認のうえ、担当者よりご連絡いたします。</p>
<dl class="contact-info">
<dt>メール</dt><dd>{email_html}</dd>
<dt>所在地</dt><dd>{esc(SITE["address"])}</dd>
<dt>受付時間</dt><dd>平日 10:00〜18:00（土日祝・年末年始を除く）</dd>
</dl>
<p>{btn}</p>
<!-- 無料の Google フォームを使う場合はここに埋め込みリンクを置く -->
<h2 class="contact-sub">お問い合わせの例</h2>
<ul class="contact-cats">{categories}</ul>
<p class="contact-note">お預かりした個人情報は、お問い合わせへの対応の目的にのみ利用します。詳しくは<a href="privacy.html">プライバシーポリシー</a>をご確認ください。</p>
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
    Page(
        filename="company.html",
        title="会社紹介 | Lead Japan 合同会社",
        description="Lead Japan 合同会社の企業理念、社名の由来、会社概要をご紹介します。",
        body=body_company,
    ),
    Page(
        filename="business.html",
        title="事業概要 | Lead Japan 合同会社",
        description="AIソリューションの展開、コンサルティング、システム開発、出版。Lead Japan 合同会社の事業をご紹介します。",
        body=body_business,
    ),
    Page(
        filename="message.html",
        title="代表挨拶 | Lead Japan 合同会社",
        description="Lead Japan 合同会社 代表からのご挨拶。",
        body=body_message,
    ),
    Page(
        filename="news.html",
        title="ニュースルーム | Lead Japan 合同会社",
        description="Lead Japan 合同会社からのお知らせ・ニュースをご案内します。",
        body=body_news,
    ),
    Page(
        filename="privacy.html",
        title="プライバシーポリシー | Lead Japan 合同会社",
        description="Lead Japan 合同会社の個人情報の取り扱いについて定めたプライバシーポリシーです。",
        body=body_privacy,
    ),
    Page(
        filename="contact.html",
        title="お問い合わせ | Lead Japan 合同会社",
        description="Lead Japan 合同会社へのお問い合わせ方法のご案内です。",
        body=body_contact,
    ),
]
