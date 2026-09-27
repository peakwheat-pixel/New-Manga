"""DSH independent review probe: does the RC2 TTL validator reject non-finite
ttl values (NaN / +Inf) on the Core service and on the stdio wire?

Not part of the delivery; reviewer evidence only. Run:
    python verification/M2-RC2/review-dsh-a8fb17ca/probe_ttl_nan.py
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "src"))

from application.resource_channel.dto import ResourceFacts  # noqa: E402
from application.resource_channel.service import ResourceChannelService  # noqa: E402
from infrastructure.resource_channel.catalog_store import ResourceCatalogStore  # noqa: E402
from infrastructure.resource_channel.host_bridge import CoreChannelServer  # noqa: E402
from infrastructure.resource_channel.scope import ScopeRoots  # noqa: E402

FACTS = ResourceFacts(volume_serial=1, file_index=0, size=4, sha256="a" * 64)


def service_level() -> None:
    print("== A. service.issue() with non-finite ttl_seconds ==")
    clock = {"now": 1000.0}
    service = ResourceChannelService(clock=lambda: clock["now"])
    for label, ttl in (("NaN", float("nan")), ("+Inf", float("inf")), ("-Inf", float("-inf")),
                       ("0", 0.0), ("301", 301.0), ("300", 300.0)):
        try:
            opaque = service.issue(
                scope_class="derived-read-only",
                resource_id=f"res-{label}",
                revision_fingerprint="rev-1",
                rel_path="asset.png",
                facts=FACTS,
                ttl_seconds=ttl,
            )
            verdict = "ACCEPTED"
        except Exception as error:  # noqa: BLE001
            verdict = f"REFUSED ({getattr(error, 'code', type(error).__name__)})"
            print(f"  ttl={label:>4}  {verdict}")
            continue
        # does the accepted reference still resolve a long time later?
        entry = service._table[opaque]  # reviewer introspection
        clock["now"] = 10 ** 9
        try:
            service.resolve(opaque, renew=False)
            long_run = "still resolves after clock jump to 1e9 (never expires)"
        except Exception as error:  # noqa: BLE001
            long_run = f"expired ({getattr(error, 'code', type(error).__name__)})"
        clock["now"] = 1000.0
        print(f"  ttl={label:>4}  {verdict}; expires_at={entry.expires_at!r}; {long_run}")


def wire_level() -> None:
    print("== B. stdio wire: raw JSON NaN / Infinity literals (json.loads default) ==")
    with tempfile.TemporaryDirectory() as temp:
        lab = Path(temp)
        derived = lab / "scope" / "derived"
        derived.mkdir(parents=True)
        (derived / "asset.png").write_bytes(b"data")
        catalog = ResourceCatalogStore(lab / "catalog.sqlite")
        catalog.upsert("res-nan", "derived-read-only", "asset.png")
        roots = ScopeRoots(derived_root=derived, managed_root=lab / "scope" / "managed")
        for payload in (
            '{"id":1,"method":"issue","params":{"resource_id":"res-nan",'
            '"revision_fingerprint":"rev-1","ttl_seconds":NaN}}',
            '{"id":1,"method":"issue","params":{"resource_id":"res-nan",'
            '"revision_fingerprint":"rev-1","ttl_seconds":Infinity}}',
            '{"id":1,"method":"issue","params":{"resource_id":"res-nan",'
            '"revision_fingerprint":"rev-1","ttl_seconds":999999}}',
        ):
            stdin = io.StringIO(payload + "\n")
            stdout = io.StringIO()
            CoreChannelServer(roots=roots, catalog=catalog, stdin=stdin, stdout=stdout).serve_forever()
            print(f"  {payload.split('ttl_seconds":')[1][:-2]:>10} -> {stdout.getvalue().strip()}")
        catalog.close()


if __name__ == "__main__":
    service_level()
    wire_level()
