from datetime import date
from pathlib import Path

import pytest

from niyam.ingestion.manifest import DocumentStatus, ManifestEntry, Regulator, load_manifest

HEADER = "file,regulator,circular_number,title,issue_date,status,source_url\n"
ROW = 'a.pdf,RBI,RBI/1,"Master Direction - KYC, 2016",2016-02-25,active,https://example.org/a\n'


def write(tmp_path: Path, *rows: str) -> Path:
    path = tmp_path / "manifest.csv"
    path.write_text(HEADER + "".join(rows), encoding="utf-8")
    return path


def test_reads_a_valid_row(tmp_path: Path) -> None:
    entries = load_manifest(write(tmp_path, ROW))
    assert entries == [
        ManifestEntry(
            file="a.pdf",
            regulator=Regulator.RBI,
            circular_number="RBI/1",
            title="Master Direction - KYC, 2016",
            issue_date=date(2016, 2, 25),
            status=DocumentStatus.ACTIVE,
            source_url="https://example.org/a",
        )
    ]


def test_unknown_status_is_rejected(tmp_path: Path) -> None:
    row = ROW.replace(",active,", ",draft,")
    with pytest.raises(ValueError, match="status"):
        load_manifest(write(tmp_path, row))


def test_unknown_regulator_is_rejected(tmp_path: Path) -> None:
    row = ROW.replace("a.pdf,RBI,", "a.pdf,IRDAI,")
    with pytest.raises(ValueError, match="regulator"):
        load_manifest(write(tmp_path, row))


def test_bad_date_is_rejected(tmp_path: Path) -> None:
    row = ROW.replace("2016-02-25", "25/02/2016")
    with pytest.raises(ValueError, match="issue_date"):
        load_manifest(write(tmp_path, row))


def test_duplicate_circular_number_is_rejected(tmp_path: Path) -> None:
    second = ROW.replace("a.pdf", "b.pdf")
    with pytest.raises(ValueError, match="circular_number"):
        load_manifest(write(tmp_path, ROW, second))


def test_missing_column_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "manifest.csv"
    path.write_text("file,regulator\na.pdf,RBI\n", encoding="utf-8")
    with pytest.raises(ValueError, match="columns"):
        load_manifest(path)
