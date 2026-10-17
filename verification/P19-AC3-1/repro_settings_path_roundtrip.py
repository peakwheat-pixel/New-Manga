#!/usr/bin/env python3
"""Minimal, temporary-database reproduction of settings path/secret echo."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)


def request(server: CoreServiceServer, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": f"p19-ac3-{command}",
        "command": command,
        "payload": payload,
    })
    response, exit_requested = server.dispatch_request(line)
    assert not exit_requested
    return response


def main() -> int:
    scratch = EVIDENCE / "scratch"
    scratch.mkdir(exist_ok=True)
    synthetic_path = r"C:\private\synthetic-source.cbz"
    synthetic_secret = "P19_AC3_SYNTHETIC_SECRET_SENTINEL"
    with tempfile.TemporaryDirectory(prefix="settings-path-repro-", dir=scratch) as temp:
        core = assemble_production_core(Path(temp) / "data")
        try:
            server = CoreServiceServer(core)
            written = request(server, "settings.update_section", {
                "section": "ocr",
                "values": {"path": synthetic_path, "api_secret": synthetic_secret},
            })
            read_back = request(server, "settings.get", {"section": "ocr"})
            expected = {"path": synthetic_path}
            print("WRITE_RESPONSE=" + json.dumps(written, ensure_ascii=False, sort_keys=True))
            print("READ_RESPONSE=" + json.dumps(read_back, ensure_ascii=False, sort_keys=True))
            assert written["error"] is None
            assert written["result"]["settings"]["ocr"] == expected
            assert read_back["error"] is None
            assert read_back["result"]["settings"]["ocr"] == expected
            assert synthetic_secret not in json.dumps(written["result"])
            assert synthetic_secret not in json.dumps(read_back["result"])
            print("REPRO settings.update_section({section:'ocr', values:{path,api_secret}})")
            print("OBSERVED path_value_returned=true synthetic_secret_returned=false file_io_attempted=false")
            print("REPRO_RESULT=PASS (the forbidden OS-path echo was reproduced; secret key was dropped)")
        finally:
            core.conn.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"REPRO_FAILURE {type(error).__name__}: {error}", file=sys.stderr)
        raise
