"""Route A -- capability-scoped resource reference / token.

Measured question
-----------------
Can a scoped, signed, expiring *reference* move a large media resource
between two processes without the media bytes ever entering the message
channel, and does the reference enforce the scope/permission/lifecycle rules
that large-media safety requires?

Shape
-----
``core`` (child process, owns the signing key and the scope root) speaks
newline-delimited JSON over stdin/stdout. ``host`` (this parent process) asks
for a reference, then asks Core to resolve it, then reads the file itself when
Core approves. Media never crosses the pipes; only the reference and the
approval/denial travel.

Roles
-----
  python probe_a_token.py --role core --lab <lab> --scope <dir>   # child
  python probe_a_token.py --lab <lab> --out <json>                # host

Status vocabulary is per-scenario: PASS / FAIL / BLOCKED / NOT_RUN.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import m2s1_lab as lab  # noqa: E402

PROBE = "A"
SCOPE_SUBDIRS = ("derived", "managed")
LIMIT = lab.MEDIA_LIMIT_BYTES


# --------------------------------------------------------------------------
# core role
# --------------------------------------------------------------------------


def run_core(lab_root: Path, scope_root: Path) -> int:
    import contextlib

    secret = bytes.fromhex(os.environ["M2S1_TOKEN_SECRET"])
    resolver = lab.ScopedResourceResolver(scope_root, secret)
    started = time.time()
    report: dict = {"role": "core", "pid": os.getpid(), "secret_hex_length": len(secret.hex())}

    def write(payload: dict) -> None:
        sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
        sys.stdout.flush()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        request = json.loads(line)
        op = request.get("op")
        request_id = request.get("request_id")
        try:
            if op == "ping":
                write({"request_id": request_id, "ok": True, "pid": os.getpid()})
                continue
            if op == "mint":
                ttl = request.get("ttl_seconds", 60)
                if ttl == "already_expired":
                    expires_at = started - 3600
                else:
                    expires_at = started + float(ttl)
                token = lab.mint_token(
                    secret,
                    resource_id=request["rid"],
                    rel_path=request["rel"],
                    scope=request.get("scope", "derived-read-only"),
                    expires_at=expires_at,
                    mode=request.get("mode", "read"),
                )
                write({"request_id": request_id, "ok": True, "ref": token})
                continue
            if op == "revoke":
                resolver.revoked.add(request["rid"])
                write({"request_id": request_id, "ok": True})
                continue
            if op == "resolve":
                with lab.Timer() as timer:
                    path = resolver.resolve(request["ref"], mode=request.get("mode", "read"))
                write(
                    {
                        "request_id": request_id,
                        "ok": True,
                        "path": str(path),
                        "resolve_ms": round(timer.seconds * 1000, 3),
                        "trace": resolver.trace[-1],
                    }
                )
                continue
            if op == "stats":
                write(
                    {
                        "request_id": request_id,
                        "ok": True,
                        "memory": lab.memory_counters(),
                        "revoked": sorted(resolver.revoked),
                    }
                )
                continue
            if op == "shutdown":
                write({"request_id": request_id, "ok": True})
                break
            write({"request_id": request_id, "ok": False, "error_code": "UNKNOWN_OP", "op": op})
        except lab.ProbeError as error:
            write(
                {
                    "request_id": request_id,
                    "ok": False,
                    "error_code": error.code,
                    "error_message": error.message,
                }
            )
        except Exception as error:  # noqa: BLE001 - report, never crash the channel
            write(
                {
                    "request_id": request_id,
                    "ok": False,
                    "error_code": "CORE_EXCEPTION",
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                }
            )
    report["memory"] = lab.memory_counters()
    report_path = lab_root / "probeA-core-report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return 0


# --------------------------------------------------------------------------
# host role
# --------------------------------------------------------------------------


class CoreChannel:
    """Newline-JSON channel with byte accounting for both directions."""

    def __init__(self, command: list[str], env: dict) -> None:
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.bytes_to_core = 0
        self.bytes_from_core = 0
        self._next = 0

    def request(self, **payload) -> dict:
        payload["request_id"] = f"r{self._next}"
        self._next += 1
        line = json.dumps(payload, separators=(",", ":")) + "\n"
        self.bytes_to_core += len(line.encode("utf-8"))
        self.proc.stdin.write(line.encode("utf-8"))
        self.proc.stdin.flush()
        raw = self.proc.stdout.readline()
        if not raw:
            raise lab.ProbeError("CHANNEL_CLOSED", "core stdout closed")
        self.bytes_from_core += len(raw)
        return json.loads(raw.decode("utf-8"))

    def close(self) -> dict:
        try:
            self.request(op="shutdown")
        except Exception:  # noqa: BLE001
            pass
        try:
            self.proc.stdin.close()
        except Exception:  # noqa: BLE001
            pass
        stderr = self.proc.stderr.read().decode("utf-8", errors="replace")
        code = self.proc.wait(timeout=60)
        return {
            "exit_code": code,
            "stderr": stderr[-2000:],
            "bytes_to_core": self.bytes_to_core,
            "bytes_from_core": self.bytes_from_core,
        }


def seed_scope(lab_root: Path, fixture_dir: Path) -> dict:
    scope = lab_root / "probeA" / "scope"
    outside = lab_root / "probeA" / "outside"
    scope.mkdir(parents=True, exist_ok=True)
    outside.mkdir(parents=True, exist_ok=True)
    for sub in SCOPE_SUBDIRS:
        (scope / sub).mkdir(parents=True, exist_ok=True)
    manifest = json.loads((fixture_dir / "fixtures.json").read_text(encoding="utf-8"))
    placed: dict[str, dict] = {}
    methods = set()
    for entry in manifest["fixtures"]:
        target = scope / "derived" / f"{entry['name']}.png"
        if target.exists():
            target.unlink()
        source = Path(entry["path"])
        try:
            os.link(source, target)
            methods.add("hardlink")
        except OSError:
            shutil.copyfile(source, target)
            methods.add("copy")
        placed[entry["name"]] = {
            "rel": f"derived/{entry['name']}.png",
            "bytes": target.stat().st_size,
            "sha256": lab.sha256_file(target),
        }
        if entry["name"] == "small_page_800x1200":
            managed = scope / "managed" / "managed_small.png"
            if managed.exists():
                managed.unlink()
            try:
                os.link(source, managed)
                methods.add("hardlink")
            except OSError:
                shutil.copyfile(source, managed)
                methods.add("copy")
            placed["managed_small"] = {
                "rel": "managed/managed_small.png",
                "bytes": managed.stat().st_size,
                "sha256": lab.sha256_file(managed),
            }
    # a stand-in "user source file" that the scope must never reach
    secret = outside / "user_source_stand_in.png"
    secret.write_bytes(b"\x89PNG\r\n\x1a\n" + os.urandom(4096))
    return {"scope": str(scope), "outside": str(outside), "placed": placed, "link_methods": sorted(methods)}


def scenario_table(placed: dict) -> list[dict]:
    return [
        {"id": "A-01-small", "kind": "happy_path", "fixture": "small_page_800x1200", "ttl": 600},
        {"id": "A-02-typical", "kind": "happy_path", "fixture": "typical_page_1600x2400", "ttl": 600},
        {"id": "A-03-webtoon-tile", "kind": "happy_path", "fixture": "webtoon_tile_00_800x4000", "ttl": 600},
        {"id": "A-04-webtoon-long-page", "kind": "happy_path", "fixture": "webtoon_long_800x24000", "ttl": 600},
        {
            "id": "A-05-oversize-rejection",
            "kind": "happy_path",
            "fixture": "oversize_2000x12000",
            "ttl": 600,
            "expect_host_read": "reject",
        },
        {"id": "A-06-expired", "kind": "expired", "fixture": "small_page_800x1200"},
        {"id": "A-07-revoked", "kind": "revoked", "fixture": "typical_page_1600x2400"},
        {"id": "A-08-tampered-signature", "kind": "tampered", "fixture": "small_page_800x1200"},
        {"id": "A-09-traversal", "kind": "traversal_rel", "rel": "../outside/user_source_stand_in.png"},
        {"id": "A-10-absolute-path", "kind": "absolute_rel", "rel": None},
        {"id": "A-11-write-mode", "kind": "write_mode", "fixture": "small_page_800x1200"},
        {"id": "A-12-scope-denied", "kind": "scope_denied", "fixture": "small_page_800x1200"},
        {"id": "A-13-reparse-escape-outside", "kind": "reparse_escape", "fixture": "small_page_800x1200"},
        {"id": "A-14-missing-file", "kind": "missing", "fixture": "small_page_800x1200"},
        {"id": "A-15-reparse-junction-inside", "kind": "reparse_inside", "fixture": "small_page_800x1200"},
    ]


def run_host(lab_root: Path) -> dict:
    fixture_dir = lab_root / "fixtures"
    seeded = seed_scope(lab_root, fixture_dir)
    placed = seeded["placed"]
    scope = Path(seeded["scope"])

    # Two junctions, both created without administrator rights (junctions,
    # unlike symlinks, do not need SeCreateSymbolicLinkPrivilege):
    #   escape_link      -> outside the scope root  (containment must catch it)
    #   link_to_managed  -> scope/managed, i.e. *inside* the scope root, so
    #                       containment passes and only the reparse walk can
    #                       reject it (the real defence-in-depth case).
    junction_specs = [
        ("derived/escape_link", Path(seeded["outside"])),
        ("derived/link_to_managed", scope / "managed"),
    ]
    junctions: list[dict] = []
    for relative, target in junction_specs:
        link = scope / relative
        if link.exists():
            os.rmdir(link)
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            timeout=30,
        )
        junctions.append(
            {
                "relative": relative,
                "target": str(target),
                "created": created.returncode == 0 and link.exists(),
                "output": (created.stdout + created.stderr).decode("utf-8", errors="replace")[:200],
            }
        )
    junction_created = all(entry["created"] for entry in junctions)
    junction_detail = "; ".join(f"{e['relative']}->{e['target']} created={e['created']}" for e in junctions)

    secret = os.urandom(32)
    env = dict(os.environ)
    env["M2S1_TOKEN_SECRET"] = secret.hex()
    env["PYTHONHASHSEED"] = "0"
    script = os.path.abspath(__file__)
    core_report_path = lab_root / "probeA-core-report.json"
    if core_report_path.exists():
        core_report_path.unlink()  # never read a stale report as this run's result
    channel = CoreChannel(
        [lab.python_exe(), script, "--role", "core", "--lab", str(lab_root), "--scope", str(scope)],
        env,
    )
    assert channel.request(op="ping")["ok"]

    results: list[dict] = []
    total_media_bytes_delivered = 0
    for scenario in scenario_table(placed):
        record: dict = {"id": scenario["id"], "kind": scenario["kind"], "status": lab.NOT_RUN}
        host_before = lab.memory_counters()
        try:
            kind = scenario["kind"]
            if kind in ("happy_path", "write_mode", "scope_denied", "missing"):
                entry = placed[scenario["fixture"]]
                fixtures = json.loads((fixture_dir / "fixtures.json").read_text(encoding="utf-8"))["fixtures"]
                expected_bytes = next(f["png_bytes"] for f in fixtures if f["name"] == scenario["fixture"])
                expected_sha = entry["sha256"]
                scope_class = "user-source" if kind == "scope_denied" else "derived-read-only"
                minted = channel.request(
                    op="mint",
                    rid=f"rid-{scenario['id']}",
                    rel=entry["rel"],
                    ttl_seconds=scenario.get("ttl", 600),
                    scope=scope_class,
                    mode="write" if kind == "write_mode" else "read",
                )
                if kind == "missing":
                    (scope / entry["rel"]).unlink()
                record["token_chars"] = len(minted["ref"])
                with lab.Timer() as resolve_timer:
                    resolved = channel.request(
                        op="resolve", ref=minted["ref"], mode="write" if kind == "write_mode" else "read"
                    )
                record["resolve_ms"] = round(resolve_timer.seconds * 1000, 3)
                record["core_resolve_ms"] = resolved.get("resolve_ms")
                if not resolved["ok"]:
                    record["error_code"] = resolved["error_code"]
                    record["status"] = lab.PASS if kind in ("write_mode", "scope_denied", "missing") else lab.FAIL
                    record["expected_rejection"] = True
                else:
                    if kind in ("write_mode", "scope_denied", "missing"):
                        record["status"] = lab.FAIL
                        record["note"] = "expected rejection but Core approved"
                    else:
                        path = Path(resolved["path"])
                        if scenario["id"] == "A-05-oversize-rejection":
                            try:
                                payload, meta = lab.read_file_bounded(path, LIMIT)
                                record["status"] = lab.FAIL
                                record["note"] = f"oversize read unexpectedly allowed ({len(payload)} bytes)"
                            except lab.ProbeError as error:
                                record["error_code"] = error.code
                                record["expected_rejection"] = True
                                record["status"] = lab.PASS
                                record["host_read_skipped_bytes"] = lab.os.path.getsize(path)
                        else:
                            with lab.Timer() as read_timer:
                                digest = lab.sha256_file(path)
                            record["read_ms"] = round(read_timer.seconds * 1000, 3)
                            record["bytes_read"] = lab.os.path.getsize(path)
                            record["sha256_match"] = digest == expected_sha
                            record["media_bytes"] = expected_bytes
                            total_media_bytes_delivered += lab.os.path.getsize(path)
                            record["status"] = lab.PASS if digest == expected_sha else lab.FAIL
            elif kind == "expired":
                entry = placed[scenario["fixture"]]
                minted = channel.request(
                    op="mint", rid="rid-expired", rel=entry["rel"], ttl_seconds="already_expired"
                )
                resolved = channel.request(op="resolve", ref=minted["ref"])
                record["error_code"] = resolved.get("error_code")
                record["status"] = lab.PASS if resolved.get("error_code") == "REF_EXPIRED" else lab.FAIL
            elif kind == "revoked":
                entry = placed[scenario["fixture"]]
                minted = channel.request(op="mint", rid="rid-revoked", rel=entry["rel"], ttl_seconds=600)
                first = channel.request(op="resolve", ref=minted["ref"])
                channel.request(op="revoke", rid="rid-revoked")
                second = channel.request(op="resolve", ref=minted["ref"])
                record["first_resolve_ok"] = first["ok"]
                record["after_revoke_error"] = second.get("error_code")
                record["status"] = (
                    lab.PASS
                    if first["ok"] and second.get("error_code") == "REF_REVOKED"
                    else lab.FAIL
                )
            elif kind == "tampered":
                entry = placed[scenario["fixture"]]
                minted = channel.request(op="mint", rid="rid-tamper", rel=entry["rel"], ttl_seconds=600)
                head, body, signature = minted["ref"].split(".")
                flipped = ("A" if body[0] != "A" else "B") + body[1:]
                resolved = channel.request(op="resolve", ref=f"{head}.{flipped}.{signature}")
                record["error_code"] = resolved.get("error_code")
                record["status"] = (
                    lab.PASS if resolved.get("error_code") == "REF_SIGNATURE_INVALID" else lab.FAIL
                )
            elif kind == "traversal_rel":
                minted = channel.request(
                    op="mint", rid="rid-traversal", rel=scenario["rel"], ttl_seconds=600
                )
                resolved = channel.request(op="resolve", ref=minted["ref"])
                record["error_code"] = resolved.get("error_code")
                record["status"] = lab.PASS if resolved.get("error_code") == "REF_OUT_OF_SCOPE" else lab.FAIL
            elif kind == "absolute_rel":
                target = (Path(seeded["outside"]) / "user_source_stand_in.png").resolve()
                minted = channel.request(
                    op="mint", rid="rid-absolute", rel=str(target), ttl_seconds=600
                )
                resolved = channel.request(op="resolve", ref=minted["ref"])
                record["error_code"] = resolved.get("error_code")
                record["status"] = lab.PASS if resolved.get("error_code") == "REF_OUT_OF_SCOPE" else lab.FAIL
            elif kind in ("reparse_escape", "reparse_inside"):
                if not junction_created:
                    record["status"] = lab.NOT_RUN
                    record["note"] = f"junction not created: {junction_detail}"
                else:
                    if kind == "reparse_escape":
                        relative = "derived/escape_link/user_source_stand_in.png"
                        expected = "REF_OUT_OF_SCOPE"
                    else:
                        relative = "derived/link_to_managed/managed_small.png"
                        expected = "REF_REPARSE_POINT"
                    minted = channel.request(
                        op="mint", rid=f"rid-{scenario['id']}", rel=relative, ttl_seconds=600
                    )
                    resolved = channel.request(op="resolve", ref=minted["ref"])
                    record["rel"] = relative
                    record["expected_error_code"] = expected
                    record["error_code"] = resolved.get("error_code")
                    record["status"] = lab.PASS if resolved.get("error_code") == expected else lab.FAIL
        except lab.ProbeError as error:
            record["status"] = lab.FAIL
            record["error_code"] = error.code
            record["error_message"] = error.message
        except Exception as error:  # noqa: BLE001
            record["status"] = lab.FAIL
            record["error_type"] = type(error).__name__
            record["error_message"] = str(error)
        host_after = lab.memory_counters()
        record["host_peak_working_set_mb"] = host_after["peak_working_set_mb"]
        record["host_working_set_delta_mb"] = round(
            host_after["working_set_mb"] - host_before["working_set_mb"], 3
        )
        results.append(record)
        suffix = record.get("error_code") or ""
        print(f"  {record['id']}: {record['status']} {suffix}".rstrip(), flush=True)

    stats = channel.request(op="stats")
    channel_info = channel.close()
    core_report = json.loads(core_report_path.read_text(encoding="utf-8")) if core_report_path.exists() else {}

    result = {
        "probe": PROBE,
        "route": "capability-scoped resource reference / token",
        "label": "PROPOSAL (research prototype; no product runtime)",
        "limit_bytes": LIMIT,
        "limit_label": "probe-configured controlled rejection limit, NOT a product threshold",
        "scope_root": seeded["scope"],
        "outside_root": seeded["outside"],
        "seed_methods": seeded["link_methods"],
        "junction_created": junction_created,
        "junction_detail": junction_detail,
        "junctions": junctions,
        "host_pid": os.getpid(),
        "host_memory": lab.memory_counters(),
        "channel": channel_info,
        "channel_media_bytes": 0,
        "channel_media_bytes_note": (
            "the JSON control channel carried no media payload; "
            "it is measured separately from the out-of-band file reads"
        ),
        "media_bytes_delivered_out_of_band": total_media_bytes_delivered,
        "core_stats": stats,
        "core_report": core_report,
        "scenarios": results,
        "summary": {
            "pass": sum(1 for r in results if r["status"] == lab.PASS),
            "fail": sum(1 for r in results if r["status"] == lab.FAIL),
            "blocked": sum(1 for r in results if r["status"] == lab.BLOCKED),
            "not_run": sum(1 for r in results if r["status"] == lab.NOT_RUN),
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", default="host", choices=("host", "core"))
    parser.add_argument("--lab", default=str(lab.DEFAULT_LAB))
    parser.add_argument("--scope")
    parser.add_argument("--out")
    args = parser.parse_args()

    lab_root = lab.lab_root(args.lab)
    if args.role == "core":
        return run_core(lab_root, Path(args.scope))
    result = run_host(lab_root)
    out = args.out or str(lab_root / "probeA-result.json")
    return lab.emit(result, out)


if __name__ == "__main__":
    raise SystemExit(main())
