---
id: M2-AC5-BUILD-FRESH-CHECKOUT
title: "fresh checkout 构建链根治：build.rs 可诊断 sidecar 缺失 + build_sidecar.ps1 增量短路（M2-AC5 候选）"
kind: fix
status: in_progress
approval: orchestrator_delegated_2026-09-30
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（待派发，非作者静态）
depends_on: []
base_commit: 251f7425a7c68e4812b09f073f5413188ad9de6f
branch: agent/zcode/M2-AC5-BUILD-FRESH-CHECKOUT
worktree: G:/CODEX/New Manga.worktrees/M2-AC5-BUILD-FRESH-CHECKOUT-zcode
integration_commit: null
---

# M2-AC5-BUILD-FRESH-CHECKOUT：fresh checkout 构建链根治

## 来源与目标

- REBASELINE_PLAN §38 与 M2-AC5 integration checkpoint 登记候选：「fresh checkout 须先跑 build_sidecar.ps1」的构建顺序脆弱性——M2-AC5 集成 i1 首跑 EXIT=101 的实际后果（tauri `bundle.resources` 指向 gitignored `target/core-sidecar/core-sidecar`，缺失时 `generate_context!` 编译期失败且报错不可操作）。
- Goal 追溯：doc/GOAL.md（2026-09-30）清算集合 T2。
- 一个可观察的交付结果：fresh checkout（无 sidecar 产物）时 `cargo check/test/build` 失败并给出**可操作指引**（运行 `packaging/m2ac5/build_sidecar.ps1`）；sidecar 已存在时构建行为与现基线逐字节一致。

## 方案冻结（编排裁决，代理裁决留痕、用户可撤销）

1. **build.rs 前置探测**：`tauri_build::try_build` 之前探测 `apps/desktop/src-tauri/target/core-sidecar/core-sidecar` 是否存在；缺失则 `panic!` 输出可操作指引（脚本路径、README 路径、原因一句话）。不自动执行 PyInstaller（build.rs 内跑重构建魔法多、耗时不可控、依赖 build venv 存在性——fail-closed + 可诊断优先）。
2. **build_sidecar.ps1 增量短路**：目标 onedir 产物已存在且未传 `-Force` 时直接输出 skipped 并 EXIT=0（为自动化调用铺路；`-Force` 全量重建）。不改变现有构建产物布局与参数。
3. **不加 `beforeBuildCommand`**：它只在 tauri CLI 流程生效，覆盖不到 cargo check/test 主路径；build.rs 方案已覆盖全部路径。理由记录于 packaging/m2ac5/README.md。

## Acceptance Criteria

- [ ] AC1（可诊断失败）：模拟缺失态（临时改名 target/core-sidecar）后 `cargo check` 失败且 stderr 含 `build_sidecar.ps1` 指引；恢复后构建正常（红绿证据）。
- [ ] AC2（增量短路）：`build_sidecar.ps1` 在产物存在时跳过（EXIT=0 + skipped 输出）；`-Force` 触发全量重建；脚本其余行为不变。
- [ ] AC3（回归）：存在态下 `cargo test` 全套 EXIT=0（T1 后基线 44 passed/1 ignored）；`cargo build` 正常。
- [ ] AC4（文档）：packaging/m2ac5/README.md 记录 fresh checkout 流程与 beforeBuildCommand 不采用的理由。
- [ ] AC5（范围纪律）：diff 仅触及允许路径；`diff --check` EXIT=0。

## 允许修改范围

- `apps/desktop/src-tauri/build.rs`
- `packaging/m2ac5/build_sidecar.ps1`、`packaging/m2ac5/README.md`
- `apps/desktop/src-tauri/src/**` 内如需为探测逻辑新增可测单元（若探测逻辑可提取为 crate 内函数供 build.rs 逻辑复用则允许；build.rs 本身不可单测，AC1 以集成红绿证覆盖）
- 本 Task 文件、Handoff、verification/M2-AC5-BUILD-FRESH-CHECKOUT/**

## 禁止范围

- `tauri.conf.json`（共享配置；方案冻结明确不加 beforeBuildCommand）
- `apps/desktop/src-tauri/gen/**`、`apps/desktop/src-tauri/permissions/**`、`Cargo.toml`/`Cargo.lock`
- `packaging/m2ac5/core_sidecar.spec`、`entries/**`、`requirements-build.txt`（PyInstaller 打包语义）
- `src/**`（Python Core）、`apps/desktop/frontend/**`

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 红证 | 改名 target/core-sidecar → cargo check 断言失败含指引 | worktree cargo | NOT_RUN | 待入 verification |
| AC1 绿证 | 恢复 → cargo check EXIT=0 | worktree cargo | NOT_RUN | 待入 verification |
| AC2 增量短路 | build_sidecar.ps1（无参，产物在）→ skipped EXIT=0；-Force → 重建 | m2ac5-build venv | NOT_RUN | 待入 verification |
| AC3 回归 | cargo test 全套 | worktree cargo | NOT_RUN | 待入 verification |
| AC5 范围 | git diff --stat + --check | worktree git | NOT_RUN | 待入 verification |

## 依赖、风险与阻塞

- 依赖：无未完成 Task（T1 已 done）。
- 风险 1：build.rs panic 信息在 CI/其他开发者环境可能被日志截断——指引文本放首行。
- 风险 2：build_sidecar.ps1 短路判定（存在即跳过）在产物损坏时可能误跳过——脚本保留 `-Force` 与 README 说明；产物完整性校验不做（超范围，登记观察）。
- 风险 3：worktree 的 target/ 独立——AC1/AC3 均在 worktree 内验证（其 target 已有 sidecar 副本，改名模拟缺失态）。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex（代行）填写 integration_commit 并改 done。
