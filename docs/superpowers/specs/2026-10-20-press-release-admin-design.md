# プレスリリース管理画面 設計書

日付: 2026-10-20
対象リポジトリ: `HP/`（Lead Japan 合同会社 コーポレートサイト）

## 目的と背景

Lead Japan 合同会社のサイトのニュース欄（ニュースルーム）に、プレスリリースやお知らせを載せるための管理画面を作る。今回は「いつでもプレスリリースを打てる状態」にすることが目的で、実際のプレスリリースはまだ出さない。

想定読者は、PMに入門する人と、若手PMを部下に持ち「部下に読ませたい」と考える上司。記事はそのまま読み応えのあるものになるので、記事ごとに個別ページがあり、SNSで共有しやすいことが大切。

## 現状

- `build.py` と `sitegen/` が Python 標準ライブラリだけで静的サイトを `site/` に生成する。
- ニュースは `sitegen/content.py` の `NEWS`（`NewsItem(date, category, title, body)` のタプル）に直書きしてあり、`news.html` に全件をまとめて表示している。トップには最新3件が出る。
- 公開先は GitHub Pages（`.github/workflows/pages.yml` がテスト→ビルド→デプロイ）。リポジトリは `github.com/koheiyamaguchi-lang/leadjapan-hp`（public）。
- テストは `python3 -m unittest discover -s tests`（60件）。

## ゴール

1. 自分の Mac 上だけで動く Django の管理画面から、ニュース記事（プレスリリース含む）を作成・編集・削除・下書き保存できる。
2. 公開前に、実際のサイトと同じデザインでプレビューできる。
3. 管理画面の「サイトに反映」操作で、公開記事がサイトに出る（GitHub に push → Cloudflare Pages が自動ビルド）。
4. ニュースの各記事に個別ページができ、一覧（`news.html`）とトップの最新3件からリンクされる。
5. 公開先を GitHub Pages から Cloudflare Pages に移す。独自ドメインを後でつなげる状態にする。

## ゴールではないもの

- プレスリリース本文を書くこと（今回は書かない。既存の3件は移行するだけ）。
- メール配信、ニュースレター、購読者管理。
- 管理画面をインターネットに公開すること、スマホからの利用。
- 複数ユーザー・権限管理。使うのは代表者1人。
- 独自ドメインの購入と DNS 設定の作業そのもの（手順の説明は README に書く）。

## やってはいけないこと（失敗とみなす）

- 管理画面が `127.0.0.1` 以外から見える。
- 下書きの記事が公開サイトに出る。
- 「サイトに反映」で、テストが通らない・壊れたサイトが push される。
- 本文に入れた HTML やスクリプトがそのままサイトに出る（XSS）。
- 既存の公開ページ（会社紹介など）の見た目や URL が変わる。`news.html` の URL も維持する。

## 制約

- 有料サービスを使わない（ドメイン代を除く）。使える言語は Python、HTML、CSS。公開サイトに JavaScript は入れない（管理画面の Django 標準 admin が内部で使う JS は可）。
- **公開サイトのビルド（`build.py` と `sitegen/`）は標準ライブラリだけのまま**にする。Cloudflare Pages 上ではこれだけを実行する。
- 管理画面側だけ、無料の Python ライブラリを追加してよい: Django（5.2 LTS）、markdown-it-py、Pillow（画像用）。依存は管理画面専用のファイル（`requirements-admin.txt`）に書く。
- 既存の制約は引き続き有効: 内部リンクはすべて相対パス、`<html lang="ja">`、固有の `<title>`、既存のパレットとデザイン、`【要入力】` の警告。
- 開発は TDD（superpowers:test-driven-development）で進める。

## 決まっていること（ユーザーが決めたこと）

- 用途はニュースレターではなく**プレスリリース**。載せる場所は会社のニュース欄。
- 管理画面は **PC（Mac）からのみ**。PythonAnywhere などの外部ホスティングは使わない。
- 公開先は **Cloudflare Pages**。URL は独自ドメインにしたい。
- 今回は管理画面を実装するだけで、プレスリリースはまだ出さない。

## 仕組み（設計者の判断。ユーザーには説明済み）

### データの流れ

```
[Mac] Django 管理画面 ──(SQLite: 下書き含む全記事)
   │「サイトに反映」
   ▼
content/news.json（公開記事のみ）＋ static/img/news/（画像）を書き出す
   ▼
テスト実行 → 通れば git commit → git push origin main
   ▼
[Cloudflare Pages] python build.py → site/ を配信
```

- **公開サイトの正本は、リポジトリにコミットされた `content/news.json` と `static/img/news/`**。`build.py` はこれを標準ライブラリの `json` で読む。`sitegen/content.py` の `NEWS` 直書きはやめ、JSON からの読み込みに置き換える（`NewsItem` は拡張して使い続ける）。
- Django の SQLite（下書きを含む作業用データ）は git に入れない。OneDrive 上にあるので消失リスクは低いが、JSON から DB を作り直す管理コマンドを用意する（初回の既存3件の移行にも使う）。
- Markdown → HTML の変換は書き出し時に Django 側で行い、JSON には `body_html`（変換済み）と `body_md`（原文）の両方を入れる。変換には markdown-it-py を **HTML 無効（`html=False`）** で使い、本文中の生 HTML はエスケープされる。リンクは `http(s)://`・`mailto:`・相対パスのみ許可。`build.py` は `body_html` を信頼済み HTML として埋め込み、それ以外の項目はすべて従来どおり `esc()` する。

### 記事の項目

| 項目 | 必須 | 内容 |
|---|---|---|
| タイトル | ○ | |
| スラッグ | ○ | URL 用の英数字とハイフン。日付から自動提案し、編集可。公開後は変えない前提（変えると URL が変わる旨を管理画面に表示） |
| 公開日 | ○ | 日付 |
| 種類 | ○ | プレスリリース／お知らせ／出版／事業 |
| 要約 | ○ | 120字以内目安。一覧・`<meta name="description">`・OGP に使う |
| 本文 | ○ | Markdown（見出し・太字・箇条書き・リンク・画像なしの引用など） |
| メイン画像 | － | 任意。JPEG/PNG/WebP。書き出し時に `static/img/news/<slug>.<ext>` へコピー。代替テキスト項目も持つ |
| 状態 | ○ | 下書き／公開 |

既存の `NewsItem.category` の値（お知らせ・出版・事業）に「プレスリリース」を加える。

### 公開サイト側の変更

- 記事ごとの個別ページを **サイト直下にフラットに** 置く: `news-<slug>.html`（例: `news-2026-04-01-founding.html`）。サブフォルダにすると全ページの相対パスが崩れるため（以前「`news/...`」と説明したが、これは設計者の判断で変更）。
- 個別ページの中身: ページ見出し帯、パンくず（ホーム / ニュースルーム / 記事タイトル）、日付・種類、タイトル、メイン画像、本文、一覧へ戻るリンク。プレスリリースの場合は末尾に「本件に関するお問い合わせ」として会社名とお問い合わせページへのリンクを出す。
- `news.html` は一覧ページにし、各行が個別ページへリンクする。トップの最新3件も個別ページへリンクする。
- 個別ページには OGP（`og:title`、`og:description`、`og:type=article`、`og:url`、`og:image`）を出す。OGP の URL は絶対 URL が必要なので、`sitegen/content.py` に `SITE_URL`（初期値は Cloudflare Pages の `*.pages.dev` アドレス。独自ドメイン取得後に差し替え）を置く。`SITE_URL` が空なら `og:url` と `og:image` は出さない。
- 本文用の CSS（見出し・箇条書き・引用・リンク・画像）を既存デザインに合わせて追加する。

### 管理画面

- Django プロジェクトはリポジトリ内の `cms/` に置く。`python3 cms/manage.py runserver 127.0.0.1:8001` で起動。起動方法は README に書く。
- Django 標準の admin を使い、日本語表示（`LANGUAGE_CODE="ja"`、`TIME_ZONE="Asia/Tokyo"`）。ログインはローカルのスーパーユーザー。
- 一覧: タイトル・公開日・種類・状態で表示、状態と種類で絞り込み、タイトル検索。
- **プレビュー**: 記事の編集画面から、実サイトと同じ `render_layout` とページ部品で組んだ個別ページを表示する（下書きでも見られる）。CSS と画像は管理画面側から配信する。
- **「サイトに反映」**: 管理画面上のボタン（admin のツールバーまたは専用ページ）。押すと順に:
  1. 公開状態の記事だけを `content/news.json` と `static/img/news/` に書き出す（公開でなくなった記事の画像は消す）。
  2. リポジトリのテスト（`python3 -m unittest discover -s tests`）を実行。失敗したら書き出しを元に戻して中止し、理由を画面に表示。
  3. 変更が無ければ「変更なし」と表示して終了。
  4. `content/` と `static/img/news/` だけを `git add` → `git commit -m "news: サイトに反映 (<日時>)"` → `git push origin main`。push に失敗したら（ネット不通・認証切れなど）画面にエラーを出す。コミットは残してよく、次回の反映で一緒に push される。
  5. 成功したら「数分でサイトに反映されます」と公開 URL を表示。
- 反映は作業ツリーに `content/`・`static/img/news/` 以外の未コミット変更があっても、それらは巻き込まない。

### Cloudflare Pages への移行

- Cloudflare Pages のプロジェクトを GitHub リポジトリに接続する（アカウント作成と接続はユーザーが Cloudflare の画面で行う。手順を README に書く）。ビルド設定: ビルドコマンド `python build.py`、出力ディレクトリ `site`、環境変数 `PYTHON_VERSION=3.13`。
- `.github/workflows/pages.yml` は、**テストだけを実行する CI**（例: `ci.yml`）に置き換え、GitHub Pages へのデプロイはやめる。GitHub Pages の公開設定も無効にする（移行完了後）。
- 独自ドメインは、取得後に Cloudflare Pages の「カスタムドメイン」から追加する手順を README に書く。`SITE_URL` の差し替えも同じ手順に含める。

### テスト

- Django 側: `cms/` 内に Django の `TestCase`。モデルの検証（スラッグ形式・一意性・必須項目）、書き出し（下書き除外・JSON の形・画像コピーと削除・Markdown の HTML 無効化と危険なリンクの除去）、プレビュー表示、反映処理（テスト失敗時の中止と巻き戻し、変更なし、git 操作は差し替え可能にしてテストでは実際に push しない）、`127.0.0.1` 限定の設定。
- 既存 `tests/`: JSON からの読み込み、個別ページの生成、一覧・トップからのリンク、OGP、`news.html` の維持。既存の全ページ用チェック（リンク切れ・JS なし・相対パス・タイトル固有）が個別ページにも効くこと。
- `tests/` は今後も Django なしで動く（Cloudflare と CI では Django を入れない）。

## 設計者（Claude）の判断で決めた点

- **Cloudflare への切り替えは段階的に行う。** Cloudflare Pages のプロジェクトはまだ無い。実装中は GitHub Pages のデプロイを残し、`SITE_URL` は空のまま（`og:url`・`og:image` は出ない）。ユーザーが Cloudflare で接続し、`*.pages.dev` のサイトが表示されたのを確認してから、`pages.yml` を CI 用に置き換えて GitHub Pages を無効にし、`SITE_URL` を設定する。この切り替えは、計画の最後のタスクとしてユーザーの確認を挟んで行う。
- **既存3件のスラッグには日付を入れない**（例: `founding`、`book-announcement`、`site-launch`）。日付はまだ推定値だからで、`UNCONFIRMED` の該当項目と README の表もそのまま残す。新しい記事のスラッグ提案は「日付＋英数字」。
- **`【要入力】` 警告**は `news.json` 由来の本文にも効く（`build.py` が生成した HTML を数える仕組みはそのまま）。
- **URL の正規形は `.html` 付き**とする（`og:url` も `news-<slug>.html`）。Cloudflare Pages は `.html` なしの URL へ 308 リダイレクトするが、リンク・正規 URL は既存どおり `.html` 付きで統一する。
- **`news.html` は一覧ページにする。** 各行は日付・種類・タイトル（個別ページへのリンク）・要約。旧 `#news-YYYYMMDD-i` アンカーは廃止する（公開から日が浅く、外部リンクは無い前提）。関連する既存テストは書き換える。
- **Python の仮想環境は OneDrive の外**（`~/.venvs/leadjapan-cms`）に作り、README に書く。SQLite は `cms/db.sqlite3`（git 対象外）に置き、OneDrive のバックアップに任せる。使うのは Mac 1台だけなので同期の衝突は起きにくい。「サイトに反映」は、管理画面を動かしている同じ Python（`sys.executable`）でテストを実行する。
- 作業ツリーにある未追跡の `site 2/`（OneDrive の同期コピー）と `.claude/` は `.gitignore` に追加する。

## 設計者に任せること

- Django アプリの名前・ファイル分割、admin のカスタマイズ方法（`ModelAdmin` のアクションか専用ビューか）。
- スラッグの自動提案ルール（日付＋英数字。日本語タイトルからの自動ローマ字化はしなくてよい）。
- 本文 CSS の細部、個別ページのレイアウト細部（既存デザインに合わせる）。
- 画像の最大サイズ制限の値（目安 5MB 以下、横 2000px 以下にリサイズしてもよい）。
- 既存3件のスラッグ。
