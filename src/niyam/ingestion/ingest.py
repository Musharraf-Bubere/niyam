"""Turn one circular file into chunks ready to be embedded and stored."""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from niyam.ingestion.chunking import TextChunk, chunk_blocks
from niyam.ingestion.cleaning import clean_blocks
from niyam.ingestion.manifest import ManifestEntry
from niyam.ingestion.status import check_status
from niyam.ingestion.types import DocumentParser


class EmptyDocumentError(Exception):
    """The parser found no usable text in the document."""


@dataclass(frozen=True)
class IngestedDocument:
    """Everything the storage step needs: the manifest entry, a file fingerprint and the chunks."""

    entry: ManifestEntry
    content_hash: str
    chunks: list[TextChunk]
    warnings: list[str]


def ingest_file(path: Path, entry: ManifestEntry, parser: DocumentParser) -> IngestedDocument:
    cleaned = clean_blocks(parser.parse(path))
    warnings = check_status(entry.status, cleaned.watermark_pages)
    chunks = chunk_blocks(cleaned.blocks)
    if not chunks:
        raise EmptyDocumentError(f"no usable text found in {path.name}")
    return IngestedDocument(
        entry=entry,
        content_hash=_sha256(path),
        chunks=chunks,
        warnings=warnings,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for piece in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(piece)
    return digest.hexdigest()
