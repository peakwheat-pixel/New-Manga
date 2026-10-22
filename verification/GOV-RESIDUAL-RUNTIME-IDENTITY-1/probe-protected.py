# -*- coding: utf-8 -*-
"""Read-only probe: which declaration protects each residual runtime identity.

No repository write. Uses the production scanner from tools/governance/clean_workspace.py
without modifying it; `fail` is neutralised only so the probe can inspect an index that
already carries the 7 known declaration errors.
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = r"G:/CODEX/New Manga"
WS = r"G:/CODEX/New Manga.workspace"
TOOL = REPO + "/tools/governance/clean_workspace.py"

spec = importlib.util.spec_from_file_location("cw", TOOL)
cw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cw)

# Neutralise only the final abort so the already-built index can be inspected.
# Every individual fail-closed guard keeps raising as designed.
cw.ProtectionIndex.finalize = lambda self: None

index, scanned = cw.scan_repo_declarations(REPO, WS, None)

print("COUNTS", json.dumps(index.counts(), ensure_ascii=False, sort_keys=True))

targets = [
    "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop",
    "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/catalog",
    "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db",
    "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/derived",
    "C:/Users/49745/AppData/Local/pyinstaller",
    "C:/Users/49745/AppData/Local/Temp/p19-ac2-r1",
    "G:/CODEX/New Manga.workspace/worktrees/P19-AC3-1",
    "G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1/apps/desktop/src-tauri/target/core-sidecar",
    "G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1/apps/desktop/frontend/dist",
    "G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-1/apps/desktop/src-tauri/target/debug/resources",
]

print("\n=== PROTECTION EVALUATION ===")
for raw in targets:
    try:
        ident = cw.resolve_identity(raw, "probe")
        norm = ident.normalised
    except Exception as exc:  # noqa: BLE001
        print("%s\n  RESOLVE_ERROR %s" % (raw, exc))
        continue
    hits = index.evaluate(norm)
    print("%s\n  normalized=%s exists=%s hits=%d"
          % (raw, norm, getattr(ident, "exists", "?"), len(hits)))
    for hit in hits:
        print("    kind=%s root=%s dispositions=%s"
              % (hit["kind"], hit["root"], ",".join(hit["dispositions"])))
        for src in hit["sources"][:6]:
            print("      source=%s" % src)

print("\n=== ERRORS ===")
for err in index.errors:
    print(json.dumps(err if isinstance(err, dict) else err.__dict__,
                     ensure_ascii=False, default=str))

print("\n=== DECLARATIONS MATCHING APPDATA/APP LEASE MACRO TEXT ===")
for decl in index.declarations:
    if "appdata" in decl.raw.lower() or "com.newmanga.m2rc1.desktop" in decl.raw.lower():
        print(json.dumps({"raw": decl.raw, "disposition": decl.disposition,
                          "source_file": decl.source_file, "locator": decl.locator,
                          "normalized": decl.normalized, "real": decl.real_normalized},
                         ensure_ascii=False))

# Machine-readable export for the evidence directory.
payload = {
    "counts": index.counts(),
    "errors": [e if isinstance(e, dict) else e.__dict__ for e in index.errors],
    "evaluations": [],
}
for raw in targets:
    try:
        ident = cw.resolve_identity(raw, "probe")
    except Exception as exc:  # noqa: BLE001
        payload["evaluations"].append({"raw": raw, "resolve_error": str(exc)})
        continue
    payload["evaluations"].append({
        "raw": raw,
        "normalized": ident.normalised,
        "exists": bool(getattr(ident, "exists", False)),
        "hits": index.evaluate(ident.normalised),
    })
out_path = Path(__file__).with_name("raw") / "protection-evaluation.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
print("\nWROTE %s" % out_path)
