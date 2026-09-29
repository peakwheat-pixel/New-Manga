# M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF Integration Record — 510202ac → merge bc2529f0

- Integrator: Codex（编排会话代行，用户 2026-09-28/29 全权授权；Owner=ZCode 子 agent，Owner≠Integrator 保持）
- Integration merge: `bc2529f02dfbd3c378d5e9cd4c9f7ac2ecfe4f15`（parents `1ca5328c`（DSH 报告 import）+ `510202acdfbf085250c7ee09bb7b6421b9d70f03`（Owner 终 tip）；--no-ff 无冲突）
- Reviewer: DeepSeek Harness（非作者，真实 DSH headless CLI，session `session-2852f301-c9e8-49cc-b6a3-97498fc08250`，cwd=Owner worktree，EXIT=0）r1 = `approved_with_conditions`，**0×P0/P1/P2**（[报告](../../../doc/reviews/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11-dsh-r1.md)，SHA256 `7ea74e7a44a5a539b22699ee3786b6f1ae2792ed156660e7bed36ec2b308cbba` 原字节 import；派发任务/JSONL/err 存档 [review-dsh-import](../review-dsh-import/)）
- 交付链: release `6c3d7b34` → claim `b43a1e2a` → perf 探针 `9df29a6f` → 实现 delivery `5d7cff11` → 交付回填 `64e6c9a7` → 终 tip `510202ac`；base=`956e6c3a`
- 日期: 2026-09-29

## 1. 交付内容（Owner 自述经 DSH A-H 独立复核）

- **单趟 hash+capture**：`resource_protocol.rs:371-404` `stream_digest_and_capture` 逐块 digest + 区间交集捕获，替换三读路径（`:434/:440-441/:449`）；`served bytes ≡ digest-covered bytes`（DSH B 判定 verified），短读 fail-closed（`served != expected_size → FILE_SIZE_CHANGED`），digest→serve TOCTOU 窗口结构性消除（AC3）。
- **GrantCache 死结构收敛**：`CachedGrant`/`GrantCache`/`GRANT_CACHE_MAX_ENTRIES` 及 map 副作用删净（DSH D verified，全仓仅注释/历史证据命中）；F-01 每请求 resolve 无条件先行语义不变（DSH C verified，identity 四判据齐全、无 mtime 门控残留）。
- **测试更名**：`identity_change_invalidates_cache_entry` → `identity_change_rejected_by_per_request_verification`（语义与名称一致）。
- **loop 卫生**：`mem::forget(dir)` → TestEnv 持有 `TempDir` 守卫，50 轮隔离与清理等价（DSH E verified）。
- **硬约束遵守**：f02 两断言与 base 逐字一致（DSH A verified，仅删 `&env.cache` 实参）；红证=F02 `g5-loop-discrimination-red.log`（EXIT=101，判别力 artefact）+ 本 head 复验绿。
- **性能**（统一探针，AC2）：release 1MiB −14.6% / 16MiB −24.4% / 32MiB −17.9%（v6c→v6a）；debug 噪声带内 ±1%（SHA256 主导）；顺带实测闭合 F02 P3-9（release 较 debug 低 ~20 倍，unverified→verified）。
- **per-chunk digest 不实施**（DSH H verified）：wire 序列化在 `host_bridge.py:103-116` 手写字段枚举，属禁止路径（`src/infrastructure/**` 不在条件允许级），实施必然越权；AC2 冻结文本明示单趟路线达标。条件允许路径未启用、Python/契约零改动。

## 2. DSH 条件闭合（集成方落字，按 F02 C1/C2 先例）

- **C1（P3-1 证据引用不实）→ 已闭**：`verification-results.md` §4 由集成方整段更正——原"6→5 warnings"数字（stash 会话、未留 raw）**作废**；改以 raw 可核验口径：基线 3 warnings（`b2:8/16/22`、`v6c:9/17/23`，含 `field 'grant' is never read`）→ 优化后 2 warnings（`v1:6/14`、`v6a:12/20`，无新增）。集成复跑 grep 集合独立证实（`raw/i1-i3` i3）。
- **C2（P3-2 终 tip 未绑定 diff-check）→ 已闭**：`v7` 已登记进 `verification-results.md` §7（格式缺陷如实保留）；终 tip `510202ac` 绑定 diff-check 由集成复跑 **i7**（`git diff --check 956e6c3a..510202ac` EXIT=0）覆盖；集成 head 复跑 i6（`956e6c3a..bc2529f0` EXIT=0）。
- **C3（P3-3 范围落字）→ 已闭（本段即确认）**：`main.rs:27/:89-97/:317-323/:345-346`（AppState 字段与 uri-scheme 调用点适配）**确认属触点 3（GrantCache 死结构删除，必做项）的必然消费方删除**，非越权——缓存本无读取方（F02 C2(b) 显式接受），删除为纯惰性结构清理；顺带移除跨 `verify_and_serve` 持锁的全局 Mutex 属并发改善。生产接线语义零变化（resolve 每请求照旧）。经 i8 范围复核与集成 head 全组测试绿证实无行为回归。
- **C4（P3-4 Task 状态机）→ 已闭**：Task frontmatter 随集成回填 `status: done` + review 链 + `integration_merge`（见 Task 文件）。

## 3. 集成复跑（tip 绑定，HEAD=`bc2529f0`，全部 EXIT 见 [raw 日志](../raw/)）

| 组 | 命令 | 结果 | EXIT |
|---|---|---|---|
| i1 | `cargo test --bin m2rc1-desktop` | **34 passed; 0 failed; 1 ignored** | 0 |
| i2 | `cargo test f02_equal_size_rewrite_stability_loop -- --nocapture` | **1 passed**（50 轮） | 0 |
| i3 | `cargo build \| grep "never read"` | 空输出 | 1（PASS 判据） |
| i4 | `TASK-012-py312 pytest tests/m2_acceptance -q` | **35 passed**（0 xfailed） | 0 |
| i5 | `npx vitest run`（apps/desktop/frontend） | 5 files / **31 tests passed** | 0 |
| i6 | `git diff --check 956e6c3a..bc2529f0` | 空 | 0 |
| i7 | `git diff --check 956e6c3a..510202ac`（Owner 终 tip 绑定） | 空 | 0 |

shell=Git Bash；interpreter=TASK-012-py312（Python 3.12.3）；日志：`raw/i1-i3-cargo-integration.log`、`raw/i4-i8-pytest-vitest-diffcheck-integration.log`（头含 shell/head/time，尾含逐条 EXIT）。

## 4. 遗留登记（不阻断 done）

- 触点 6 机理对照实验（可选）：未实施——mtime 已不参与判定，两机理同向失效（Owner 论证，DSH 无异议）。
- P3-5（DSH 新发现，既有隐患非本交付引入）：`resource_protocol.rs:331-333` `SetFilePointer(offset as i32)` 高位恒空且返回值未检查，当前 `MAX_RESOURCE_BYTES=256 MiB` 下不可达；若未来 T1 线超过 2 GiB 须先修——**登记为 planning 候选**（未释放禁止实施）。
- 可选 nit（无需处理）：`main.rs:811` 断言消息与 `:740-741` 注释措辞陈旧（保留原样以满足"断言一字未放宽"）；`main.rs:419` `unused import: CHUNK_SIZE` 为基线既有。
- Owner 分支/worktree 保留于终 tip `510202ac`。

## 5. 结论

DSH r1 `approved_with_conditions`（0×P0/P1/P2）四条件全部闭合（C1/C2 证据落字、C3 本记录落字、C4 状态回填）；集成 head 全组复跑绿；"等长重写必拒"语义与判别力保持（红证 artefact 引用 + 终 head 复验绿）；m2_acceptance 35 passed 基线不回退。**M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF 置 `done`。**
