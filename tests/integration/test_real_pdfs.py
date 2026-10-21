import os
from pathlib import Path

import pytest

from niyam.ingestion.ingest import ingest_file
from niyam.ingestion.manifest import ManifestEntry, load_manifest
from niyam.ingestion.types import DocumentParser

ROOT = Path(__file__).resolve().parents[2]
ENTRIES = load_manifest(ROOT / "data" / "manifest.csv")

pytestmark = pytest.mark.skipif(
    os.environ.get("NIYAM_RUN_SLOW") != "1",
    reason="Slow: parses real PDFs with Docling. Set NIYAM_RUN_SLOW=1 to run.",
)


@pytest.fixture(scope="module")
def parser() -> DocumentParser:
    pytest.importorskip("docling")
    from niyam.ingestion.docling_parser import DoclingParser

    return DoclingParser()


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda entry: entry.file)
def test_real_pdf_ingests_cleanly(entry: ManifestEntry, parser: DocumentParser) -> None:
    path = ROOT / "data" / "raw" / entry.file
    if not path.exists():
        pytest.skip(f"{entry.file} is not in data/raw")
    result = ingest_file(path, entry, parser)
    assert result.chunks
    assert result.warnings == []
    for chunk in result.chunks:
        assert chunk.page_number >= 1
        assert "<!-- image -->" not in chunk.text
        assert chunk.text.strip().lower() != "withdrawn"
