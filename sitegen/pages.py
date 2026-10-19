"""Page registry. PAGES is filled by later tasks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Page:
    filename: str
    title: str
    description: str
    body: Callable[[], str]


PAGES: list[Page] = []
