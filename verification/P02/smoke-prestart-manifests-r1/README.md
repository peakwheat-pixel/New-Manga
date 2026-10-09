# INVALID_PARTIAL_HISTORY: Smoke HostFolder manifest R1

Status: `INVALID_PARTIAL_HISTORY / NOT_GATE_EVIDENCE / SUPERSEDED_BY_R2`.

These three records are a partial R1 capture. The scan stopped at mapping 4 because R1 used `DirEntry.stat()` whose `st_ino` was zero on this host. R1 has no summary and must not be treated as a complete scan, a PASS, or the current R2 baseline. Its recorded files have zero verified file hashes.

Use the corrected R2 capture at [smoke-prestart-manifests-r2](../smoke-prestart-manifests-r2/summary.json). The retained R1 collector is marked invalid in its header and is preserved only to explain the failed attempt.