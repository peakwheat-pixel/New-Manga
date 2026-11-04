"""FEA-11 tests: source scan/diff/plan + matching + sync + durable operation.

Shared fixtures build a fully migrated (v8) library with the production
migration runner, a REAL ``SourceReadGrantRegistry`` (HMAC-signed grants,
strict verified reads, real leases) and the production source-sync stack.
All scratch data stays under the isolated FEA-11 workspace root
``G:/CODEX/New Manga.workspace/FEA-11/`` (Appointment hard boundary).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import sqlite3  # noqa: E402

import pytest  # noqa: E402

from application.sources.model import identity_digest_of  # noqa: E402
from infrastructure.resource_channel.source_read_refs import (  # noqa: E402
    SourceReadGrantRegistry,
)
from infrastructure.resource_channel.source_strict_read import (  # noqa: E402
    read_verified_bytes as strict_read_verified_bytes,
)
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from infrastructure.sqlite.source_sync import SourceSyncStore  # noqa: E402
from application.importing.referenced import scanner as referenced_scanner  # noqa: E402

referenced_scanner.install_verified_reader(strict_read_verified_bytes)

#: Isolated workspace root (Appointment §4 hard boundary).
WORKSPACE_ROOT = Path("G:/CODEX/New Manga.workspace/FEA-11")
FIXTURE_ROOT = WORKSPACE_ROOT / "fixtures"

NOW = "2026-11-04T00:00:00.000+00:00"


@pytest.fixture()
def scratch_dir(request) -> Path:
    """Per-test scratch directory inside the isolated FEA-11 root."""
    root = FIXTURE_ROOT / f"{request.node.name}-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


@pytest.fixture()
def conn() -> sqlite3.Connection:
    connection = sqlite3.connect(
        ":memory:", check_same_thread=False, isolation_level=None
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(connection, default_migrations()).apply_pending()
    return connection


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> SqliteLibraryRepository:
    return SqliteLibraryRepository(conn)


@pytest.fixture()
def store(conn: sqlite3.Connection) -> SourceSyncStore:
    return SourceSyncStore(conn)


@pytest.fixture()
def registry() -> SourceReadGrantRegistry:
    return SourceReadGrantRegistry()


@pytest.fixture()
def stack(store, registry, repo):
    from application.sources.ports import build_source_sync_stack

    return build_source_sync_stack(
        store=store, access=registry, repository=repo
    )


@pytest.fixture()
def book_chapter(conn: sqlite3.Connection) -> tuple[str, str]:
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()
    return "b1", "c1"


# ---------------------------------------------------------------------------
# Grant minting (real HMAC-signed payloads against the real registry)
# ---------------------------------------------------------------------------

def file_facts(path: str | Path) -> dict:
    """Host-style physical identity facts for one real file."""
    from application.importing.referenced.identity import normalize_identity

    info = os.stat(path)
    data = Path(path).read_bytes()
    volume_serial, file_id = normalize_identity(info.st_dev, info.st_ino)
    return {
        # C-16/C-17 §5: the single normalized physical identity.
        "volume_serial": volume_serial,
        "file_id": file_id,
        "size": int(info.st_size),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def png_bytes(width: int = 4, height: int = 3, color=(255, 0, 0)) -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (width, height), color).save(buffer, format="PNG")
    return buffer.getvalue()


def write_zip(path: str | Path, members: list[tuple[str, bytes]]) -> Path:
    import zipfile

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w") as archive:
        for name, data in members:
            archive.writestr(name, data)
    return target


def _sign(key: bytes, fields: dict) -> str:
    encoded = json.dumps(
        fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return base64.urlsafe_b64encode(
        hmac.new(key, encoded, hashlib.sha256).digest()
    ).decode().rstrip("=")


def mint_grant(
    registry: SourceReadGrantRegistry,
    *,
    grant_id: str | None = None,
    source_id: str = "s1",
    version: str = "candidate",
    kind: str = "zip",
    entries: list[tuple[str, str, int]] | None = None,
    session_id: str = "sess-fea11-0001",
    registry_id: str = "reg-1",
    generation: int = 1,
    budget: dict | None = None,
    clock: float | None = None,
) -> tuple[str, dict]:
    """Register one real signed source-read grant over real files.

    ``entries`` items are ``(path, locator, ordinal)``; facts are captured
    from the real filesystem. Returns ``(grant_id, facts_of_first_entry)``.
    """
    now = clock if clock is not None else time.time()
    signing_key = secrets_bytes(32)
    grant_id = grant_id or ("grant-" + uuid.uuid4().hex[:16])
    items = []
    facts0 = None
    for index, (path, locator, ordinal) in enumerate(entries or []):
        facts = file_facts(path)
        if facts0 is None:
            facts0 = facts
        items.append(
            {
                "entry_key": f"entry-{index}",
                "locator": locator,
                "ordinal": ordinal,
                "path": str(Path(path).resolve()),
                "facts": facts,
            }
        )
    expires_at = now + 300.0
    payload = {
        "grant_id": grant_id,
        "session_id": session_id,
        "operation": "source-read",
        "scope_class": "user-source",
        "registry_id": registry_id,
        "generation": generation,
        "expires_at": expires_at,
        "budget": budget
        or {
            "max_bytes": 8 * 1024 * 1024,
            "max_decode_bytes": 8 * 1024 * 1024,
            "max_entries": 10000,
        },
        "scope": {
            "source_id": source_id,
            "version": version,
            "rendition": {
                "decoder": kind,
                "scale": 1.0,
                "params_digest": "0" * 64,
            },
            "entries": items,
        },
    }
    signed = dict(payload)
    signed["expires_at"] = f"{expires_at:.6f}"
    payload["signing_key"] = base64.urlsafe_b64encode(signing_key).decode().rstrip("=")
    payload["signature"] = _sign(signing_key, signed)
    registry.register(payload)
    return grant_id, (facts0 or {})


def secrets_bytes(length: int) -> bytes:
    import secrets

    return secrets.token_bytes(length)


# ---------------------------------------------------------------------------
# Source tree builders (real DB rows + real zip files)
# ---------------------------------------------------------------------------

def add_referenced_page(
    conn: sqlite3.Connection,
    page_id: str,
    chapter_id: str,
    book_id: str,
    *,
    order: int,
    source_id: str,
    version_id: str,
    entry_id: str,
    digest: str,
    binding_status: str = "healthy",
    binding_version: int = 1,
    width: int | None = 4,
    height: int | None = 3,
) -> str:
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref,"
        " source_mode, integrity_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, 'referenced',"
        " 'complete')",
        (page_id, chapter_id, order, NOW, NOW, f"{page_id}.png", order, digest,
         10, width, height),
    )
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, authorization_generation, authorized_at, verified_digest,"
        " created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)",
        (f"pb-{page_id}", page_id, book_id, binding_version, source_id,
         entry_id, version_id, binding_status, NOW, digest, NOW, NOW),
    )
    conn.commit()
    return f"pb-{page_id}"


def add_source_tree(
    conn: sqlite3.Connection,
    *,
    source_id: str,
    version_id: str,
    digest: str,
    entries: list[tuple[str, str, str]],  # (entry_id, locator, content_digest)
    volume_serial: int = 7,
    file_id: int = 8,
    legacy_v7_evidence: bool = True,
    registry_id: str = "reg-1",
    generation: int = 1,
) -> str:
    """sources + current location + one version + entries.

    ``legacy_v7_evidence`` writes the honest v7 shape: pixel/orientation
    NULL and (by default) width/height present only when a page was bound.
    """
    conn.execute(
        "INSERT INTO sources (source_id, source_kind, created_at, updated_at)"
        " VALUES (?, 'zip', ?, ?)",
        (source_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_locations (location_id, source_id, registry_id,"
        " authorization_generation, content_digest, volume_serial, file_id,"
        " size_bytes, observed_at, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, 100, ?, ?)",
        (f"sl-{source_id}", source_id, registry_id, generation, digest,
         volume_serial, file_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_versions (version_id, source_id, location_id,"
        " content_digest, size_bytes, observed_at, created_at)"
        " VALUES (?, ?, ?, ?, 100, ?, ?)",
        (version_id, source_id, f"sl-{source_id}", digest, NOW, NOW),
    )
    for ordinal, (entry_id, locator, content_digest) in enumerate(entries):
        conn.execute(
            "INSERT INTO source_entries (source_id, version_id, entry_id,"
            " locator, ordinal, stable_sort_key, content_digest_kind,"
            " content_digest, encoded_digest, size_bytes, width, height,"
            " orientation, decoder_name, decoder_version, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, 'encoded', ?, ?, 9, ?, ?, ?, 'zip',"
            " '1.0', ?)",
            (source_id, version_id, entry_id, locator, ordinal,
             f"{ordinal:08d}", content_digest, content_digest,
             None if legacy_v7_evidence else 5,
             None if legacy_v7_evidence else 5,
             None, NOW),
        )
    conn.commit()
    return f"sl-{source_id}"


def authorization_for(grant_facts: dict, *, registry_id: str = "reg-1",
                      generation: int = 1) -> dict:
    return {
        "registry_id": registry_id,
        "generation": generation,
        "identity_digest": identity_digest_of(
            grant_facts["sha256"],
            grant_facts["volume_serial"],
            grant_facts["file_id"],
            grant_facts["size"],
        ),
    }


def host_authorization(
    *, operation_id: str, request_digest: str, authorizations: list[dict]
) -> dict:
    from application.sources.model import authorization_digest_of, now_millis

    return {
        "host_receipt_id": "host-" + uuid.uuid4().hex[:16],
        "operation_id": operation_id,
        "request_digest": request_digest,
        "authorization_digest": authorization_digest_of(authorizations),
        "authorizations": authorizations,
        "authorized_at": now_millis(),
    }


def build_plan_body(
    scan: dict,
    *,
    kind: str = "resync",
    plan_id: str | None = None,
    decisions: list[dict] | None = None,
    resync_content: bool = True,
    scope: str = "current",
) -> dict:
    """Assemble a PlanBody from a Scan result with explicit decisions."""
    from application.sources.model import now_millis

    if decisions is None:
        decisions = default_decisions(scan)
    return {
        "format": "source-sync-plan/1",
        "plan_id": plan_id or ("plan-" + uuid.uuid4().hex[:16]),
        "scan_id": scan["scan_id"],
        "source_id": scan["source"]["source_id"],
        "kind": kind,
        "project_ids": sorted({base["project_id"] for base in scan["bases"]})
        or ["b1"],
        "scope": scope,
        "base_sources": scan["base_sources"],
        "authorizations": scan["authorizations"],
        "missing": scan["missing"],
        "bases": scan["bases"],
        "target": scan["source"],
        "reference_set_digest": scan["reference_set_digest"],
        "diff": scan["diff"],
        "totals": scan["totals"],
        "decisions": decisions,
        "confirmation": {
            "kind": kind,
            "project_ids": sorted(
                {base["project_id"] for base in scan["bases"]}
            ) or ["b1"],
            "reference_set_digest": scan["reference_set_digest"],
            "resync_content": resync_content,
        },
    }


def default_decisions(scan: dict) -> list[dict]:
    """keep unchanged / bind changed / tombstone missing / add added / defer
    ambiguous (AC11-2: ambiguities always need an explicit user decision)."""
    decisions = []
    for item in scan["diff"]:
        classification = item["classification"]
        decision = {
            "item_id": item["item_id"],
            "action": {
                "unchanged": "keep",
                "added": "add",
                "missing": "tombstone",
                "changed": "bind",
                "ambiguous": "defer",
            }[classification],
            "target_page_id": item["page_id"]
            if classification in ("unchanged", "changed", "missing")
            else None,
            "target_chapter_id": "c1" if classification == "added" else None,
            "new_source_order": None,
            "new_sort_order": None,
            "migrate_revision_ids": [],
        }
        if classification == "added":
            decision["new_source_order"] = 900 + int(item["item_id"][-4:])
            decision["new_sort_order"] = 900 + int(item["item_id"][-4:])
        decisions.append(decision)
    decisions.sort(key=lambda row: row["item_id"])
    return decisions


def run_full_sync(
    stack,
    scan: dict,
    *,
    grant_ids: list[str],
    kind: str = "resync",
    decisions: list[dict] | None = None,
    operation_id: str | None = None,
    command: str = "ResyncSource",
) -> tuple[dict, dict]:
    """plan → preview → confirm → apply, returning (plan, dispatch)."""
    from application.sources.model import (
        plan_digest_of,
        request_digest_of,
    )

    body = build_plan_body(scan, kind=kind, decisions=decisions)
    plan = stack["planner"].create(body)
    stack["planner"].preview({"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]})
    stack["planner"].confirm(
        {
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )
    operation_id = operation_id or ("op-" + uuid.uuid4().hex[:16])
    request_digest = request_digest_of(
        operation_id, body["plan_id"], plan["plan_digest"], kind
    )
    dispatch = stack["service"].apply(
        command,
        {
            "operation_id": operation_id,
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "grant_ids": grant_ids,
            "authorization": host_authorization(
                operation_id=operation_id,
                request_digest=request_digest,
                authorizations=scan["authorizations"],
            ),
        },
    )
    return plan, dispatch
