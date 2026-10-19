from pathlib import Path

from niyam.ingestion.manifest import DocumentStatus, Regulator, load_manifest

MANIFEST = Path(__file__).resolve().parents[1] / "data" / "manifest.csv"


def test_real_manifest_is_valid() -> None:
    by_file = {entry.file: entry for entry in load_manifest(MANIFEST)}
    assert by_file["rbi_kyc_master_direction.pdf"].regulator is Regulator.RBI
    assert by_file["sebi_mf_categorisation_2026.pdf"].regulator is Regulator.SEBI
    assert by_file["rbi_digital_lending_2025.pdf"].status is DocumentStatus.WITHDRAWN
