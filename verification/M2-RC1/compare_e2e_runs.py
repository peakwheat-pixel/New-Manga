"""Compare two run_e2e.py result JSONs and emit a consistency artefact.

R-03: the previous fix-repeat-consistency.json claimed ``differences: {}``
with no generator. This script IS the generator; it reports real
observed-layer differences and classifies them against an explicit
whitelist of nondeterministic fields, so ``consistent`` means exactly:
identical id+status sets AND observed differences only in whitelisted
timing/randomness fields.

Usage:
  python compare_e2e_runs.py FIRST.json REPEAT.json OUT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Fields whose values legitimately differ between two runs of the same
# binary+fixtures: E-06 mints fresh random references per run; E-07 is a
# wall-clock timing measurement.
NONDETERMINISTIC = {
    "E-06-remount-fresh-references": {"observed"},
    "E-07-per-reference-first-byte-p95": {"observed.p95_ms", "observed.timings_ms"},
    # pre-rename id (historical rounds)
    "E-07-hot-cache-p95": {"observed.p95_ms", "observed.timings_ms"},
}


def flatten(record: dict, prefix: str = "") -> dict:
    flat: dict = {}
    for key, value in record.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten(value, path))
        else:
            flat[path] = value
    return flat


def main() -> int:
    first_path, repeat_path, out_path = (Path(a) for a in sys.argv[1:4])
    first = json.loads(first_path.read_text(encoding="utf-8"))
    repeat = json.loads(repeat_path.read_text(encoding="utf-8"))

    def by_id(results: list[dict]) -> dict[str, dict]:
        return {r["id"]: r for r in results}

    first_map, repeat_map = by_id(first["results"]), by_id(repeat["results"])
    ids_first, ids_repeat = set(first_map), set(repeat_map)

    status_differences = [
        {"id": i, "first": first_map[i].get("status"), "repeat": repeat_map[i].get("status")}
        for i in sorted(ids_first & ids_repeat)
        if first_map[i].get("status") != repeat_map[i].get("status")
    ]
    ids_missing_in_repeat = sorted(ids_first - ids_repeat)
    ids_missing_in_first = sorted(ids_repeat - ids_first)

    observed_differences: list[dict] = []
    unclassified: list[dict] = []
    for scenario_id in sorted(ids_first & ids_repeat):
        flat_a = flatten(first_map[scenario_id])
        flat_b = flatten(repeat_map[scenario_id])
        for field in sorted(set(flat_a) | set(flat_b)):
            value_a, value_b = flat_a.get(field), flat_b.get(field)
            if value_a == value_b:
                continue
            entry = {
                "id": scenario_id,
                "field": field,
                "first": value_a,
                "repeat": value_b,
            }
            whitelist = NONDETERMINISTIC.get(scenario_id, set())
            observed_differences.append(entry)
            if field not in whitelist and not any(
                field.startswith(w + ".") or w.startswith(field) for w in whitelist
            ):
                unclassified.append(entry)

    consistent = (
        not status_differences
        and not ids_missing_in_repeat
        and not ids_missing_in_first
        and not unclassified
    )
    report = {
        "generator": "verification/M2-RC1/compare_e2e_runs.py",
        "first": first_path.name,
        "repeat": repeat_path.name,
        "first_status_counts": {
            s: sum(1 for r in first["results"] if r.get("status") == s)
            for s in {r.get("status") for r in first["results"]}
        },
        "repeat_status_counts": {
            s: sum(1 for r in repeat["results"] if r.get("status") == s)
            for s in {r.get("status") for r in repeat["results"]}
        },
        "status_differences": status_differences,
        "ids_missing_in_repeat": ids_missing_in_repeat,
        "ids_missing_in_first": ids_missing_in_first,
        "observed_differences": observed_differences,
        "unclassified_differences": unclassified,
        "nondeterministic_whitelist": {
            k: sorted(v) for k, v in sorted(NONDETERMINISTIC.items())
        },
        # "consistent" = id+status identical AND every observed difference is
        # a whitelisted timing/randomness field (NOT "no differences")
        "consistent": consistent,
    }
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"consistent={consistent} -> {out_path}")
    return 0 if consistent else 1


if __name__ == "__main__":
    sys.exit(main())
