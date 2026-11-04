"""FEA-11 real-IPC apply payload generator.

The C# IPC test performs the real Core calls; this Python helper computes the
frozen C-17 payload shapes and digests (plan body, confirmation, request_digest,
host authorization) from the *real* ScanSourceSync result the C# side wrote to
disk. It runs against the same isolated v8 library and only reads/writes that
library (plus the payload JSON).

Usage:
  ipc_apply.py --data-root R --db D --scan-json S --grant-id G --out O
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "fea11"))

from application.sources.model import (  # noqa: E402
    authorization_digest_of,
    now_millis,
    plan_digest_of,
    request_digest_of,
)
import conftest as fea11_conftest  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--scan-json", type=Path, required=True)
    parser.add_argument("--grant-id", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kind", default="resync")
    parser.add_argument("--mode", choices=("body", "apply"), default="body")
    parser.add_argument("--body-json", type=Path)
    parser.add_argument("--plan-digest")
    args = parser.parse_args()

    root = args.data_root.resolve()
    fixture_root = (REPO.parent / f"{REPO.name}.workspace" / "FEA-11" / "fixtures").resolve()
    if not root.is_relative_to(fixture_root) or args.db.resolve() != root / "library.db":
        parser.error("only an isolated FEA-11 fixture library.db is allowed")

    scan = json.loads(args.scan_json.read_text(encoding="utf-8"))
    if args.mode == "body":
        body = fea11_conftest.build_plan_body(scan, kind=args.kind)
        payloads = {
            "kind": args.kind,
            "plan_id": body["plan_id"],
            "plan_digest": plan_digest_of(body),
            "plan_body": body,
            "confirmation": body["confirmation"],
        }
        args.out.write_text(json.dumps(payloads, indent=1), encoding="utf-8")
        print("FEA11_IPC_APPLY_OK body " + json.dumps({"plan_id": body["plan_id"]}))
        return 0

    if args.body_json is None or not args.plan_digest:
        parser.error("apply mode requires --body-json and --plan-digest")
    body_payload = json.loads(args.body_json.read_text(encoding="utf-8"))
    body = body_payload["plan_body"]
    plan_id = body["plan_id"]
    plan_digest = args.plan_digest
    operation_id = "op-" + uuid.uuid4().hex[:16]
    request_digest = request_digest_of(operation_id, plan_id, plan_digest, args.kind)
    authorization = {
        "host_receipt_id": "host-" + uuid.uuid4().hex[:16],
        "operation_id": operation_id,
        "request_digest": request_digest,
        "authorization_digest": authorization_digest_of(scan["authorizations"]),
        "authorizations": scan["authorizations"],
        "authorized_at": now_millis(),
    }
    apply = {
        "operation_id": operation_id,
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "grant_ids": [args.grant_id],
        "authorization": authorization,
    }
    payloads = {
        "kind": args.kind,
        "plan_id": plan_id,
        "plan_digest": plan_digest,
        "preview": {"plan_id": plan_id, "plan_digest": plan_digest},
        "confirm": {
            "plan_id": plan_id,
            "plan_digest": plan_digest,
            "confirmation": body["confirmation"],
        },
        "operation_id": operation_id,
        "request_digest": request_digest,
        "apply": apply,
        "ack": {
            "operation_id": operation_id,
            "request_digest": request_digest,
            "host_receipt_id": authorization["host_receipt_id"],
            "authorization": authorization,
            "grant_ids": [args.grant_id],
        },
    }
    args.out.write_text(json.dumps(payloads, indent=1), encoding="utf-8")
    print("FEA11_IPC_APPLY_OK apply " + json.dumps({"operation_id": operation_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
