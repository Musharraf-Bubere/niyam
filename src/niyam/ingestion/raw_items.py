"""Plain items read from a parser result, and the rules that turn them into ParsedBlocks."""

from collections.abc import Iterable
from dataclasses import dataclass

from niyam.ingestion.types import BlockKind, ParsedBlock

# Labels that are known noise. Everything else is kept, so new labels never silently delete content.
_SKIPPED_LABELS = frozenset({"picture", "page_header", "page_footer", "document_index"})
_HEADING_LABELS = frozenset({"section_header", "title"})
_TABLE_LABELS = frozenset({"table"})


@dataclass(frozen=True)
class RawItem:
    """One item from a parser, reduced to the three facts we use."""

    label: str
    text: str
    page_number: int | None


def blocks_from_items(items: Iterable[RawItem]) -> list[ParsedBlock]:
    blocks: list[ParsedBlock] = []
    for item in items:
        if item.label in _SKIPPED_LABELS or item.page_number is None:
            continue
        text = item.text.strip()
        if not text:
            continue
        blocks.append(
            ParsedBlock(kind=_kind_for(item.label), text=text, page_number=item.page_number)
        )
    return blocks


def _kind_for(label: str) -> BlockKind:
    if label in _HEADING_LABELS:
        return BlockKind.HEADING
    if label in _TABLE_LABELS:
        return BlockKind.TABLE
    return BlockKind.TEXT
