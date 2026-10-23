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

The service never writes plugin files, never imports plugin code into the
Core process, and never stores payload bytes in the audit ledger.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import uuid

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

#: The audit ledger's dedup window: the list endpoint re-discovers plugins on
#: every read, so identical reject/load events within this window are not
#: written twice (they are still visible as one row).
_EVENT_DEDUP_SECONDS = 60

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
    ) -> None:
        self._conn = conn
        self._plugin_root = Path(plugin_root)
        self._app_version = app_version
        self._hook_timeout_seconds = hook_timeout_seconds

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
            "plugin_root": str(self._plugin_root),
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

    def _invoke(self, manifest: PluginManifest, hook_name: str, payload: dict) -> object:
        runner = Path(__file__).with_name("_hook_runner.py")
        env = {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        if "PATH" in os.environ:
            env["PATH"] = os.environ["PATH"]
        interpreter = _hook_interpreter()
        try:
            completed = subprocess.run(
                [
                    interpreter,
                    "-I",
                    str(runner),
                    str(manifest.entry_path),
                    hook_name,
                ],
                input=json.dumps(payload, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=self._hook_timeout_seconds,
                cwd=str(manifest.root),
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise PluginError(
                "PLUGIN_HOOK_TIMEOUT",
                f"{hook_name} exceeded {self._hook_timeout_seconds}s",
            ) from error
        except OSError as error:
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"could not start hook process: {error.strerror}"
            ) from error
        if completed.returncode != 0:
            raise PluginError(
                "PLUGIN_HOOK_FAILED", f"{hook_name} exited with {completed.returncode}"
            )
        try:
            response = json.loads(completed.stdout or "{}")
        except json.JSONDecodeError as error:
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
        for candidate in sorted(self._plugin_root.iterdir(), key=lambda path: path.name):
            if not candidate.is_dir() or candidate.name.startswith("."):
                continue
            try:
                manifest = parse_manifest(candidate, app_version=self._app_version)
            except ManifestError as error:
                discoveries.append(
                    {
                        "plugin_id": candidate.name,
                        "manifest": None,
                        "reason": f"{error.code}: {error.detail}",
                    }
                )
                if record_events:
                    self._record_event(
                        candidate.name,
                        "load_rejected",
                        detail={"code": error.code, "detail": error.detail[:200]},
                    )
                continue
            discoveries.append({"plugin_id": manifest.plugin_id, "manifest": manifest, "reason": None})
            if record_events:
                self._record_event(
                    manifest.plugin_id,
                    "load_ok",
                    detail={"version": manifest.version, "hooks": list(manifest.hooks)},
                )
        return discoveries

    def _global_enabled(self) -> bool:
        return bool(self._state_rows().get(_GLOBAL_PLUGIN_ID, 0))

    def _state_rows(self) -> dict[str, int]:
        rows = self._conn.execute(
            "SELECT plugin_id, enabled FROM plugin_state"
        ).fetchall()
        return {row["plugin_id"]: int(row["enabled"]) for row in rows}

    def _write_state(
        self, plugin_id: str, enabled: bool, *, manifest: PluginManifest | None
    ) -> None:
        now = _now()
        manifest_json = (
            json.dumps(
                {
                    "id": manifest.plugin_id,
                    "name": manifest.name,
                    "version": manifest.version,
                    "hooks": list(manifest.hooks),
                    "permissions": list(manifest.permissions),
                },
                ensure_ascii=False,
            )
            if manifest is not None
            else None
        )
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
        detail_json = json.dumps(detail or {}, ensure_ascii=False, sort_keys=True)
        now = _now()
        cutoff = (
            datetime.now(timezone.utc) - timedelta(seconds=_EVENT_DEDUP_SECONDS)
        ).isoformat(timespec="seconds")
        try:
            recent = self._conn.execute(
                "SELECT detail_json FROM plugin_events"
                " WHERE plugin_id = ? AND event_type = ? AND IFNULL(hook_name, '') = IFNULL(?, '')"
                " AND occurred_at >= ? ORDER BY occurred_at DESC LIMIT 1",
                (plugin_id, event_type, hook_name, cutoff),
            ).fetchone()
        except Exception:  # noqa: BLE001 - ledger must never break a hook
            recent = None
        if recent is not None and recent["detail_json"] == detail_json:
            return
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
