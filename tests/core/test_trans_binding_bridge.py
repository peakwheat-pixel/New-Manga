"""TRANS-BINDING-BRIDGE (L1-T-A): P15 profiles/bindings → run-side provider settings.

The Run runtime reads provider configuration from the single ``pipeline_defaults``
row (``settings["providers"]["profiles"][profile_id]`` + ``provider_bindings[step]``),
while P15 persists to JSON stores. These tests pin the bridge that joins them.

Every test drives the REAL Core command surface (``CoreServiceServer`` +
``assemble_production_core``); nothing is stubbed at the seam under test, so a
removal of the mirror turns them RED (no profile under ``settings``, no step
binding, or a half-written store).
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.settings.errors import BindingValidationError  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    _P15_PROTOCOL_MINOR,
    assemble_production_core,
)
from infrastructure.providers.fallback import chain_from_binding  # noqa: E402
from infrastructure.providers.runtime import (  # noqa: E402
    PROVIDER_OPENAI_TRANSLATION,
    _apply_profile_bindings,
)


@pytest.fixture()
def env(tmp_path: Path):
    core = assemble_production_core(tmp_path / "data")
    server = CoreServiceServer(core)
    try:
        yield core, server
    finally:
        server.close()
        core.conn.close()


def request(server, command: str, payload: dict, *, minor: int = _P15_PROTOCOL_MINOR) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": minor},
        "request_id": "trans-binding",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def create_profile(
    server,
    *,
    capabilities=("Translation",),
    endpoint: str = "https://api.example.test/v1",
    model: str = "model-a",
    name: str = "Primary",
) -> dict:
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": "shared-provider",
        "display_name": name,
        "capabilities": list(capabilities),
        "endpoint": endpoint,
        "model": model,
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is None, response["error"]
    return response["result"]["profile"]


def mirror_state(core) -> tuple[dict, dict]:
    defaults = core.pipeline_defaults.read()
    providers = defaults.settings.get("providers") or {}
    return dict(providers.get("profiles") or {}), dict(defaults.provider_bindings)


# ---------------------------------------------------------------- AC1 / AC6

def test_profile_and_binding_are_mirrored_into_run_settings(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    bound = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert bound["error"] is None, bound["error"]

    profiles, bindings = mirror_state(core)
    assert profile_id in profiles, f"profile was not mirrored: {profiles}"
    entry = profiles[profile_id]
    # AC1 key set: exactly what runtime.providers reads (plus the observability list).
    assert entry["provider_type"] == "shared-provider"
    assert entry["base_url"] == "https://api.example.test/v1"
    assert entry["model"] == "model-a"
    assert entry["enabled"] is True
    assert entry["credential_ref"] is None
    assert entry["capabilities"] == ["translation"]
    assert entry["proxy_policy"] == "inherit"
    assert entry["network_profile_id"] == ""
    assert entry["options"] == {}

    # The step binding is what handlers._chain reads; a missing one is the actual
    # PROVIDER_NOT_CONFIGURED source.
    assert bindings["translate"] == profile_id
    chain = chain_from_binding(bindings["translate"])
    assert chain is not None and chain.primary == profile_id

    # And the runtime projection accepts the mirrored pair: the user profile is
    # copied onto the fixed registry slot and aliased per capability.
    effective, aliases = _apply_profile_bindings(
        core.pipeline_defaults.read().settings, core.pipeline_defaults.read().provider_bindings
    )
    projected = effective["providers"]["profiles"][PROVIDER_OPENAI_TRANSLATION]
    assert projected["base_url"] == "https://api.example.test/v1"
    assert projected["provider_type"] == "shared-provider"
    assert aliases[(profile_id, "translation")] == PROVIDER_OPENAI_TRANSLATION


def test_profile_update_and_delete_keep_the_mirror_in_sync(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    updated = request(server, "settings_provider_profiles_update", {
        "profile_id": profile_id,
        "display_name": "Renamed",
        "capabilities": ["Translation"],
        "endpoint": "https://second.example.test/v1",
        "model": "model-b",
        "network_profile_id": None,
        "enabled": False,
    })
    assert updated["error"] is None, updated["error"]
    profiles, _ = mirror_state(core)
    assert profiles[profile_id]["base_url"] == "https://second.example.test/v1"
    assert profiles[profile_id]["model"] == "model-b"
    assert profiles[profile_id]["enabled"] is False

    deleted = request(server, "settings_provider_profiles_delete", {"profile_id": profile_id})
    assert deleted["error"] is None, deleted["error"]
    profiles, _ = mirror_state(core)
    assert profile_id not in profiles


def test_binding_clear_removes_the_mirrored_step_binding(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    assert request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })["error"] is None
    assert mirror_state(core)[1]["translate"] == profile_id

    cleared = request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "global"}, "capability": "Translation",
    })
    assert cleared["error"] is None, cleared["error"]
    assert "translate" not in mirror_state(core)[1]


def test_rendering_capability_never_invents_a_pipeline_step(env) -> None:
    core, server = env
    profile = create_profile(server, capabilities=("Rendering",))
    profile_id = profile["profile_id"]

    bound = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Rendering", "profile_id": profile_id,
    })
    assert bound["error"] is None, bound["error"]
    # The P15 row exists (unchanged behaviour) but no pipeline step is created for it:
    # render is local and consumes no remote provider profile.
    rows = core.provider_binding_store.list_bindings()
    assert any(row["capability"] == "Rendering" for row in rows)
    _, bindings = mirror_state(core)
    assert "render" not in bindings and "rendering" not in bindings


# ---------------------------------------------------------------- AC2

class _MemoryCredentials:
    """Same fake the P15 suite uses: refs only, never a secret value."""

    def __init__(self):
        self.refs = set()

    def has_credential(self, ref):
        return ref in self.refs

    def delete_credential(self, ref):
        self.refs.discard(ref)


def test_mirror_carries_credential_ref_but_never_the_secret(env) -> None:
    core, server = env
    core.credential_store = _MemoryCredentials()
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    credential_ref = f"NewManga/provider/{profile_id}/api-key"
    core.credential_store.refs.add(credential_ref)

    bound = request(server, "BindProfileCredential", {
        "target": {"kind": "provider_api", "profile_id": profile_id},
        "credential_ref": credential_ref,
    })
    assert bound["error"] is None, bound["error"]

    profiles, _ = mirror_state(core)
    assert profiles[profile_id]["credential_ref"] == credential_ref
    dumped = json.dumps(core.pipeline_defaults.read().settings)
    assert credential_ref in dumped  # the reference rides the mirror
    lowered = dumped.lower()
    for forbidden in ("api_key", "apikey", "secret", "password", "bearer "):
        assert forbidden not in lowered, f"mirror leaked a secret-shaped key: {forbidden}"


# ---------------------------------------------------------------- AC3 / AC6

def test_profile_mirror_failure_is_typed_and_leaves_no_half_write(env, monkeypatch) -> None:
    core, server = env

    def boom(*args, **kwargs):
        raise BindingValidationError("mirror write refused")

    monkeypatch.setattr(core.pipeline_defaults, "save_settings_section", boom)
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": "shared-provider",
        "display_name": "Primary",
        "capabilities": ["Translation"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    # Fail-closed in the strong direction: the JSON store was never written either.
    assert core.provider_profile_store.list_profiles() == []
    assert mirror_state(core)[0] == {}


def test_binding_mirror_failure_rolls_back_the_binding_rows(env, monkeypatch) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(*args, **kwargs):
        raise BindingValidationError("binding mirror refused")

    monkeypatch.setattr(core.pipeline_defaults, "save_provider_binding", boom)
    response = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert core.provider_binding_store.list_bindings() == []
    assert "translate" not in mirror_state(core)[1]


# ------------------------------------------------- P1-1: scope-aware mirroring
#
# `provider_bindings` (pipeline_defaults) has ONE flat slot per step: the run's
# `provider_binding_snapshot[step]` read by `handlers._chain`
# (src/infrastructure/providers/handlers.py:1266-1274) and by
# `infrastructure/pipeline/executor.py:27`. There is no per-book step slot there —
# the P15 book/chapter resolution rides `provider_binding_snapshot[_p15_settings_snapshot]`
# (built by `prepare_run_snapshot`, core_service.py:6704-6709) and is only a display face.
# Therefore a book/chapter-scoped P15 binding must NEVER write the flat slot.

def test_book_scoped_binding_does_not_overwrite_the_global_step(env) -> None:
    core, server = env
    global_profile = create_profile(server, name="Global")
    book_profile = create_profile(server, name="PerBook")
    global_id = global_profile["profile_id"]
    book_id = book_profile["profile_id"]
    book = core.library.create_book("Scoped Book")

    assert request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": global_id,
    })["error"] is None
    assert mirror_state(core)[1]["translate"] == global_id

    scoped = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "book", "book_id": book.book_id},
        "capability": "Translation",
        "profile_id": book_id,
    })
    assert scoped["error"] is None, scoped["error"]

    # The P15 row is stored for that book ...
    rows = core.provider_binding_store.list_bindings()
    assert any(row["scope"] == {"kind": "book", "book_id": book.book_id} for row in rows)
    # ... but the global flat slot (the one _chain reads) is untouched.
    assert mirror_state(core)[1]["translate"] == global_id, "book scope hijacked the global step"

    # The P15 resolve face still returns the book-scoped profile for that book.
    resolved = request(server, "settings_provider_bindings_resolve", {
        "capability": "Translation", "book_id": book.book_id,
    })
    assert resolved["error"] is None, resolved["error"]
    assert resolved["result"]["profile_id"] == book_id


def test_clearing_a_book_scope_never_clears_the_global_step(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    book = core.library.create_book("Scoped Book")
    assert request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })["error"] is None
    assert mirror_state(core)[1]["translate"] == profile_id

    # Clearing a book scope that has no binding at all must not touch the global slot.
    cleared = request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "book", "book_id": book.book_id}, "capability": "Translation",
    })
    assert cleared["error"] is None, cleared["error"]
    assert mirror_state(core)[1]["translate"] == profile_id, "book clear wiped the global step"


def test_clearing_a_chapter_scope_never_clears_the_global_step(env) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]
    book = core.library.create_book("Scoped Book")
    chapter = core.library.create_chapter(book.book_id, "Ch 1")
    assert request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })["error"] is None

    cleared = request(server, "settings_provider_bindings_clear", {
        "scope": {"kind": "chapter", "chapter_id": chapter.chapter_id},
        "capability": "Translation",
    })
    assert cleared["error"] is None, cleared["error"]
    assert mirror_state(core)[1]["translate"] == profile_id


# ------------------------------------------------- P1-2: reverse (store-fails) windows
#
# The mirror is written FIRST, so the reverse window is "mirror already new, store
# write fails". Each of the four store writes is exercised here; after the typed
# failure the mirror must be back at the pre-call value (both sides consistent).

def test_store_update_failure_rolls_the_mirror_back(env, monkeypatch) -> None:
    core, server = env
    profile = create_profile(server, endpoint="https://old.example.test/v1")
    profile_id = profile["profile_id"]
    assert mirror_state(core)[0][profile_id]["base_url"] == "https://old.example.test/v1"

    def boom(profile_arg):
        raise KeyError(profile_arg.provider_profile_id)

    monkeypatch.setattr(core.provider_profile_store, "update_profile", boom)
    response = request(server, "settings_provider_profiles_update", {
        "profile_id": profile_id,
        "display_name": "Renamed",
        "capabilities": ["Translation"],
        "endpoint": "https://new.example.test/v1",
        "model": "model-z",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    # Reverse window closed: the mirror still carries the OLD value, matching the store.
    assert mirror_state(core)[0][profile_id]["base_url"] == "https://old.example.test/v1"
    assert core.provider_profile_store.get_profile(profile_id).base_url == "https://old.example.test/v1"


def test_store_create_failure_rolls_the_mirror_back(env, monkeypatch) -> None:
    core, server = env

    def boom(profile_arg):
        raise OSError("disk full")

    monkeypatch.setattr(core.provider_profile_store, "add_profile", boom)
    response = request(server, "settings_provider_profiles_create", {
        "provider_id": "shared-provider",
        "display_name": "Dangling",
        "capabilities": ["Translation"],
        "endpoint": "https://api.example.test/v1",
        "model": "model-a",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert mirror_state(core)[0] == {}, "mirror kept an entry the store rejected"
    assert core.provider_profile_store.list_profiles() == []


def test_store_delete_failure_restores_the_mirror(env, monkeypatch) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(profile_id_arg):
        raise OSError("locked")

    monkeypatch.setattr(core.provider_profile_store, "delete_profile", boom)
    response = request(server, "settings_provider_profiles_delete", {"profile_id": profile_id})
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert profile_id in mirror_state(core)[0], "mirror lost a profile the store still owns"
    assert core.provider_profile_store.get_profile(profile_id) is not None


def test_store_binding_failure_rolls_the_mirror_back(env, monkeypatch) -> None:
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(bindings):
        raise OSError("locked")

    monkeypatch.setattr(core.provider_binding_store, "save_bindings", boom)
    response = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert "translate" not in mirror_state(core)[1], "mirror kept a step the store rejected"
    assert core.provider_binding_store.list_bindings() == []

# ------------------------------------------------- r2 R2-001 / R2-002: remaining catch families
#
# Every member of `_write_with_rollback`'s catch tuple must be hit by at least one
# reverse test, otherwise "we catch X" is an unverified claim. The three below cover
# sqlite3.Error (the mirror's own persistence), ValueError (profile-file format) and
# TypeError (serialisation), which the four earlier reverse tests did not reach.

def test_sqlite_write_failure_rolls_the_mirror_back(env, monkeypatch) -> None:
    """r2 R2-001: the mirror's only persistence is SQLite.

    A transient SQLite write failure must be caught, rolled back and reported typed —
    previously it escaped the tuple and left "mirror new / store old" with no rollback.
    The failure is made one-shot so the rollback itself can still succeed (the
    persistent-unwritable window is registered in README §6.2 as unrecoverable).
    """
    import sqlite3

    from infrastructure.sqlite import pipeline as pipeline_store

    core, server = env
    profile = create_profile(server, endpoint="https://old.example.test/v1")
    profile_id = profile["profile_id"]

    original = pipeline_store.SqliteSnapshotProvider.set_defaults
    calls = {"count": 0}

    def commit_then_fail(self, **kwargs):
        # The realistic r2 R2-001 shape: the row IS written (mirror now new), and the
        # failure happens right after -- e.g. the lock is lost while finishing the
        # operation. Raising *before* the write would leave the mirror untouched and
        # prove nothing about the rollback.
        calls["count"] += 1
        original(self, **kwargs)
        if calls["count"] == 1:
            raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(pipeline_store.SqliteSnapshotProvider, "set_defaults", commit_then_fail)

    response = request(server, "settings_provider_profiles_update", {
        "profile_id": profile_id,
        "display_name": "Renamed",
        "capabilities": ["Translation"],
        "endpoint": "https://new.example.test/v1",
        "model": "model-z",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert mirror_state(core)[0][profile_id]["base_url"] == "https://old.example.test/v1", (
        "sqlite failure escaped the rollback whitelist"
    )
    assert core.provider_profile_store.get_profile(profile_id).base_url == "https://old.example.test/v1"


def test_store_format_error_rolls_the_mirror_back(env, monkeypatch) -> None:
    """ValueError family: an unparsable profile file must roll the mirror back."""
    from infrastructure.settings.json_profile_stores import ProfileFileFormatError

    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(bindings):
        raise ProfileFileFormatError("provider_bindings.json has an unsupported format")

    monkeypatch.setattr(core.provider_binding_store, "save_bindings", boom)
    response = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert "translate" not in mirror_state(core)[1]
    assert core.provider_binding_store.list_bindings() == []


def test_store_type_error_rolls_the_mirror_back(env, monkeypatch) -> None:
    """TypeError family: an unserialisable value must roll the mirror back."""
    core, server = env
    profile = create_profile(server)
    profile_id = profile["profile_id"]

    def boom(bindings):
        raise TypeError("Object of type object is not JSON serializable")

    monkeypatch.setattr(core.provider_binding_store, "save_bindings", boom)
    response = request(server, "settings_provider_bindings_set", {
        "scope": {"kind": "global"}, "capability": "Translation", "profile_id": profile_id,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert "translate" not in mirror_state(core)[1]

def test_seam_validation_error_after_write_rolls_back_the_mirror(env, monkeypatch) -> None:
    """`BindingValidationError` arriving AFTER the mirror write committed.

    A seam validation error usually fires before anything is written (nothing to roll
    back), which would make the catch member undiscriminated. Here the section is really
    written first and the validation error is raised afterwards, so dropping the member
    from the catch tuple leaves "mirror new / store old" and this test goes RED.
    """
    core, server = env
    profile = create_profile(server, endpoint="https://old.example.test/v1")
    profile_id = profile["profile_id"]

    original = core.pipeline_defaults.save_settings_section
    calls = {"count": 0}

    def commit_then_reject(section, values):
        calls["count"] += 1
        result = original(section, values)
        if calls["count"] == 1:
            raise BindingValidationError("rejected after the section was written")
        return result

    monkeypatch.setattr(core.pipeline_defaults, "save_settings_section", commit_then_reject)
    response = request(server, "settings_provider_profiles_update", {
        "profile_id": profile_id,
        "display_name": "Renamed",
        "capabilities": ["Translation"],
        "endpoint": "https://new.example.test/v1",
        "model": "model-z",
        "network_profile_id": None,
        "enabled": True,
    })
    assert response["error"] is not None
    assert response["error"]["code"] == "SETTINGS_UNAVAILABLE", response["error"]
    assert mirror_state(core)[0][profile_id]["base_url"] == "https://old.example.test/v1", (
        "seam validation error escaped without rolling the committed mirror write back"
    )