# Codex freeze build attempt 1 — abandoned before dispatch

- RunId: baseline-20261014T091112CST-p02-admission
- Freeze manifest: G:/CODEX/New Manga.workspace/agent-output/zcode/P02-NEW-TIME-BASELINE/baseline-20261014T091112CST-p02-admission/freeze-manifest.json
- Freeze manifest SHA-256: C160010A590CE73641A4A3FE2F57A33887902D20B83F2C35C673C79C3DD735B0
- Fail-closed reason: mutableObservationPaths is empty; the manifest contract requires at least one absolute path.
- Collector and ZCode were not dispatched. The CreateNew output target is absent, and no source file changed.
- This manifest and candidate RunId are preserved and will not be overwritten or reused. I1/I2 remains 2/2; this was a Codex freeze-input assembly error, not a source finding or Owner repair.

The next attempt uses a new RunId and a newly built freeze manifest with the current Task, STATUS, Plan, index, and checkpoint included as mutable observations.