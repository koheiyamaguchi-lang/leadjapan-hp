from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal, Protocol

from django.utils import timezone

from sitegen import content

from .export import IMAGE_DIR, ExportError, export_published

NEWS_JSON = "content/news.json"
COMMIT_PATHS = ["content", IMAGE_DIR]
FALLBACK_URL = "https://koheiyamaguchi-lang.github.io/leadjapan-hp/"


class GitError(Exception):
    pass


@dataclass
class PublishResult:
    status: Literal["published", "no_changes", "tests_failed", "push_failed", "blocked"]
    message: str
    url: str | None = None
    output: str = ""


class Git(Protocol):
    def current_branch(self) -> str: ...
    def has_changes(self, paths: list[str]) -> bool: ...
    def commit(self, paths: list[str], message: str) -> None: ...
    def push(self) -> None: ...


class SubprocessGit:
    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    def _run(self, *args: str, timeout: int = 120) -> str:
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        try:
            p = subprocess.run(["git", *args], cwd=self.repo_root, capture_output=True, text=True,
                               timeout=timeout, env=env)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise GitError(f"git {args[0]}: {e}") from e
        if p.returncode != 0:
            raise GitError((p.stderr or p.stdout).strip() or f"git {args[0]} failed ({p.returncode})")
        return p.stdout

    def current_branch(self) -> str:
        return self._run("rev-parse", "--abbrev-ref", "HEAD").strip()

    def has_changes(self, paths: list[str]) -> bool:
        return bool(self._run("status", "--porcelain", "--", *paths).strip())

    def commit(self, paths: list[str], message: str) -> None:
        self._run("add", "-A", "--", *paths)
        self._run("commit", "-m", message, "--", *paths)

    def push(self) -> None:
        self._run("push", "origin", "main", timeout=120)


def run_site_tests(repo_root: Path) -> tuple[bool, str]:
    p = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                       cwd=repo_root, capture_output=True, text=True)
    out = "\n".join(((p.stdout or "") + (p.stderr or "")).splitlines()[-40:])
    return p.returncode == 0, out


class _Snapshot:
    def __init__(self, repo_root: Path, tmp: Path):
        self.news = repo_root / NEWS_JSON
        self.imgs = repo_root / IMAGE_DIR
        self.saved_news = tmp / "news.json"
        self.saved_imgs = tmp / "img"
        self.had_news = self.news.exists()
        self.had_imgs = self.imgs.exists()
        if self.had_news:
            shutil.copy2(self.news, self.saved_news)
        if self.had_imgs:
            shutil.copytree(self.imgs, self.saved_imgs)

    def restore(self) -> None:
        if self.had_news:
            self.news.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.saved_news, self.news)
        else:
            self.news.unlink(missing_ok=True)
        if self.imgs.exists():
            shutil.rmtree(self.imgs)
        if self.had_imgs:
            shutil.copytree(self.saved_imgs, self.imgs)


def publish(repo_root: Path, *, git: Git | None = None,
            run_tests: Callable[[Path], tuple[bool, str]] = run_site_tests,
            now: Callable[[], datetime] = timezone.localtime) -> PublishResult:
    repo_root = Path(repo_root)
    git = git or SubprocessGit(repo_root)

    try:
        branch = git.current_branch()
    except GitError as e:
        return PublishResult("blocked", f"ブランチを確認できません: {e}")
    if branch != "main":
        return PublishResult("blocked", f"main ブランチで実行してください（現在: {branch}）")

    with tempfile.TemporaryDirectory() as tmp:
        snap = _Snapshot(repo_root, Path(tmp))
        try:
            try:
                export_published(repo_root)
            except ExportError as e:
                snap.restore()
                return PublishResult("blocked", str(e))
            ok, output = run_tests(repo_root)
            if not ok:
                snap.restore()
                return PublishResult("tests_failed", "テストが失敗したため反映を中止しました", output=output)
            if not git.has_changes(COMMIT_PATHS):
                return PublishResult("no_changes", "変更はありません")
            git.commit(COMMIT_PATHS, f"news: サイトに反映 ({now():%Y-%m-%d %H:%M})")
        except GitError as e:
            snap.restore()
            return PublishResult("blocked", f"コミットに失敗しました: {e}")
        except BaseException:
            snap.restore()
            raise

    try:
        git.push()
    except GitError as e:
        return PublishResult(
            "push_failed",
            f"GitHub への送信に失敗しました（コミットは保存済み。次回の反映で送信されます）: {e}")
    url = content.SITE_URL or FALLBACK_URL
    return PublishResult("published", f"数分でサイトに反映されます: {url}", url)
