---
task_id: M2-FIX-DIGEST-SEEK-2GIB
author: ZCode（orchestrator 派发实现 Owner）
recipient: DeepSeek Harness（非作者 Reviewer，r2 复审）；Codex（集成）
base_commit: d1a4b4067a2222732867d16fc42ee0b6e4bfa228
delivery_head: r3 实现 head = `git log --grep "address DSH r2 C4"`（本 Handoff 与代码同一 fix commit，parent `d459d7bb`；自引用 hash 由集成方在集成 commit 回填。前序：r1 实现 `9fa92475`、r2 返修 `d459d7bb`）
status: in_review
---

# Handoff：M2-FIX-DIGEST-SEEK-2GIB — read_through 64 位 seek 修复

## 交付结果

分支 `agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`、worktree
`G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`。
base `d1a4b406`（release commit，parent `915cea99`）。

`resource_protocol.rs` 的 `read_through` 弃用 32 位
`SetFilePointer(offset as i32, high=NULL)`（u64 截断 + 高位恒空），改用
`SetFilePointerEx`（单个 64 位 LARGE_INTEGER，FFI 以 `i64` 内联，无新依赖）；
seek 返回位置与请求 offset 校验一致，且 seek 前对
`offset > MAX_RESOURCE_BYTES` 增加 typed fail-closed 防御。256 MiB 规则线内
行为逐字节不变（issue 校验、digest 逻辑、wire 契约未动）。

**r1 复审轨迹（2026-09-30）**：DSH r1 `approved_with_conditions`
（报告 `G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/t1-dsh-review-r1.md`，
评审对象 `ea07b4b1`）。r2 返修在同一允许路径内关闭：

- **C1（P2-1）**：新增 `large_offset_high_bits_reach_the_64_bit_seek` ——
  直接对 fixture 句柄调 `win32::SetFilePointerEx(handle, 0x1_0000_0000i64,
  &mut landed, FILE_BEGIN)`，断言 `ok != 0` 且 `landed == 0x1_0000_0000`
  （Windows 允许 seek 越过 EOF）。这是 AC1「≥2^31 位宽」子句的首个判别性
  artefact（guard 之上的 rejection 测试判别的是 guard 本身，r1 已如实记入
  Task）。
- **C2（P2-2）**：新增 `read_through_invalid_handle_fails_closed_with_open_failed`
  —— 无效句柄 `null_mut()` 调 `read_through(handle, 0, 4)`，断言错误串以
  `OPEN_FAILED` 开头，seek 失败分支首次被测试触发。
- **P3-5**：seek 失败错误串拼入 `win32::last_error()` 原始码（参照
  `open_once` 风格）；`typed_error` 冒号截断保持 wire code 仍为
  `OPEN_FAILED`（→400，与既有 ReadFile 失败路径一致）。
- **P3-1/P3-2/P3-6/P3-7**：Task frontmatter base_commit 锚定 `d1a4b406`；
  f02/f05 空引用改为实际测试名；passed 计数改为「含新增 N」表述；
  `read_through_at_limit_offset_yields_empty_tail` 注明「== MAX 为界内且
  生产调用链不可达」。
- **C3（P2-3，集成前证据顺带补齐）**：`raw/r2-scope-audit.log` 记录
  `git diff --name-status d1a4b406..ea07b4b1`，范围审计覆盖到 r1 交付链
  最终 tip。

r1 历史内容（AC 对照、提交列表）保留如下；r2 后的完整五列证据见下节。

### 提交列表

| commit | 说明 |
|---|---|
| `298aa24b` | chore(M2-FIX-DIGEST-SEEK-2GIB): claim (base d1a4b406) |
| `9fa92475` | fix(M2-FIX-DIGEST-SEEK-2GIB): 64-bit seek via SetFilePointerEx + fail-closed offset guard（r1 实现 head） |
| `b4baf7c2` | task(...): delivery — AC1-AC5 PASS, red/green evidence, handoff 9fa92475（r1 交付） |
| `ea07b4b1` | docs(...): add s2 delivery range audit log (AC5 evidence)（r1 证据补交） |
| `d459d7bb` | fix(...): address DSH r1 conditions C1/C2 + P3 doc fixes（r2 返修，DSH r2 评审对象） |
| r3 返修 commit | fix(M2-FIX-DIGEST-SEEK-2GIB): address DSH r2 C4 (P3-10 assert strengthening)（= delivery_head，parent `d459d7bb`） |

## r2 复审轨迹（2026-09-30）

DSH r2 `approved_with_conditions`（报告
`G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/t1-dsh-review-r2.md`，评审
对象 `d459d7bb`）：r1 各条件全部判 closed，无新增 P0/P1/P2，代码层判「严格
改进」。唯一 Owner 动作 C4（=P3-10）已在 r3 返修关闭：

- `read_through_invalid_handle_fails_closed_with_open_failed` 断言从仅
  `starts_with("OPEN_FAILED")` 强化为同时校验 `landed_at=` 与
  `last_error=`（seek 分支专属标记，保留原前缀断言）。判别理由：若删掉
  seek 失败检查，裸 null 句柄会在 ReadFile 以同码 `OPEN_FAILED` 失败、原
  用例仍绿——`landed_at=`/`last_error=` 只可能出自 seek 分支，删除即红。
  P3-5 的 `last_error` 后缀由此由测试输出支撑（r2 日志未 `--nocapture`
  的证据缺口同步关闭）。
- Task AC2 括注补 `last_error=<n>` 并区分「seek 分支执行覆盖」与「判别性
  artefact」口径（P3-12）。
- 复跑 `cargo test`：44 passed / 1 ignored，EXIT=0
  （`raw/r3-cargo-test-full.log`）。
- 集成侧待办（不在 Owner 允许路径，r2 报告 §3 P3-11/13/14）：`ea07b4b1..`
  范围审计、r1/r2 报告归档 `doc/reviews/`、`REBASELINE_PLAN`/`STATUS`/
  `tasks/README` 的 base 与状态修正、`delivery_head` hash 回填。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC3 大 offset fail-closed（r0 红绿） | `cargo test read_through_ -- --nocapture`（先在修复前代码跑红，再转绿） | worktree cargo 1.98.1 / rustc 1.98.1，win32；被测 commit `298aa24b`（红）/工作树（绿） | PASS（红 2 failed EXIT=101：2^32 实测 `Ok([48,49,50,51])` 误读文件头、MAX+1 实测 `Ok([])`；绿后 4/4） | `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/r1-red-large-offset.log`、`raw/g1-cargo-test-full.log` |
| AC1 64 位位宽判别（r2，C1=P2-1） | `cargo test`（用例直接驱动 `SetFilePointerEx` 至 0x1_0000_0000 断言落点） | 同上；被测 commit = r2 返修 head | PASS：`large_offset_high_bits_reach_the_64_bit_seek` ok（r1 时该子句按 Q-009 记 NOT_RUN，r2 关闭） | `raw/r2-cargo-test-full.log` |
| AC2 seek 失败分支（r2，C2=P2-2；r3 强化，C4=P3-10） | `cargo test`（无效句柄 `read_through(null_mut(), 0, 4)`：前缀断言 + `landed_at=`/`last_error=` seek 分支专属标记断言） | 同上；r2 被测 `d459d7bb`、r3 被测 = r3 返修 head | PASS：`read_through_invalid_handle_fails_closed_with_open_failed` ok（r2 执行覆盖；r3 起具判别力——删除 seek 失败检查后用例必红）；`last_error=` 后缀由测试断言支撑（P3-5/P3-10） | `raw/r2-cargo-test-full.log`、`raw/r3-cargo-test-full.log` |
| AC3 回归（全套） | `cargo test` | 同上；r1 时点被测 `9fa92475` 工作树、r2 时点被测 r2 返修 head | PASS：r1 42 passed / 0 failed / 1 ignored EXIT=0；r2 复跑 44 passed（含新增 6）/ 1 ignored（`perf_chunk_request_digest_cost` 基线既有；基线 39+1）EXIT=0 | `raw/g1-cargo-test-full.log`、`raw/r2-cargo-test-full.log` |
| AC4 clippy 无新增 | `cargo clippy --bin m2rc1-desktop -- -D warnings`；基线经 `git stash` 回退 resource_protocol.rs 复测 | 同上；被测：修复后工作树（c1）vs claim `298aa24b`（c0） | PASS：6 error 集合与位置完全一致（DSH r1 逐条独立比对确认），无新增；均 EXIT=101（基线本不干净，如实记录） | `raw/c0-clippy-baseline.log`、`raw/c1-clippy-deny-warnings.log` |
| AC5 范围纪律 | `git diff --name-status <range>` + `git diff --check` | worktree git；r1 覆盖 `d1a4b406..9fa92475`，r2 补审 `d1a4b406..ea07b4b1`（关闭 P2-3 交付链缺口） | PASS：仅 `resource_protocol.rs`、Task、Handoff、`verification/**`；`diff --check` EXIT=0；gen/、permissions/、Cargo.lock 无改动 | `raw/s1-scope-audit.log`、`raw/s2-delivery-range-audit.log`、`raw/r2-scope-audit.log` |

未运行项：产品级端到端套件（`tests/m2_acceptance`、vitest）未复跑 —— AC4
只要求 `cargo test`，Rust 层 `real_core_sidecar_round_trip` 等已覆盖服务
路径（DSH r1 同口径，不判缺失）。clippy 余留 6 error 见「风险与遗留」。

## 接收方式

- 分支 `agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`，worktree
  `G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`（HEAD = r2
  返修 commit）。
- 复现：`cd apps/desktop/src-tauri && cargo test`；单测过滤
  `cargo test read_through_ large_offset_high_bits`。
- 前置条件（gitignored，不入库）：worktree 需
  `apps/desktop/src-tauri/target/core-sidecar/`（tauri-build resources
  校验）与 `apps/desktop/frontend/dist`（`generate_context!` 宏要求），
  可从主工作区复制；缺失时 build.rs / proc-macro 失败，属环境前置而非代码
  问题。
- 数据路径：单测全部自建 tempfile fixture，无外部数据。
- 已批准依赖变化：无（`i64` 内联，Cargo.toml/lock 零改动）。
- 接收者具体检查：核对 `raw/r3-cargo-test-full.log` 计数 44/1 与
  `raw/r2-scope-audit.log` 的 name-status 集合；确认 C4 强化断言
  （`landed_at=`/`last_error=`）具判别力（模拟删除 seek 失败检查应致该
  用例红）。

## 下一任务建议（必填）

由集成方在集成 commit 补齐（§5.1 下一任务建议义务随 `done` 落字）：届时由
Codex（代行）补 `d1a4b406..<集成tip>` 的 name-status 与 `--check` 证据、
回填 `integration_commit`、按需更新 `doc/STATUS.md` / `doc/REBASELINE_PLAN.md`
（两份不在本 Task 允许路径内）。当前直接下一步：Codex 派发 DeepSeek Harness
r2 复审（对象 = r2 返修 head，条件闭合清单见上文 r1 复审轨迹）。

## 风险与遗留

- 无功能遗留。2 GiB+ 资源仍由 issue 路径 256 MiB 上游拒绝（Task 预期）；
  `read_through` 内部防御在生产调用链不可达（`served < size ≤ MAX`），
  `read_through_at_limit_offset_yields_empty_tail` 钉住的是边界内不变行为
  而非防御缺口（P3-7 已注明）。
- clippy 6 个**基线既有** error（`main.rs:40` unused import、
  `core_bridge.rs` MockCoreChannel/MockEntry dead-code、
  `library_bridge.rs:306`、`resource_protocol.rs:136`
  `double_ended_iterator_last`）不在本 Task 范围，建议另立清理 Task。
- P3-4（s1/s2 日志无 `# EXIT=` 尾行的历史格式不统一）由集成方处理；r2 起
  新日志统一 `# shell:` 头 + `# EXIT=` 尾。
- P3-8（release 记录 `verification/<Task>/release-<hash>.md`）属编排/集成
  侧产物，待集成 commit 补/声明。
- seek 失败码 `OPEN_FAILED` → 400 的语义取舍（IO 类失败映射 5xx）为后续
  可选项，r1 P3-5 仅要求 last_error 可观测，未改映射。
