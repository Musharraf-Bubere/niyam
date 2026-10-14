import json
from collections.abc import Iterator

import pytest
import structlog

from niyam.core.logging_config import configure_logging


@pytest.fixture(autouse=True)
def reset_struclog() -> Iterator[None]:
    yield
    structlog.reset_defaults()


def test_messages_below_level_are_dropped(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO")
    log = structlog.get_logger()
    log.info("app_started")
    log.debug("hidden_at_info")
    output = capsys.readouterr().out
    assert "app_started" in output
    assert "hidden_at_info" not in output


def test_json_logs_are_parseable_with_expected_fields(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("DEBUG", json_logs=True)
    log = structlog.get_logger()
    log.info("app_started", component="demo")
    record = json.loads(capsys.readouterr().out)
    assert record["event"] == "app_started"
    assert record["level"] == "info"
    assert record["component"] == "demo"
    assert "timestamp" in record
