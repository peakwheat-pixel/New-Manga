"""Fixtures for the editing suite."""

from __future__ import annotations

import pytest

import region_helpers  # noqa: F401  (injects src into sys.path first)
from application.editing.service import RegionEditingService

from region_helpers import InMemoryRegionRepository


@pytest.fixture()
def repo() -> InMemoryRegionRepository:
    return InMemoryRegionRepository()


@pytest.fixture()
def service(repo) -> RegionEditingService:
    return RegionEditingService(repo)


@pytest.fixture()
def page_id() -> str:
    return "page-0001"
