"""FEA-09 referenced-import orchestration (C-15 §3/C-16 §4–§5).

Submodules:
- ``model``    — dataclasses, locator safety, natural/stable sort keys.
- ``errors``   — the frozen C-16 §6 error table.
- ``scanner``  — five-kind source scan with budgets and safety checks.
- ``planner``  — PlanImportReferences (preview, digest, dedup policy).
- ``runtime``  — Start/GetReceipt/Cancel state machine with per-page units.
- ``secrets``  — one-shot DPAPI password secret references.
- ``pdf_probe``— pypdfium2 page-count/size inspector.
- ``access``   — the source-read grant port consumed by the orchestration.
"""

from application.importing.referenced.errors import SourceImportError  # noqa: F401
