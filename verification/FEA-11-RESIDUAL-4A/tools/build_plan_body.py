"""FEA-11-RESIDUAL-4A (AC-R3-2) evidence helper: build a PlanBody with an
explicit bind for the seeded legacy page.

The isolated FEA-11 IPC seed binds ONE referenced page to a legacy entry whose
v7-era row carries no pixel evidence, so the frozen matcher honestly degrades
the page to ``ambiguous``/``missing_old`` (C-17 §7.3 row 4) and the DEFAULT
decision for it is ``defer`` — which publishes no new binding and therefore
leaves the ACK gate with nothing to open.

C-17 §5.1/§5.3 and ``planner._assert_all_ambiguities_decided`` allow exactly
this user decision: an ambiguous item may be explicitly ``bind``-ed. This helper
reuses the frozen ``tests/fea11/conftest.py`` builders (no second construction
rule, no contract drift) and only changes the decision for ambiguous items that
carry a page id.

Provenance: same construction rule as
``verification/FEA-11-HOST-AUTH-2/tools/build_plan_body.py`` (that card's tool
stays a read-only precedent; this copy keeps the R4A evidence self-contained).

Usage:
  python build_plan_body.py --scan-json S --out O [--kind resync]
Output: {"kind", "plan_id", "plan_digest", "plan_body", "confirmation"}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "tests" / "fea11"))

from application.sources.model import plan_digest_of  # noqa: E402
import conftest as fea11_conftest  # noqa: E402

FIXTURE_ROOT = (REPO.parent / f"{REPO.name}.workspace" / "FEA-11" / "fixtures").resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-json", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--kind", default="resync")
    args = parser.parse_args()

    scan_path = args.scan_json.resolve()
    if not scan_path.is_relative_to(FIXTURE_ROOT):
        print("refused: only an isolated FEA-11 fixture scan is allowed", file=sys.stderr)
        return 2
    scan = json.loads(scan_path.read_text(encoding="utf-8"))

    decisions = fea11_conftest.default_decisions(scan)
    bound = 0
    for decision, item in zip(decisions, scan["diff"]):
        if item["classification"] != "ambiguous" or item["page_id"] is None:
            continue
        # Explicit user decision: keep the page id and bind the candidate entry.
        decision.update(
            {
                "action": "bind",
                "target_page_id": item["page_id"],
                "target_chapter_id": None,
                "new_source_order": None,
                "new_sort_order": None,
                "migrate_revision_ids": [],
            }
        )
        bound += 1

    body = fea11_conftest.build_plan_body(scan, kind=args.kind, decisions=decisions)
    payloads = {
        "kind": args.kind,
        "plan_id": body["plan_id"],
        "plan_digest": plan_digest_of(body),
        "plan_body": body,
        "confirmation": body["confirmation"],
    }
    args.out.write_text(json.dumps(payloads, indent=1), encoding="utf-8")
    print(
        "FEA11_R4A_PLAN_OK "
        + json.dumps({"plan_id": body["plan_id"], "ambiguous_bound": bound})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
