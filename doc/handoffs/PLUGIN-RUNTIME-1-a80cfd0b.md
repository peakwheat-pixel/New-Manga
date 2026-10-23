---
task_id: PLUGIN-RUNTIME-1
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: c793442946801bea7ab53799683cecc76260f672
delivery_head: 97485b89d8d341e78c7c7160a9aba0291b662f42
status: done
authorization: 用户 2026-10-23「授权 PLUGIN-RUNTIME-1，按建议值 D1–D6」
---

# Handoff — PLUGIN-RUNTIME-1（本地插件运行时，首发 `permissions: []`）

## 1. 交付摘要

按 `doc/design/SETTINGS_SECTION_C_SCHEMAS.md` §4.1–§4.4（冻结）+ 用户 2026-10-23 授权（D1–D6 按建议值）实现本地目录插件运行时，实现范围 `c7934429..97485b89`（实现 `a80cfd0b`，r1 修复 `7253286f`，r2 修复 `97485b89`）：

- **发现**（D4）：插件根 `<data_root>/plugins/<plugin_id>/`；只读扫描，不写插件文件，不做安装器/市场。
- **manifest v1**（§4.2）：fail-closed 校验（id 正则 + 目录名一致、name ≤80、semver、entry 相对 `.py` 且存在/不越界、hooks ⊆ 6 组、permissions ⊆ 词表且**非空拒绝**、min_app_version）；拒绝码稳定（`PLUGIN_MANIFEST_MISSING/INVALID`、`PLUGIN_ID_MISMATCH`、`PLUGIN_UNKNOWN_HOOK`、`PLUGIN_UNKNOWN_PERMISSION`、`PLUGIN_PERMISSIONS_UNSUPPORTED`、`PLUGIN_ENTRY_INVALID`、`PLUGIN_MIN_APP_VERSION`）。
- **默认禁用**（§4.3/D5）：迁移 **v6** 新增 `plugin_state`（`__global__` 行 = 全局开关，默认 0）与 `plugin_events`（append-only 审计）；启用状态与审计在 DB，插件文件只读。
- **隔离**（§4.3/D1）：每个 Hook 在独立 `python -I` 子进程执行（runner 读 stdin JSON、单次请求-响应、10s 硬超时、干净 env、cwd=插件目录）；崩溃/超时/坏输出 → `plugin_error` 审计 + 跳过该 Hook，主流程继续；`_hook_interpreter` 对打包环境 fail-closed（`PLUGIN_HOOK_UNAVAILABLE`）。
- **Hook 契约**（§4.4/D3）：`HOOK_NAMES` 六组冻结；`before_*` 可返回 override（`WRITABLE_HOOKS`），`after_*` 只读；payload/结果为 JSON dict。
- **审计**（D2）：`plugin_events(event_id, plugin_id, event_type, hook_name, detail_json, occurred_at)`，事件类型 6 种；60s 去重窗口防 list 重复写；审计失败不阻断 Hook。
- **wire**（应用层通道，minor 保持 3）：`plugins.list`、`plugins.set_enabled`、`plugins.set_plugin_enabled`、`plugins.audit_list`；错误码 `PLUGIN_NOT_FOUND`(not_found)/`PLUGIN_NOT_LOADED`(validation)/`PLUGIN_INVALID_REQUEST`(validation)/`PLUGIN_HOOK_TIMEOUT`(conflict,retryable)/`PLUGIN_HOOK_FAILED`(internal,retryable)/`CORE_UNAVAILABLE`(unavailable)。
- **Rust**：`LibraryChannel`/`Mock`/`Resilient`/`Stdio` 4 方法；5 个 production-only Tauri 命令（4 channel + `plugins_open_directory` 用 `tauri-plugin-opener`，Rust 本地）；`PRODUCTION_COMMANDS` 61→66、build.rs ACL、capabilities、`command_allowlist` 过滤、probe/AC1 表面测试同步。
- **前端**（D6）：`SettingsClient` 5 方法 + 类型；`PluginSettingsPanel`（默认关全局开关、逐插件启停、拒绝原因、审计最近 20 条、打开插件目录、错误映射）；`SettingsPage` **12/12 分类开放**（`DISABLED_SECTION_TEST_IDS` 为空）。

## 2. 验证

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/infrastructure/test_plugin_runtime.py tests/core/test_core_plugin_wire.py -q` | PASS（**24 passed**：17 runtime + 7 wire） |
| `python -m pytest tests -q` | **2633 passed** / 9 skipped / **3 既有失败**（2×`test_detection_manga_real` detector 权重环境、1×`test_workbench_viewmodel` 时序 flaky；与本改动无关；迁移 v6 后同步修正了 schema/restore/packaging 测试的版本硬编码） |
| `cargo test --locked -- --skip packaged_sidecar_tests --test-threads=1` | PASS（**153 passed** / 1 ignored / 12 filtered） |
| `npx vitest run` | PASS（**45 files / 434 tests**） |
| `tsc --noEmit` | exit 0 |
| GUI 烟测（dev preview） | PASS：12 开；插件面板发现 demo-detect + bad-permissions（拒绝原因可见）；审计 load_ok/load_rejected；全局启用 + 逐插件启用后审计新增 2 条——`screenshots/01-plugin-panel-enabled.png` |

原始日志/截图：`verification/PLUGIN-RUNTIME-1/**`。

## 3. 未执行 / 明确非本 Task 范围

1. **流水线 Hook 接线点未接入真实 Run**：`PluginService.run_hook` API + 隔离/审计/超时已有真实子进程测试，但 before/after detect/ocr/export 在流水线运行中的触发点属于后续批次（本 Task 授权范围是运行时与只读面）。
2. **打包环境 Hook 解释器**：PyInstaller onedir 无独立 `python.exe` 时 fail-closed（`PLUGIN_HOOK_UNAVAILABLE` + 审计）；捆绑解释器/sidecar 特殊入口是发布前 follow-up。
3. **带权限插件**（files_read/files_write/network/model）按 §4.3 首发限制一律拒绝加载。
4. `plugins_open_directory` 用既有 `tauri-plugin-opener`，不新增插件依赖。

## 4. 推荐下一步

- C-2/C-3/PLUGIN-RUNTIME-1 均关闭后，设置分区 A/B/C 与插件运行时主体完成；后续自然候选：
  1. **PLUGIN-RUNTIME-2（Hook 流水线接线）**：把 `run_hook` 接到 detect/ocr/export 真实步骤（before_* override / after_* 只读），并补 Run 内触发测试；
  2. 插件打包解释器 follow-up；
  3. 保留项 `V1-RELEASE-SIGNING-1`（`in_review`）等待发布签核。

## 5. Review r1 处置（changes_requested）

- **P1-1 安全边界（诚实降级）**：插件是**受信任的本地代码**。`permissions: []` 的承诺收窄为「Core 不授予任何能力句柄」：不传 Core 对象/DB/模型/凭据/配置路径/网络配置，子进程最小 env + `-I` + cwd=插件目录；**不承诺 OS 沙箱**——恶意插件仍可用用户 OS 权限自行读写文件/联网。UI/Task/Handoff/manifest/service 文案同步修正；补「子进程无 Core env、无法 import Core 模块、输出 >256KB 被拒」测试。OS 沙箱另立 `PLUGIN-RUNTIME-SANDBOX-1`（proposed，未授权）。
- **P1-2 manifest 未知字段**：`_ALLOWED_KEYS` 白名单，未知顶层键 → `PLUGIN_MANIFEST_INVALID`；目录/manifest 符号链接根校验（`resolve().is_relative_to(root)`）；补拒绝测试。
- **P1-3 生命周期**：Task/STATUS/TASK_LEDGER 统一 `in_review`；Task Closeout 改为「待 Review approved 后 closeout」；allowed_paths 补 doc 指针。
- **P2**：`plugins.list` 移除 `plugin_root` 绝对路径投影（前端未使用）；`plugins_open_directory` 按 Core 同源 data root 解析（`NEWMANGA_DATA_ROOT` → `LOCALAPPDATA/New Manga`）+ `plugins`；审计改为**状态驱动**（load 事件只在状态变化时写，严格 append-only，删 60s 窗口）；Hook payload 注入 `schema_ref=nm-plugin-hook/1`；AC6 拆为 AC6a（API/隔离，已覆盖）/AC6b（GUI 触发 Hook，**NOT_RUN**，流水线接线属 PLUGIN-RUNTIME-2）。
- **v6 专项**：`test_v6_tables_start_empty_and_are_indexed` 断言两表 0 行 + 两索引；`test_frozen_runtime_contract` 改为双源校验（`application_metadata` vs `schema_migrations` max）。

## 6. Review r2 处置

- **P1-1 剩余承诺**：Task 目标 4/非目标、设计 §4.3/§4.5 全部加「trusted-code 边界」实现注记——`permissions: []` = Core 不授予能力句柄，**不是 OS 沙箱**；旧「无文件/网络/模型访问」表述已由注记替换。
- **P1-3 剩余**：Task 正文 `in_progress` → `in_review`；Closeout「未开始」→「待 Review approved 后 closeout」。
- **P2**：前端 `plugin_root` 类型/规范化/测试 fake 删除；Hook 输出改为**流式字节上限**（`Popen` + 读线程，超 256KB 立即 kill，stderr `DEVNULL`；中文 100k 字符用例覆盖）；`_write_state` 复用 `_manifest_fingerprint`（enable 后不再重复 `load_ok`，补测试）；`test_frozen_runtime_contract` 改为 `application_metadata` vs `schema_migrations` MAX 双源；`schema_ref` 注入处做类型校验；GUI 实测「打开插件目录」打开 `.../data-root/plugins`（与 Core 一致）并截图 `screenshots/02`。
- **验证（r2 修复后）**：定向 31 passed；全量 2640 passed / 3 既有失败；cargo 153；vitest 45/434；tsc 0；check.ps1 PASS。

## 7. Closeout（2026-10-23）

- 独立 Review 结论：**approved**（`verification/PLUGIN-RUNTIME-1/review-r3.md`，审查头 `992225d5`；r1/r2 为 changes_requested，均已修复）。
- Task 状态 `done`；证据 pin `verification/PLUGIN-RUNTIME-1/**`。
- 后续（未授权）：`PLUGIN-RUNTIME-2`（Hook 流水线接线）、`PLUGIN-RUNTIME-SANDBOX-1`（OS 沙箱）、打包解释器 follow-up。
