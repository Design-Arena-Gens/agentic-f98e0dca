from __future__ import annotations

from typing import Iterable, List


def human_join(parts: Iterable[str]) -> str:
    items: List[str] = [part for part in parts if part]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" & {items[-1]}"
