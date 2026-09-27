---
task_id: M2-RC2
author: ZCode
recipient: DeepSeek Harness（非作者独立 Review）与 Codex（集成）
base_commit: 22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5
delivery_head: a8fb17ca（精确 SHA `a8fb17cab78e53cdafb8656ab3d9e7044da0f411`）
status: delivered
review_status: awaiting_review
parent_task: doc/tasks/M2-RC2.md
parent_deferrals: M2-RC1 F-03/F-05（accepted_deferral，702b02b0 Handoff 登记）
---

# Handoff：M2-RC2 — Resource Channel Command Surface and Sidecar Boundary Hardening

- **交付 head**：`a8fb17cab78e53cdafb8656ab3d9e7044da0f411`（branch `agent/zcode/M2-RC2-resource-channel-hardening`；worktree `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`）。
- **Head 链**：`22a2c2bf`（frozen base）→ `b4a78f0c`（claim：仅取入 Task 文件 + in_progress）→ `9b50dedc`（Python：catalog authority + import 隔离）→ `65ea015e`（Rust：命令面硬化 + ACL/CSP）→ `24da5a91`（前端 deny 矩阵 + RC2 场景）→ `a8fb17ca`（RC2 E2E runner + allowlist 自报 + 证据）。
- **范围**：39 路径（`git diff --name-status 22a2c2bf..a8fb17ca`，转录 [raw/final-diff-name-status.txt](../../verification/M2-RC2/raw/final-diff-name-status.txt)），全部在 Task 允许路径内；无共享 Contract、无 SQLite schema/migrations（`src/infrastructure/sqlite/` 未触碰）、无 Legacy QML、无根依赖/锁文件、无打包 release 面（`bundle.active` 保持 false，Cargo.toml/lock 未改）。

## AC 逐项 disposition

### RC2-AC1 命令面收敛（F-03）——已实现并测试

**WebView 可达面（六层边界，逐层证据见 [allow-deny-matrix.md](../../verification/M2-RC2/allow-deny-matrix.md)）**：

1. `register_catalog` **从所有模式删除**（Rust 函数已不存在，编译期收敛）；probe/interactive 两阶段的真实 WebView invoke 均被拒（E2E D-01 / IP-1）。
2. 生产 invoke 面恰好 3 命令：`issue_resource_url`（无 TTL 参数形状）、`revoke_ref`、`revoke_resource_refs`；`probe_config`/`probe_write_results`/`probe_exit`/`probe_issue_url` 仅在 `M2RC1_PROBE_OUT` 存在的 probe 模式注册。启动时向 stderr 自报生效 allowlist（`[m2rc2-allowlist]`），runner 两阶段对照 PASS。
3. Tauri ACL：命令经 inlined plugin `m2rc1-commands` 声明，`capabilities/m2rc1-commands.json` 仅授权 main 窗口；regenerated `gen/schemas` 快照入库。
4. CSP 从 `null` 收敛为显式策略（self + blob:/m2res.localhost + ipc 端点）；asset protocol 保持禁用。
5. **Catalog authority 移入 Core/SQLite**：新 `catalog_store.py`（独立 DB 文件，经 `M2RC2_CATALOG_DB` 注入；**未触碰共享 schema/migrations**）；host 的 `StdioCoreChannel` 不再持有 catalog map；wire issue 只带 `resource_id`/`revision_fingerprint`，`rel_path`/`scope_class` 参数出现即 `REF_MALFORMED`；未编目 id fail-closed（`RESOURCE_NOT_CATALOGED`）；无 catalog 源时空库启动（ping/shutdown 仍响应）。
6. **TTL 不可被调用方延长**：`service.issue` 拒绝 ≤0 或 > 默认 300 s 的 `ttl_seconds`（`REF_MALFORMED`）；TTL override 只存在于 probe 专用命令 `probe_issue_url`（仅 probe 模式）；生产形状走私 `ttlOverride` 键实测惰性（E2E D-02/IP-6：引用仍可服务）。

**拒绝矩阵证据**：pytest 17 项（`test_catalog_authority.py`：store 写入校验、bridge 参数拒绝、fail-closed、TTL 矩阵）、Rust 7 项新增（allowlist 矩阵、wire 形状、真实 sidecar 未编目拒绝 + TTL 延长拒绝）、vitest 7 项（`commandSurface.test.ts`）、E2E D-01..D-03 + IP 系列。

### RC2-AC2 独立 sidecar 入口（F-05）——已实现并测试

- **修前证据**（[raw/sidecar-import-before-fix.log](../../verification/M2-RC2/raw/sidecar-import-before-fix.log)，claim head `b4a78f0c`、任何代码修改之前抓取）：sidecar 入口传递加载 `infrastructure.filesystem`、`infrastructure.sqlite`、`infrastructure.sqlite.reading_export`、`domain.books.entities`。
- **修复**：`src/infrastructure/__init__.py` 改 PEP 562 惰性导入（Task 条件允许路径；理由：`__init__` 的传递导入是 sidecar 隔离障碍，修前证据构成必要性证明；产品侧 `from infrastructure import sqlite` 经惰性路径保持可用，有专门测试）。
- **修后门禁**：pytest 子进程白名单门禁（`test_sidecar_isolation.py` 4 项）+ E2E headless 检查 + **真实 sidecar 模块 dump**（`M2RC2_MODULE_DUMP`；probe/interactive 两阶段各 9 个项目模块，全部白名单内，无 filesystem/sqlite/domain）。汇总：[sidecar-isolation.md](../../verification/M2-RC2/sidecar-isolation.md)。

### RC2-AC3 诚实 Gate 与证据——已交付

- 四条冻结命令在交付树的记录：见下节；全部 exit 0，原始日志在 `verification/M2-RC2/raw/`。
- **E2E runner 是本 Task 交付项**：[run_e2e.py](../../verification/M2-RC2/run_e2e.py)（claim 时 BLOCKED → 交付且 GATE PASS）。
- S1-B 状态见下节；无产品级安全/安装/打包声明。

## 冻结命令验证（交付树 `a8fb17ca`，claim 基线对照 `b4a78f0c`）

| 命令 | 交付树结果（exit） | claim 基线 |
|---|---|---|
| `python -m pytest tests/m2_resource_channel -q` | **64 passed（0）** | 43 passed（0） |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | **19 passed（0）** | 12 passed（0） |
| `npm test --prefix apps/desktop/frontend -- --run` | **15 passed（0）** | 8 passed（0） |
| `python verification/M2-RC2/run_e2e.py` | **GATE PASS 10/10，probe 13/13（0）** | BLOCKED（runner 不存在） |

环境与释放基线一致（Windows 11 26200 / Python 3.14.6 / Cargo 1.98.1 / Node 24.15.0 / npm 12.0.1 / Vitest 2.1.9）。汇总：[final-verification.log](../../verification/M2-RC2/final-verification.log)；逐命令原始日志 `raw/final-*.log`、`raw/claim-baseline-*.log`。

## E2E 结果摘要（真实 sidecar + WebView2）

- probe 阶段 13/13 PASS：RC1 回归 E-00..E-09（含 F-01 暖缓存撤销、F-02 等大小改写、E-07 P95、E-08 256 MiB、E-09 超限 typed）+ RC2 新增 D-01（register_catalog 全模式拒绝）、D-02（ttlOverride 走私惰性）、D-03（probe issue 在 probe 模式可用——allow 侧对照）。
- interactive 阶段：production allowlist 自报恰 3 命令；进程整个观察窗存活（无退出命令泄漏）；无 probe 结果文件。

## 已知限制与登记事项（Reviewer 请重点核对）

1. **interactive 矩阵结果无法离开页面（设计后果，非缺陷）**：生产面无写通道、无退出命令；实测 `document.title` 不反映到 Tauri `window.title()` 也不反映到 Win32 窗口标题，脚本 `window.close()` 被 WebView2 阻止。因此 interactive gate 由外部可观察事实承载（allowlist 自报 + 存活 + 无结果文件），IP/IA 矩阵保留为页面自检。协议详见矩阵文档「Interactive 判定协议」。
2. `python -m` 下 `host_bridge` 以 `__main__` 名义运行，故真实 dump 的模块集合中不含 `infrastructure.resource_channel.host_bridge` 名目（headless `import` 检查含它，10 个）；白名单门禁只断言"不得加载"，不断言"必须加载"。
3. catalog store 用**独立 SQLite DB 文件**（lab 经 `M2RC2_CATALOG_DB` 注入）；共享产品 schema/migrations 未触碰（禁改路径）。产品库接线属后续产品化切片。
4. wire v1 issue 形状变化：host 不再携带 `rel_path`/`scope_class`（F-03 catalog authority 移入 Core 的直接结果）；Contract 文档未改动（禁改路径），信任边界（T5.2 host=可信层拿 facts）不变。
5. capability/ACL 授权面为当前单窗口形态的 `main` 窗口；多窗口/远程内容属产品化后续。
6. probe 命令面是证据 runner 特权面（依赖主机环境变量 `M2RC1_PROBE_OUT`），非 WebView 可切换状态。

## 诚实边界（S1-B 系列，逐项）

| 项 | 状态 | 说明 |
|---|---|---|
| S1-B3（DACL/完整性，产品级） | **NOT_RUN** | 本切片的完整性语义仅限 RC1 的 handle/digest 链；产品级 DACL 未触及 |
| S1-B5（生命周期） | **UNVERIFIED** | RC1 仅覆盖"Core 重启后旧 ID 不重绑"；其余生命周期（含 catalog 行生命周期与产品事件联动）未验证 |
| S1-B6（冷页缓存 1 s） | **NOT_RUN** | E-07 为每引用首字节（暖 OS 页缓存），不代言冷缓存 |
| S1-B8（打包/沙箱） | **NOT_RUN** | `bundle.active=false`；无安装/分发/沙箱声明 |

不宣称产品级安全、安装或打包就绪。

## DSH 独立 Review 复核清单

1. 复跑四条冻结命令（64 / 19 / 15 / GATE PASS），exit 0；对照 [final-verification.log](../../verification/M2-RC2/final-verification.log)。
2. **修前 FAIL 证据**核对：[raw/sidecar-import-before-fix.log](../../verification/M2-RC2/raw/sidecar-import-before-fix.log) 时间戳（2026-09-27T07:34:49Z）与 claim head `b4a78f0c` 早于实现提交；`src/infrastructure/__init__.py` 条件路径使用的必要性与最小性。
3. allow/deny 矩阵逐行对照实现与测试（[allow-deny-matrix.md](../../verification/M2-RC2/allow-deny-matrix.md)）：`register_catalog` 删除、probe 条件注册、TTL 形状、catalog authority、fail-closed。
4. E2E runner 门控逻辑（NOT_RUN/MISSING 计失败）与 13 场景的诚实性；`raw/e2e-gate.json` 与 stdout 转录一致。
5. 范围核对：`git diff --name-status 22a2c2bf..a8fb17ca` = 39 路径，无禁改路径；`gen/schemas` 4 文件为 capability 收敛的真实再生产物。
6. 上述「已知限制」逐条——特别是第 1 条（interactive 证据边界）是否接受为诚实披露。

复核报告路径建议：`doc/reviews/M2-RC2-a8fb17ca.md`。approve 后交 Codex 集成。
