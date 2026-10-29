"""PLUGIN-RUNTIME-SANDBOX-1: real Windows AppContainer isolation for hooks."""

from __future__ import annotations

import json
import socket
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
    root: Path,
    plugin_id: str,
    source: str,
    *,
    hooks: list[str] | None = None,
    permissions: list[str] | None = None,
) -> Path:
    plugin = root / "plugins" / plugin_id
    plugin.mkdir(parents=True, exist_ok=True)
    (plugin / "plugin.py").write_text(source, encoding="utf-8")
    manifest = _manifest(plugin_id, hooks)
    if permissions is not None:
        manifest["permissions"] = permissions
    (plugin / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
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


def test_sandbox_uses_per_plugin_profiles(sandboxed, tmp_path) -> None:
    a = _write_plugin(tmp_path, "acme-a", "def after_detect(p):\n    return {}\n")
    b = _write_plugin(tmp_path, "acme-b", "def after_detect(p):\n    return {}\n")
    sids = {
        sandboxed.sandbox._ensure_profile(a.name),
        sandboxed.sandbox._ensure_profile(b.name),
    }
    # SANDBOX-2: each plugin gets its own container SID.
    assert len(sids) == 2
    assert sandboxed.sandbox.shared_profile is False


def test_shared_profile_is_an_explicit_opt_in(tmp_path) -> None:
    from infrastructure.plugins.sandbox import AppContainerSandbox

    shared = AppContainerSandbox(shared_profile=True)
    try:
        assert shared.shared_profile is True
        assert shared._ensure_profile("acme-a") == shared._ensure_profile("acme-b")
    finally:
        shared.close()


def test_plugin_cannot_read_another_plugins_directory(sandboxed, tmp_path) -> None:
    trick = _write_plugin(
        tmp_path,
        "acme-trick",
        (
            "import os\n"
            "def after_detect(payload):\n"
            "    root = os.path.dirname(os.path.abspath(__file__))\n"
            "    other = os.path.join(os.path.dirname(root), 'acme-secret', 'plugin.py')\n"
            "    try:\n"
            "        data = open(other, encoding='utf-8').read()\n"
            "        return {'read': 'OK', 'data': data}\n"
            "    except OSError as error:\n"
            "        return {'read': 'BLOCKED', 'winerror': getattr(error, 'winerror', None)}\n"
        ),
    )
    _write_plugin(tmp_path, "acme-secret", "def after_detect(p):\n    return {}  # SIBLING-SECRET\n")
    service = sandboxed.service
    service.set_global_enabled(True)
    # Run the sibling FIRST so its directory has been granted to the sibling's
    # container: under a shared profile this grant would let the trick read the
    # secret (READ_OK); with per-plugin profiles the trick's SID never sees it.
    service.set_plugin_enabled("acme-secret", True)
    warm = service.run_hook("after_detect", {})
    assert warm["applied"] is True
    sibling_acl_was_granted = "acme-secret" in sandboxed.sandbox._profiles
    assert sibling_acl_was_granted

    service.set_plugin_enabled("acme-trick", True)
    outcome = service.run_hook("after_detect", {})

    assert outcome["applied"] is True
    result = next(
        item["result"] for item in outcome["results"] if item["plugin_id"] == "acme-trick"
    )
    assert result["read"] == "BLOCKED"
    assert "data" not in result


def test_interpreter_acl_is_granted_once_per_profile_sid(sandboxed, tmp_path) -> None:
    _write_plugin(tmp_path, "acme-cache", "def after_detect(p):\n    return {}\n")
    _write_plugin(tmp_path, "acme-cache-b", "def after_detect(p):\n    return {}\n")
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-cache", True)
    service.run_hook("after_detect", {})
    first = set(sandboxed.sandbox._interpreter_sids)
    service.run_hook("after_detect", {})
    assert set(sandboxed.sandbox._interpreter_sids) == first  # cached per SID
    assert len(first) == 1
    # a second plugin brings a second SID and its own one-time grant
    service.set_plugin_enabled("acme-cache-b", True)
    service.run_hook("after_detect", {})
    assert len(sandboxed.sandbox._interpreter_sids) == 2

# ---------------------------------------------------------------------------
# review r1: production wiring, minimal env, byte cap, job tree
# ---------------------------------------------------------------------------
def test_production_assembly_wires_the_sandbox(tmp_path) -> None:
    """The REAL production assembly constructs a sandboxed PluginService."""
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services

    class _Decoder:
        def decode(self, data: bytes):  # pragma: no cover - never called
            raise AssertionError("not used")

    class _Analyzer:
        def analyze(self, original_png: bytes, box):  # pragma: no cover
            raise AssertionError("not used")

    plugin = tmp_path / "plugins" / "acme-prod"
    plugin.mkdir(parents=True)
    (plugin / "plugin.py").write_text(
        "def after_detect(payload):\n"
        "    return {'ok': True}\n",
        encoding="utf-8",
    )
    (plugin / "manifest.json").write_text(
        json.dumps(_manifest("acme-prod")), encoding="utf-8"
    )
    core = assemble_core_services(
        tmp_path / "library.db",
        tmp_path / "managed",
        image_decoder=_Decoder(),
        font_catalog=object(),
        layout_engine=object(),
        compositor=object(),
        source_styles=SourceStyleService(_Analyzer()),
    )
    try:
        assert core.plugins is not None
        assert core.plugins._sandbox is not None, "production must run hooks sandboxed"
        assert core.plugins._sandbox.shared_profile is False
        core.plugins.set_global_enabled(True)
        core.plugins.set_plugin_enabled("acme-prod", True)
        outcome = core.plugins.run_hook("after_detect", {"pages": []})
        assert outcome["applied"] is True
    finally:
        core.conn.close()


def test_hook_child_sees_only_the_minimal_environment(sandboxed, tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("NEWMANGA_DATA_ROOT", "G:/secret")
    monkeypatch.setenv("M2RC1_PYTHON", "G:/secret/python.exe")
    monkeypatch.setenv("DSH_SECRET", "leak")
    source = (
        "import os\n"
        "def after_detect(payload):\n"
        "    return {'env': sorted(os.environ)}\n"
    )
    _write_plugin(tmp_path, "acme-env2", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-env2", True)

    outcome = service.run_hook("after_detect", {})

    env = outcome["results"][0]["result"]["env"]
    # Windows/AppContainer injects a few profile variables of its own; the
    # guarantee is that NO application-private, proxy or credential variable
    # crosses the boundary and the Python markers are present.
    assert "PYTHONIOENCODING" in env
    assert "PYTHONDONTWRITEBYTECODE" in env
    forbidden_prefixes = ("DSH_", "M2RC1_", "NEWMANGA_", "PYTEST_", "CODEX_", "ZCODE_", "AGY_")
    forbidden_exact = {
        "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
    }
    for key in env:
        assert not key.upper().startswith(forbidden_prefixes), key
        assert key.upper() not in forbidden_exact, key


def test_sandbox_output_cap_counts_bytes(sandboxed, tmp_path) -> None:
    source = (
        "def after_detect(payload):\n"
        "    return {'blob': '\u4e2d' * 100000}\n"
    )
    _write_plugin(tmp_path, "acme-loud2", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-loud2", True)

    outcome = service.run_hook("after_detect", {})

    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_FAILED"


def test_sandbox_job_kills_grandchildren(sandboxed, tmp_path) -> None:
    import ctypes

    source = (
        "import subprocess, sys\n"
        "def after_detect(payload):\n"
        "    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
        "    return {'pid': child.pid}\n"
    )
    _write_plugin(tmp_path, "acme-tree", source)
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-tree", True)

    outcome = service.run_hook("after_detect", {})
    assert outcome["applied"] is True
    pid = int(outcome["results"][0]["result"]["pid"])

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    # FLAKY-PYTEST-1: the kernel reclaims a closed job asynchronously, and under
    # heavy machine load the old fixed 2 s budget was occasionally exceeded even
    # though the tree died milliseconds later (the run itself, and a direct
    # AppContainerSandbox probe, killed the grandchild in ~20 ms).  A bounded
    # 20 s wait keeps the assertion strict — a genuinely leaked tree still
    # fails — without asserting on kernel-notification latency.
    still_alive = True
    deadline = time.monotonic() + 20.0
    while True:
        handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        try:
            still_alive = bool(handle)
        finally:
            if handle:
                kernel32.CloseHandle(ctypes.c_void_p(handle))
        if not still_alive or time.monotonic() >= deadline:
            break
        time.sleep(0.1)
    assert still_alive is False, "the job object must kill the whole tree"

# ---------------------------------------------------------------------------
# PLUGIN-RUNTIME-CAPABILITY-1: network capability enforcement
# ---------------------------------------------------------------------------
def _network_probe_source() -> str:
    """Connect to a public endpoint; report the error CLASS.

    AppContainer without the network capability fails with ``PermissionError``
    (the network stack is denied), while a plugin holding ``internetClient`` is
    allowed through and reaches the real network (success, or a timeout /
    connection error when the host/endpoint is unreachable from this machine).
    """
    return (
        "import socket\n"
        "def after_detect(payload):\n"
        "    try:\n"
        "        sock = socket.create_connection(('1.1.1.1', 443), timeout=4)\n"
        "        sock.close()\n"
        "        return {'net': 'OK'}\n"
        "    except OSError as error:\n"
        "        return {'net': 'BLOCKED', 'kind': type(error).__name__}\n"
    )


def test_network_capability_requires_the_network_permission(sandboxed, tmp_path) -> None:
    source = _network_probe_source()
    _write_plugin(tmp_path, "acme-no-net", source)
    _write_plugin(tmp_path, "acme-net", source, permissions=["network"])
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-no-net", True)
    service.set_plugin_enabled("acme-net", True)

    outcome = service.run_hook("after_detect", {})
    results = {item["plugin_id"]: item["result"] for item in outcome["results"]}

    # CAPABILITY-1: the container's network stack is denied for a plugin that
    # declares no permission; the network plugin is allowed through.
    assert results["acme-no-net"]["net"] == "BLOCKED"
    assert results["acme-no-net"]["kind"] == "PermissionError"
    assert results["acme-net"]["kind"] != "PermissionError"


def test_network_capability_survives_repeated_hooks(sandboxed, tmp_path) -> None:
    source = (
        "def after_detect(payload):\n"
        "    return {'ok': True}\n"
    )
    _write_plugin(tmp_path, "acme-net-repeat", source, permissions=["network"])
    service = sandboxed.service
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-net-repeat", True)
    for _ in range(3):
        outcome = service.run_hook("after_detect", {})
        assert outcome["applied"] is True
        assert outcome["errors"] == []


def test_manifest_rejects_unsupported_permissions_and_accepts_network(tmp_path) -> None:
    from infrastructure.plugins.manifest import ManifestError, parse_manifest

    def _write(permissions: list[str]) -> Path:
        plugin = tmp_path / ("p-" + "-".join(permissions or ["none"]).replace("_", "-"))
        plugin.mkdir(parents=True, exist_ok=True)
        (plugin / "plugin.py").write_text("def after_detect(p):\n    return {}\n", encoding="utf-8")
        (plugin / "manifest.json").write_text(
            json.dumps(
                {
                    "id": plugin.name,
                    "name": plugin.name,
                    "version": "1.0.0",
                    "entry": "plugin.py",
                    "hooks": ["after_detect"],
                    "permissions": permissions,
                }
            ),
            encoding="utf-8",
        )
        return plugin

    accepted = parse_manifest(_write(["network"]), app_version="0.1.0")
    assert accepted.permissions == ("network",)
    with pytest.raises(ManifestError) as excinfo:
        parse_manifest(_write(["files_read"]), app_version="0.1.0")
    assert excinfo.value.code == "PLUGIN_PERMISSIONS_UNSUPPORTED"
    with pytest.raises(ManifestError) as mixed:
        parse_manifest(_write(["network", "model"]), app_version="0.1.0")
    assert mixed.value.code == "PLUGIN_PERMISSIONS_UNSUPPORTED"
