# M2-C1 Source Trace

固定证据基线：`eec1aa49d07119f0aa66ff461ebbb55e4595e624`（Task 登记时实测的 master HEAD）。以下源码/测试均从该 commit 读取；已集成文档随该基线固定。标记：AS-IS=当前代码/测试；TO-BE=已批准架构约束；PROPOSAL=本 Task 设计；UNKNOWN/UNVERIFIED=无证据或未运行。

| Contract claim | Evidence at fixed base | Classification | Supported conclusion / limit |
|---|---|---|---|
| Python Core owns business and persistent SQLite writes; UI/Rust are not independent writers | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:17-36`, AD-001 commit ancestor of base | TO-BE | Authoritative architecture. Does not assert current application has no legacy writes outside the intended migration boundary. |
| Current app has no Typed IPC runtime/schema | AD-001 `:40-48`; `doc/research/M2-D1_HEADLESS_QT_COUPLING_AUDIT.md` summary; no Tauri/React runtime source in base | AS-IS / NOT_IMPLEMENTED | IPC messages below are proposals, not existing capability. |
| Core assembly boundary is reusable without QML | `src/bootstrap/core_assembly.py` (M2-I1 integration `cff1e0a8658f57a2e9caf774a9de0961e8f65da3`); `src/bootstrap/app.py` remains Qt entry; M2-I1 Task/Handoff | AS-IS | Qt-free assembly exists; no IPC process/session interface was added. |
| Projection authority moved from UI tree to application | `src/application/tasks/projection.py:82-119,159-239`; `src/ui/models/tasks/projection.py` reexports; M2-I2 integration `7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9` | AS-IS | UI import compatibility is re-export; no reverse dependency is permitted by architecture. |
| Projection page precedence | `src/application/tasks/projection.py:242-259`; `tests/workbench/test_projection.py:39-107` | AS-IS | `failed > processing > blocked > completed > skipped > waiting`. Page status aggregation only. |
| Projection DTO fields, progress unit, focus, flow, control enablement | `src/application/tasks/projection.py:82-119,217-239,261-338`; `tests/workbench/test_projection.py:39-228` | AS-IS | Current data projection supports cited fields; tests assert progress parity with service and button/status behavior. No wire serialization tested. |
| Pipeline command/scope/status vocabulary | `src/domain/tasks/models.py:53-143,160-180,389-447` | AS-IS | Lists are source enum/dataclass values. Do not silently extend as part of this docs task. |
| Run creation persists a frozen target/settings snapshot | `src/application/tasks/service.py:213-270`; `tests/pipeline/test_pipeline.py:136-166` | AS-IS | Run service creates typed domain object and persists it; exact IPC result is proposal. |
| Pause/stop/continue/restart/abandon semantics and stable errors | `src/application/tasks/service.py:829-884`; `src/domain/tasks/models.py:150-157,439-444` | AS-IS | Core transitions and `PipelineError.code/detail`; requests via Qt adapter are not IPC. |
| Retry links a new run; startup recovery turns running into interrupted | `src/application/tasks/service.py:886-919`; `tests/pipeline/test_pipeline.py:467-510`; `tests/pipeline/test_pipeline_production_seam.py:130+`; SQLite store `src/infrastructure/sqlite/pipeline.py:386+`; M2-I1 integrated Core wiring | AS-IS | Recovery behavior exists in service; cross-process reconnection guarantee does not. |
| SQLite production pipeline adapter exists | `src/infrastructure/sqlite/pipeline.py:386+`; `tests/core/test_bootstrap.py:396-430` | AS-IS | This adapter persists Run state; Python Core target owns DB writes (AD-001). |
| Qt workbench exposes current UI actions/signals | `src/ui/viewmodels/workbench/viewmodel.py:66-78,331-479,593-795,921-1003` | AS-IS | QML/VM API; distinguish local selection/filter/view-mode/dirty-editor state from service calls. Signals are not wire events. |
| Current Workbench calls task, editing and catalog services | `src/ui/viewmodels/workbench/viewmodel.py:184-220,526-535,628-715,805-848,921-1015` | AS-IS | Supports command/query inventory; per-method app invocation is currently in-process. |
| Current Bookshelf calls Library and Import services | `src/ui/viewmodels/bookshelf/viewmodel.py:193-216,242-263,287-393` | AS-IS | Supports coarse list/CRUD/import operations; import source reference for future IPC is unresolved. |
| Current Reader persists reading progress and gets page catalog | `src/ui/viewmodels/reader/viewmodel.py:79-109,246-280,398-430` | AS-IS | Current page movement is UI-local; save offset is a Core-facing persistence call. Large tile transfer not defined. |
| Current Settings mutates profiles/defaults/credentials | `src/ui/viewmodels/settings/viewmodel.py:200-443,453-553` | AS-IS | Existing Python-side services; secret wire representation is absent and remains deferred/unknown. |
| Current Export delegates to application service from Qt worker | `src/ui/viewmodels/export/viewmodel.py:256-345` | AS-IS | Export exists in-process; future path/permission protocol is not defined. |
| Canvas conversion and error behavior | `src/application/editing/region_canvas.py:10-99`; `tests/workbench/test_region_canvas.py:25-135` | AS-IS | Half-up rounding, rectangle/polygon rules, typed rejection (`PAGE_SIZE_UNAVAILABLE`, `TOO_FEW_POINTS`, `DEGENERATE_GEOMETRY`), and compatibility re-export test. No wire error-code catalog is generated. |
| Region edit/revision operations exist in application | `src/application/editing/service.py:91-174,247-283,521-622`; `src/application/editing/ports.py:30-76` | AS-IS | Supports Region/revision service inventory. View/QML coverage is partial; do not infer all commands are presently user exposed. |
| Large media not allowed in ordinary JSON/Base64; data channel later | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:33`, user-approved M2-C1 scope | TO-BE | Exact URI/handle/shared-memory/stream choice is deliberately deferred to independent Spike. |
| Preserve source, Managed Copy, manual edits, Lock, current/pinned revisions, task recovery | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:35`; M2-I1/I2 and M2-UI1 integrated evidence | TO-BE | Safety invariants; specific wire token/locking conflict response remains unverified. |
| Page-level blocked visual mapping is not settled | `doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md:3.3,4.3` | USER_DECISION_REQUIRED / DEFERRED | Keep transport status separate; do not choose glyph or behavior. |
| IPC envelope/version/error taxonomy, event delivery/replay, source import token | This contract §3-8 | PROPOSAL / UNKNOWN | No current runtime verifies these semantics. |

M2-R1 evidence is deliberately narrow: its Task/Handoff reports a Qt runtime feasibility submatrix with QML/QQuickWindow and production main paths still unverified. It is not evidence of a headless IPC/runtime lifecycle.

## Import direction check

At the fixed base, authoritative modules are `src/application/tasks/projection.py` and `src/application/editing/region_canvas.py`; legacy UI modules are compatibility imports as recorded by M2-I2. Direct source inspection confirms both legacy modules import symbols from the application modules and contain no duplicate definitions. The Task does not change this graph. A future implementation must retain `application → domain/ports` and `ui adapter → application`; any `src.application → src.ui` import is an architecture violation. `application.export.pdf_qt` is an existing Qt-coupled migration-audit exception, not evidence that the two target seams may acquire Qt imports. M2-C1 does not claim an IPC runtime or add import edges.

## Test evidence boundary

The cited test files are source evidence only and were not rerun by this documentation Task. Product pytest, GUI, serialization, Core process, runtime/reconnect, and large-media capacity tests are `NOT_RUN` by scope. The only executed validation for this Task is documented in `verification/M2-C1/verification.log`.
