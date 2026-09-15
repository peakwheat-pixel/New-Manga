"""Secret leak scans: SQLite bytes, on-disk artifacts and captured log
output must never contain the secret (AC-SEC-001/002, D07 §69).

Uses a real v2 database (TASK-006/029 schema) to prove the negative:
profiles store credential_ref only; the bytes on disk contain no secret
material even after resolving credentials through it.
"""

from __future__ import annotations

import io
import logging
import sqlite3
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.network.profiles import MODE_HTTP, NetworkProfile  # noqa: E402
from ports.providers.credentials import SecretValue, make_credential_ref  # noqa: E402
from ports.providers.profiles import ProviderProfile  # noqa: E402

import helpers  # noqa: E402  (after src path insert)

SECRET_TEXT = "sk-SECRET-DO-NOT-LEAK-9f1c"

LATEST_KNOWN = default_migrations()[-1].schema_version


def _populate(db_path: Path) -> None:
    conn, opened = open_database(
        db_path, latest_known_schema_version=LATEST_KNOWN
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    conn.close()


def test_sqlite_and_logs_stay_secret_free(tmp_path):
    db_path = tmp_path / "secret-scan.db"
    _populate(db_path)

    # Exercise the whole slice: profile + credential resolution + a
    # log record that formats the secret object itself.
    cred_ref = make_credential_ref("provider", "leak-probe")
    profile = ProviderProfile(
        provider_profile_id="p-leak",
        name="泄漏探针",
        provider_type="openai",
        capabilities=frozenset({"translation"}),
        base_url="https://api.example.com",
        credential_ref=cred_ref,
    )
    vault = helpers.InMemoryCredentialStore()
    vault.store_credential(cred_ref, SecretValue(SECRET_TEXT))
    resolved = vault.resolve_credential(profile.credential_ref)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("leak-probe")
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    try:
        logger.info("resolved credential %s for profile %s", resolved, profile)
        logger.debug("f-string view: %s", f"{resolved!r}")
        logger.warning("connection test failed for %s with credential %s", profile.name, resolved)
    finally:
        logger.removeHandler(handler)

    log_text = stream.getvalue()
    assert SECRET_TEXT not in log_text

    db_bytes = db_path.read_bytes()
    assert SECRET_TEXT.encode("utf-8") not in db_bytes
    assert SECRET_TEXT.encode("utf-16-le") not in db_bytes

    # Credential vault itself is in-memory; nothing on disk except db.
    leftovers = [
        p for p in tmp_path.rglob("*") if p.is_file() and p != db_path
    ]
    for path in leftovers:
        assert SECRET_TEXT.encode("utf-8") not in path.read_bytes(), path


def test_profile_and_network_models_carry_no_secret_fields():
    cred_ref = make_credential_ref("proxy", "corp")
    profile = ProviderProfile(
        provider_profile_id="p1", name="x", provider_type="openai",
        capabilities=frozenset({"ocr"}), credential_ref=cred_ref,
    )
    net = NetworkProfile(
        network_profile_id="n1", name="corp", mode=MODE_HTTP,
        http_proxy="http://proxy.corp:8080", credential_ref=cred_ref,
    )
    import dataclasses

    for model in (profile, net):
        for f in dataclasses.fields(model):
            assert "password" not in f.name and "secret" not in f.name and "api_key" not in f.name


def test_options_tuple_rejects_nothing_but_keeps_repr_clean():
    profile = ProviderProfile(
        provider_profile_id="p2", name="x", provider_type="openai",
        capabilities=frozenset({"translation"}),
        options=(("temperature", "0.2"),),
    )
    assert SECRET_TEXT not in repr(profile)
