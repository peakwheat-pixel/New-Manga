# M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF 非作者 Review（DeepSeek Harness，只读静态）

**decision: approved_with_conditions**

方法与边界：全程未执行命令、未写任何文件。为取得 base 对照，除本 worktree 外还**只读**了主仓库工作树（`G:\CODEX\New Manga\...`）；主仓库 `.git/logs/HEAD:617-618` 证明其 tip=`6c3d7b34`＝`956e6c3a` + 纯文档 release commit，且其 `resource_protocol.rs` 仍是三读 + `CachedGrant` 版，故主仓库 Rust 文件即 base 内容，可做逐字对照。交付链经 worktree reflog 独立确认：`6c3d7b34 → b43a1e2a(claim) → 9df29a6f(探针) → 5d7cff11(实现) → 64e6c9a7(handoff/evidence/checkpoint/Task 回填) → 510202ac(v7 日志)`（`G:\CODEX\New Manga\.git\worktrees\M2-FIX-DIGEST-PERF-zcode\logs\HEAD:3-8`），与 handoff/交付 tip 一致。

## A–H 判定表

| 项 | 判定 | 证据（path:line） | 说明 |
|---|---|---|---|
| **A** AC1 硬约束 | **verified** | 交付 `apps/desktop/src-tauri/src/main.rs:826-830`、`:848-867`；base 对照 `G:\CODEX\New Manga\apps\desktop\src-tauri\src\main.rs:821-825`、`:857-862`；行为 `resource_protocol.rs:464-466` + `:107`（默认 400）；绿证 `verification/.../raw/v1-cargo-full.log:46,55,61`、`raw/v2-cargo-loop.log:25-29`；红证 `verification/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY/integration-3cef4831/raw/g5-loop-discrimination-red.log:26,32-36,45` | 两处断言与 base **逐字一致**（仅删去 `&env.cache` 实参）；仍是 `400` + `{"code":"CONTENT_DIGEST_MISMATCH"}`。红证存在、EXIT=101、`left:200 right:400`，其 "origin=6a404c19 修复前文件" 正是"digest 重验被弱化即被 loop 抓住"的判别力证明，与本 Task 语义直接相关。补充：`raw/b1-baseline-loop.log:37-41` 证明紧邻的优化前提交本身为绿，故"父提交先红"逻辑上不成立，引用 F02 artefact 是 AC1 明文允许的做法 |
| **B** 单趟 hash+capture 正确性 | **verified** | `resource_protocol.rs:371-404`（循环/捕获）、`:380-399`（交集与边界）、`:400-402`（`served != expected_size → FILE_SIZE_CHANGED`）、`:461-463`（`want=min(size-offset,CHUNK_SIZE)`）、`:513-520`（`checked_mul` + `offset < size` 守卫）、`:349-357`（读满或到 EOF）、`:464-466` + `:111-118` + `:107`（错误路径）、`:522-525`（仅 Ok 返回 200） | ① digest 覆盖区间恒为 `[0,expected_size)`，`captured` 是同一趟读取的 `[chunk_offset, chunk_offset+chunk_len)` 子区间，`chunk_end ≤ expected_size` ⇒ **served bytes ≡ digest-covered bytes 成立**；② 块切分按 `min(剩余,CHUNK_SIZE)` 推进，`block_start=served` 自洽，**短读也不会错位**（交集用实际 block 边界），越界可证不成立（`into+len ≤ chunk_len`、`to ≤ block.len()`）；③ 末 chunk 截断正确，`offset ≥ size` 在 `:518` 前拒；④ digest 不匹配/尺寸变化一律 typed 400，无部分内容；⑤ 相对 base（`:434`/`:440-441`/`:449`）还**顺带修掉**"digest 后重读可能返回短 body"的旧路径（现为 `FILE_SIZE_CHANGED`），是严格改进 |
| **C** F-01 语义 | **verified** | `resource_protocol.rs:508-511`（每请求无条件 resolve，先于任何文件操作）、`:437-438`（volume/index）、`:440-442`（size）、`:464-466`（sha256）；`:436`/`:447-460` | 四条 identity 判据齐全；全仓无 `needs_digest`/`verified_mtime`/mtime 门控残留（`_mtime` 仅解构丢弃）；Core 拒绝→typed error 早退，无缓存旁路 |
| **D** AC4 收敛与更名 | **verified** | `resource_protocol.rs:65-71`（考古注释）、`:10`、`:504`；`main.rs:27`、`:89-97`、`:317-323`、`:345-346`（消费方删除）、`:423-430`、`:447-459`；更名 `main.rs:714-721`、断言 `:735-736`；grep 全仓 `CachedGrant|GrantCache|GRANT_CACHE_MAX_ENTRIES` 仅命中注释与历史证据 | `HashMap`/`Mutex` import 亦随删（base `:33/:35` 有，交付 `:34-37` 无）；无死 map 操作。测试名与语义一致：新 inode 替换 → 每请求 identity 比对拒绝，doc-comment 已写明更名缘由 |
| **E** 触点 5 TestEnv 守卫 | **verified** | `main.rs:423-430`（`_dir: tempfile::TempDir`）、`:447-459`（构造，无 `mem::forget`）、loop `:841-869` | 全仓 `mem::forget` 仅剩注释；每次 `env_with_fixture` 独立 `tempfile::tempdir()`，50 轮每轮 `env` 于轮末 drop ⇒ 隔离与清理等价替代（drop 忽略删除失败，不会 panic）；所有调用点均绑定 `env`，无"立即 drop"误用 |
| **F** 范围 | **verified（带范围注记）** | `raw/v5-diff-check-namestatus.log:9-18`（`956e6c3a..5d7cff11` 仅 `main.rs`、`resource_protocol.rs`、5 份治理文档、release evidence；**无 `src/**`、contracts、tests/core**）；条件路径未启用证据：`core_bridge.rs:18-35` 无 chunk 字段、`src/application/resource_channel/dto.py` 与主仓库逐行一致（各 110 行）、`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 无 per-chunk 命中（`:263` 反而明示不选 chunk transport）、`tests/core` 无命中 | 注记：`main.rs:27/:89-97/:317-323/:345-346` 属**生产接线**（AppState 字段与 uri-scheme 调用点），严格字面超出"main.rs 资源通道测试段"限定；但它是触点 3（必做）删除死缓存的**必然消费方删除**，语义惰性（缓存本就无读取方），无行为变化（另删去的是原来跨 `verify_and_serve` 持锁的全局 Mutex，属并发改善）。建议 Integrator 落字确认（C4）。交付 commit `64e6c9a7/510202ac` 的增量按 glob 可枚举，全在允许路径 |
| **G** 证据纪律 | **partially_verified** | 头/尾齐全：`v1:1-5,63`、`v2:1-5,29`、`v3:1-6`、`v4:1-6,9`、`v5:1-7,18`、`v6a:1-10,38`、`v6b:1-6,33`、`v6c:1-7,45-49`、`b1:1-6,41`、`b2:1-6,44`、`b3:1-6,34`；perf 口径自洽（探针 `main.rs:877-913`：warm 1 次 + N 次计时，1MiB×20/16MiB×10/32MiB×5，`#[ignore]`；b2/v6b 同 profile，v6c 以 checkout 9df29a6f 两文件保持自洽并 restore+porcelain，`:46-49`）；`v5` 覆盖实现 commit 与 release 文档 commit，`v7:1` 覆盖交付 commit `64e6c9a7` | 扣分项：① `verification-results.md:44-48` 称 6→5 warning 集合对照"证据见 raw/v3 头注"，但 `raw/v3:1-6` **只有命令与 grep exit，无任何 warning 清单**（该对照在 raw/ 内无原件；AC4 实质仍由 `v6c:9-31`/`b1:8-30`/`b2:8-30`（基线 3 warnings 含 `field 'grant' is never read`）对 `v1:6-18`/`v6a:12-24`/`v6b:7-19`（2 warnings）独立支撑）；② `v7` 未登记进 `verification-results.md` §1 或 Handoff §4，其格式缺命令回显与尾部 EXIT 行（仅头部 `# EXIT=0`），且终 tip `510202ac` 自身（唯一增量是 v7 日志）未被任何 diff-check 覆盖；③ `b3` 仅在 §3 脚注提及，未入 §1 表 |
| **H** per-chunk 不实施裁决 | **verified** | `src/infrastructure/resource_channel/host_bridge.py:103-116`（`resolve` 分支手写字段枚举 `"sha256": grant.facts.sha256` 等）；Handoff §5、Task 状态段、`:11` 声明；契约 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:263,277` | 事实核对成立：grant→wire 是**手写字段枚举**，per-chunk 摘要不在此处显式加字段就永远到不了 Rust；而 `host_bridge.py` 位于 `src/infrastructure/**`，属 Task 明文的"禁止：其余 src/**"，条件允许路径（dto/service/core_bridge/契约/tests/core）**不含**它 ⇒ 实施必然越权。AC2 冻结文本允许"单趟路线"，且半实施会复刻"写入即弃死字段"，不实施理由充分、已书面留痕 |

## 新问题分级

**P0 / P1 / P2：none。** 未发现错误路径回归、usize 溢出、大文件 offset 计算错误或探针对既有测试的干扰（探针 `#[ignore]`，`:877-879`，不进默认套件；v1 显示 35 tests = 34 passed + 1 ignored，与基线计数一致）。

- **P3-1（证据引用不实，AC4 论证链）**：`verification-results.md:48`/`:44-47` 把"基线 6 warnings / 优化后 5 warnings 逐条 diff"归因于 `raw/v3` 头注，而 `raw/v3:1-6` 无该内容；该对照在 raw/ 无原始日志。AC4 结论本身不受影响（v6c/b1/b2 对 v1/v6a/v6b 已直接证明 `field 'grant' is never read` 消失且无新增）。建议改引上述 6 份日志，或补一份 `cargo build` 基线/后 warning 全量日志。
- **P3-2（终 tip 未绑定 diff-check）**：`raw/v7-post-delivery-diffcheck.log:1,5` 绑定 `64e6c9a7`（交付 commit），而终 tip `510202ac` 只追加 v7 日志本身（reflog `:8`），该 tip 未复跑；`v7` 也缺命令回显与尾部 EXIT 行，且 `:8` 自曝一个 untracked 文件（自洽披露，非隐瞒）。`v7` 亦未进入 evidence 汇总/HANDOFF 台账。
- **P3-3（范围解释需落字）**：`main.rs:27/:89-97/:317-323/:345-346` 生产接线改动超出"资源通道测试段"字面，属触点 3 的必然结果，需 Integrator 显式确认，避免集成时被误判为越权。
- **P3-4（文档状态机不同步）**：Task frontmatter `doc/tasks/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF.md:5` 仍是 `status: in_progress`，而正文末行写 `ready → in_review`、`:20` `dispatch_state: DELIVERED_FOR_REVIEW`；协议 `doc/09_COLLABORATION.md:65,71` 规定交付 head 固定 + 测试/Handoff 齐全即 `in_review`。建议随集成回填修正。
- **P3-5（既有潜在隐患，非本交付引入）**：`resource_protocol.rs:331-333` `SetFilePointer(offset as i32, null, FILE_BEGIN)` 高位恒空且返回值未检查；当前 `MAX_RESOURCE_BYTES=256 MiB`（`:41`、`:443-445` 先于读取）使其不可达，单趟改造也未新增暴露面（`served ≤ size`）。若未来 T1 线超过 2 GiB，此处会先于任何断言静默失效，建议登记为候选。
- **可选 nit（无需处理）**：`main.rs:811` 断言消息仍写 "first fetch verifies and caches"、`:740-741` 注释仍提 pre-fix cache；为满足"断言一字未放宽"，保留原样是对的，仅提示语义措辞已陈旧。另 `main.rs:419` 的 `unused import: CHUNK_SIZE` 是**基线既有**（`verification/M2-RC2/raw/claim-baseline-cargo.log:12` 等 40 处同源），非本交付新增，`cargo build` 的 `never read` 判据（`raw/v3`）不受影响。

## 是否达到可集成标准

**是。** 代码面 0×P0/P1/P2，A/B/C/D/E/H 独立复核通过，F 仅需范围落字，G 的两处为证据台账问题；**不要求任何代码修订**。集成前需闭合以下 4 项（全部为文档/证据/范围确认，可由 Owner 修订或 Integrator 在集成记录内落字，参照 F02 集成 C1/C2 先例）：

- **C1**：更正 `verification-results.md` §4 对 `raw/v3` 头注的引用，或补一份 `cargo build` 基线/优化后 warning 全量对照原始日志（P3-1）。
- **C2**：把 `raw/v7-post-delivery-diffcheck.log` 登记进 `verification-results.md` §1 与 Handoff §4，并对终 tip `510202ac` 复跑一次 `git diff --check` + `--name-status`（或书面声明该 tip 唯一增量是 v7 日志本身），使交付 tip 有绑定证据（P3-2）。
- **C3**：Integrator 在集成记录显式确认 `main.rs:27/:89-97/:317-323/:345-346` 属触点 3 死缓存消费方的必然删除、非越权（P3-3）。
- **C4**：Task frontmatter `status` 与 `review` 回填（`in_progress → in_review`，review 链指向本报告），与协议状态机一致（P3-4）。

建议 Review 锚点复测（Owner 自报数字静态采信、集成时复跑）：`cargo test --bin m2rc1-desktop`（34 passed 1 ignored）、`f02_equal_size_rewrite_stability_loop`（50 轮）、`m2_acceptance`（35 passed 0 xfailed）、`cargo build | grep "never read"`（空）、`git diff --check`。

## 推荐下一步

由 Integrator（Codex，另一子 agent 代行，保持 Owner≠Integrator）在本 Task 上闭合 C1–C4 并做集成 merge；Owner 无需返工。可直接转发给 Integrator 的指令：

> 请以 Integrator 身份集成 M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF：Owner=ZCode，delivery_head=`5d7cff11`、交付 tip=`510202ac`、branch `agent/zcode/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF`、base=`956e6c3a`。先读 DSH 非作者 Review（approved_with_conditions，0×P0/P1/P2），逐条闭合 C1（更正 verification-results §4 对 raw/v3 头注的引用或补 cargo build warning 对照日志）、C2（登记 raw/v7 并对终 tip `510202ac` 复跑 `git diff --check` + `--name-status`）、C3（落字确认 main.rs:27/89-97/317-323/345-346 生产接线属触点 3 必然删除，非越权）、C4（Task frontmatter status → in_review 并回填 review 链）。随后按惯例在集成 tip 绑定复跑 cargo 全量 + f02 loop 50 轮 + `m2_acceptance` + `git diff --check`，写 integration 记录与 STATUS/REBASELINE_PLAN 同步，merge 后回填 `integration_merge` 并把 Task 置 done。

无需下一步操作之外的建议。