---
id: M2-RC4-DOMAIN-COMMANDS
title: 撤销、重渲染与修订历史 Core 域命令面端到端闭环
kind: feature
status: ready
approval: user_2026-10-07_autonomous_rc4_and_next_priority
suggested_owner: Codex Executor
owner: Codex Executor
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-WORKBENCH-REACT-1, M2-SFX-MISROUTE-UI-IMPL-1, M2-REGION-RETYPE-CORE]
base_commit: 444210085dacaa92a56400bc21aadb64fce1fbf1
branch: codex/rc4-domain-commands
worktree: G:/CODEX/New Manga.worktrees/RC4-domain-commands
integration_commit: null
---

# M2-RC4-DOMAIN-COMMANDS

## 来源与目标

用户接管授权；三前置已 done，A/B/C 不重新打开。RC-4 原登记为 UI-MITIGATION 偏差 2/3/4/7。以 [冻结契约](../contracts/M2-RC4_DOMAIN_COMMANDS.md) 为本任务实施规格，解除撤销/重渲染/历史硬禁用并完成 Core→stdio→Tauri→React→持久化/图像读取闭环。

Codex 实测未发现 ZCode CLI 或 connector 可用，因此使用本会话 Executor 实施；不依赖 ZCode 聊天历史。DeepSeek 为非作者 Reviewer。

## Acceptance Criteria

- [ ] AC1 三命令 DTO、校验、typed errors、协议 minor 4、Tauri production allowlist/ACL 全接通；旧命令保持语义，probe/AC1 零扩权。
- [ ] AC2 restore 新建 restored revision，保持旧历史/pin/人工文字/Lock，含事务内并发零写守卫；history 摘要真实可追溯。
- [ ] AC3 实际 headless 文字渲染；sfx skip/manual 不绘制旧译文，clean 缺失 fail-closed，无 AI 调用；新产物与原始文件保护证据；preview 经既有资源通道读取。
- [ ] AC4 UI 三入口、10 秒 undo、确认恢复、失败显示、busy/切页/陈旧响应保护、实际交互检查全部可运行。
- [ ] AC5 Handoff/逐次 raw 测试日志/独立 DeepSeek Review/返修/Integration Gate/merge/post-merge 回归齐全，Codex 才可置 done。

## 允许修改范围（allowed_paths）

- `src/application/editing/service.py`、`src/application/editing/errors.py`；`src/application/rendering/service.py`（仅 RC-4 必要保护/错误修复）。
- `src/bootstrap/core_service.py`；`src/infrastructure/rendering/pillow_rendering.py`（拟议 headless 适配器）；`src/infrastructure/resource_channel/render_preview.py`（拟议只读预览发布适配器）。不修改 ports/Schema。
- `apps/desktop/src-tauri/src/library_bridge.rs`、`src/main.rs`、`build.rs`、`capabilities/**`、`permissions/**`（均相对 src-tauri，只有三命令/生产子进程配置）。
- `apps/desktop/frontend/src/region/**`、`src/workbench/**`、`src/resourceChannel/commandSurface.test.ts`、`src/testSupport/**`（均相对 frontend）；不新增生产依赖。测试依赖确需增加先由 Codex 记录范围。
- `tests/core/**`、`tests/editing/**`、`tests/rendering/**`、`tests/resource_channel/**`（任务所需测试）。
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
- Handoff/Review/实际测试：尚无。
