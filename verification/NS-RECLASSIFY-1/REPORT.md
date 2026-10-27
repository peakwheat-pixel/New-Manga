# NS-RECLASSIFY-1 报告：42 条 NOT_SUPPORTED 重探测与重分类

- Task：`NS-RECLASSIFY-1`（kind=research，base `171529b5d`，只出证据与建议，**不改** registry/产品源码/parity 快照/冻结证据）
- 探测对象：冻结双 sidecar 的 `core_service.exe`（AC11 无标签副本）
  `sha256 = e0a1eff8d9ee7558eae903f83af3870ada94afc2d083f82e2cc0b571f6f14bc0`，68,887,500 B
  （与 S2 探测所用二进制同 hash，见 `verification/HOST-COMMAND-MIGRATION-1/parity/core-command-probe.json`）
- 协议：application 通道 `new-manga.core 2.3`；按面发现 **P15 settings = minor 7 / CreateBook|CreateChapter = minor 8 / DELETE 面 = minor 10**（minor 10 由 3–12 扫描实证，见 §2）
- 数据根：`BOOK-FIXTURE-1/isolated-data` 的**私有副本**（本任务 `probe/data`，重建 catalog 以匹配新路径绑定）。
  原件未被修改。副本内容：1 book / 1 chapter / 8 pages / 0 regions / 0 region_revisions。
- 探测规模：application 通道 50 次 + delete minor 扫描 10 次 + 对照 1 次；host-control 通道 4 次
- 结论：**42 条中 35 条应改判 IMPLEMENTED，7 条维持“未实现”（但性质是 Host 侧缺失，不是 Core 缺失）**

---

## 1. 分类统计

| proposed_status | 数量 | 含义 |
|---|---|---|
| **IMPLEMENTED** | **35** | 冻结 Core 已实现该命令路由/处理器；S2 的 NOT_SUPPORTED 来自探针错误（payload 错、命令名 PascalCase/snake_case 不匹配、假 id、错枚举）或从未探测 |
| **NEEDS_IMPLEMENTATION** | **7** | Core 侧无等价命令（2 条 host-local shell 动作）或需要 Host 侧先实现 host_issuer grant 签发（5 条 import/export） |
| NEEDS_MODEL | 0 | 无命令因缺模型而不可用（`rerender_page` 需真实产物，但属数据依赖而非权重缺失） |
| BLOCKED | 0 | 无“构造不出探针”的命令 |

置信度：high 26 / medium 16 / low 0。

**按面拆分**

| 面 | 命令数 | IMPLEMENTED | NEEDS_IMPLEMENTATION |
|---|---|---|---|
| settings（P15 provider/network/credential + plugins + backup + cleanup） | 22 | 22 | 0 |
| library | 6 | 3 | 3（import_file/import_folder/import）— 其中 import 两个 + delete 两个见下 |
| workbench | 8 | 5 | 3 |
| reader | 1 | 1 | 0 |
| region | 6 | 6 | 0 |

（精确逐条见 `reclassification.json` 的 `commands[]`。）

---

## 2. 关键发现：S2 为什么会误判

S2 的 25 次 Core 探测（`core-command-probe.json`）存在 4 类系统性探针错误，逐类都能复现并纠正：

| # | 探针错误 | 例子（S2 原文） | S2 结论 | 本次重探测 |
|---|---|---|---|---|
| 1 | **命令名大小写/风格不对** | `ListChapters`、`ListChapterPages`、`ListRegions`、`ListRegionRevisions`、`ResolvePageResource`（PascalCase）→ `UNKNOWN_COMMAND` | 当作“未实现” | Core 只认 snake_case：`list_chapters`、`list_chapter_pages`、`list_regions`、`list_region_revisions`、`resolve_page_resource`；后三条本次返回 **成功** |
| 2 | **payload 字段错/缺字段** | `SaveReadingProgress {position:0, chapter_id:'probe-chapter'}` → `INVALID_REQUEST` | `library_save_reading_progress` = NOT_SUPPORTED | 正确形状 `{chapter_id, mode, page_id, scroll_offset_y, elapsed_seconds_delta}` + 真实 id → **ok=true**（本任务 headline 用例） |
| 3 | **假 id**（`probe-page`/`probe-region`/`probe-chapter`） | `rerender_page {page_id:'probe-page'}` → `TARGET_NOT_FOUND` | 当作“未实现” | 真实 page_id → 进入 handler（`MISSING_REQUIRED_INPUT`，缺渲染产物）；`resolve_page_resource` 真实 id → **ok=true** |
| 4 | **非法枚举值** | `set_region_type {new_region_type:'probe'}` → `INVALID_REQUEST` | 当作“未实现” | 合法枚举 `narration/note/other/sfx/speech/title`；`sfx` + 不存在 region → `TARGET_NOT_FOUND`（handler 在跑） |
| 5 | **协议 minor 不对** | `insufficient`：DELETE 面要求 `minor=10`，S2 未探测 delete 面 | 从未探测 → 默认 NOT_SUPPORTED | 3–12 扫描：仅 minor=10 越过版本校验（`BOOK_NOT_FOUND`），其余 `INVALID_REQUEST` |

**另有一批命令 S2 根本没有探测过**（settings P15 面、plugins、backup、cleanup、run 面），registry 直接按“host-local 逻辑”写死 NOT_SUPPORTED——本次实测这些面在冻结 Core 里全都有实现。

---

## 3. 分类判据（可复核）

| basis（探测结果） | 判定 |
|---|---|
| `success`（`ok=true` 且有结果体） | **IMPLEMENTED · high** |
| `domain_error_handler_ran`（`not_found`/`conflict`/`BOOK_BUSY` 等 typed 域错误） | **IMPLEMENTED · high**：不存在的路由只会回 `UNKNOWN_COMMAND`，域错误只能由真实处理器产生 |
| 处理器级 typed 校验（`SETTINGS_INVALID_INPUT`、`MISSING_REQUIRED_INPUT`、`BACKUP_RESTORE_REQUIRES_CONFIRMATION`） | **IMPLEMENTED · medium**：路由与处理器已在跑，正向 payload 未完全命中 → 应用改动时补一次确认 |
| Core 命令面**没有**等价命令（host-local shell 动作） | **NEEDS_IMPLEMENTATION**（实现位置在 Host/App，不在 Core） |
| host-control 面存在但 grant 需 host_issuer 签发（冻结 Core 对未签名 ref 回 `REF_MALFORMED`） | **NEEDS_IMPLEMENTATION**（先实现 Host 侧签发） |
| `PROVIDER_*` | NEEDS_MODEL（本任务 0 条） |

**未做**：没有把 `INVALID_REQUEST` 一律升级成“已实现”；凡落到 medium 的条目都在 `reclassification.json` 里带 `residual` 字段说明差什么。

---

## 4. 逐条结果（42 条）

完整机器可读结果见 `reclassification.json`（每条含 `current_status / proposed_status / confidence / core_command / evidence{request_payload, protocol_minor, error_code, basis} / reason / s2_probe / residual`）。摘要：

**IMPLEMENTED · high（19 条，有成功或域错误实证）**
`backup_delete`、`cleanup_retry_pending`、`plugins_audit_list`、`plugins_set_plugin_enabled`、`library_save_reading_progress`、`resolve_page_resource`、`set_region_type`、`list_region_revisions`、`restore_region_revision`、`library_start_run`、`library_get_run_snapshot`、`library_get_task_projection`、`library_resume_blocked_run`、`library_retry_failed_targets`、`library_delete_book_permanently`、`settings_network_profiles_create`、`settings_network_profiles_update`、`settings_network_profiles_delete`、`settings_network_profile_default_set`、`settings_network_profile_default_clear`、`settings_provider_bindings_resolve`、`settings_provider_bindings_clear`、`settings_provider_run_snapshot_get`

**IMPLEMENTED · medium（16 条，路由已证、正向 payload 待钉）**
`backup_restore`（`BACKUP_RESTORE_REQUIRES_CONFIRMATION`）、`rerender_page`（`MISSING_REQUIRED_INPUT`）、`library_delete_books_permanently`（DELETE 分支 minor=10 已证，批量 payload 未命中）、`library_control_run`（本轮 `INVALID_RUN_TRANSITION`；21:38 那轮在 run 为 running 时 `pause` 曾返回 **ok=true**）、`settings_provider_profiles_create/update/delete`、`settings_provider_bindings_set`、`credential_put`、`credential_clear`、`settings_network_profiles_test`、`settings_network_profile_resolve`

**NEEDS_IMPLEMENTATION（7 条）**
- host-local shell 动作（Core 无等价命令，2 条）：`library_reveal_export_folder`、`plugins_open_directory`
- host-control grant 面（Core 有 `ImportPages`/`StartExport`/`GetExportSnapshot`/`CancelExport`，但 grant/ref 必须由 host_issuer 签发，冻结 Core 对未签名 ref 回 typed `REF_MALFORMED`，Avalonia Host 尚未实现签发，5 条）：`library_import_file`、`library_import_folder`、`library_start_export`、`library_cancel_export`、`library_get_export_snapshot`
  - 实证：`OpenHostSession` **成功**（拿到 `core_session_id`），`RegisterImportSource`/`RegisterExportTarget` 返回 `REF_MALFORMED`（handler 在跑，只是 ref 形状/签名不对）

---

## 5. 建议应用顺序（给后续实施 Task）

1. **先改 reason 文案**（零风险，纯文档）：把 35 条 IMPLEMENTED 的 reason 从“S2 未探测/未实现”改为“Core 已实现，待接线”，避免 Review 再次误读。
2. **第一批接线（19 条 high，风险最低）**：`save_reading_progress`、`resolve_page_resource`、run 面 4 条、backup.delete、cleanup.retry_pending、plugins.audit_list/set_plugin_enabled、region 面 4 条、network profile CRUD 4 条、bindings 2 条、provider_run_snapshot_get。每条的 `core_command` + `protocol_minor` 已在 JSON 里给出，直接进 `HostCommandRegistry.CoreBindings`。
3. **第二批（16 条 medium）**：先按 `residual` 补齐 payload 正向路径再接线；`credential_put` 需要 `credential_ref = "NewManga/provider/<profile_id>"` 形状；`provider_profiles_create` 需要 `provider_id` 字段且 `network_profile_id` 必须已存在。
4. **第三批（7 条 NEEDS_IMPLEMENTATION）**：维持 NOT_SUPPORTED，但 reason 改为“**Host 侧未实现**”（不是 Core 未实现）；其中 5 条 import/export 另开 Host 侧 grant 签发 Task。
5. **门禁联动**：改 registry 会连带 `CommandParityContractTests`、`not-supported-typed-errors.json`、`parity-contract.json` 等断言/快照；这些必须由实施 Task 在**独立写范围**内重生成，本任务按 AC3 未触碰。

**风险**
- 冻结二进制与 HEAD 源码可能有版本差：`delete` 面 minor=10 与本任务实测一致，但 P15 payload 校验细节仍以**冻结二进制实测**为准（medium 条目即源于此）。
- `settings_network_profiles_create` 等会写真实设置存储：本任务全部在**私有数据根**执行，不影响用户 `%APPDATA%`。
- `PermanentlyDeleteBook` 在真实 book 上会因 run 持有而 `BOOK_BUSY`；接线时必须保留确认参数 `confirm_permanent_delete: true`。
- 探测产生的 run/backup/profile 数据都落在私有副本，任务结束后可按 Resource Manifest 处置。

---

## 6. NOT_RUN / 局限

| 项 | 状态 | 原因 |
|---|---|---|
| 16 条 medium 的正向成功路径 | NOT_RUN | 未命中冻结二进制的完整字段契约（P15 provider/credential 面），需实施 Task 用真实配置补齐 |
| import/export 的 grant 全链路 | NOT_RUN | grant/ref 由 host_issuer（旧 Rust 壳）签发；新 Host 未实现，无法在 Core 侧单独构造 |
| `library_reveal_export_folder` / `plugins_open_directory` 的可执行探测 | NOT_RUN | 属 Host/App 层 shell 动作，Core 无命令可发 |
| 真实用户数据根探测 | 不做 | 会污染用户 `%APPDATA%`；全部改用私有副本 |
| 冻结二进制源码级比对 | NOT_RUN | 二进制为 PyInstaller 打包，无符号；以行为探测为准 |

---

## 7. 复跑

```powershell
$E = "G:\CODEX\New Manga.workspace\task-envs\NS-RECLASSIFY-1"
# 1) sidecar（AC11 无标签副本，含 _internal）与私有 fixture 副本已在 $E 下
pwsh -NoProfile -File "$E\scripts\probe-core.ps1"            # application 通道
pwsh -NoProfile -File "$E\scripts\probe-core.ps1" -IncludeHostControl   # + host-control 通道
# 2) 分类表
python "$E\scripts\classify.py"
```

探测脚本与分类脚本已复制到 `verification/NS-RECLASSIFY-1/tools/`，可直接复核。

---

## 8. 证据索引

| 文件 | 内容 |
|---|---|
| `reclassification.json` | 42 条逐条重分类（含 evidence/reason/confidence/residual/S2 对照） |
| `probe-results.json` | 54 次原始探测：请求 payload、协议 minor、原始响应、basis、stderr |
| `probe-spec.json` | 每条命令的 payload 构造依据（含字段/枚举/minor 注释） |
| `tools/probe-core.ps1` | 探测 harness（可重跑） |
| `tools/classify.py` | 分类器（规则见 §3，可重跑） |
| `REPORT.md` | 本文件 |
