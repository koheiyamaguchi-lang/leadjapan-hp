"""Site content for Lead Japan 合同会社. Unknown facts use PLACEHOLDER."""
from __future__ import annotations

import datetime
from dataclasses import dataclass

PLACEHOLDER = "【要入力】"

SITE: dict[str, str] = {
    "name": "Lead Japan 合同会社",
    "name_en": "Lead Japan LLC",
    "tagline": "日本を導き、世界へ。",
    "philosophy": (
        "Lead Japan 合同会社は、日本を導き、世界の中で日本の立ち位置を発展させていく。"
        "その思いを込めて名付けました。日本の成長に寄与するか――それが私たちの価値基準です。"
    ),
    "location": "東京都",
    "address": "東京都" + PLACEHOLDER,
    "founded": "2026年" + PLACEHOLDER,
    "representative": PLACEHOLDER,
    "email": PLACEHOLDER,
    "status": "2026年設立。現在、各事業の立ち上げを進めています。",
}


@dataclass(frozen=True)
class Business:
    slug: str
    number: str
    title: str
    title_en: str
    summary: str
    details: tuple[str, ...]


BUSINESSES: tuple[Business, ...] = (
    Business(
        slug="ai",
        number="01",
        title="AIソリューションの展開",
        title_en="AI Solutions",
        summary="生成AIをはじめとするAI技術を、日本の企業の現場で実際に使える形にして届けます。",
        details=(
            "業務の中でAIを活用できる領域の整理と、導入方針のご提案",
            "生成AIを活用した業務効率化ソリューションの企画・展開",
            "AI活用を社内に定着させるための運用設計と支援",
        ),
    ),
    Business(
        slug="consulting",
        number="02",
        title="コンサルティング",
        title_en="Consulting",
        summary="事業とプロジェクトの課題に向き合い、成果につながる実行まで伴走します。",
        details=(
            "プロジェクトの立ち上げから推進までを支えるマネジメント支援",
            "事業課題の整理と、実行可能な改善計画の策定",
            "グローバルな視点を取り入れた組織・業務プロセスの見直し",
        ),
    ),
    Business(
        slug="system",
        number="03",
        title="システム開発",
        title_en="System Development",
        summary="現場の業務に寄り添い、使いやすく成長に合わせて拡張できるシステムを開発します。",
        details=(
            "プロジェクトマネジメント関連システムの開発",
            "スタートアップ向け業務システムの開発",
            "既存業務の見直しを伴うシステム化のご相談",
        ),
    ),
    Business(
        slug="publishing",
        number="04",
        title="出版",
        title_en="Publishing",
        summary="実務で培った知見を書籍にまとめ、多くの方に届けます。",
        details=(
            "『外資系PM1年目の教科書』（2026年刊行予定）の企画・出版",
            "プロジェクトマネジメントやキャリアに関する実践的な知見の発信",
        ),
    ),
)


@dataclass(frozen=True)
class NewsItem:
    date: datetime.date
    category: str
    title: str
    body: str


NEWS: tuple[NewsItem, ...] = (
    NewsItem(
        date=datetime.date(2026, 10, 19),
        category="お知らせ",
        title="コーポレートサイトを公開しました",
        body="Lead Japan 合同会社のコーポレートサイトを公開いたしました。今後、事業の進捗や出版に関する情報を随時お知らせしてまいります。",
    ),
    NewsItem(
        date=datetime.date(2026, 6, 1),  # 【要入力】 実際の日付に置換
        category="出版",
        title="『外資系PM1年目の教科書』を2026年に刊行予定",
        body="外資系企業でプロジェクトマネージャーとして歩み始める方に向けた書籍『外資系PM1年目の教科書』を、2026年に刊行する予定です。詳細が決まり次第、本サイトでご案内いたします。",
    ),
    NewsItem(
        date=datetime.date(2026, 1, 1),  # 【要入力】 実際の日付に置換
        category="お知らせ",
        title="Lead Japan 合同会社を設立しました",
        body="Lead Japan 合同会社を東京都に設立いたしました。日本の成長に寄与することを価値基準として、事業を進めてまいります。",
    ),
)

MESSAGE_TITLE = "日本を導き、世界へ。"

MESSAGE: tuple[str, ...] = (
    "この度は Lead Japan 合同会社のウェブサイトをご覧いただき、誠にありがとうございます。",
    "当社の社名には、日本を導き、世界の中で日本の立ち位置を発展させていきたいという思いを込めています。日本の成長に寄与するかどうか。それを、私たちはすべての判断の拠り所としています。",
    "事業の柱は、AIソリューションの展開、コンサルティング、システム開発、出版の四つです。AIという新しい力を現場で使える形にし、プロジェクトマネジメントの知見を通じて、日本企業が世界で力を発揮するための土台づくりをお手伝いします。",
    "出版では、私自身の経験をもとに『外資系PM1年目の教科書』を2026年に刊行する予定です。働き方や仕事の進め方を言葉にして共有することも、日本の成長につながると考えています。",
    "まだ歩み始めたばかりの会社ですが、一つひとつの取り組みを誠実に積み重ねてまいります。今後とも、ご指導ご鞭撻を賜りますようお願い申し上げます。",
)

PRIVACY: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "基本方針",
        (
            "Lead Japan 合同会社（以下「当社」）は、個人情報の重要性を認識し、個人情報の保護に関する法令を遵守するとともに、適切に取り扱うことに努めます。",
        ),
    ),
    (
        "取得する個人情報",
        (
            "当社は、お問い合わせの際にお客様からご提供いただく氏名、メールアドレス、お問い合わせ内容などの個人情報を取得することがあります。",
            "個人情報は、適法かつ公正な手段により取得いたします。",
        ),
    ),
    (
        "利用目的",
        (
            "取得した個人情報は、お問い合わせへの回答、ご連絡、およびサービスのご案内のために利用します。",
            "上記の目的以外には利用いたしません。",
        ),
    ),
    (
        "第三者提供",
        (
            "当社は、法令に基づく場合を除き、ご本人の同意なく個人情報を第三者に提供することはありません。",
        ),
    ),
    (
        "安全管理",
        (
            "当社は、個人情報の漏えい、滅失、毀損を防止するため、必要かつ適切な安全管理措置を講じます。",
        ),
    ),
    (
        "開示・訂正・削除の請求",
        (
            "ご本人から個人情報の開示、訂正、削除などのご請求があった場合は、ご本人であることを確認のうえ、法令に基づき速やかに対応いたします。",
            "ご請求は、下記のお問い合わせ窓口までご連絡ください。",
        ),
    ),
    (
        "お問い合わせ窓口",
        (
            f"個人情報の取り扱いに関するお問い合わせは、次のメールアドレスにお寄せください。{SITE['email']}",
        ),
    ),
    (
        "改定",
        (
            "当社は、法令の変更や運用の見直しに応じて、本方針を改定することがあります。改定後の内容は、本サイトに掲載した時点から効力を生じます。",
            "制定日：2026年10月19日",
        ),
    ),
)

NAV: tuple[tuple[str, str], ...] = (
    ("company.html", "会社紹介"),
    ("business.html", "事業概要"),
    ("message.html", "代表挨拶"),
    ("news.html", "ニュースルーム"),
    ("contact.html", "お問い合わせ"),
)
