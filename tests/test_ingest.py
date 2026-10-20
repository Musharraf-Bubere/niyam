import hashlib
from datetime import date
from pathlib import Path

import pytest

from niyam.ingestion.ingest import EmptyDocumentError, ingest_file
from niyam.ingestion.manifest import DocumentStatus, ManifestEntry, Regulator
from niyam.ingestion.status import StatusConflictError
from niyam.ingestion.types import BlockKind, ParsedBlock

PDF_BYTES = b"fake pdf bytes"


class FakeParser:
    """Returns fixed blocks, so tests need no real PDF and no PyTorch."""

    def __init__(self, blocks: list[ParsedBlock]) -> None:
        self.blocks = blocks

    def parse(self, path: Path) -> list[ParsedBlock]:
        return self.blocks


def make_entry(status: DocumentStatus = DocumentStatus.ACTIVE) -> ManifestEntry:
    return ManifestEntry(
        file="a.pdf",
        regulator=Regulator.RBI,
        circular_number="RBI/1",
        title="Master Direction",
        issue_date=date(2016, 2, 25),
        status=status,
        source_url="https://example.org/a",
    )


def make_file(tmp_path: Path, name: str = "a.pdf", content: bytes = PDF_BYTES) -> Path:
    path = tmp_path / name
    path.write_bytes(content)
    return path


def block(kind: BlockKind, text: str, page: int = 1) -> ParsedBlock:
    return ParsedBlock(kind=kind, text=text, page_number=page)


def test_ingest_cleans_chunks_and_fingerprints_the_file(tmp_path: Path) -> None:
    parser = FakeParser(
        [
            block(BlockKind.HEADING, "KYC norms"),
            block(BlockKind.TEXT, "<!-- image -->"),
            block(BlockKind.TEXT, "Verify identity.", page=2),
        ]
    )
    result = ingest_file(make_file(tmp_path), make_entry(), parser)
    assert result.entry == make_entry()
    assert result.content_hash == hashlib.sha256(PDF_BYTES).hexdigest()
    assert len(result.chunks) == 1
    assert result.chunks[0].section == "KYC norms"
    assert result.chunks[0].page_number == 2
    assert result.chunks[0].text == "Verify identity."
    assert result.warnings == []


def test_same_content_gives_the_same_hash_whatever_the_file_name(tmp_path: Path) -> None:
    parser = FakeParser([block(BlockKind.TEXT, "Text.")])
    first = ingest_file(make_file(tmp_path, "one.pdf"), make_entry(), parser)
    second = ingest_file(make_file(tmp_path, "two.pdf"), make_entry(), parser)
    assert first.content_hash == second.content_hash


def test_active_document_with_a_watermark_is_refused(tmp_path: Path) -> None:
    parser = FakeParser([block(BlockKind.TEXT, "Withdrawn"), block(BlockKind.TEXT, "Text.")])
    with pytest.raises(StatusConflictError):
        ingest_file(make_file(tmp_path), make_entry(DocumentStatus.ACTIVE), parser)


def test_withdrawn_without_watermark_is_ingested_with_a_warning(tmp_path: Path) -> None:
    parser = FakeParser([block(BlockKind.TEXT, "Text.")])
    result = ingest_file(make_file(tmp_path), make_entry(DocumentStatus.WITHDRAWN), parser)
    assert len(result.chunks) == 1
    assert len(result.warnings) == 1


def test_a_document_with_no_usable_text_is_an_error(tmp_path: Path) -> None:
    parser = FakeParser([block(BlockKind.TEXT, "<!-- image -->")])
    with pytest.raises(EmptyDocumentError):
        ingest_file(make_file(tmp_path), make_entry(), parser)
