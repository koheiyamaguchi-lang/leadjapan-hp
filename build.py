"""Static site build: python3 build.py -> site/"""
from __future__ import annotations

import pathlib
import shutil

from sitegen.content import UNCONFIRMED
from sitegen.pages import PAGES
from sitegen.render import find_placeholders, render_layout

ROOT = pathlib.Path(__file__).resolve().parent
STATIC = ROOT / "static"


def build(out_dir: pathlib.Path) -> list[pathlib.Path]:
    out_dir = pathlib.Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    written: list[pathlib.Path] = []
    for page in PAGES:
        html = render_layout(
            title=page.title,
            description=page.description,
            body=page.body(),
            current=page.filename,
        )
        path = out_dir / page.filename
        path.write_text(html, encoding="utf-8")
        written.append(path)
    if STATIC.exists():
        shutil.copytree(STATIC, out_dir / "static")
    return written


def placeholder_report(paths: list[pathlib.Path]) -> dict[str, int]:
    """filename -> count of 【要入力】 markers, only for files with at least one."""
    report: dict[str, int] = {}
    for p in paths:
        n = find_placeholders(pathlib.Path(p).read_text(encoding="utf-8"))
        if n:
            report[pathlib.Path(p).name] = n
    return report


def format_warnings(report: dict[str, int], unconfirmed: tuple[str, ...] = UNCONFIRMED) -> str:
    lines: list[str] = []
    total = sum(report.values())
    if total:
        lines.append(f"警告: 【要入力】 が {total} 箇所残っています ({', '.join(report)})")
    if unconfirmed:
        lines.extend(f"要確認: {item}" for item in unconfirmed)
    return "\n".join(lines)


def main() -> None:
    written = build(ROOT / "site")
    print(f"{len(written)} ページを site/ に生成しました")
    warnings = format_warnings(placeholder_report(written))
    if warnings:
        print(warnings)


if __name__ == "__main__":
    main()
