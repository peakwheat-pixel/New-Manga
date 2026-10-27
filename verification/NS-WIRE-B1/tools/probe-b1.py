# -*- coding: utf-8 -*-
"""NS-WIRE-B1 AC1/AC2: wire-level probe of the 13 newly wired commands against the frozen
core_service (AC11 unlabelled copy), using exactly the payloads/minors recorded by
verification/NS-RECLASSIFY-1/reclassification.json.

The C# dispatcher test (NewManga.CoreClient.Tests Commands/CommandWiringB1Tests) proves the same
through the real Host command surface; this probe is the independent, byte-level record: request
line (protocol minor), response, basis (success / typed domain error) and the version controls
that show why the P15 settings face needs minor 7 and the DELETE face needs minor 10.

Usage:
  python verification/NS-WIRE-B1/tools/probe-b1.py --sidecar <dir with core_service.exe> \
      --output verification/NS-WIRE-B1/probe-results.json
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

DEFAULT_SIDECAR = r"G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy"
REPO = r"G:\CODEX\New Manga.workspace\worktrees\NS-WIRE-B1"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class CorePipe:
    def __init__(self, sidecar_dir, data_root):
        env_root = os.path.join(data_root, "_env")
        for sub in ("Roaming", "Local", "Temp"):
            os.makedirs(os.path.join(env_root, sub), exist_ok=True)
        for sub in ("derived", "catalog", "managed"):
            os.makedirs(os.path.join(data_root, sub), exist_ok=True)
        env = dict(os.environ)
        env.update(
            {
                "NEWMANGA_DATA_ROOT": data_root,
                "M2RC1_DERIVED_ROOT": os.path.join(data_root, "derived"),
                "M2RC2_CATALOG_DB": os.path.join(data_root, "catalog", "catalog.sqlite"),
                "M2RC1_MANAGED_ROOT": os.path.join(data_root, "managed"),
                "APPDATA": os.path.join(env_root, "Roaming"),
                "LOCALAPPDATA": os.path.join(env_root, "Local"),
                "TEMP": os.path.join(env_root, "Temp"),
            }
        )
        self.process = subprocess.Popen(
            [os.path.join(sidecar_dir, "core_service.exe")],
            cwd=sidecar_dir,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=0,
        )
        self.counter = 0

    def send(self, core_command, minor, payload, timeout=60.0):
        self.counter += 1
        request_id = f"b1-{self.counter:03d}"
        request = {
            "protocol": "new-manga.core",
            "version": {"major": 2, "minor": minor},
            "request_id": request_id,
            "command": core_command,
            "payload": payload,
        }
        request_line = json.dumps(request, ensure_ascii=True, separators=(",", ":"))
        self.process.stdin.write(request_line + "\n")
        self.process.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self.process.stdout.readline()
            if not raw:
                return request_line, None, None
            raw = raw.strip()
            if not raw:
                continue
            try:
                frame = json.loads(raw)
            except ValueError:
                continue
            if "event_type" in frame and "request_id" not in frame:
                continue
            return request_line, frame, raw
        return request_line, None, None

    def close(self):
        try:
            self.process.stdin.close()
        except Exception:
            pass
        try:
            self.process.wait(timeout=10)
        except Exception:
            self.process.kill()


def classify(frame):
    if frame is None:
        return "no_response", None, None
    error = frame.get("error")
    if not error:
        return "success", None, None
    code = error.get("code")
    category = error.get("category")
    if code == "UNKNOWN_COMMAND" or code == "PROTOCOL_VERSION_UNSUPPORTED":
        return "route_or_version_absent", code, category
    if code == "INVALID_REQUEST":
        return "payload_rejected", code, category
    if category in ("not_found", "conflict"):
        return "domain_error_handler_ran", code, category
    return "other_error", code, category


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sidecar", default=DEFAULT_SIDECAR)
    parser.add_argument("--output", default=os.path.join(REPO, "verification", "NS-WIRE-B1", "probe-results.json"))
    args = parser.parse_args()

    core_exe = os.path.join(args.sidecar, "core_service.exe")
    if not os.path.isfile(core_exe):
        raise SystemExit(f"core_service.exe not found under {args.sidecar}")

    data_root = os.path.join(tempfile.gettempdir(), "ns-b1-" + uuid.uuid4().hex[:8])
    os.makedirs(data_root, exist_ok=True)
    pipe = CorePipe(args.sidecar, data_root)
    results = []
    try:
        ping_line, ping_frame, ping_raw = pipe.send("core.ping", 3, {})
        ping = {
            "ns_command": "core_ping",
            "core_command": "core.ping",
            "minor": 3,
            "payload": {},
            "request_line": ping_line,
            "response": ping_frame,
            "response_raw": ping_raw,
            "basis": classify(ping_frame)[0],
        }
        if ping_frame is None:
            raise SystemExit("core.ping did not answer; cannot continue")

        backup_id = None
        profile_id = None
        book_id = None

        def probe(ns, core, minor, payload, note=None):
            request_line, frame, raw = pipe.send(core, minor, payload)
            basis, code, category = classify(frame)
            row = {
                "ns_command": ns,
                "core_command": core,
                "minor": minor,
                "payload": payload,
                "note": note,
                "request_line": request_line,
                "ok": frame is not None and frame.get("error") is None,
                "error_code": code,
                "error_category": category,
                "basis": basis,
                "result": (frame or {}).get("result"),
                "response_raw": raw,
            }
            results.append(row)
            return row

        def require_ok(row):
            if not row["ok"]:
                raise SystemExit(f"probe {row['ns_command']} unexpectedly failed: {row['error_code']} {row['basis']}")
            return row["result"]

        # cleanup / plugins / backup face (minor 3)
        probe("cleanup_retry_pending", "cleanup.retry_pending", 3, {})
        probe("plugins_audit_list", "plugins.audit_list", 3, {"limit": 5})
        probe(
            "plugins_set_plugin_enabled",
            "plugins.set_plugin_enabled",
            3,
            {"plugin_id": "no-such-plugin", "enabled": False},
            "typed PLUGIN_NOT_FOUND proves the handler runs",
        )
        created = require_ok(probe("backup_create", "backup.create", 3, {"backup_type": "manual"}, "control probe: yields backup_id"))
        backup_id = created.get("backup_id")
        require_ok(probe("backup_delete", "backup.delete", 3, {"backup_id": backup_id}))

        # P15 settings face (minor 7)
        created_profile = require_ok(
            probe(
                "settings_network_profiles_create",
                "settings_network_profiles_create",
                7,
                {"display_name": "NS-WIRE-B1 probe network", "mode": "Direct", "proxy_endpoint": None},
            )
        )
        profile_id = created_profile.get("profile", {}).get("network_profile_id")
        require_ok(probe("settings_network_profile_default_set", "settings_network_profile_default_set", 7, {"network_profile_id": profile_id}))
        require_ok(
            probe(
                "settings_network_profiles_update",
                "settings_network_profiles_update",
                7,
                {
                    "network_profile_id": profile_id,
                    "display_name": "NS-WIRE-B1 probe network v2",
                    "mode": "Direct",
                    "proxy_endpoint": None,
                    "verify_tls": True,
                    "allow_proxy_failure_direct_fallback": False,
                },
            )
        )
        require_ok(probe("settings_network_profile_default_clear", "settings_network_profile_default_clear", 7, {}))
        require_ok(probe("settings_network_profiles_delete", "settings_network_profiles_delete", 7, {"network_profile_id": profile_id}))
        require_ok(probe("settings_provider_bindings_clear", "settings_provider_bindings_clear", 7, {"scope": {"kind": "global"}, "capability": "Translation"}))
        require_ok(probe("settings_provider_bindings_resolve", "settings_provider_bindings_resolve", 7, {"capability": "Translation"}))
        probe(
            "settings_provider_run_snapshot_get",
            "settings_provider_run_snapshot_get",
            7,
            {"run_id": "no-such-run"},
            "typed TARGET_NOT_FOUND proves the handler runs",
        )

        # version controls: the same settings/deletion faces on the wrong minor must not be accepted
        probe(
            "settings_network_profile_default_set@minor3",
            "settings_network_profile_default_set",
            3,
            {"network_profile_id": "x"},
            "version control: P15 face must reject the pre-P15 minor",
        )

        # permanent delete face (minor 10, protocol CREATE face is minor 8)
        created_book = require_ok(probe("library_create_book", "CreateBook", 8, {"title": "NS-WIRE-B1 delete probe"}, "control probe: minor 8 CREATE face"))
        book_id = created_book.get("book_id")
        probe(
            "PermanentlyDeleteBook@minor3",
            "PermanentlyDeleteBook",
            3,
            {"book_id": "no-such-book", "confirm_permanent_delete": True},
            "version control: DELETE face must reject minors below 10",
        )
        require_ok(
            probe(
                "library_delete_book_permanently",
                "PermanentlyDeleteBook",
                10,
                {"book_id": book_id, "confirm_permanent_delete": True},
            )
        )

        payload = {
            "ac": "AC1/AC2/AC3",
            "task": "NS-WIRE-B1",
            "sidecar": core_exe,
            "sidecar_sha256": sha256_file(core_exe),
            "reclassification_source": "verification/NS-RECLASSIFY-1/reclassification.json",
            "data_root": data_root,
            "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ping": ping,
            "results": results,
            "summary": {
                "probes": len(results),
                "wired_commands_probed": len({r["ns_command"] for r in results if "@" not in r["ns_command"]}) ,
                "success": sum(1 for r in results if r["basis"] == "success"),
                "typed_domain_error": sum(1 for r in results if r["basis"] == "domain_error_handler_ran"),
                "version_controls": sum(1 for r in results if "@" in r["ns_command"]),
            },
        }
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(json.dumps(payload["summary"], ensure_ascii=False))
        for row in results:
            print(f"{row['ns_command']:<55} {row['core_command']:<42} minor={row['minor']:<3} basis={row['basis']} code={row['error_code']}")
    finally:
        pipe.close()
        shutil.rmtree(data_root, ignore_errors=True)


if __name__ == "__main__":
    main()
