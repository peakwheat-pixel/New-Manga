"""FEA-14-AI-1: prompt templates over schema v14 (additive)."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.ai.prompt_templates import (  # noqa: E402
    BUILTIN_PROMPT_TEMPLATES,
    PromptTemplateError,
    PromptTemplateService,
)
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.prompt_templates import SqlitePromptTemplateStore  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version


def _service(tmp_path: Path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    return conn, PromptTemplateService(SqlitePromptTemplateStore(conn))


def test_v14_adds_prompt_templates_and_keeps_legacy_rows(tmp_path):
    conn = sqlite3.connect(tmp_path / "library.db")
    conn.row_factory = sqlite3.Row
    MigrationRunner(conn, MIGRATIONS[:-1]).apply_pending()
    assert read_schema_version(conn) == LATEST - 1 == 13
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('legacy-b', 'Legacy', '2026-01-01', '2026-01-01')"
    )
    conn.commit()
    rows_before = [tuple(row) for row in conn.execute("SELECT * FROM books ORDER BY rowid")]
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert read_schema_version(conn) == LATEST == 14
    tables = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"prompt_templates", "prompt_template_references"} <= tables
    indexes = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    assert {"idx_prompt_templates_name", "idx_prompt_template_references_template"} <= indexes
    assert [tuple(row) for row in conn.execute("SELECT * FROM books ORDER BY rowid")] == rows_before
    assert conn.execute("SELECT COUNT(*) FROM prompt_templates").fetchone()[0] == 0


def test_list_has_builtins_and_user_templates(tmp_path):
    conn, service = _service(tmp_path)
    templates, builtin_count = service.list_templates()
    assert builtin_count == len(BUILTIN_PROMPT_TEMPLATES)
    assert [item["builtin"] for item in templates[:builtin_count]] == [True] * builtin_count
    assert {item["template_id"] for item in templates} == {
        item.template_id for item in BUILTIN_PROMPT_TEMPLATES
    }

    created = service.save_template("My template", "Translate carefully.")
    templates, builtin_count = service.list_templates()
    assert templates[-1] == {
        "template_id": created.template_id,
        "name": "My template",
        "version": 1,
        "builtin": False,
    }
    assert builtin_count == len(BUILTIN_PROMPT_TEMPLATES)


def test_save_versions_and_name_uniqueness(tmp_path):
    conn, service = _service(tmp_path)
    created = service.save_template("Mine", "v1 body")
    assert created.version == 1
    updated = service.save_template("Mine renamed", "v2 body", created.template_id)
    assert updated.template_id == created.template_id
    assert updated.version == 2 and updated.name == "Mine renamed"

    other = service.save_template("Other", "body")
    with pytest.raises(PromptTemplateError) as caught:
        service.save_template("Other", "body")
    assert caught.value.code == "TEMPLATE_NAME_EXISTS"
    with pytest.raises(PromptTemplateError) as caught:
        service.save_template("Other", "body", created.template_id)
    assert caught.value.code == "TEMPLATE_NAME_EXISTS"

    for bad in (("", "body"), ("name", " ")):
        with pytest.raises(PromptTemplateError) as caught:
            service.save_template(*bad)
        assert caught.value.code == "INVALID_REQUEST"
    with pytest.raises(PromptTemplateError) as caught:
        service.save_template("name", "x" * 20001)
    assert caught.value.code == "INVALID_REQUEST"

    # builtin ids are read-only
    builtin_id = BUILTIN_PROMPT_TEMPLATES[0].template_id
    with pytest.raises(PromptTemplateError) as caught:
        service.save_template("Hijack", "body", builtin_id)
    assert caught.value.code == "INVALID_REQUEST"


def test_copy_builtin_and_delete_with_replacement(tmp_path):
    conn, service = _service(tmp_path)
    builtin = BUILTIN_PROMPT_TEMPLATES[0]
    copied = service.copy_builtin(builtin.template_id)
    assert copied.name == f"{builtin.name} (copy)"
    assert copied.version == 1 and copied.body == builtin.body

    named = service.copy_builtin(builtin.template_id, "Explicit copy")
    assert named.name == "Explicit copy"
    with pytest.raises(PromptTemplateError) as caught:
        service.copy_builtin(builtin.template_id, "Explicit copy")
    assert caught.value.code == "TEMPLATE_NAME_EXISTS"
    with pytest.raises(PromptTemplateError) as caught:
        service.copy_builtin("missing-builtin")
    assert caught.value.code == "TARGET_NOT_FOUND"

    replacement = service.copy_builtin(builtin.template_id, "Replacement")
    # reference fixture: the AI-2/UI cards write these rows; delete must reassign.
    with conn:
        conn.execute(
            "INSERT INTO prompt_template_references (template_id, kind, owner_id, label)"
            " VALUES (?, 'translation', 'owner-1', 'Chapter 1')",
            (copied.template_id,),
        )
    references = service.list_references(copied.template_id)
    assert [(ref.kind, ref.owner_id, ref.label) for ref in references] == [
        ("translation", "owner-1", "Chapter 1")
    ]

    for bad_replacement in ("", copied.template_id, builtin.template_id):
        with pytest.raises(PromptTemplateError) as caught:
            service.delete_template(copied.template_id, bad_replacement)
        assert caught.value.code in {"INVALID_REQUEST", "TARGET_NOT_FOUND"}
    with pytest.raises(PromptTemplateError) as caught:
        service.delete_template(copied.template_id, "missing-template")
    assert caught.value.code == "TARGET_NOT_FOUND"
    with pytest.raises(PromptTemplateError) as caught:
        service.delete_template(builtin.template_id, replacement.template_id)
    assert caught.value.code == "INVALID_REQUEST"

    assert service.delete_template(copied.template_id, replacement.template_id) is True
    visible, _ = service.list_templates()
    visible_ids = {item["template_id"] for item in visible}
    assert copied.template_id not in visible_ids
    # the reference row moved to the replacement in the same delete.
    assert service.list_references(replacement.template_id)[0].label == "Chapter 1"
    # a soft-deleted template is gone for the reference face too.
    with pytest.raises(PromptTemplateError) as caught:
        service.list_references(copied.template_id)
    assert caught.value.code == "TARGET_NOT_FOUND"
    with pytest.raises(PromptTemplateError) as caught:
        service.delete_template(copied.template_id, replacement.template_id)
    assert caught.value.code == "TARGET_NOT_FOUND"


def test_delete_without_references_still_requires_replacement(tmp_path):
    conn, service = _service(tmp_path)
    first = service.save_template("First", "body")
    second = service.save_template("Second", "body")
    assert service.delete_template(first.template_id, second.template_id) is True
    visible, _ = service.list_templates()
    assert {item["template_id"] for item in visible} >= {second.template_id}
