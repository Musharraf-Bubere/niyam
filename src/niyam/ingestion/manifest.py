"""Read and validate data/manifest.csv, the source of truth for each circular."""

import csv
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from pathlib import Path


class Regulator(StrEnum):
    RBI = "RBI"
    SEBI = "SEBI"


class DocumentStatus(StrEnum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True)
class ManifestEntry:
    file: str
    regulator: Regulator
    circular_number: str
    title: str
    issue_date: date
    status: DocumentStatus
    source_url: str


_COLUMNS = ("file", "regulator", "circular_number", "title", "issue_date", "status", "source_url")


def load_manifest(path: Path) -> list[ManifestEntry]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        present = reader.fieldnames or []
        missing = [name for name in _COLUMNS if name not in present]
        if missing:
            raise ValueError(f"manifest is missing columns: {', '.join(missing)}")
        entries = [_parse_row(row, line) for line, row in enumerate(reader, start=2)]
    _reject_duplicates(entries)
    return entries


def _parse_row(row: dict[str, str], line: int) -> ManifestEntry:
    return ManifestEntry(
        file=_field(row, "file", line, _non_blank),
        regulator=_field(row, "regulator", line, Regulator),
        circular_number=_field(row, "circular_number", line, _non_blank),
        title=_field(row, "title", line, _non_blank),
        issue_date=_field(row, "issue_date", line, date.fromisoformat),
        status=_field(row, "status", line, DocumentStatus),
        source_url=_field(row, "source_url", line, _non_blank),
    )


def _field[T](row: dict[str, str], name: str, line: int, convert: Callable[[str], T]) -> T:
    raw = (row.get(name) or "").strip()
    try:
        return convert(raw)
    except ValueError as error:
        raise ValueError(f"manifest line {line}: invalid {name} {raw!r} ({error})") from error


def _non_blank(value: str) -> str:
    if not value:
        raise ValueError("must not be blank")
    return value


def _reject_duplicates(entries: list[ManifestEntry]) -> None:
    seen: set[str] = set()
    for entry in entries:
        if entry.circular_number in seen:
            raise ValueError(f"duplicate circular_number {entry.circular_number!r}")
        seen.add(entry.circular_number)
