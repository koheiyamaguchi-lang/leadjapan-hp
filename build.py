"""Static site build: python3 build.py -> site/"""
from __future__ import annotations

import pathlib
import shutil

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


def main() -> None:
    written = build(ROOT / "site")
    total = 0
    files = []
    for p in written:
        n = find_placeholders(p.read_text(encoding="utf-8"))
        if n:
            total += n
            files.append(p.name)
    print(f"{len(written)} ページを site/ に生成しました")
    if total:
        print(f"警告: 【要入力】 が {total} 箇所残っています ({', '.join(files)})")


if __name__ == "__main__":
    main()
