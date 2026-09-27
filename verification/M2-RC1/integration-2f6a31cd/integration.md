# M2-RC1 集成核验

日期：2026-09-27（Asia/Shanghai）

## 固定对象与合并

- 固定 base：`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`。
- Owner branch：`agent/zcode/M2-RC1-large-media-resource-channel-runtime`；reviewed head=`2f6a31cd67e983e789c02cb4e33c194f0e012f23`。
- DeepSeek Harness 第 4 轮 Review：`approve`，无新 P0/P1/P2，R-01..R-06 closed；报告 [M2-RC1-FIX3-2f6a31cd.md](../../../doc/reviews/M2-RC1-FIX3-2f6a31cd.md)。
- Owner tip=`ce3c3771d15c60b743b1e1da936edc445676b305`，仅导入 Review/dispatch 原件并回填 Task/Handoff；`2f6a31cd..ce3c3771` 的 5 个路径都是审查/文档证据，产品源码不变。Owner 分支仍指向 `ce3c3771`，集成前后均未推进；测试后 Owner worktree 干净。
- Codex merge=`3a24684007fd5a5e855f324077ad996841300f27`，parents=`cb6e6d5113ee3224e48e3c54b930792c4734be7b` + `ce3c3771d15c60b743b1e1da936edc445676b305`。唯一冲突为 `doc/tasks/M2-RC1.md` add/add；以 master release Task 为基础回填 Owner AC、运行证据和 Handoff 内容，再登记 pytest.ini 的窄范围例外。

## Codex 命令级复跑

全部命令在 Owner worktree、Windows PowerShell 7.6.6、Python 3.14.6、Cargo 1.98.1、Node v24.15.0、npm 12.0.1 下运行；完整 stdout/stderr 与逐命令退出码见 [codex-command-transcript.log](codex-command-transcript.log)。E2E 使用此前不存在的独立 `TEMP=G:\CODEX\NewManga-M2-RC1-integration-temp-20260927`。

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/m2_resource_channel -q` | `43 passed`，EXIT=0 |
| `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --locked` | `12 passed`，EXIT=0；有 unused-import 警告 |
| `npm test --prefix apps/desktop/frontend -- --run` | `8 passed`，EXIT=0 |
| `cargo build --release --locked --manifest-path apps/desktop/src-tauri/Cargo.toml`（E2E 前置构建） | EXIT=0；有未使用 mock/导入的警告 |
| `python verification/M2-RC1/run_e2e.py`（连续两次） | 每次 `10/10 PASS`、EXIT=0；E-00..E-09 全 PASS |

WebView2 两次关闭时均打印 Chromium `Failed to unregister class Chrome_WidgetWin_0` / Win32 1412 诊断，但 runner 两次均正常 exit 0 且 10 项全部 PASS。

## 范围与 Contract

- `git diff --name-status 2dca20cd..2f6a31cd`：62 条（61 个新增路径 + `pytest.ini` 修改），EXIT=0；逐项转录见命令日志。除 `pytest.ini` 外，其余路径均匹配 M2-RC1 Task 已登记的授权模式；未触碰 forbidden product paths。merge 的 first-parent delta 为 66 路径，增加项是 DSH 证据导入与本日志，不等于 Owner reviewed delivery 数。
- `git diff --check 2dca20cd 2f6a31cd`：EXIT=0；集成工作树相对 first parent 的 `git diff --check`：EXIT=0，无 whitespace 诊断。
- `git rev-parse master:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 与 reviewed head 的同一 blob 均为 `fc35913801297ee1876ea395f9c5041a16226f20`；Contract 1.1 未被改写。
- `pytest.ini` 位于仓库根目录，Task 原白名单未逐项列出它；其唯二新增行只注册本 Task 需要的 pytest `slow` marker，不是依赖/锁文件。Codex 将这项单文件、单用途配置明确接受为本次集成的窄范围例外，并回填 Task；其它根配置仍未获授权。
- `src/ui/**`、`src/bootstrap/app.py`、`src/domain/**`、`src/ports/**`、`packaging/**` 的集成差异为零。

## Review 观察与实现边界

- O-01：`final-verification.log` §0 的 “only the paths in porcelain” 把 FIX-3 代码差异与随后定稿的 Handoff/log 范围混在一起，62 条固定 reviewed-head 路径差异转录仍准确。
- O-03：根 `pytest.ini` 是只注册 `slow` marker 的测试配置文件，不是依赖/锁文件；它不在 Owner Task 原白名单逐项列举中，故本集成已按单文件、单用途回填窄例外。
- `MEDIA_TOO_LARGE_BY_HANDLE` 是真实的 wire 名称偏离，语义由 `RESOURCE_TOO_LARGE` 承载；Contract §10.2 允许后续命名微调。
- `REF_REPARSE_POINT` 是 Python-only；Rust 没有 pre-open walk，句柄 containment 仍承担权威校验。
- F-03（command surface / capability / ACL / CSP 与 Core/SQLite catalog authority）和 F-05（sidecar 独立入口）均保留为 `accepted_deferral`，已登记在 [M2-RC2](../../../doc/tasks/M2-RC2.md)，状态 `proposed / NOT_RELEASED`，本次没有授权实现。
- M2-C2 的 4×P3 advisory 仍须折叠进下次实际触碰 Contract 的 Task，不得仅为修措辞单独变更 Contract blob。
- S1-B3 与 S1-B8=`NOT_RUN`，S1-B6=`NOT_RUN`，S1-B5 仅验证旧引用不因 Core 重启重绑、密钥生命周期仍未验证；该集成没有宣称产品级安全或打包就绪。

## 状态

`doc/tasks/M2-RC1.md` 已标记 `done`，`integration_commit=3a24684007fd5a5e855f324077ad996841300f27`。M2-RC1 当前无遗留阻断项；后继唯一治理提案为 M2-RC2，待 Codex 单独释放后才可实施。