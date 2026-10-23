"""PLUGIN-RUNTIME-SANDBOX-1: real Windows AppContainer isolation for hooks."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.plugins.manifest import HOOK_NAMES  # noqa: E402
from infrastructure.plugins.sandbox import AppContainerSandbox, SandboxError  # noqa: E402
from infrastructure.plugins.service import PluginError, PluginService  # noqa: E402

pytestmark = pytest.mark.skipif(
    sys.platform != "win32", reason="AppContainer sandbox is Windows-only"
)


def _manifest(plugin_id: str, hooks: list[str] | None = None) -> dict:
    return {
        "id": plugin_id,
        "name": plugin_id,
        "version": "1.0.0",
        "entry": "plugin.py",
        "hooks": hooks or ["after_detect"],
        "permissions": [],
        "description": "sandbox test plugin",
    }


def _write_plugin(
    root: Path, plugin_id: str, source: str, *, hooks: list[str] | None = None
) -> Path:
    plugin = root / "plugins" / plugin_id
    plugin.mkdir(parents=True, exist_ok=True)
    (plugin / "plugin.py").write_text(source, encoding="utf-8")
    (plugin / "manifest.json").write_text(
        json.dumps(_manifest(plugin_id, hooks)), encoding="utf-8"
    )
    return plugin


class _Runtime:
    def __init__(self, conn, root: Path) -> None:
        self.root = root
        self.sandbox = AppContainerSandbox()
        self.service = PluginService(
            conn, root / "plugins", app_version="0.1.0", sandbox=self.sandbox
        )

    def close(self) -> None:
        self.sandbox.close()


@pytest.fixture()
def sandboxed(tmp_path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    conn, _opened = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    (tmp_path / "plugins").mkdir(parents=True, exist_ok=True)
    runtime = _Runtime(conn, tmp_path)
    try:
        yield runtime
    finally:
        runtime.close()
        conn.close()


def test_sandbox_blocks_reading_files_outside_the_plugin_root(sandboxed, tmp_path) -> None:
    secret = tmp_path / "top-secret.txt"
    secret.write_text("TOP-SECRET", encoding="utf-8")
    source = (
        "import os\n"
        "def after_detect(payload):\n"
        "    root = os.path.dirname(os.path.abspath(__file__))\n"
        "    secret = os.path.join(os.path.dirname(root), 'top-secret.txt')\n"
        "    try:\n"
        "        data = open(secret, encoding='utf-8').read()\n"
        "        return {'fs': 'READ_OK', 'data': data}\n"
        "    except OSError as error:\n"
        "        return {'fs': 'BLOCKED', 'winerror': getattr(error, 'winerror', None)}\n"
    )
    _write_plugin(tmp_path, "acme-secret-reader", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-secret-reader", True)

    outcome = service.run_hook("after_detect", {"pages": []})

    assert outcome["applied"] is True
    result = outcome["results"][0]["result"]
    assert result["fs"] == "BLOCKED"
    assert "data" not in result


def test_sandbox_blocks_network_access(sandboxed, tmp_path) -> None:
    source = (
        "import socket\n"
        "def after_detect(payload):\n"
        "    try:\n"
        "        socket.create_connection(('1.1.1.1', 80), timeout=2)\n"
        "        return {'net': 'NET_OK'}\n"
        "    except OSError as error:\n"
        "        return {'net': 'NET_BLOCKED', 'kind': type(error).__name__}\n"
    )
    _write_plugin(tmp_path, "acme-net", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-net", True)

    outcome = service.run_hook("after_detect", {"pages": []})

    assert outcome["applied"] is True
    assert outcome["results"][0]["result"]["net"] == "NET_BLOCKED"


def test_sandbox_still_runs_a_benign_hook(sandboxed, tmp_path) -> None:
    source = (
        "def after_detect(payload):\n"
        "    return {'pages': len(payload.get('pages', [])), 'schema_ref': payload.get('schema_ref')}\n"
    )
    _write_plugin(tmp_path, "acme-benign", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-benign", True)

    outcome = service.run_hook("after_detect", {"pages": [1, 2, 3]})

    assert outcome["applied"] is True
    assert outcome["results"][0]["result"] == {
        "pages": 3,
        "schema_ref": "nm-plugin-hook/1",
    }
    audit = [event["event_type"] for event in service.audit_list(20)]
    assert "hook_invoked" in audit


def test_sandbox_failure_is_fail_closed_and_audited(sandboxed, tmp_path) -> None:
    source = "def after_detect(payload):\n    return {'ok': True}\n"
    _write_plugin(tmp_path, "acme-failclosed", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-failclosed", True)

    class _Broken(AppContainerSandbox):
        def prepare_plugin(self, *args, **kwargs):  # type: ignore[override]
            raise SandboxError("cannot grant sandbox access")

    broken = PluginService(
        service._conn, tmp_path / "plugins", app_version="0.1.0", sandbox=_Broken()
    )
    broken.set_global_enabled(True)
    broken.set_plugin_enabled("acme-failclosed", True)
    outcome = broken.run_hook("after_detect", {})

    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_UNAVAILABLE"
    audit = broken.audit_list(20)
    assert any(event["event_type"] == "plugin_error" for event in audit)
    # A sandbox problem never breaks the caller.
    assert outcome["errors"][0]["plugin_id"] == "acme-failclosed"


def test_sandbox_kills_a_hanging_hook_within_the_timeout(sandboxed, tmp_path) -> None:
    source = (
        "import time\n"
        "def after_detect(payload):\n"
        "    time.sleep(60)\n"
        "    return {'ok': True}\n"
    )
    _write_plugin(tmp_path, "acme-hang", source)
    short = PluginService(
        sandboxed.service._conn,
        tmp_path / "plugins",
        app_version="0.1.0",
        hook_timeout_seconds=1,
        sandbox=AppContainerSandbox(),
    )
    try:
        short.set_global_enabled(True)
        short.set_plugin_enabled("acme-hang", True)
        started = time.perf_counter()
        outcome = short.run_hook("after_detect", {})
        elapsed = time.perf_counter() - started
    finally:
        pass
    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_TIMEOUT"
    assert elapsed < 15


def test_sandbox_uses_one_shared_container(sandboxed, tmp_path) -> None:
    a = _write_plugin(tmp_path, "acme-a", "def after_detect(p):\n    return {}\n")
    b = _write_plugin(tmp_path, "acme-b", "def after_detect(p):\n    return {}\n")
    sids = {
        sandboxed.sandbox._ensure_profile(a.name),
        sandboxed.sandbox._ensure_profile(b.name),
    }
    # One shared container keeps the interpreter ACL a single one-time grant;
    # per-plugin isolation is enforced by directory ACLs.
    assert len(sids) == 1
