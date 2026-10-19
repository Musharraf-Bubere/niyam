"""Turn parsed blocks into chunks sized for embedding and citation."""

from dataclasses import dataclass

from niyam.ingestion.types import BlockKind, ParsedBlock

DEFAULT_MAX_CHARS = 1200
_JOINER = "\n\n"


@dataclass(frozen=True)
class TextChunk:
    """One passage ready to be embedded. Matches the chunks table, minus embedding and document."""

    chunk_index: int
    page_number: int
    section: str | None
    text: str


def chunk_blocks(blocks: list[ParsedBlock], max_chars: int = DEFAULT_MAX_CHARS) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    section: str | None = None
    pending: list[ParsedBlock] = []

    def flush() -> None:
        if not pending:
            return
        chunks.append(
            TextChunk(
                chunk_index=len(chunks),
                page_number=pending[0].page_number,
                section=section,
                text=_JOINER.join(block.text for block in pending),
            )
        )
        pending.clear()

    for block in blocks:
        if block.kind is BlockKind.HEADING:
            flush()
            section = block.text
        elif block.kind is BlockKind.TABLE:
            flush()
            pending.append(block)
            flush()
        else:
            if pending and _size(pending) + len(_JOINER) + len(block.text) > max_chars:
                flush()
            pending.append(block)
    flush()
    return chunks


def _size(blocks: list[ParsedBlock]) -> int:
    return len(_JOINER.join(block.text for block in blocks))
