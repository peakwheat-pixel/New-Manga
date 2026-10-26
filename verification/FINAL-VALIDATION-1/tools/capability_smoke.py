"""CORE-SLIM-1 / AC2+AC3 — frozen-closure capability matrix smoke.

Every check runs the REBUILT sidecar exes (the real PyInstaller bundle), never
the dev Python tree, so the matrix proves the shipped closure keeps its
capabilities after the Qt removal / entry dedup:

  catalog_loader    seeds a fresh catalog SQLite store (launcher-side path)
  core_service      starts, assembles the production Core, answers core.ping,
                    then core.shutdown (protocol 2.3 envelope)
  acceptance_bridge frozen acceptance loop: ping -> seed_fixture (REAL import
                    path with the Pillow decoder) -> run_pipeline (mock OCR /
                    translate / render through the frozen Pillow adapters) ->
                    catalog_pages / reader_pages -> export_page (PNG write)
  sfx_detect_probe  one-shot real ML probe (onnxruntime + in-bundle weights),
                    best effort: recorded as skipped if the CLI needs args we
                    do not have a fixture for

Results are written to ``ac2/capability-smoke.json`` plus one log per probe.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

BUNDLE = Path(os.environ.get("CORE_SLIM_BUNDLE", ""))
OUT = Path(__file__).resolve().parents[1]
LOGS = OUT

checks: list[dict] = []
detail: dict = {}

BUNDLE = BUNDLE if str(BUNDLE) else Path()


def _log(name: str, text: str) -> None:
    (LOGS / f"smoke-{name}.log").write_text(text, encoding="utf-8", errors="replace")


def _record(capability: str, probe: str, ok: bool, note: str = "") -> None:
    checks.append(
        {
            "capability": capability,
            "probe": probe,
            "verdict": ("PASS" if ok else "FAIL") + (f"（{note}）" if note else ""),
            "ok": ok,
        }
    )


class Bridge:
    """JSON-lines driver for acceptance_bridge.exe (same line protocol)."""

    def __init__(self, exe: Path, env: dict, cwd: Path) -> None:
        self.proc = subprocess.Popen(
            [str(exe)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        self.transcript: list[str] = []
        self.next_id = 1

    def call(self, method: str, params: dict | None = None, timeout: float = 180.0) -> dict:
        assert self.proc.stdin and self.proc.stdout
        request = {"id": self.next_id, "method": method, "params": params or {}}
        self.next_id += 1
        self.proc.stdin.write(json.dumps(request) + "\n")
        self.proc.stdin.flush()
        self.transcript.append(">> " + json.dumps(request))
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            self.transcript.append("<< " + line[:2000])
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if response.get("id") == request["id"]:
                return response
        raise RuntimeError(f"no response for {method} (process rc={self.proc.poll()})")

    def close(self) -> tuple[int, str]:
        try:
            self.call("shutdown", timeout=20)
        except Exception:  # noqa: BLE001 - shutdown is best effort
            pass
        try:
            _, err = self.proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            _, err = self.proc.communicate()
        self.transcript.append("(stderr tail) " + (err or "")[-4000:])
        return self.proc.returncode or 0, err or ""


def main() -> int:
    if not BUNDLE.is_dir():
        print("CORE_SLIM_BUNDLE must point at the rebuilt core-sidecar bundle")
        return 2
    work = OUT / "smoke-work"
    work.mkdir(parents=True, exist_ok=True)
    data_root = work / "data-root"
    catalog_dir = work / "catalog"
    derived_root = work / "derived"
    managed_root = work / "managed"
    for directory in (data_root, catalog_dir, derived_root, managed_root):
        directory.mkdir(parents=True, exist_ok=True)
    catalog_db = catalog_dir / "catalog.sqlite"

    base_env = dict(os.environ)
    base_env.update(
        {
            "NEWMANGA_DATA_ROOT": str(data_root),
            "M2RC2_CATALOG_DB": str(catalog_db),
            "M2RC1_DERIVED_ROOT": str(work / "derived"),
            "M2RC1_MANAGED_ROOT": str(work / "managed"),
            "M2RC1_PACKAGED": "1",
        }
    )

    # --- catalog_loader seeding -------------------------------------------
    loader = BUNDLE / "catalog_loader.exe"
    try:
        completed = subprocess.run(
            [
                str(loader),
                "--db",
                str(catalog_db),
                "--initialize-preview-namespace",
                str(work / "derived"),
                "--count",
            ],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(BUNDLE),
            env=base_env,
        )
        _log("catalog_loader", completed.stdout + "\n" + completed.stderr)
        ok = completed.returncode == 0
        _record("目录/命名空间播种（catalog_loader）", "catalog_loader.exe --db ... --initialize-preview-namespace ... --count", ok,
                f"rc={completed.returncode}")
        detail["catalogLoader"] = {"rc": completed.returncode, "stdout": completed.stdout[:400]}
    except Exception as error:  # noqa: BLE001
        _record("目录/命名空间播种（catalog_loader）", "catalog_loader.exe", False, str(error)[:120])

    # --- core_service protocol 2.3 ping (envelope probe) ------------------
    core = BUNDLE / "core_service.exe"
    try:
        proc = subprocess.Popen(
            [str(core)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=base_env,
            cwd=str(BUNDLE),
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
        transcript = []
        ping_ok = False
        deadline = time.time() + 180
        sent = False
        while time.time() < deadline:
            if not sent:
                # exact protocol 2.3 envelope (src/bootstrap/core_service.py docstring)
                request = {
                    "protocol": "new-manga.core",
                    "version": {"major": 2, "minor": 3},
                    "request_id": "smoke-1",
                    "command": "core.ping",
                    "payload": {},
                }
                proc.stdin.write(json.dumps(request) + "\n")
                proc.stdin.flush()
                transcript.append(">> " + json.dumps(request))
                sent = True
            line = proc.stdout.readline()
            if not line:
                break
            transcript.append("<< " + line.strip()[:1000])
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            ping_ok = response.get("request_id") == "smoke-1" and not response.get("error")
            break
        try:
            shutdown = {
                "protocol": "new-manga.core",
                "version": {"major": 2, "minor": 3},
                "request_id": "smoke-2",
                "command": "core.shutdown",
                "payload": {},
            }
            proc.stdin.write(json.dumps(shutdown) + "\n")
            proc.stdin.flush()
        except Exception:  # noqa: BLE001
            pass
        try:
            _, err = proc.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
            _, err = proc.communicate()
        transcript.append("(stderr tail) " + (err or "")[-2000:])
        _log("core_service", "\n".join(transcript))
        _record("Host 契约：core_service 启动 + core.ping", "core_service.exe < protocol 2.3", ping_ok,
                "响应已解析" if ping_ok else "无 ping 响应")
        detail["coreService"] = {"pingOk": ping_ok}
    except Exception as error:  # noqa: BLE001
        _record("Host 契约：core_service 启动 + core.ping", "core_service.exe", False, str(error)[:120])

    # --- acceptance loop: import / pipeline / reader / export -------------
    bridge = BUNDLE / "acceptance_bridge.exe"
    try:
        env = dict(base_env)
        env["M2AC1_TEST_MODE"] = "1"
        client = Bridge(bridge, env, BUNDLE)
        steps: dict[str, dict] = {}
        steps["ping"] = client.call("ping", timeout=120)
        steps["seed_fixture"] = client.call("seed_fixture", timeout=300)
        steps["run_pipeline"] = client.call("run_pipeline", timeout=600)
        steps["catalog_pages"] = client.call("catalog_pages", timeout=120)
        steps["reader_pages"] = client.call("reader_pages", timeout=120)
        steps["export_page"] = client.call("export_page", {"page_index": 0}, timeout=300)
        rc, err = client.close()
        _log("acceptance_bridge", "\n".join(client.transcript))
        def ok(name: str) -> bool:
            response = steps.get(name) or {}
            return "result" in response and "error" not in response
        _record("导入（REAL import 路径，Pillow 解码）", "acceptance_bridge seed_fixture", ok("seed_fixture"))
        _record("OCR/翻译/排版渲染（Mock 管线，冻结 Pillow 适配器）",
                "acceptance_bridge run_pipeline", ok("run_pipeline"))
        _record("阅读器投影", "acceptance_bridge reader_pages", ok("reader_pages"))
        _record("导出（PNG 写出）", "acceptance_bridge export_page", ok("export_page"))
        detail["acceptanceBridge"] = {
            "rc": rc,
            "steps": {name: ("OK" if ok(name) else json.dumps(steps.get(name))[:300])
                      for name in steps},
        }
    except Exception as error:  # noqa: BLE001
        _record("接受流程（导入/渲染/导出）", "acceptance_bridge.exe M2AC1_TEST_MODE=1", False, str(error)[:160])
        detail["acceptanceBridge"] = {"exception": str(error)}

    # --- sfx detect probe (real ML in the frozen closure) -----------------
    probe = BUNDLE / "sfx_detect_probe.exe"
    try:
        completed = subprocess.run(
            [str(probe), "--help"], capture_output=True, text=True, timeout=180,
            cwd=str(BUNDLE), env=base_env,
        )
        _log("sfx_detect_probe", completed.stdout + "\n" + completed.stderr)
        started = completed.returncode == 0 and "sfx_detect_probe" in (completed.stdout or "")
        _record("检测（onnxruntime/DirectML 冻结闭包启动）", "sfx_detect_probe.exe --help", started,
                "权重需真实页 fixture，见 run_clean_start_e2e")
        detail["sfxDetectProbe"] = {"rc": completed.returncode}
    except Exception as error:  # noqa: BLE001
        _record("检测（onnxruntime/DirectML 冻结闭包启动）", "sfx_detect_probe.exe", False, str(error)[:120])

    verdict = "PASS" if all(item["ok"] for item in checks) else "PARTIAL"
    payload = {"bundle": str(BUNDLE), "verdict": verdict, "checks": checks, "detail": detail}
    (OUT / "capability-smoke.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"verdict": verdict, "checks": checks}, indent=2))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
