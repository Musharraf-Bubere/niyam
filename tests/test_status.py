import pytest

from niyam.ingestion.manifest import DocumentStatus
from niyam.ingestion.status import StatusConflictError, check_status


def test_active_without_watermark_is_consistent() -> None:
    assert check_status(DocumentStatus.ACTIVE, []) == []


def test_withdrawn_with_watermark_is_consistent() -> None:
    assert check_status(DocumentStatus.WITHDRAWN, [1, 2]) == []


def test_active_with_watermark_stops_ingestion() -> None:
    with pytest.raises(StatusConflictError, match="active"):
        check_status(DocumentStatus.ACTIVE, [1])


def test_withdrawn_without_watermark_gives_a_warning() -> None:
    warnings = check_status(DocumentStatus.WITHDRAWN, [])
    assert len(warnings) == 1
    assert "withdrawn" in warnings[0]
