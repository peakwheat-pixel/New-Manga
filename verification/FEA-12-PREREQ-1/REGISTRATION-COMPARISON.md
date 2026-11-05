# FEA-12-PREREQ-1 — Host registration comparison（rev 2.13）

- 生成时间：2026-11-05（Asia/Shanghai）
- 基线：`base_commit=035468a81`（另见 `logs/baseline-negative-control-base-035468a81.log`）
- 实现 head：交付 commit（见 Task/Handoff）；主工作树 main
- 对照方式：改动前 Release 程序集反射探针 + 改动后同一探针（`tools/baseline-negative-control.ps1` 与测试）

## 1. `HostCommandRegistry` 命令面

| 项 | 改动前（base 035468a81） | 改动后 |
|---|---|---|
| `HostCommandRegistry.All.Count` | **106** | **111**（+5 additive） |
| `library_preview_permanent_delete_books` | 不存在；`Get()` → typed `HostCommandUnknownException`（`code=UNKNOWN_COMMAND`） | `PreviewPermanentDeleteBooks`，wire minor **11**，`CoreService` channel |
| `library_move_to_trash` | 不存在；typed `UNKNOWN_COMMAND` | `MoveToTrash`，wire minor **13** |
| `library_restore_from_trash` | 不存在；typed `UNKNOWN_COMMAND` | `RestoreFromTrash`，wire minor **13** |
| `library_list_trash` | 不存在；typed `UNKNOWN_COMMAND` | `ListTrash`，wire minor **13** |
| `library_purge_trash` | 不存在；typed `UNKNOWN_COMMAND` | `PurgeTrash`，wire minor **13**（首版 CORE 不实现） |
| `library_delete_book_permanently` | `PermanentlyDeleteBook`，minor **10** | **不变**（minor 10；仅 additive 透传 `inventory_digest`） |
| `library_delete_books_permanently` | `PermanentlyDeleteBooks`，minor **10** | **不变**（minor 10；仅 additive 透传 `inventory_digest`/`inventory_digests`） |
| frozen 66 snapshot 命令 | 全部存在 | **全部存在且语义/映射零改动**（CommandParity 测试） |

## 2. capability 注册（契约元数据；运行期 probe 归 FEA-12-CORE）

| capability | 命令 |
|---|---|
| `library.delete.preview/1` | `library_preview_permanent_delete_books` |
| `library.trash.read/1` | `library_list_trash` |
| `library.trash.write/1` | `library_move_to_trash` / `library_restore_from_trash` / `library_purge_trash` |

- `HostCommandRegistry.DeleteTrashCapabilities` = 恰好这 3 个；`RequiredCapabilities(name)` 未列命令返回空集。
- 本卡**不**接运行时 `core.ping` probe（`NewManga.Host/HostRuntime.cs` 不在本卡写域；CORE 卡已窄批该文件）。缺失能力 → `CORE_CAPABILITY_MISSING` 的运行时门由 CORE 实现。

## 3. 错误投影白名单

| 项 | 改动前 | 改动后 |
|---|---|---|
| run 族白名单 `AllowedRunErrorCodes` | 19 码 | 不变（本卡不改 run 投影） |
| delete/trash 族白名单 | **不存在**（Core 错误透传，未注册 code 不降级） | `AllowedDeleteTrashErrorCodes` **20 码**（15 既有 delete/protocol/host 码 + 5 新码） |
| 新码 `BOOK_DELETE_STALE_PREVIEW` | 不在任何白名单；旧投影（C-08 run projector）降级 `category=unknown`、code 原样 | conflict / false（冻结值） |
| 新码 `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` | 同上 | unavailable / true（冻结值） |
| 新码 `TRASH_ENTRY_NOT_FOUND` | 同上 | not_found / false（冻结值） |
| 新码 `TRASH_RESTORE_CONFLICT` | 同上 | conflict / false（冻结值） |
| 新码 `TRASH_RESTORE_LAYER_MISMATCH` | 同上 | conflict / false（冻结值） |
| 白名单外 code | （无 delete 白名单） | **保留原 code 原文**，投影 `category=unknown` / `retryable=false`，不得作为 UI 分支/重试依据 |

## 4. 冻结（旧）Core 负向对照（实测）

- 证据：`test-evidence/commands/fea12-old-core-negative-control.json`（`[SidecarFact] Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`）
- `PreviewPermanentDeleteBooks`（request minor 11）→ typed `UNKNOWN_COMMAND` / validation / false，响应 `result=null`。
- `MoveToTrash` / `ListTrash` / `PurgeTrash`（request minor 13）→ 同 typed `UNKNOWN_COMMAND`，不静默丢弃。
- 既有 `PermanentlyDeleteBook`（minor 10）+ 追加 `inventory_digest` → 旧 Core closed-shape 校验返回 `INVALID_REQUEST`（fail-closed，不忽略 digest 继续删除）。

## 5. 回归（同一次 sidecar 运行）

- `B1Commands_ExecuteAgainstFrozenCore`、`B2Commands_ExecuteAgainstFrozenCore` 仍通过（既有 delete 命令行为零回归）；证据 `test-evidence/commands/ns-b1-integration.json`、`ns-b2-integration.json`。
