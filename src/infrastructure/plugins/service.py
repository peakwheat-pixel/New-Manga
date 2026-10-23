"""Local-directory plugin runtime (PLUGIN-RUNTIME-1, design §4.1–§4.4).

Scope of this release (user authorization 2026-10-23, decisions D1–D6):

* discovery of ``<data_root>/plugins/<plugin_id>/manifest.json`` (D4);
* fail-closed manifest v1 validation (:mod:`manifest`);
* a global kill switch (``plugins.enabled``) plus per-plugin enable state,
  both **disabled by default** (D5, stored in ``plugin_state``);
* an append-only ``plugin_events`` audit ledger (D2);
* hook invocation in a **separate** ``python -I`` subprocess with a hard
  timeout; a crash/timeout skips that hook and keeps the main pipeline
  running (D1);
* only permission-free plugins (``permissions: []``) are loadable (design
  §4.3 first-release limit).

Security boundary (review r1 P1-1): plugins are trusted local code. The
``permissions: []`` first release means the Core grants the plugin process NO
capability handles (no Core objects, database, model, credentials, configured
paths or network configuration); the hook subprocess runs with a minimal
environment, ``-I`` and the plugin directory as cwd. It is NOT an OS sandbox --
the plugin still has the user's OS rights -- so a malicious plugin could open
files or sockets itself; that boundary is documented, tested (no Core env/core
imports leak into the child) and tracked as the separate
PLUGIN-RUNTIME-SANDBOX-1 follow-up.

The service never writes plugin files, never imports plugin code into the
Core process, and never stores payload bytes in the audit ledger.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import subprocess
import threading
import sys
import time
import uuid

from infrastructure.plugins.sandbox import (
    AppContainerSandbox,
    SandboxError,
    SandboxResult,
)
from infrastructure.plugins.manifest import (
    HOOK_NAMES,
    WRITABLE_HOOKS,
    ManifestError,
    PluginManifest,
    parse_manifest,
)

#: D1: hard per-hook timeout (seconds). A timeout is `plugin_error` +
#: skipped hook, never a Core failure.
HOOK_TIMEOUT_SECONDS = 10

#: D3: the versioned schema marker injected into every hook payload.
HOOK_SCHEMA_REF = "nm-plugin-hook/1"

#: The hook subprocess may not emit more than this much stdout (a runaway
#: plugin must not exhaust Core memory; the hook is then skipped + audited).
_MAX_HOOK_OUTPUT_BYTES = 256 * 1024

_GLOBAL_PLUGIN_ID = "__global__"
_MAX_AUDIT_LIMIT = 500


class PluginError(ValueError):
    """Typed plugin runtime error (stable code + short detail)."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def resolve_hook_interpreter() -> str:
    """Public wrapper used by the production assembly for sandbox ACL setup."""
    return _hook_interpreter()


def _hook_interpreter() -> str:
    """The interpreter used for the isolated hook subprocess (D1).

    In source runs it is the running interpreter. In a packaged onedir build
    ``sys.executable`` is the sidecar itself, not a Python CLI, so the
    sibling ``python.exe`` is used when present; otherwise the hop fails
    closed with a typed error and the hook is skipped (the packaged-runtime
    interpreter bundling is tracked as a follow-up, never a silent crash).
    """

    if not getattr(sys, "frozen", False):
        return sys.executable
    for candidate in ("python.exe", "python3.exe", "python3"):
        sibling = Path(sys.executable).with_name(candidate)
        if sibling.is_file():
            return str(sibling)
    raise PluginError(
        "PLUGIN_HOOK_UNAVAILABLE",
        "no python interpreter is bundled next to the sidecar",
    )


class PluginService:
    """Discovery + state + audit + isolated hook invocation."""

    def __init__(
        self,
        conn,
        plugin_root: str | Path,
        *,
        app_version: str,
        hook_timeout_seconds: int = HOOK_TIMEOUT_SECONDS,
        sandbox: AppContainerSandbox | None = None,
    ) -> None:
        self._conn = conn
        self._plugin_root = Path(plugin_root)
        self._app_version = app_version
        self._hook_timeout_seconds = hook_timeout_seconds
        self._sandbox = sandbox

    # ------------------------------------------------------------------
    # discovery / listing
    # ------------------------------------------------------------------
    def list_plugins(self) -> dict:
        """Return the snapshot the settings panel renders (read-only)."""

        discovered = self._discover(record_events=True)
        state = self._state_rows()
        global_enabled = bool(state.get(_GLOBAL_PLUGIN_ID, 0))
        plugins = []
        for item in discovered:
            manifest: PluginManifest | None = item["manifest"]
            plugin_id = item["plugin_id"]
            if manifest is None:
                plugins.append(
                    {
                        "plugin_id": plugin_id,
                        "status": "rejected",
                        "enabled": False,
                        "name": "",
                        "version": "",
                        "description": "",
                        "hooks": [],
                        "reason": item["reason"],
                    }
                )
                continue
            enabled = bool(state.get(plugin_id, 0))
            plugins.append(
                {
                    "plugin_id": manifest.plugin_id,
                    "status": "enabled" if enabled else "disabled",
                    "enabled": enabled,
                    "name": manifest.name,
                    "version": manifest.version,
                    "description": manifest.description,
                    "hooks": list(manifest.hooks),
                    "reason": None,
                }
            )
        return {
            "global_enabled": global_enabled,
            # The plugin root is never projected over IPC (review r1 P2: an
            # absolute OS path does not belong in a settings projection); the
            # opener resolves the same directory Rust-side.
            "plugins": plugins,
        }

    def set_global_enabled(self, enabled: bool) -> dict:
        if not isinstance(enabled, bool):
            raise PluginError("PLUGIN_INVALID_REQUEST", "enabled must be a boolean")
        self._write_state(_GLOBAL_PLUGIN_ID, enabled, manifest=None)
        self._record_event(
            _GLOBAL_PLUGIN_ID, "enabled" if enabled else "disabled", detail={"scope": "global"}
        )
        return {"global_enabled": enabled}

    def set_plugin_enabled(self, plugin_id: str, enabled: bool) -> dict:
        if not isinstance(plugin_id, str) or not isinstance(enabled, bool):
            raise PluginError(
                "PLUGIN_INVALID_REQUEST", "plugin_id must be a string and enabled a boolean"
            )
        discovered = {item["plugin_id"]: item for item in self._discover(record_events=True)}
        item = discovered.get(plugin_id)
        if item is None:
            raise PluginError("PLUGIN_NOT_FOUND", plugin_id)
        if item["manifest"] is None:
            raise PluginError("PLUGIN_NOT_LOADED", item["reason"] or "plugin rejected")
        self._write_state(plugin_id, enabled, manifest=item["manifest"])
        self._record_event(
            plugin_id, "enabled" if enabled else "disabled", detail={"scope": "plugin"}
        )
        return {"plugin_id": plugin_id, "enabled": enabled}

    def audit_list(self, limit: int = 50) -> list[dict]:
        if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1 or limit > _MAX_AUDIT_LIMIT:
            raise PluginError("PLUGIN_INVALID_REQUEST", f"limit must be 1..{_MAX_AUDIT_LIMIT}")
        rows = self._conn.execute(
            "SELECT event_id, plugin_id, event_type, hook_name, detail_json, occurred_at"
            " FROM plugin_events ORDER BY occurred_at DESC, event_id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        events = []
        for row in rows:
            try:
                detail = json.loads(row["detail_json"] or "{}")
            except json.JSONDecodeError:
                detail = {}
            events.append(
                {
                    "event_id": row["event_id"],
                    "plugin_id": row["plugin_id"],
                    "event_type": row["event_type"],
                    "hook_name": row["hook_name"],
                    "detail": detail if isinstance(detail, dict) else {},
                    "occurred_at": row["occurred_at"],
                }
            )
        return events

    # ------------------------------------------------------------------
    # hook invocation (D1 isolation)
    # ------------------------------------------------------------------
    def run_hook(self, hook_name: str, payload: dict | None = None) -> dict:
        """Invoke one frozen hook across enabled plugins.

        Returns ``{"applied", "reason", "results", "overrides", "errors"}``.
        A disabled global switch is a silent no-op (``applied=False``); an
        enabled plugin whose hook crashes/times out adds a typed error and
        never raises to the caller.
        """

        if hook_name not in HOOK_NAMES:
            raise PluginError("PLUGIN_HOOK_UNKNOWN", f"unknown hook {hook_name!r}")
        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise PluginError("PLUGIN_INVALID_REQUEST", "hook payload must be a JSON object")
        if not self._global_enabled():
            return {
                "applied": False,
                "reason": "plugins_disabled",
                "results": [],
                "overrides": [],
                "errors": [],
            }
        payload = {**payload, "schema_ref": HOOK_SCHEMA_REF}
        if not isinstance(payload["schema_ref"], str):  # defensive: frozen constant
            raise PluginError("PLUGIN_INVALID_REQUEST", "schema_ref must be a string")

        results: list[dict] = []
        overrides: list[dict] = []
        errors: list[dict] = []
        state = self._state_rows()
        for item in self._discover(record_events=False):
            manifest: PluginManifest | None = item["manifest"]
            if manifest is None or hook_name not in manifest.hooks:
                continue
            if not state.get(manifest.plugin_id, 0):
                continue
            started = time.perf_counter()
            try:
                result = self._invoke(manifest, hook_name, payload)
            except PluginError as error:
                self._record_event(
                    manifest.plugin_id,
                    "plugin_error",
                    hook_name=hook_name,
                    detail={"code": error.code, "detail": error.detail[:200]},
                )
                errors.append(
                    {"plugin_id": manifest.plugin_id, "code": error.code, "detail": error.detail[:200]}
                )
                continue
            duration_ms = int((time.perf_counter() - started) * 1000)
            self._record_event(
                manifest.plugin_id,
                "hook_invoked",
                hook_name=hook_name,
                detail={"duration_ms": duration_ms},
            )
            results.append({"plugin_id": manifest.plugin_id, "result": result})
            if hook_name in WRITABLE_HOOKS and isinstance(result, dict):
                overrides.append({"plugin_id": manifest.plugin_id, "override": result})
        return {
            "applied": bool(results),
            "reason": None,
            "results": results,
            "overrides": overrides,
            "errors": errors,
        }

    def apply_input(self, hook_name: str, payload: dict, validate) -> dict:
        """Apply validated writable fields; bad overrides cannot fail a Run."""
        current = dict(payload["input"])
        for item in self.run_hook(hook_name, payload)["overrides"]:
            override = item["override"]
            try:
                if not override.keys() <= current.keys():
                    raise ValueError("unknown input field")
                candidate = {**current, **override}
                validate(candidate)
            except (ValueError, TypeError) as error:
                self._record_event(item["plugin_id"], "plugin_error", hook_name=hook_name,
                                   detail={"code": "PLUGIN_INVALID_OVERRIDE", "detail": str(error)[:200]})
                continue
            current = candidate
        return current

    def _invoke_sandboxed(
        self,
        manifest: PluginManifest,
        hook_name: str,
        payload_bytes: bytes,
        runner: Path,
        interpreter: str,
    ) -> object:
        """Run one hook inside the plugin's AppContainer (fail-closed)."""
        try:
            self._sandbox.prepare_plugin(
                manifest.plugin_id,
                manifest.root,
                runner_path=runner,
                interpreter=interpreter,
            )
            outcome: SandboxResult = self._sandbox.run(
                manifest.plugin_id,
                [interpreter, "-I", str(runner), str(manifest.entry_path), hook_name],
                cwd=manifest.root,
                payload=payload_bytes,
                timeout_seconds=self._hook_timeout_seconds,
                max_output_bytes=_MAX_HOOK_OUTPUT_BYTES,
                interpreter=interpreter,
            )
        except SandboxError as error:
            message = str(error)
            if "output exceeded" in message:
                raise PluginError(
                    "PLUGIN_HOOK_FAILED", f"{hook_name} produced too much output"
                ) from error
            raise PluginError("PLUGIN_HOOK_UNAVAILABLE", message) from error
        if outcome.timed_out:
            raise PluginError(
                "PLUGIN_HOOK_TIMEOUT",
                f"{hook_name} exceeded {self._hook_timeout_seconds}s",
            )
        if outcome.returncode != 0:
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"{hook_name} exited with {outcome.returncode}"
            )
        try:
            response = json.loads(outcome.stdout.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise PluginError("PLUGIN_HOOK_FAILED", "hook returned non-JSON output") from error
        if not isinstance(response, dict) or response.get("ok") is not True:
            code = response.get("error") if isinstance(response, dict) else "hook_failed"
            raise PluginError("PLUGIN_HOOK_FAILED", f"hook reported {code}")
        return response.get("result")

    def _invoke(self, manifest: PluginManifest, hook_name: str, payload: dict) -> object:
        runner = Path(__file__).with_name("_hook_runner.py")
        env = {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        if "PATH" in os.environ:
            env["PATH"] = os.environ["PATH"]
        interpreter = _hook_interpreter()
        payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if self._sandbox is not None:
            return self._invoke_sandboxed(
                manifest, hook_name, payload_bytes, runner, interpreter
            )
        try:
            process = subprocess.Popen(
                [
                    interpreter,
                    "-I",
                    str(runner),
                    str(manifest.entry_path),
                    hook_name,
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=str(manifest.root),
                env=env,
            )
        except OSError as error:
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"could not start hook process: {error.strerror}"
            ) from error
        # Bounded streaming read (review r2 P2): the first byte past the cap
        # kills the child, so a runaway plugin can never buffer an unbounded
        # stdout/stderr inside the Core. stderr is discarded outright.
        collected: dict[str, object] = {}

        def pump_stdout() -> None:
            chunks: list[bytes] = []
            total = 0
            assert process.stdout is not None
            while True:
                chunk = process.stdout.read(65536)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MAX_HOOK_OUTPUT_BYTES:
                    collected["overflow"] = True
                    process.kill()
                    break
                chunks.append(chunk)
            collected["stdout"] = b"".join(chunks)

        reader = threading.Thread(target=pump_stdout, daemon=True)
        reader.start()
        try:
            assert process.stdin is not None
            process.stdin.write(payload_bytes)
            process.stdin.close()
        except OSError:
            pass
        try:
            process.wait(timeout=self._hook_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            raise PluginError(
                "PLUGIN_HOOK_TIMEOUT",
                f"{hook_name} exceeded {self._hook_timeout_seconds}s",
            ) from None
        reader.join(timeout=2)
        if collected.get("overflow"):
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"{hook_name} produced too much output"
            )
        if process.returncode != 0:
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"{hook_name} exited with {process.returncode}"
            )
        stdout_bytes = collected.get("stdout") or b""
        try:
            response = json.loads(stdout_bytes.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise PluginError("PLUGIN_HOOK_FAILED", "hook returned non-JSON output") from error
        if not isinstance(response, dict) or response.get("ok") is not True:
            code = response.get("error") if isinstance(response, dict) else "hook_failed"
            raise PluginError("PLUGIN_HOOK_FAILED", f"hook reported {code}")
        return response.get("result")

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _discover(self, *, record_events: bool) -> list[dict]:
        discoveries: list[dict] = []
        if not self._plugin_root.is_dir():
            return discoveries
        state = self._state_full() if record_events else {}
        for candidate in sorted(self._plugin_root.iterdir(), key=lambda path: path.name):
            if not candidate.is_dir() or candidate.name.startswith("."):
                continue
            try:
                manifest = parse_manifest(candidate, app_version=self._app_version)
            except ManifestError as error:
                reason = f"{error.code}: {error.detail}"
                discoveries.append(
                    {"plugin_id": candidate.name, "manifest": None, "reason": reason}
                )
                if record_events:
                    previous = state.get(candidate.name)
                    if previous is None or previous["last_error"] != reason:
                        self._record_event(
                            candidate.name,
                            "load_rejected",
                            detail={"code": error.code, "detail": error.detail[:200]},
                        )
                        self._upsert_discovery_state(
                            candidate.name,
                            manifest_json=previous["manifest_json"] if previous else None,
                            last_error=reason,
                        )
                continue
            discoveries.append({"plugin_id": manifest.plugin_id, "manifest": manifest, "reason": None})
            if record_events:
                fingerprint = self._manifest_fingerprint(manifest)
                previous = state.get(manifest.plugin_id)
                if (
                    previous is None
                    or previous["manifest_json"] != fingerprint
                    or previous["last_error"]
                ):
                    self._record_event(
                        manifest.plugin_id,
                        "load_ok",
                        detail={"version": manifest.version, "hooks": list(manifest.hooks)},
                    )
                    self._upsert_discovery_state(
                        manifest.plugin_id, manifest_json=fingerprint, last_error=None
                    )
        return discoveries

    @staticmethod
    def _manifest_fingerprint(manifest: PluginManifest) -> str:
        return json.dumps(
            {
                "id": manifest.plugin_id,
                "name": manifest.name,
                "version": manifest.version,
                "hooks": list(manifest.hooks),
                "permissions": list(manifest.permissions),
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    def _upsert_discovery_state(
        self, plugin_id: str, *, manifest_json: str | None, last_error: str | None
    ) -> None:
        """Discovery metadata only -- the enabled flag is preserved."""
        now = _now()
        with self._conn:
            self._conn.execute(
                "INSERT INTO plugin_state"
                " (plugin_id, enabled, manifest_json, installed_at, updated_at, last_error)"
                " VALUES (?, 0, ?, ?, ?, ?)"
                " ON CONFLICT(plugin_id) DO UPDATE SET"
                " manifest_json = COALESCE(excluded.manifest_json, plugin_state.manifest_json),"
                " last_error = excluded.last_error,"
                " updated_at = excluded.updated_at",
                (plugin_id, manifest_json, now, now, last_error),
            )

    def _global_enabled(self) -> bool:
        return bool(self._state_rows().get(_GLOBAL_PLUGIN_ID, 0))

    def _state_rows(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT plugin_id, enabled FROM plugin_state"
        ).fetchall()
        return {row["plugin_id"]: int(row["enabled"]) for row in rows}

    def _state_full(self) -> dict[str, dict]:
        rows = self._conn.execute(
            "SELECT plugin_id, enabled, manifest_json, last_error FROM plugin_state"
        ).fetchall()
        return {
            row["plugin_id"]: {
                "enabled": int(row["enabled"]),
                "manifest_json": row["manifest_json"],
                "last_error": row["last_error"],
            }
            for row in rows
        }

    def _write_state(
        self, plugin_id: str, enabled: bool, *, manifest: PluginManifest | None
    ) -> None:
        now = _now()
        manifest_json = self._manifest_fingerprint(manifest) if manifest is not None else None
        with self._conn:
            self._conn.execute(
                "INSERT INTO plugin_state"
                " (plugin_id, enabled, manifest_json, installed_at, updated_at, last_error)"
                " VALUES (?, ?, ?, ?, ?, NULL)"
                " ON CONFLICT(plugin_id) DO UPDATE SET"
                " enabled = excluded.enabled,"
                " manifest_json = COALESCE(excluded.manifest_json, plugin_state.manifest_json),"
                " updated_at = excluded.updated_at",
                (plugin_id, 1 if enabled else 0, manifest_json, now, now),
            )

    def _record_event(
        self,
        plugin_id: str,
        event_type: str,
        *,
        hook_name: str | None = None,
        detail: dict | None = None,
    ) -> None:
        """Append one audit row. Strictly append-only: no time-window dedup
        (discovery load events are already state-driven by ``_discover``)."""
        detail_json = json.dumps(detail or {}, ensure_ascii=False, sort_keys=True)
        now = _now()
        try:
            with self._conn:
                self._conn.execute(
                    "INSERT INTO plugin_events"
                    " (event_id, plugin_id, event_type, hook_name, detail_json, occurred_at)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (uuid.uuid4().hex, plugin_id, event_type, hook_name, detail_json, now),
                )
        except Exception:  # noqa: BLE001 - audit failure must not fail the hook
            pass
