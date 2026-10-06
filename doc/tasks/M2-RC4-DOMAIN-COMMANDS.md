---
id: M2-RC4-DOMAIN-COMMANDS
title: 撤销、重渲染与修订历史 Core 域命令面端到端闭环
kind: feature
status: done
approval: user_2026-10-07_autonomous_rc4_and_next_priority
suggested_owner: Codex Executor
owner: Codex Executor
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-WORKBENCH-REACT-1, M2-SFX-MISROUTE-UI-IMPL-1, M2-REGION-RETYPE-CORE]
base_commit: 444210085dacaa92a56400bc21aadb64fce1fbf1
branch: codex/rc4-domain-commands
worktree: G:/CODEX/New Manga.worktrees/RC4-domain-commands
integration_commit: 0a7e0d5b
---

# M2-RC4-DOMAIN-COMMANDS

## 来源与目标

用户接管授权；三前置已 done，A/B/C 不重新打开。RC-4 原登记为 UI-MITIGATION 偏差 2/3/4/7。以 [冻结契约](../contracts/M2-RC4_DOMAIN_COMMANDS.md) 为本任务实施规格，解除撤销/重渲染/历史硬禁用并完成 Core→stdio→Tauri→React→持久化/图像读取闭环。

Codex 实测未发现 ZCode CLI 或 connector 可用，因此使用本会话 Executor 实施；不依赖 ZCode 聊天历史。DeepSeek 为非作者 Reviewer。

## Acceptance Criteria

- [x] AC1 三命令 DTO、校验、typed errors、协议 minor 4、Tauri production allowlist/ACL 全接通；旧命令保持语义，probe/AC1 零扩权。
- [x] AC2 restore 新建 restored revision，保持旧历史/pin/人工文字/Lock，含事务内并发零写守卫；history 摘要真实可追溯。
- [x] AC3 实际 headless 文字渲染；sfx skip/manual 不绘制旧译文，clean 缺失 fail-closed，无 AI 调用；新产物与原始文件保护证据；preview 经既有资源通道读取。
- [x] AC4 UI 三入口、10 秒 undo、确认恢复、失败显示、busy/切页/陈旧响应保护、实际交互检查全部可运行。
- [x] AC5 Handoff/逐次 raw 测试日志/独立 DeepSeek Review/返修/Integration Gate/merge/post-merge 回归齐全，Codex 才可置 done。

## 允许修改范围（allowed_paths）

- `src/application/editing/service.py`、`src/application/editing/errors.py`；`src/application/rendering/service.py`（仅 RC-4 必要保护/错误修复）。
- `src/bootstrap/core_service.py`；`src/infrastructure/rendering/pillow_rendering.py`（拟议 headless 适配器）；`src/infrastructure/resource_channel/render_preview.py`（拟议只读预览发布适配器）。不修改 ports/Schema。
- `src/bootstrap/core_assembly.py`：Codex 于 2026-10-07 授权可将 optional original Managed Copy reader 透传给 `RenderService`，以支持正常导入/clean 流未创建 ORIGINAL artifact 行时恢复被 SFX skip 遮盖的原始像素；默认 `None` 保持既有调用行为。
- `apps/desktop/src-tauri/src/library_bridge.rs`、`src/main.rs`、`build.rs`、`capabilities/**`、`permissions/**`（均相对 src-tauri，只有三命令/生产子进程配置）。
- `apps/desktop/frontend/src/region/**`、`src/workbench/**`、`src/resourceChannel/commandSurface.test.ts`、`src/testSupport/**`（均相对 frontend）；不新增生产依赖。测试依赖确需增加先由 Codex 记录范围。
- `apps/desktop/frontend/package.json`、`apps/desktop/frontend/package-lock.json`：Codex 于 2026-10-07 授权仅为真实 DOM 交互测试增加 `jsdom@26.1.0` devDependency，必要时可加测试用 `@types/jsdom@21.x`；不得增加生产依赖或改全局 Vitest 配置。
- `tests/core/**`、`tests/editing/**`、`tests/rendering/**`、`tests/m2_resource_channel/**`（任务所需测试；Codex 于 2026-10-07 重启后核实仓库现存资源通道测试目录实际为 `tests/m2_resource_channel/`，本路径事实纠正已授权）。
- 本 Task、`doc/handoffs/M2-RC4-DOMAIN-COMMANDS*`、`verification/M2-RC4-DOMAIN-COMMANDS/**`。C1 rev 1.6 与新冻结契约只由 Codex 修改；总索引/STATUS/PLAN/Review 只由 Codex 维护。

## 禁止范围

不修改 A/B/C Task 或重新实现既有能力；不修改 Legacy src/ui、数据库 Schema/ports、业务阈值 0.90、SFX 默认策略、BJ13 补标/补画、模型权重、GATE runner 场景集、用户实际数据库/源文件；不合并 main、不 push、不清理旧 worktree。

## 测试要求

解释器：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`；PowerShell，隔离 temp data root。每次日志带 shell/venv/commit/命令/EXIT，skip 逐条解释。

| 场景 | 计划命令 | 初始结果 |
|---|---|---|
| Core/SQLite/render/preview | python -m pytest tests/core tests/editing tests/rendering tests/resource_channel | NOT_RUN |
| frontend 全量与 build | npm test / npm run build | NOT_RUN |
| Rust bridge/ACL + real sidecar | cargo test -- --test-threads=1 | NOT_RUN |
| 全量回归 | python -m pytest tests | NOT_RUN（已知 test_catalog 基线失败单列） |

## 依赖、风险与阻塞

全部硬依赖已集成。生产 headless renderer object() 占位是本任务必要影响面；本契约采用同步 page render service，明确不声称完整 PipelineRun 接线。preview 发布与 Artifact commit 是两步，已提交但预览失败需显式结果。零新产品设计，沿 FROZEN 三入口与既有视觉。当前无业务阻塞。

## 交付与运行记录

- 2026-10-07 Codex refresh/rebaseline：main 44421008，干净；详见 verification/rebaseline-20261007.md。释放 commit 为本文件首次提交，base 字段为审计基线，Owner worktree 起点取该 release commit（文档漂移，无产品变更）。
- 2026-10-07 Core/Rust 子面交付：claim 0fba6079 → feat 37110749（三命令 Python/Rust/Pillow headless/preview 发布）→ 测试轮 58b3706d（envelope minor 4 期望、skip-SFX 原图像素恢复断言、typed fail-closed、preview 轮换、真实 stdio/Pillow 新测试）→ Handoff e6b3e811。验证：focused 399 passed / 全量 1852+1sk+1 既有 catalog 失败 / cargo 51 passed+1 ignored / sidecar EXIT=0（raw 见 verification/M2-RC4-DOMAIN-COMMANDS/raw/core-*）。
- 2026-10-07 React 子面交付：a27b3443 初版 → 独立 Review changes_requested（R-1 P1 切页/迟到响应覆盖、R-2 P2 预览 mock、R-3 P2 过期文案，doc/reviews/M2-RC4-DOMAIN-COMMANDS-a27b3443-react-reviewer.md）→ 返修 6f3544a2（统一请求版本+page epoch 守卫、迟到 URL revoke、非零 PNG bytes、PREVIEW_UNAVAILABLE、文案更新）→ Handoff ada80767。验证：117 tests + build EXIT=0（raw react-review-fix-*）。
- 2026-10-07 组合与 Gate（RC4-integration@5954bb4b）：Core+React 串行组合，reviewer-core 37110749 证据 4 份（组合树曾 7 failed=契约行为 vs 旧期望，已由测试轮按契约处置）import 入库；组合树复跑 focused 399 / 全量 1852+1sk+1 既有 / cargo 51 / sidecar EXIT=0（HEAD 绑定 78e4f24d）/ frontend 117+build / 代码面 diff --check EXIT=0。
- 2026-10-07 DeepSeek 独立 Review r1（对 58b3706d + 6f3544a2，组合树 5954bb4b）：**approved_with_conditions**（0×P0/P1；3 blocking + 5 非阻塞 + 5 nit），报告 doc/reviews/M2-RC4-DOMAIN-COMMANDS-5954bb4b-dsh-r1.md。r1 独立确认 7 failed 测试更新为契约驱动正当更新（非迁就实现）、范围纪律基本 PASS。
- 2026-10-07 r1 返修：Core `e495910f`（RC4-01 list/restore wire 级 SQLite 测试 7 用例；RC4-02 墨水显式断言 ≥400 实测 1389 + diff 口径写明；RC4-06 可注入 revoke 失败 fail-closed 测试；RC4-08 compose ValueError→MISSING_REQUIRED_INPUT / OSError→ARTIFACT_WRITE_FAILED 拆分+两测试；RC4-09 四处陈旧命名注释；RC4-11 等值短路+测试）→ focused 408 / cargo 53 / stdio+revision 8 全绿；React `7021d34c`（RC4-07 卸载 in-flight 作废；RC4-09 ViewerPanel 注释；RC4-13 非冻结码判别用例）→ vitest 118 / build EXIT=0。逐项处置表见两份 Handoff 返修段。
- 2026-10-07 RC4-05 追认（Codex/集成方）：`gen/schemas/*.json` 4 文件系 build.rs 生成器对 RC-4 三命令权限条目的实质再生，随 58b3706d 入库，属交付必要生成物；按 M2-REGION-RETYPE-CORE P3-2 先例追认为 allowed_paths 授权范围内，后续同源生成物再生不再单列审批。
- 2026-10-07 组合返修 Gate（RC4-integration@7c9d3a32 = merge Core e495910f + React 7021d34c）：focused **408 passed** / cargo **53 passed+1 ignored** / frontend vitest **118 passed** + build EXIT=0 / 代码面 diff --check EXIT=0 / 全量 **1859 passed + 1 skipped + 3 failed**——failed 定性：① `test_catalog` 122≠97 既有登记基线失败（main 同口径）；② ③ `tests/ui_shell/test_repair13_import_entry.py` 两例 QML 环境敏感失败（btnImport isEnabled），main@8c8e0eb4 基线对照同样 2 failed（raw combined-gate-r2fix-uishell-main-baseline.log），且 `git diff 0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/` 为空＝RC-4 改动零接触该路径，非本任务回归。1 skipped=registry_readiness（dev venv 有意携带 ML 栈，用户批准）；Owner 轮 7 skipped 与此差异=PowerShell 驱动下 openssl 不在 PATH 的 6 个 TLS skip（RC4-04 口径闭合）。日志 combined-gate-r2fix-*。
- 2026-10-07 DeepSeek 独立 Review r2（对组合树 1e6b58b9）：**approved_with_conditions（0×P0/P1/P2；r1 三项 blocking 全部闭合）**，报告 doc/reviews/M2-RC4-DOMAIN-COMMANDS-1e6b58b9-dsh-r2.md。裁决：RC4-01/03/05/06/07/08/09/11/13 闭合，RC4-02/04/10/12 降级接受（登记口径）；新 finding=2×P3（N-1 范围追认、N-2 git 原始日志缺档）+3×P4（N-3 SKIPPED 原行、N-4 注释补行、N-5 head 等价句）。AC 层：AC2 证据面已满足（RC4-01 闭合）；AC5 待 merge+post-merge。
- 2026-10-07 r2 条件处置（Codex/集成方）：① **N-1 追认（RC4-05 同款）**：`apps/desktop/src-tauri/src/core_bridge.rs`（`MockCoreChannel.fail_revoke_for` test-only 注入口，生产路径不可达）由 r1 返修引入，属 allowed_paths 授权范围（`apps/desktop/src-tauri/**` 意旨涵盖；与 RC4-05 生成物先例同理），Codex 追认登记，并把「test-only Rust 注入面」视为该条 allowed_paths 的既定解释；② **N-2/N-5**：五条 git 原始日志入库 `raw/combined-gate-r2fix-gitlogs.log`——代码面 diff --check EXIT=0、`0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/` 为空、`37110749..58b3706d -- src/` 仅 service.py（+38/−16，与 Handoff 口径逐字一致＝RC4-02 残留闭合）、`7c9d3a32..1e6b58b9` 仅 docs/verification、`1e6b58b9..d625d6d0` 仅 test_core_service.py；③ **N-3**：`raw/combined-gate-r2fix-full2.log`（-ra 重跑，绑 d625d6d0）含 `SKIPPED [1] tests/providers/test_registry_readiness.py:237` 原行，3 failed/1859 passed/1 skipped 数字与前轮一致；④ **N-4**：`tests/core/test_core_service.py` 两处 minor 注释链补 `M2-RC4-DOMAIN-COMMANDS: 3 -> 4`（Core r2fix 6a7b4c3d，已 merge）。
- 2026-10-07 head 等价性（N-5 闭合）：被审代码 head **d625d6d0** = r2 被审 head `1e6b58b9` + Core r2fix `6a7b4c3d`（仅 tests 注释）+ 本收口 commit（仅 docs/verification）；`git diff --name-status` 逐段证明见 raw/combined-gate-r2fix-gitlogs.log，Gate 证据（full2 -ra 绑 d625d6d0；focused/cargo/frontend 绑 7c9d3a32 代码树经 [4][5] 等价链覆盖 d625d6d0）对被审 head 成立。
- 2026-10-07 Integration Gate 通过并 merge：main fast-forward 至 `0a7e0d5b`（= r2 收口 commit，integration_commit 同值）。post-merge 三套件回归（raw postmerge-*）：pytest 全量 **1859 passed + 1 skipped + 3 failed**（与组合 Gate 等量同因：test_catalog 既有 + ui_shell QML 两例 main 基线同样失败）；cargo **53 passed + 1 ignored**；frontend **npm ci 后 vitest 118 passed + build EXIT=0**（main 工作区 node_modules 缺 jsdom 属环境漂移，非代码回归，已由 npm ci 修复并如实登记）。AC5 闭合，Task 置 done。
