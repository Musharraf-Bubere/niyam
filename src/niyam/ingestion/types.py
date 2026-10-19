"""Types shared by every document parser."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Protocol


class BlockKind(StrEnum):
    HEADING = "heading"
    TEXT = "text"
    TABLE = "table"


@dataclass(frozen=True)
class ParsedBlock:
    """One piece of a parsed document, tied to the page it came from."""

    kind: BlockKind
    text: str
    page_number: int

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError(f"page_number must be at least 1, got {self.page_number}")
        if not self.text.strip():
            raise ValueError("text must not be blank")


class DocumentParser(Protocol):
    """Anything that turns a file into blocks. Docling is one implementation; a fake is another."""

    def parse(self, path: Path) -> list[ParsedBlock]: ...
