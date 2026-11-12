"""Synthetic observations of the production translation-context boundary.

No API, user database, or manga material is read. These tests characterize
which metadata the current handler passes into a frozen provider request.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from dataclasses import make_dataclass
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[3] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.providers.translation_openai import OpenAiTranslationProvider
from infrastructure.sqlite.pipeline import SqliteTargetCatalog
from ports.translation.protocol import ContextPage, RegionInput, TranslationRequestPayload


def test_sqlite_frozen_context_uses_nearest_pages_from_the_same_chapter():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(
        """
        CREATE TABLE pages (
            page_id TEXT, chapter_id TEXT, sort_order INTEGER, deleted_at TEXT
        );
        CREATE TABLE regions (
            region_id TEXT, page_id TEXT, current_revision_id TEXT,
            text_json TEXT, deleted_at TEXT, reading_order INTEGER
        );
        """
    )
    pages = (
        ("chapter-a-far-before", "chapter-a", 10),
        ("chapter-a-before", "chapter-a", 19),
        ("chapter-a-target", "chapter-a", 20),
        ("chapter-a-after", "chapter-a", 21),
        ("chapter-a-far-after", "chapter-a", 30),
        ("chapter-b-near", "chapter-b", 20),
    )
    connection.executemany(
        "INSERT INTO pages(page_id, chapter_id, sort_order, deleted_at) VALUES (?, ?, ?, NULL)",
        pages,
    )
    for page_id, _, sort_order in pages:
        connection.execute(
            "INSERT INTO regions(region_id, page_id, current_revision_id, text_json, deleted_at, reading_order) "
            "VALUES (?, ?, ?, ?, NULL, 1)",
            (f"region-{page_id}", page_id, f"revision-{page_id}",
             json.dumps({"ocr_text": f"synthetic text for {page_id}"})),
        )

    Target = make_dataclass(
        "Target", ["page_id", "chapter_id", "page_order", "metadata"]
    )
    target = Target(
        page_id="chapter-a-target",
        chapter_id="chapter-a",
        page_order=20,
        metadata={"preserved": "yes"},
    )
    frozen = SqliteTargetCatalog(connection).freeze_context((target,), window=2)[0]

    contexts = frozen.metadata["context_pages"]
    assert [(item["page_id"], item["position"]) for item in contexts] == [
        ("chapter-a-before", "before"),
        ("chapter-a-after", "after"),
    ]
    assert all("chapter-b" not in item["page_id"] for item in contexts)
    assert frozen.metadata["preserved"] == "yes"
    connection.close()


def test_translation_wire_request_carries_page_context_without_work_or_chapter_ids():
    payload = TranslationRequestPayload(
        page_id="page-a-7",
        regions=(RegionInput("region-a-7", "synthetic source", "sfx"),),
        context=(ContextPage("page-a-6", "before", "synthetic neighboring text", 6),),
        glossary={"synthetic source": "synthetic target"},
    )
    provider = object.__new__(OpenAiTranslationProvider)
    provider.target_language = "zh-CN"
    user_text = OpenAiTranslationProvider._build_user_text(provider, payload)
    request = json.loads(user_text)

    assert request["page_id"] == "page-a-7"
    assert request["context"][0]["page_id"] == "page-a-6"
    assert request["glossary"] == {"synthetic source": "synthetic target"}
    assert "book_id" not in request
    assert "chapter_id" not in request
