from pathlib import Path

import pytest


@pytest.fixture
def no_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run from an empty folder so the real .env file is never read."""
    monkeypatch.chdir(tmp_path)
