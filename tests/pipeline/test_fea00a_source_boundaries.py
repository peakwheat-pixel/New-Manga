"""Static AC4 pins for prepare/live-write ownership boundaries."""

from __future__ import annotations

import inspect
import re

from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter


def test_region_prepare_only_inserts_a_prepared_candidate() -> None:
    source = inspect.getsource(RegionStepWriter._persist)
    assert "INSERT INTO step_result_candidates" in source
    assert "status" in source and "'prepared'" in source
    assert not re.search(
        r"\b(?:INSERT\s+INTO\s+region_revisions|UPDATE\s+regions)\b",
        source,
        flags=re.IGNORECASE,
    )


def test_artifact_prepare_has_no_live_database_or_publish_write() -> None:
    source = inspect.getsource(ArtifactStepWriter.prepare_revision)
    assert "write_temp(" in source
    assert "verify_temp(" in source
    for forbidden in (
        r"\bINSERT\s+INTO\s+media_artifacts\b",
        r"\bUPDATE\s+media_artifacts\b",
        r"\bINSERT\s+INTO\s+artifact_revisions\b",
        r"\bstorage\.publish\s*\(",
    ):
        assert not re.search(forbidden, source, flags=re.IGNORECASE)
    assert "INSERT INTO step_result_candidates" in source
    for field in (
        "temp_handle",
        "relative_path",
        "artifact_type",
        "page_id",
        "book_id",
        "chapter_id",
        "base_revision_id",
        "sha256",
        "size",
        "mime_type",
        "content_format",
    ):
        assert f'"{field}"' in source
    assert '"revision_no"' not in source
