# Lead Japan 合同会社 コーポレートサイト

Python 標準ライブラリだけで生成する静的サイトです。外部サービス・有料サービスは使用しません（フォントのみ Google Fonts を利用）。

## 構成

- `build.py` — ビルドスクリプト。`site/` に HTML と `static/` を出力します。
- `sitegen/content.py` — サイトの文言とデータ（会社情報、事業、ニュース、プライバシーポリシーなど）。
- `sitegen/pages.py` — 各ページの構成。
- `sitegen/render.py` — 共通レイアウト（ヘッダー、フッター、ナビゲーション）。
- `static/css/style.css`, `static/css/motion.css` — スタイルとスクロール演出。
- `static/img/tokyo-skyline.svg` — 東京の街並みのイラスト。
- `tests/` — テスト。
- `.github/workflows/pages.yml` — GitHub Pages への自動公開設定。

## 文言の編集

文言の編集は `sitegen/content.py` のみで行ってください。HTML を直接編集する必要はありません。

## 【要入力】 の一覧と埋め方

まだ確定していない情報は `【要入力】` と表示されています。ビルド時に残数と該当ファイルが警告として表示されます（ニュースの日付は `【要入力】` の文字ではなく仮の日付値として入っているため、警告の件数には含まれません）。

| 場所 | 内容 | 埋め方 |
| --- | --- | --- |
| `sitegen/content.py` の会社情報 `"representative"` | 代表者名 | 代表者名を入力 |
| `sitegen/content.py` の会社情報 `"founded"` | 設立日（「2026年」の後ろ） | 例: `1月15日` のように入力 |
| `sitegen/content.py` の会社情報 `"address"` | 住所の詳細（「東京都」の後ろ） | 番地などを入力 |
| `sitegen/content.py` の会社情報 `"email"` | お問い合わせ用メールアドレス | メールアドレスを入力 |
| `sitegen/content.py` の `NEWS`（ニュース） 2件 | 日付が推定値のニュース 2件（`# 【要入力】` コメント付き） | 実際の日付に置き換え |

ニュースの日付は次の2件が推定値です。

- 『外資系PM1年目の教科書』の刊行予定に関するお知らせ（2026-06-01）
- Lead Japan 合同会社の設立に関するお知らせ（2026-01-01）

埋めたら `python3 build.py` を実行し、警告が消えたことを確認してください。

## ビルド

```
python3 build.py
```

`site/` ディレクトリが作成されます（Git 管理対象外）。

## プレビュー

```
python3 -m http.server -d site 8000
```

ブラウザで http://localhost:8000 を開きます。

## テスト

```
python3 -m unittest discover -s tests -v
```

## 公開手順（GitHub Pages・無料）

1. GitHub で **public** リポジトリを作成します。
2. このプロジェクトを push します（`main` ブランチ）。
3. リポジトリの **Settings › Pages › Source** を **「GitHub Actions」** に設定します。
4. `main` への push で `.github/workflows/pages.yml` が実行され、公開されます。手動で実行する場合は Actions タブから `workflow_dispatch` を使います。
5. 公開 URL は `https://<ユーザー名>.github.io/<リポジトリ名>/` になります。

すべての内部リンクは相対パスのため、サブパスでも動作します。

## お問い合わせ

お問い合わせはメールアドレスでの受付です。有料のフォームサービスは使用していません。無料の Google フォームを追加する場合は、`sitegen/pages.py` の `body_contact` にあるコメント箇所に埋め込みを追加してください。

## 注意事項

- プライバシーポリシーの文面は草案です。公開前に内容を確認してください。
- スクロール演出は Chrome / Edge / Safari 26 以降で動作します。それ以外のブラウザでは、演出なしでコンテンツが静的に表示されます。
- 独自ドメインを後で使う場合は、ドメイン取得費用のみ有料です（任意）。GitHub Pages の設定でカスタムドメインを指定し、DNS の設定を行ってください。
