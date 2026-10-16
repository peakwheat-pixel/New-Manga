"""Run pytest with per-test temporary folders inside the writable worktree."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys

import pytest


WORKSPACE = Path(__file__).resolve().parents[2]
TEMP_ROOT = WORKSPACE / "verification" / "P09" / "test-runs" / f"run-{os.getpid()}"


class WorkspaceTempPlugin:
    @pytest.fixture
    def tmp_path(self, request: pytest.FixtureRequest) -> Path:
        name = hashlib.sha256(request.node.nodeid.encode("utf-8")).hexdigest()[:16]
        path = TEMP_ROOT / name
        path.mkdir(parents=True, exist_ok=True)
        return path


if __name__ == "__main__":
    raise SystemExit(
        pytest.main(
            ["-p", "no:cacheprovider", *sys.argv[1:]],
            plugins=[WorkspaceTempPlugin()],
        )
    )
