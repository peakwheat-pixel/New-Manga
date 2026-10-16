"""Run one local Core-sidecar P18 probe without touching a user library."""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

from PIL import Image


PROTOCOL = {"protocol": "new-manga.core", "version": {"major": 2, "minor": 1}}


def _request(request_id: str, command: str, payload: dict | None = None) -> dict:
    return {
        **PROTOCOL,
        "request_id": request_id,
        "command": command,
        "payload": payload or {},
    }


def _response_summary(stdout: str) -> list[dict]:
    rows = []
    for line in stdout.splitlines():
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            rows.append({"unparsed_line": line})
            continue
        row = {"request_id": response.get("request_id")}
        error = response.get("error")
        result = response.get("result")
        if error:
            row["error"] = {
                "code": error.get("code"),
                "category": error.get("category"),
                "message": error.get("message"),
            }
        elif isinstance(result, dict):
            row["result"] = {
                key: result[key]
                for key in ("status", "protocol_version", "capabilities", "elapsed_ms")
                if key in result
            }
            if isinstance(result.get("candidates"), list):
                row["result"]["candidate_count"] = len(result["candidates"])
        else:
            row["result_type"] = type(result).__name__
        rows.append(row)
    return rows


def _self_check() -> None:
    response = '{"request_id":"self-check","result":{"status":"ready"},"error":null}'
    assert _response_summary(response) == [
        {"request_id": "self-check", "result": {"status": "ready"}}
    ]


def main() -> int:
    _self_check()
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=("ja", "ko"), required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    image_path = args.image.resolve(strict=True)
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    image_bytes = image_path.read_bytes()
    with Image.open(image_path) as image:
        image_format = image.format
        width, height = image.size
    if image_format not in {"PNG", "JPEG"}:
        raise ValueError(f"Core detect accepts PNG/JPEG, got {image_format!r}")

    image_hash = hashlib.sha256(image_bytes).hexdigest()
    data_root = output / "data"
    detect_payload = {
        "page": base64.b64encode(image_bytes).decode("ascii"),
        "width": width,
        "height": height,
    }
    requests = [
        _request(f"p18-{args.lang}-ping", "core.ping"),
        # This is a deliberate real IPC probe: the current production allowlist
        # has no import command, so P18 can record the frozen boundary directly.
        _request(f"p18-{args.lang}-import", "ImportPages"),
        _request(f"p18-{args.lang}-detect", "core.detect", detect_payload),
        _request(f"p18-{args.lang}-shutdown", "core.shutdown"),
    ]
    request_text = "".join(json.dumps(request, ensure_ascii=False) + "\n" for request in requests)

    env = os.environ.copy()
    for name in tuple(env):
        if any(marker in name.upper() for marker in ("KEY", "SECRET", "TOKEN")):
            env.pop(name)
    env.update(
        {
            "PYTHONPATH": str(Path("src").resolve()),
            "PYTHONDONTWRITEBYTECODE": "1",
            "NEWMANGA_DATA_ROOT": str(data_root),
            "M2RC1_DERIVED_ROOT": str(data_root / "derived"),
            "M2RC2_CATALOG_DB": str(data_root / "catalog" / "catalog.sqlite"),
            "NEWMANGA_DETECTOR_BACKEND": "manga",
            "NEWMANGA_DETECTOR_DEVICE": "cpu",
        }
    )
    for name in ("NEWMANGA_DETECTOR_WEIGHTS", "NEWMANGA_SFX_WEIGHTS"):
        env.pop(name, None)

    started = perf_counter()
    timed_out = False
    try:
        process = subprocess.run(
            [sys.executable, "-B", "-m", "bootstrap.core_service"],
            cwd=Path.cwd(),
            env=env,
            input=request_text.encode("utf-8"),
            capture_output=True,
            timeout=240,
            check=False,
        )
        stdout, stderr, returncode = process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired as error:
        timed_out = True
        stdout = error.stdout if isinstance(error.stdout, bytes) else (error.stdout or b"")
        stderr = error.stderr if isinstance(error.stderr, bytes) else (error.stderr or b"")
        returncode = 124

    (output / "sidecar-stdout.bin").write_bytes(stdout)
    (output / "sidecar-stderr.bin").write_bytes(stderr)
    decoded_stdout = stdout.decode("utf-8", "replace")
    (output / "sidecar-stdout.jsonl").write_text(decoded_stdout, encoding="utf-8")
    (output / "sidecar-stderr.log").write_text(stderr.decode("utf-8", "replace"), encoding="utf-8")
    (output / "sidecar-exit-code.txt").write_text(f"{returncode}\n", encoding="ascii")
    (output / "request-sequence.json").write_text(
        json.dumps(
            [{"request_id": row["request_id"], "command": row["command"]} for row in requests],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        git_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path.cwd(),
            check=True,
            capture_output=True,
            text=True,
            encoding="ascii",
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_head = "unavailable"
    package_versions = {}
    for label in ("PIL", "PySide6", "onnxruntime", "torch", "doctr", "manga_ocr", "paddleocr"):
        try:
            package_versions[label] = getattr(importlib.import_module(label), "__version__", None)
        except ImportError:
            package_versions[label] = None

    summary = {
        "language": args.lang,
        "input": {
            "path": str(image_path),
            "sha256": image_hash,
            "bytes": len(image_bytes),
            "format": image_format,
            "width": width,
            "height": height,
        },
        "runtime": {
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "git_head": git_head,
            "package_versions": package_versions,
            "module_available": {
                name: importlib.util.find_spec(name) is not None
                for name in ("PIL", "PySide6", "onnxruntime", "torch", "manga_ocr", "paddleocr")
            },
            "detector_backend": env["NEWMANGA_DETECTOR_BACKEND"],
            "detector_device": env["NEWMANGA_DETECTOR_DEVICE"],
            "model": {
                "id": "ogkalu/comic-text-and-bubble-detector",
                "revision": "16e8a622f91fabc6b5b65c96d32d1183f8843546",
                "weights_sha256": None,
                "state": "not loaded; pinned weights absent from isolated P18 data root",
            },
            "endpoint": "local stdio Core sidecar; no remote request configured or sent",
        },
        "device": {
            "inference_device": "cpu",
            "processor": platform.processor() or "not reported by Python",
            "gpu_inference": False,
        },
        "isolation": {"data_root": str(data_root), "credential_environment_variables_removed": True},
        "requests": _response_summary(decoded_stdout),
        "sidecar_exit_code": returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(perf_counter() - started, 3),
        "capture_status": "BLOCKED" if timed_out or returncode != 0 or not stdout else "RESPONSES_CAPTURED",
        "raw_stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "raw_stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "raw_stdout_bytes": "sidecar-stdout.bin",
        "raw_stderr_bytes": "sidecar-stderr.bin",
        "raw_stdout": "sidecar-stdout.jsonl",
        "raw_stderr": "sidecar-stderr.log",
        "raw_exit_code": "sidecar-exit-code.txt",
    }
    (output / "probe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "requests"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
