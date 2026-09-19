"""TASK-060 review probe 2: is Q-007 ① (root-internal `..` through the trash
pending-purge face) actually closed by this slice, or was it already reachable
on the pre-fix tree?  Run against both trees with the same script:

    python t060_q007_pre_post.py <tree_root>

Prints one line per tree so the two can be diffed.  Read-only for the repo;
all files go to %TEMP%.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))

from application.maintenance.trash import TrashService, _JsonTrashManifest  # noqa: E402
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402

print(f"== tree: {ROOT}")


class DeadPages:
    """Stub store: the batch is not in the ledger and no row references the
    target (the exact shape of a degraded/lost ledger, F-7)."""

    def get_pages_by_ids(self, ids):
        return ()

    def list_live_managed_refs(self, refs):
        return set()

    def list_trashed_page_groups(self):
        return ()


tmp = Path(tempfile.mkdtemp(prefix="t060-q007-"))
storage = ManagedFileStorage(tmp / "managed")
storage.ensure_layout()
victim = tmp / "managed" / "revisions" / "keep.png"
victim.parent.mkdir(parents=True, exist_ok=True)
victim.write_bytes(b"committed revision")

manifest = _JsonTrashManifest(tmp / "trash.json")
manifest.write_manifest(
    {
        "batches": [],
        "pending_purges": [
            {"batch_id": "tampered", "targets": ["books/../revisions/keep.png"]}
        ],
    }
)

try:
    cleared = TrashService(DeadPages(), storage, manifest).retry_pending_purges()
except Exception as error:  # noqa: BLE001 - the exception is a valid outcome
    print(f"   retry_pending_purges raised {type(error).__name__}: {str(error)[:120]}")
    cleared = None
print(
    f"   cleared={cleared} protected revision file survives? {victim.exists()}"
    "   <-- survives=False means the trash face can unlink a root-internal"
    " neighbour through a tampered manifest entry"
)

try:
    from application.maintenance.cleanup import is_safe_relative_path  # noqa: E402
except ImportError:
    print("   is_safe_relative_path: absent on this tree (no single predicate yet)")
else:
    print(
        "   is_safe_relative_path('books/../revisions/keep.png') ="
        f" {is_safe_relative_path('books/../revisions/keep.png')}"
        "   (the single authority refuses it; the trash face never calls it)"
    )
