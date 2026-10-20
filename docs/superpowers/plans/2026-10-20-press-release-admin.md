# Press Release Admin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local-only Django admin to write, preview and publish news/press-release articles; the static site reads published articles from a committed JSON file, gets one page per article, and moves hosting to Cloudflare Pages.

**Architecture:** Django (in `cms/`, local SQLite) is the editing tool only. "サイトに反映" exports published articles to `content/news.json` + `static/img/news/`, runs the site tests, then commits those paths and pushes. The public build (`build.py` + `sitegen/`) stays standard-library-only: it loads the JSON, renders `news.html` as a list and `news-<slug>.html` per article. Cloudflare Pages runs `python build.py` on push; the GitHub Pages deploy stays until the user confirms Cloudflare works (Task 8).

**Tech Stack:** Python 3.13; public site: stdlib only (`json`, `html`, `unittest`); admin: Django 5.2 LTS, markdown-it-py 3.x, Pillow; Cloudflare Pages; GitHub Actions (CI only after cutover).

**Spec:** `docs/superpowers/specs/2026-10-20-press-release-admin-design.md`

## Global Constraints

- No paid services (domain fee excepted). Public site: no JavaScript, no `<script>`; internal links relative; every page `<html lang="ja">`, unique `<title>`, existing palette/CSS.
- `build.py`, `sitegen/`, `tests/` must import nothing outside the standard library. `tests/` runs with plain `python3 -m unittest discover -s tests` (no Django installed).
- Admin dependencies only in `requirements-admin.txt`: `Django>=5.2,<5.3`, `markdown-it-py>=3.0,<4`, `Pillow>=11`.
- Admin venv: `~/.venvs/leadjapan-cms` (outside OneDrive). Below, `VPY` = `~/.venvs/leadjapan-cms/bin/python`. Admin tests: `VPY cms/manage.py test press`.
- Admin is local only: `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]`; documented start command `VPY cms/manage.py runserver 127.0.0.1:8001`. `LANGUAGE_CODE = "ja"`, `TIME_ZONE = "Asia/Tokyo"`. DB `cms/db.sqlite3`, uploads `cms/media/` (both git-ignored).
- Categories, exactly: `("プレスリリース", "お知らせ", "出版", "事業")`.
- Slug format: `^[a-z0-9]+(?:-[a-z0-9]+)*$`, unique. Article page filename: `news-<slug>.html` at site root (flat). Canonical URLs keep `.html`.
- Migrated slugs: `site-launch` (2026-10-19), `book-announcement` (2026-06-01), `founding` (2026-04-01). Keep `UNCONFIRMED` entries and the `【要入力】` warning.
- Markdown: markdown-it-py with `html=False`; links allowed only `http://`, `https://`, `mailto:`, or relative (no scheme). JSON stores both `body_md` and `body_html`; `build.py` embeds `body_html` as trusted HTML, everything else via `esc()`.
- Publish commit message: `news: サイトに反映 (YYYY-MM-DD HH:MM)`; only `content/` and `static/img/news/` are staged/committed; push `origin main`.
- `SITE_URL` in `sitegen/content.py`, initially `""`; when empty, omit `og:url` and `og:image`.
- Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Bad slug input** (Japanese, spaces, uppercase, duplicate) — admin shows a validation error on save; never reaches export. Test: Task 3 `test_slug_rejects_invalid_and_duplicate`.
2. **Hostile Markdown** (`<script>`, `<img onerror>`, `[x](javascript:alert(1))`) — rendered escaped / link dropped. Test: Task 4 `test_render_markdown_escapes_html_and_unsafe_links`.
3. **Push fails** (offline, auth expired) — admin shows the error, local commit kept, nothing else changed; next publish pushes it. Test: Task 6 `test_push_failure_reports_and_keeps_commit`.
4. **Article unpublished or image removed** — its page and image disappear from the site and no link points at them. Tests: Task 4 `test_export_removes_stale_images`, Task 2 `test_unpublished_article_has_no_page_or_link` (via link checker).
5. **Broken `content/news.json`** (hand-edited, missing field, bad date) — build stops with an error naming the file and the slug, not an empty newsroom. Test: Task 1 `test_load_news_rejects_invalid_entries`.

---

## File Structure

```
content/news.json              # published articles (source of truth for the site)
static/img/news/               # exported article images
sitegen/news.py                # NewsItem, CATEGORIES, SLUG_RE, load_news(), NEWS_JSON
sitegen/content.py             # NEWS = load_news(); SITE_URL; PAGE_META unchanged
sitegen/pages.py               # news list, article page body, article_pages(), og_tags()
sitegen/render.py              # render_layout(..., head_extra="")
static/css/style.css           # .article-body etc.
requirements-admin.txt
cms/manage.py
cms/cms_site/{__init__,settings,urls}.py
cms/press/{__init__,apps,models,admin,rendering,export,publish,views,urls}.py
cms/press/management/commands/import_news.py
cms/press/templates/admin/press/article/{change_form,change_list,publish}.html
cms/press/tests/{__init__,test_models,test_rendering,test_export,test_preview,test_publish}.py
.github/workflows/ci.yml       # Task 8 (replaces pages.yml)
```

---

### Task 1: News data in JSON

**Files:**
- Create: `sitegen/news.py`, `content/news.json`, `tests/test_news.py`
- Modify: `sitegen/content.py` (remove `NewsItem` class and `NEWS` literal; `from sitegen.news import NewsItem, load_news`; `NEWS = load_news()`; add `SITE_URL = ""`), `tests/test_content.py:27-28` (categories set → `CATEGORIES`), `tests/test_build.py:87-88` (keep; still passes)

**Interfaces:**
- Produces (`sitegen/news.py`):
  - `CATEGORIES: tuple[str, ...] = ("プレスリリース", "お知らせ", "出版", "事業")`
  - `SLUG_RE: re.Pattern` = `^[a-z0-9]+(?:-[a-z0-9]+)*$`
  - `NEWS_JSON: pathlib.Path` = repo root `/content/news.json`
  - `@dataclass(frozen=True) class NewsItem: slug: str; date: datetime.date; category: str; title: str; summary: str; body_html: str; body_md: str = ""; image: str | None = None; image_alt: str = ""` — `image` is a site-relative path like `static/img/news/founding.jpg`.
  - `class NewsDataError(ValueError)`
  - `load_news(path: pathlib.Path = NEWS_JSON) -> tuple[NewsItem, ...]` — newest first (ties: slug ascending). Missing file → `()`. Any invalid entry → `NewsDataError` whose message contains the file path and the slug (or index if no slug).
  - `news_to_json(items: Sequence[NewsItem]) -> str` — `{"version": 1, "items": [...]}`, `ensure_ascii=False`, `indent=2`, trailing newline, items in newest-first order, date as `YYYY-MM-DD`. (Used by Task 4 so both sides share one format.)
- JSON item keys: `slug, date, category, title, summary, body_md, body_html, image, image_alt`.

- [ ] **Step 1: Write failing tests** in `tests/test_news.py`:

```python
def test_roundtrip(self):            # news_to_json → write tmp → load_news equals input, newest first
def test_missing_file_is_empty(self): self.assertEqual(load_news(tmp / "nope.json"), ())
def test_load_news_rejects_invalid_entries(self):
    for bad in ({"slug": "Bad Slug"}, {"category": "広告"}, {"date": "2026-13-01"},
                {"title": ""}, "duplicate-slug", "missing summary key"):
        ...  # assertRaises(NewsDataError) and assertIn(str(path), str(err)) and slug/index in message
def test_repo_news_json_has_migrated_items(self):
    self.assertEqual([n.slug for n in load_news()], ["site-launch", "book-announcement", "founding"])
    self.assertTrue(all(n.body_html.startswith("<p>") for n in load_news()))
```

- [ ] **Step 2: Run** `python3 -m unittest tests.test_news -v` — Expected: FAIL (ImportError)
- [ ] **Step 3: Implement `sitegen/news.py`; write `content/news.json`** with the 3 existing items (same titles/dates/categories; `summary` = existing body text; `body_md` = existing body; `body_html` = `<p>` + escaped body + `</p>`; `image: null`). Rewire `sitegen/content.py`; update `tests/test_content.py` category assertion to `<= set(CATEGORIES)`.
- [ ] **Step 4: Run** `python3 -m unittest discover -s tests -v` — Expected: all OK (pages still use `NEWS`, fields `date/category/title` unchanged; `body` callers: replace `item.body` uses in `sitegen/pages.py` with `item.summary` for now, and update the `NewsItem(...)` constructions in `tests/test_pages.py` to the new fields)
- [ ] **Step 5: Commit** — `feat: load news from content/news.json`

---

### Task 2: Article pages, news list, OGP

**Files:**
- Modify: `sitegen/render.py` (`render_layout`), `sitegen/pages.py`, `build.py`, `static/css/style.css`, `tests/test_pages.py`, `tests/test_render.py`, `tests/test_build.py`

**Interfaces:**
- Consumes: Task 1 `NewsItem`, `NEWS`, `SITE_URL`.
- Produces:
  - `render_layout(*, title, description, body, current, head_extra: str = "") -> str` — `head_extra` inserted verbatim before `</head>`.
  - `Page` gains `nav_current: str | None = None` and `head_extra: str = ""`; `build()` passes `current=page.nav_current or page.filename`, `head_extra=page.head_extra`.
  - `news_page_filename(item: NewsItem) -> str` → `f"news-{item.slug}.html"`
  - `news_list_html(items, *, with_summary: bool = False) -> str` — rows link to `news_page_filename(item)`; with summary adds `<p class="news-summary">`.
  - `body_news_article(item: NewsItem, *, image_src: str | None = None) -> str` — `image_src` overrides `item.image` (used by Task 5 preview).
  - `og_tags(item: NewsItem, site_url: str) -> str`
  - `article_pages(items: Sequence[NewsItem] = NEWS) -> list[Page]`; `PAGES` = the 8 existing pages followed by `article_pages()`.
  - Remove `news_anchor` and its tests.
- Article page content (spec): hero band `ニュースルーム` / `NEWSROOM` (it holds the page's `<h1>`); breadcrumb `ホーム / ニュースルーム / <title>` (ニュースルーム links `news.html`; extend `page_hero` with an optional `crumbs: Sequence[tuple[str, str | None]]` parameter); meta row (`<time>` + `.news-cat`); title as `<h2 class="article-title">`; optional `<figure class="article-image"><img src alt></figure>`; `<div class="article-body">{body_html}</div>`; for category `プレスリリース` a `<aside class="press-contact">` with heading `本件に関するお問い合わせ`, `SITE["name"]`, link `contact.html`; link back `news.html` text `ニュース一覧へ戻る`.
- Page title `f"{item.title} | Lead Japan 合同会社"`, description `item.summary`, `nav_current="news.html"`.
- `og_tags`: always `og:title`, `og:description`, `og:type=article`, `og:site_name=Lead Japan 合同会社`; when `site_url` non-empty also `og:url = site_url.rstrip("/") + "/" + filename` and (if image) `og:image` absolute likewise. All values escaped.

- [ ] **Step 1: Write failing tests** (`tests/test_pages.py`, `tests/test_render.py`, `tests/test_build.py`):

```python
def test_head_extra_inserted_before_head_close(self)       # render_layout(..., head_extra="<meta x>") has "<meta x>\n</head>" or "<meta x></head>"
def test_news_list_links_article_pages(self):
    out = news_list_html([item], with_summary=True)
    self.assertIn(f'href="news-{item.slug}.html"', out); self.assertIn('class="news-summary"', out)
def test_article_body_trusted_html_rest_escaped(self):     # body_html "<p><strong>x</strong></p>" kept; title "<b>" → "&lt;b&gt;"
def test_press_release_has_contact_block(self):            # category プレスリリース → "本件に関するお問い合わせ" and href="contact.html"; お知らせ → absent
def test_og_tags_without_site_url(self):                   # no og:url / og:image
def test_og_tags_with_site_url(self):                      # og:url == "https://x.pages.dev/news-founding.html"; og:image absolute when image set
def test_pages_order(self):                                # [p.filename for p in PAGES][:8] == existing 8; rest == ["news-site-launch.html", "news-book-announcement.html", "news-founding.html"]
# tests/test_build.py
def test_article_pages_written_and_linked(self)            # each news-*.html exists; news.html and index.html link to it; nav aria-current on news.html link
def test_unpublished_article_has_no_page_or_link(self):    # build with article_pages() over NEWS[:2] via mock → no news-founding.html, no href to it anywhere
```

Existing whole-site tests (links resolve, no JS, relative URLs, unique titles) must cover the new pages unchanged.

- [ ] **Step 2: Run** `python3 -m unittest discover -s tests -v` — Expected: new tests FAIL
- [ ] **Step 3: Implement** per Interfaces; `body_news` = hero + `news_list_html(NEWS, with_summary=True)`; index top news keeps `NEWS[:3]` without summary. Add CSS: `.article-body` (h2/h3 serif, `p` margins, `ul/ol` indent, `blockquote` left border `--gold`, `a` color `--tower-text` underline, `img` max-width 100%), `.article-title`, `.article-image`, `.press-contact` (mist box), `.news-summary` (muted, small).
- [ ] **Step 4: Run** full suite — Expected: OK. `python3 build.py` writes 11 pages.
- [ ] **Step 5: Commit** — `feat: per-article news pages with OGP`

---

### Task 3: Django project, Article model, admin list

**Files:**
- Create: `requirements-admin.txt`, `cms/manage.py`, `cms/cms_site/{__init__,settings,urls}.py`, `cms/press/{__init__,apps,models,admin}.py`, `cms/press/migrations/0001_initial.py` (generated), `cms/press/tests/{__init__,test_models}.py`
- Modify: `.gitignore` (add `cms/db.sqlite3`, `cms/media/`, `site 2/`, `.claude/`)

**Interfaces:**
- Consumes: `sitegen.news.CATEGORIES`, `SLUG_RE` (settings put repo root on `sys.path`; `REPO_ROOT` setting = `Path(__file__).resolve().parents[2]`).
- Produces:
  - `press.models.Article`: `title CharField(200)`, `slug CharField(80, unique, validators=[RegexValidator(SLUG_RE)])` with help text `公開後に変更するとURLが変わります`, `published_on DateField`, `category CharField(choices=CATEGORIES)`, `summary CharField(200)`, `body_md TextField`, `image ImageField(upload_to="news/", blank=True)`, `image_alt CharField(200, blank=True)`, `status CharField(choices=[("draft","下書き"),("published","公開")], default="draft")`, `updated_at DateTimeField(auto_now=True)`. Ordering `-published_on, slug`. `verbose_name` Japanese (`記事`).
  - `Article.clean()`: image present ⇒ `image_alt` required; image > 5 MB rejected.
  - `press.models.suggest_slug(on: datetime.date) -> str` → `on.isoformat()`, appending `-2`, `-3`… if taken.
  - Admin: `list_display = ("title", "published_on", "category", "status")`, `list_filter = ("status", "category")`, `search_fields = ("title",)`; add form initial `published_on=today`, `slug=suggest_slug(today)`.
  - Settings: `ALLOWED_HOSTS = ["127.0.0.1", "localhost"]`, `DEBUG = True`, `SECRET_KEY` read from env `CMS_SECRET_KEY` with a fixed dev fallback (local-only), `MEDIA_ROOT = BASE_DIR/"media"`, `MEDIA_URL = "/media/"`, `DATABASES` sqlite `BASE_DIR/"db.sqlite3"`, `LANGUAGE_CODE="ja"`, `TIME_ZONE="Asia/Tokyo"`, `REPO_ROOT`.

- [ ] **Step 1: Create venv and install** — `python3 -m venv ~/.venvs/leadjapan-cms && VPY -m pip install -r requirements-admin.txt` (write the requirements file first). Expected: installs cleanly.
- [ ] **Step 2: Write failing tests** `cms/press/tests/test_models.py`:

```python
def test_slug_rejects_invalid_and_duplicate(self):
    for bad in ("日本語", "Has Space", "UPPER", "-lead", "a--b"):
        with self.assertRaises(ValidationError): make_article(slug=bad).full_clean()
    make_article(slug="ok-1").save()
    with self.assertRaises(ValidationError): make_article(slug="ok-1").full_clean()
def test_category_choices_match_site(self): self.assertEqual([c for c, _ in Article._meta.get_field("category").choices], list(CATEGORIES))
def test_default_status_is_draft(self)
def test_image_requires_alt(self)
def test_suggest_slug(self):  # "2026-10-20", then "2026-10-20-2" when taken
def test_allowed_hosts_local_only(self): self.assertEqual(settings.ALLOWED_HOSTS, ["127.0.0.1", "localhost"])
def test_admin_changelist_loads(self): # superuser client GET admin:press_article_changelist → 200, contains "記事"
```

- [ ] **Step 3: Run** `VPY cms/manage.py test press` — Expected: FAIL (no app/model)
- [ ] **Step 4: Implement** project, app, model, admin; `VPY cms/manage.py makemigrations press`
- [ ] **Step 5: Run** `VPY cms/manage.py test press` and `python3 -m unittest discover -s tests` — Expected: both OK
- [ ] **Step 6: Commit** — `feat: Django admin project with Article model`

---

### Task 4: Markdown rendering, export, import

**Files:**
- Create: `cms/press/rendering.py`, `cms/press/export.py`, `cms/press/management/{__init__,commands/__init__,commands/import_news}.py`, `cms/press/tests/{test_rendering,test_export}.py`

**Interfaces:**
- Consumes: `Article` (Task 3); `sitegen.news.NewsItem`, `news_to_json`, `load_news` (Task 1).
- Produces:
  - `rendering.render_markdown(md: str) -> str` — `MarkdownIt("commonmark", {"html": False})` with `validateLink` allowing only `http://`, `https://`, `mailto:`, or scheme-less URLs; disallowed links render as plain text.
  - `export.image_target(article: Article) -> str | None` → `static/img/news/<slug><ext lower>` or `None`.
  - `export.article_to_newsitem(article: Article, *, image: str | None = ...) -> NewsItem` (default: `image_target(article)`).
  - `export.export_published(repo_root: Path) -> list[str]` — writes `content/news.json` (published only, via `news_to_json`), copies images to their targets, deletes files in `static/img/news/` not referenced; returns repo-relative paths written/removed.
  - Management command `import_news [--path PATH]` — creates/updates Articles from JSON by slug, `status="published"`, `body_md` from JSON; does not touch images; idempotent.

- [ ] **Step 1: Write failing tests**:

```python
def test_render_markdown_basic(self):  # "## 見出し\n\n**太字**\n\n- a" → "<h2>見出し</h2>", "<strong>太字</strong>", "<li>a</li>"
def test_render_markdown_escapes_html_and_unsafe_links(self):
    out = render_markdown('<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[x](javascript:alert(1)) [ok](https://a.jp) [m](mailto:a@b.jp) [r](contact.html)')
    self.assertNotIn("<script", out); self.assertNotIn("<img", out); self.assertNotIn("javascript:", out)
    for href in ("https://a.jp", "mailto:a@b.jp", "contact.html"): self.assertIn(f'href="{href}"', out)
def test_export_only_published(self)       # draft absent from news.json; load_news(repo/content/news.json) == published items
def test_export_copies_image(self)         # tmp repo; published article with image → static/img/news/<slug>.png exists, json image path matches
def test_export_removes_stale_images(self) # pre-existing static/img/news/old.png and unpublished article's image → removed
def test_import_news_idempotent(self)      # call_command twice on repo content/news.json → 3 Articles, published, slugs match
```

Use a temp copy of the repo layout (`content/`, `static/img/news/`) for export tests; never write into the real repo from tests.

- [ ] **Step 2: Run** `VPY cms/manage.py test press` — Expected: new tests FAIL
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run** `VPY cms/manage.py test press` — Expected: OK
- [ ] **Step 5: Commit** — `feat: markdown rendering, JSON export and import`

---

### Task 5: Preview

**Files:**
- Create: `cms/press/views.py`, `cms/press/urls.py`, `cms/press/templates/admin/press/article/change_form.html`, `cms/press/tests/test_preview.py`
- Modify: `cms/cms_site/urls.py`

**Interfaces:**
- Consumes: `sitegen.render.render_layout`, `sitegen.pages.body_news_article`, `og_tags` (Task 2); `export.article_to_newsitem` (Task 4).
- Produces: URL name `press:preview` → `/preview/<int:pk>.html` (staff only; 404 for missing). Serves `render_layout(title=..., description=item.summary, body=body_news_article(item, image_src="media/<name>" or None), current="news.html")`. Routes `/preview/static/<path>` (repo `static/`) and `/preview/media/<path>` (`MEDIA_ROOT`) so the page's relative URLs resolve. Change form shows a `プレビュー` link (opens new tab) for saved articles.

- [ ] **Step 1: Write failing tests**:

```python
def test_preview_requires_staff(self)          # anonymous → redirect to admin login
def test_preview_renders_draft_with_site_layout(self)  # draft article → 200, contains title, rendered body_html, 'href="static/css/style.css"'
def test_preview_static_served(self)           # GET /preview/static/css/style.css → 200
def test_change_form_has_preview_link(self)    # admin change page contains reverse("press:preview", args=[pk])
```

- [ ] **Step 2: Run** `VPY cms/manage.py test press` — Expected: FAIL
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run** — Expected: OK. Manual: `VPY cms/manage.py runserver 127.0.0.1:8001`, open a preview; CSS and fonts load.
- [ ] **Step 5: Commit** — `feat: article preview with site layout`

---

### Task 6: 「サイトに反映」

**Files:**
- Create: `cms/press/publish.py`, `cms/press/templates/admin/press/article/{change_list,publish}.html`, `cms/press/tests/test_publish.py`
- Modify: `cms/press/admin.py` (extra URL), `cms/press/views.py`

**Interfaces:**
- Consumes: `export.export_published` (Task 4); `sitegen.content.SITE_URL`.
- Produces:
  - `@dataclass class PublishResult: status: Literal["published", "no_changes", "tests_failed", "push_failed"]; message: str; url: str | None = None`
  - `class Git(Protocol): def has_changes(self, paths: list[str]) -> bool; def commit(self, paths: list[str], message: str) -> None; def push(self) -> None` (raise `GitError(str)` on failure). `SubprocessGit(repo_root)` default implementation: `git status --porcelain -- <paths>`, `git add -A -- <paths>`, `git commit -m <msg> -- <paths>`, `git push origin main`.
  - `run_site_tests(repo_root: Path) -> tuple[bool, str]` — `subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=repo_root)`; returns (ok, last 40 lines of output).
  - `publish(repo_root: Path, *, git: Git | None = None, run_tests: Callable[[Path], tuple[bool, str]] = run_site_tests, now: Callable[[], datetime] = timezone.localtime) -> PublishResult` — snapshot `content/news.json` and `static/img/news/` to a temp dir; export; if tests fail → restore snapshot, `tests_failed` with output; if no changes → `no_changes`; commit with message `news: サイトに反映 (%Y-%m-%d %H:%M)` on paths `["content", "static/img/news"]`; push; on `GitError` from push → `push_failed` (commit kept); success → `published`, `url = SITE_URL or "https://koheiyamaguchi-lang.github.io/leadjapan-hp/"`, message `数分でサイトに反映されます`.
  - Admin: changelist shows button `サイトに反映`; GET `admin/press/article/publish/` shows confirm page; POST runs `publish(settings.REPO_ROOT)` and redirects to changelist with a Django message (success/warning/error per status).

- [ ] **Step 1: Write failing tests** (fake `Git` recording calls; fake `run_tests`; temp repo layout):

```python
def test_tests_failed_restores_files_and_skips_git(self)    # pre-existing news.json content unchanged after; git.commit not called; status "tests_failed"
def test_no_changes(self)                                    # has_changes False → "no_changes", commit not called
def test_published_commits_only_content_paths(self)          # commit paths == ["content", "static/img/news"]; message matches r"^news: サイトに反映 \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}\)$"; push called; status "published"
def test_push_failure_reports_and_keeps_commit(self)         # push raises GitError("offline") → "push_failed", "offline" in message, commit called once, files not restored
def test_admin_publish_requires_post_and_staff(self)         # GET shows confirm; anonymous POST → login redirect
def test_admin_publish_shows_message(self)                   # patch press.views.publish → result message appears after redirect
```

- [ ] **Step 2: Run** `VPY cms/manage.py test press` — Expected: FAIL
- [ ] **Step 3: Implement**
- [ ] **Step 4: Run** `VPY cms/manage.py test press` and `python3 -m unittest discover -s tests` — Expected: both OK
- [ ] **Step 5: Commit** — `feat: publish button exports, tests, commits and pushes`

---

### Task 7: README and first import

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write README section 「プレスリリース管理画面」** (Japanese): venv creation, `pip install -r requirements-admin.txt`, `VPY cms/manage.py migrate`, `createsuperuser`, `import_news` (first time), start `runserver 127.0.0.1:8001`, open `http://127.0.0.1:8001/admin/`; writing an article (fields, Markdown cheatsheet: 見出し `##`, 太字 `**`, 箇条書き `-`, リンク `[文字](URL)`), preview, 下書き/公開, 「サイトに反映」 and what each result message means; slug warning; backup note (DB in OneDrive; JSON is the site's source; `import_news` rebuilds).
- [ ] **Step 2: Verify end to end locally (no push):** run the README steps in order; create a draft and a published test article with an image; preview; run `export_published` via `VPY cms/manage.py shell -c` into a temp copy, then `python3 build.py` in that copy and open the article page. Delete the test articles afterwards and confirm `git status` shows no changes to `content/`.
- [ ] **Step 3: Commit** — `docs: press release admin usage`

---

### Task 8: Cloudflare Pages cutover (user checkpoint)

**Files:**
- Modify: `README.md` (公開 section), `sitegen/content.py` (`SITE_URL`)
- Create: `.github/workflows/ci.yml`; Delete: `.github/workflows/pages.yml`

- [ ] **Step 1: Write README 「Cloudflare Pages での公開」**: create Cloudflare account; Workers & Pages → Create → Pages → Connect to Git → `koheiyamaguchi-lang/leadjapan-hp`; production branch `main`; build command `python build.py`; output directory `site`; env var `PYTHON_VERSION=3.13`; after first deploy note the `*.pages.dev` URL; custom domain: Pages project → Custom domains → add domain, follow DNS instructions; then set `SITE_URL`. Commit — `docs: Cloudflare Pages setup`.
- [ ] **Step 2: STOP — ask the user** to do the Cloudflare steps and send the `*.pages.dev` URL. Do not continue until they confirm the site loads there.
- [ ] **Step 3: Verify** with `curl -s -o /dev/null -w '%{http_code}'` that `<pages.dev>/`, `/news.html`, `/news-founding.html`, `/static/css/style.css` return 200 (or 308→200 for `.html`).
- [ ] **Step 4: Cut over:** set `SITE_URL = "<pages.dev URL>"`; replace `pages.yml` with `ci.yml` (on push/PR to main: checkout, setup-python 3.13, `python -m unittest discover -s tests -v`); run full suite; commit — `chore: move hosting to Cloudflare Pages`; push (user approved publishing in Step 2).
- [ ] **Step 5: Disable GitHub Pages** — `gh api -X DELETE repos/koheiyamaguchi-lang/leadjapan-hp/pages`; confirm the Cloudflare site shows `og:url` on an article page.
