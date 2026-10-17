"""Equivalent to the P19 settings path round-trip reproducer."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)

PATH = r"C:\Users\sec-fix-path-echo-1\AppData\Local\model\runner.exe"
SECRET = "synthetic-secret-must-stay-omitted"


def request(server: CoreServiceServer, command: str, payload: dict) -> dict:
    response, should_exit = server.dispatch_request(json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "sec-fix-path-echo-1",
        "command": command,
        "payload": payload,
    }))
    assert not should_exit
    return response


def contains_text(value: object, needle: str) -> bool:
    if isinstance(value, dict):
        return any(contains_text(key, needle) or contains_text(item, needle) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_text(item, needle) for item in value)
    return isinstance(value, str) and needle in value


def main() -> int:
    temp_root = ROOT / "verification" / "SEC-FIX-PATH-ECHO-1" / "tmp"
    temp_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="settings-path-repro-", dir=temp_root) as data_root:
        core = assemble_production_core(Path(data_root) / "data")
        try:
            server = CoreServiceServer(core)
            print("REPRO settings.update_section({section:'ocr', values:{path, api_secret}})")
            write = request(
                server,
                "settings.update_section",
                {"section": "ocr", "values": {"path": PATH, "api_secret": SECRET}},
            )
            read = request(server, "settings.get", {"section": "ocr"})
            print("WRITE_RESPONSE=" + json.dumps(write, ensure_ascii=False))
            print("READ_RESPONSE=" + json.dumps(read, ensure_ascii=False))
            path_value_returned = contains_text((write, read), PATH)
            secret_returned = contains_text((write, read), SECRET)
            print(
                "OBSERVED "
                f"path_value_returned={str(path_value_returned).lower()} "
                f"synthetic_secret_returned={str(secret_returned).lower()} "
                "file_io_attempted=false"
            )
            print("REPRO_RESULT=" + ("FAIL" if path_value_returned else "PASS"))
            return int(path_value_returned)
        finally:
            core.conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
