"""Pytest fixtures for the provider suite.

The shared doubles moved to :mod:`providers_helpers` (TASK-034 AC ④, closing
TASK-035 R-02) so that a bare ``conftest`` module name can no longer collide
with ``tests/editing/conftest.py`` when both directories are collected in one
pytest invocation. Only pytest-injectable fixtures stay here.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from providers_helpers import FakeTransport  # noqa: E402


@pytest.fixture()
def fake_transport() -> FakeTransport:
    return FakeTransport()


@pytest.fixture()
def credential_resolver() -> Callable[[str], str | None]:
    secrets = {"provider-ref": "unit-test-secret"}
    return secrets.get
