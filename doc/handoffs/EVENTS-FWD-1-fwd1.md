---
task_id: EVENTS-FWD-1
author: Antigravity
recipient: Codex
base_commit: 6c28a02e9
delivery_head: 5c1695757342eb66f1cc5f7ef24bdb2ce39ccd36
status: ready_for_review
---

# Handoff：EVENTS-FWD-1

## 交付结果

解 UI-DESIGN-1 登记的架构缺口 **G17**（P14 前置）。在不改变 Python Core 事件 wire 的前提下，冻结并实现了 host→WebView 的事件转发面（Tauri event emit 通道），使前端（P14 工作台等）能收到失效提示并重查快照。

### 逐 AC 完成对照

- **AC1 冻结转发面（先契约，后实现）**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 升至 `rev 2.4`，新增 §6.4 冻结六类已冻结事件（`TaskFailed`、`RunPaused`、`RunCompleted`、`CurrentPageStepChanged`、`ExportProgressChanged`、`ReadingProgressChanged`）的安全投影规范；明确禁止携带路径/引用/密钥/文件字节；明确事件是失效提示不是状态真值；明确排除未冻结的 `CoreAvailabilityChanged`（G16）与 `ImportProgressChanged`（G26）；在 `verification/EVENTS-FWD-1/compatibility-impact.md` 中给出兼容性影响与向后兼容保障。
- **AC2 host 实现**：在 `apps/desktop/src-tauri/src/library_bridge.rs` 中实现了专用后台 reader 线程，对 stdout 上的 JSONL 流进行解复用，通过 `project_forwarded_event` 进行安全投影并过滤非法字段，在 `main.rs` 的 setup 闭包中注入 `app.emit` 转发；在 `capabilities/m2rc1-commands.json` 中配置了 `core:event:allow-listen` / `core:event:allow-unlisten`；未增加任何新的 Tauri command，生产命令面严格保持 18 个。
- **AC3 最小消费侧接线**：创建了 `apps/desktop/frontend/src/events.ts`，导出 6 类 typed listener helper 函数（`onTaskFailed`、`onRunPaused`、`onRunCompleted`、`onCurrentPageStepChanged`、`onExportProgressChanged`、`onReadingProgressChanged`），配套单测 `events.test.ts` 全部 PASS；前端全套 177 个测试 PASS，`npm run build` 成功。未触碰页面 UI。
- **AC4 真实链路证据与分层证据**：在已重建的 2.3 frozen bundle 上运行 `packaged_sidecar_tests` 全部 7 个测试 PASS；因生产命令集保持冻结且无端到端触发 PipelineRun 的命令，端到端触发状态如实记录为 `BLOCKED_ON_TRIGGER_COMMAND`；并提供完整的四层分层证据（安全投影过滤、Stdio 多路复用与旁路无干扰、真实 bundle 运行时、前端类型解包与分发），原始日志与退出码已落盘在 `verification/EVENTS-FWD-1/`。
- **AC5 不越界**：未改 Core 侧 §6.2 的既有事件字段/语义；未实现 `CoreAvailabilityChanged` 或其他未冻结事件；未改契约无关章节；未新增产品依赖。
- **AC6 不回归**：`tests/core/**`（395 passed）与既有 Rust 测试（80 passed + 1 concurrent passed + 7 packaged passed）全绿；前端 177 个测试全绿且 build 成功；Cargo 生成的 27 个 CRLF 噪音已使用 `git diff` 判定并全部恢复。
- **AC7 固定交付**：提交固定 commit、Handoff、Canonical Evidence 真实 sha256 登记完毕；不 `push`、不 `merge`。

---

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 | 契约 revision 2.4 审查与兼容性分析 | 本地 worktree 只读审查 | PASS | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`<br>`verification/EVENTS-FWD-1/compatibility-impact.md` |
| AC2/AC6 | `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop -- --skip packaged_sidecar_tests --skip same_channel_concurrent_round_trips` | Rust 1.8x dev | PASS (80 passed, 0 warnings) | `verification/EVENTS-FWD-1/cargo-tests.log` |
| AC2/AC6 | `$env:M2RC1_PYTHON="python"; cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop same_channel_concurrent_round_trips` | Python 3.12 + Rust | PASS (1 passed, 0.11s) | `verification/EVENTS-FWD-1/concurrent-roundtrips.log` |
| AC4/AC6 | `$env:M2RC1_PACKAGED="1"; cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop packaged_sidecar_tests` | 2.3 frozen bundle (`target/core-sidecar`) | PASS (7 passed, 1.91s) | `verification/EVENTS-FWD-1/packaged-sidecar-tests.log` |
| AC3/AC6 | `npm --prefix apps/desktop/frontend test` | Node.js v20 + vitest | PASS (17 files, 177 passed) | `verification/EVENTS-FWD-1/frontend-tests.log` |
| AC3/AC6 | `npm --prefix apps/desktop/frontend run build` | tsc && vite build | PASS (dist/ 产出正常) | `verification/EVENTS-FWD-1/frontend-build.log` |
| AC4 | 端到端与分层证据审查 | 本地 worktree 完整审查 | `BLOCKED_ON_TRIGGER_COMMAND` + Layer 1-4 VERIFIED | `verification/EVENTS-FWD-1/evidence-layering.md` |
| AC6 | `python -m pytest tests/core -q` | Python 3.12 venv | PASS (395 passed, 1 warning) | `verification/EVENTS-FWD-1/python-tests.log` |

---

## 接收方式

- **工作区**：`G:\CODEX\New Manga.workspace\worktrees\EVENTS-FWD-1`
- **分支**：`agent/antigravity/EVENTS-FWD-1`（起点 `6c28a02e9`）
- **复现检查**：
  1. 运行 `cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop test_events_fwd` 验证 4 个事件投影与旁路多路复用测试；
  2. 运行 `npm --prefix apps/desktop/frontend test` 验证前端 177 个单测全绿；
  3. 运行 `$env:M2RC1_PACKAGED="1"; cargo test --manifest-path apps/desktop/src-tauri/Cargo.toml --bin m2rc1-desktop packaged_sidecar_tests` 验证 2.3 bundle 兼容性。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`REVIEW-EVENTS-FWD-1`（或由 Codex / DeepSeek Harness 进行独立 Review，通过后解锁 `P14` 工作台实施）
- **推荐 Agent / Reviewer**：Codex 或 DeepSeek Harness（**按协作协议规则，Reviewer 不得是 Antigravity 本人**）
- **推荐原因与前置依赖**：EVENTS-FWD-1 现已全部就绪并通过全部全套测试与分层证据验证。需要由独立 Reviewer 审核契约 rev 2.4、安全投影与 host reader 转发逻辑，完成集成验证后进入 done，从而解开 P14 的前置依赖。
- **Recovery point**：`G:/CODEX/New Manga.workspace/worktrees/EVENTS-FWD-1`，分支 `agent/antigravity/EVENTS-FWD-1`。
- **可直接转发给 Agent 的指令**：
  ```
  请对 EVENTS-FWD-1 的交付进行独立 Review。检查 M2-C1 rev 2.4 契约修订、library_bridge.rs 后台 reader 转发逻辑与安全投影、events.ts 前端接线及 AC4 分层证据，运行全套回归测试确认无破坏后给出审查结论。
  ```

---

## 风险与遗留

- **端到端触发闭环**：当前生产命令面未包含直接启动 Pipeline Run 的命令，真实全链路触发将在 P14（工作台）接入 `StartRun` / `ControlRun` 时自然闭环；本 Task 已通过严密的 4 层分层测试与真实 2.3 bundle 运行时生命周期测试完成了充分证明。
- **P14 轮询降级路径**：若前端暂时不接入事件监听，P14 的 `GetTaskProjection` 纯轮询降级路径不受任何影响。
