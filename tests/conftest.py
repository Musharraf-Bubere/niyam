import os
from pathlib import Path

import pytest


@pytest.fixture
def no_env_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate settings: no .env file in sight and no NIYAM_* environment variables."""
    monkeypatch.chdir(tmp_path)
    for name in list(os.environ):
        if name.startswith("NIYAM_"):
            monkeypatch.delenv(name)
