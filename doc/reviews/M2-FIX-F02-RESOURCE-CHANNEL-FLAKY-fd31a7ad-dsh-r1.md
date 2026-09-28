# M2-FIX-F02-RESOURCE-CHANNEL-FLAKY 非作者静态 Review（DSH r1）

**approved_with_conditions**

- Reviewer：DeepSeek Harness（非作者）；Owner：ZCode；被审对象：base `2b81f91c` → delivery_head `fd31a7ad` → 回填 tip（声称 `3cef4831`），worktree `G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode`
- 审查方式：**纯静态**（本会话 pwsh 因沙箱 ACL grant 失败全程不可用：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，任意命令包括 `git --version` 均被拒）。因此"verified-by-reading"只覆盖文件内容（源码、Task/Handoff/results、16 份 raw 日志）；一切 Git 级事实（commit 内容、作者、范围）为 not_verified。
- 总结论：AC1 诊断证据链成立且**足以支撑"真实产品缺口"定性**；AC2 修复方向正确、语义未弱化、无残留 mtime 短路；AC3/AC4 日志数字自洽；范围纪律基本达标。扣留全绿的两个条件：①交付树残留**修复引入的 dead-code（`CachedGrant.grant` 从未被读取，整个 GrantCache 变成只写结构）**，且 Handoff 对该结构的描述与代码不符；②**没有任何日志绑定 delivery_head/tip**，Rust 侧全部证据跑在 claim commit 工作树上。二者都不改变安全语义判定，但需要集成方复核/收口。

---

## 一、六轴核查结论（verified-by-reading）

### 轴 1 诊断证据质量 —— 成立，机制归因有残留不确定性（P3）

- `raw/f02_diag_run1.log:54-61`、`run2:49-59`、`run3:50-57`：三份 dump 相互独立（file index 分别 `2251799817143236` / `1125899910300645` / `1688849863722048`，mtime 三个不同值），且都以 `mtime_equal=true mtime_delta_100ns=0` + `facts_before == facts_after` + `entry=(Some((true, Some(<同一 mtime>))))` + `second_status=200` 收尾。这**正面证明了**"重写未改变经 `GetFileInformationByHandle` 读回的 LastWriteTime，且产品短路放行了重写内容"，不是推理。
- 自证偏差排除：dump 的 `facts_*` 走的是产品同一 `identity_size_mtime`（`resource_protocol.rs:270-282`），触发路径是产品入口 `handle_m2res_request`（run2 中**原 f02 测试本身同时失败**：`raw/f02_diag_run2.log:49-54` 给出 `left:200 right:400` @`main.rs:821`），探针只是旁挂读取 entry，不改变被测路径。**同构性 OK。**
- "3/3 捕获"与原 flake 频率**相容**，但 Handoff 对它的解读不准确：捕获轮次为 0/2/5，说明单轮碰撞概率约 0.3–0.5（`p≈1/(mean round+1)`），50 轮不命中的概率约 `0.6^50≈1e-11`——这既解释了 LISTBOOKS "首跑红"，也解释了基线单跑绿（`raw/f02_baseline_run1.log:286,299`：33 passed、f02 ok，P(绿)≈0.5 量级）。**把"3/3 运行捕获"说成"失败概率极高"（`handoff:42`）是把 retry-loop 的 run 级必捕获率当成了单次失败率；结论方向不变，措辞应改。**

### 轴 2 修复语义完整性 —— 核心正确，落下一个死结构（P2）

- **无残留 mtime 短路**：`resource_protocol.rs:426-437` 每请求无条件 `stream_digest` 并与 `grant.sha256` 比对；全仓 grep `needs_digest|digest_verified|verified_mtime` 在 `src/` 内只剩注释性提及，`identity_size_mtime` 的 mtime 分支只被 `_mtime` 丢弃（`:415`）与测试辅助使用（`:551`）。**verified-by-reading ✓**
- **err 路径语义自洽**：`stream_digest`（`:367-383`）读失败→`OPEN_FAILED`，长度不足→`FILE_SIZE_CHANGED`；两者都落在 `typed_error`/`status_for` 的默认 400，且 `FILE_SIZE_CHANGED` 在驱逐清单内（`:517-523`）。行为与修复前同类错误一致，未见新暴露的错误码。**✓**
- **F-01 未受影响**：`channel.resolve` 仍在缓存之前无条件执行（`:483-489`），Core 拒绝即驱逐并 typed 传播；f01 两个测试在 5 份修复后日志中均绿。**✓**
- **P2 —— 修复把缓存变成了只写死结构**：`CachedGrant { grant: Grant }`（`:67-69`）+ `guard.insert(...)`（`:506-511`）写入的 `grant` 在全仓**从未被读取**，`GrantCache` 只剩 `len()/clear()/remove()`（`:486,501-502,525`）三种无观察效果的副作用。编译器在交付树状态下的 6 份日志里直接给出 `warning: field 'grant' is never read --> src\resource_protocol.rs:68:5`（`raw/f02_fix_round1.log:21-29`、`f02_fix_round2/3.log`、`f02_fix_directed_loop.log:20-28`、`f02_fix_singlethread.log`、`f02_final_tip_verify.log:20-28`、`f02_perf_postfix.log:19-27`；修复前 4 份基线/诊断日志**无**该警告）。因此：
  - Handoff `:16` 的"grant cache 退化为只 memoise Core resolve 结果（F-01 语义不变）"**不成立**——它没有 memoise 任何被消费的东西（每请求本来就无条件 resolve 并直接用 `fresh_grant`），属于**事实性描述错误**；
  - `handle_m2res_request` 每请求多出一次 `Mutex` 加锁 + `String` clone + `HashMap` 插入（`:500-511`），以及 `GRANT_CACHE_MAX_ENTRIES` 的 1024 条清理，全部是纯开销；
  - 候选处置（均在冻结允许路径 `resource_protocol.rs` 内）：**(a)** 删除 `CachedGrant/GrantCache` 及两处死驱逐，或 **(b)** 让缓存真正被消费（但 F-01 要求每请求 resolve，故 (b) 无意义）→ 推荐 (a)，但会使已录证据失效、需重跑。

### 轴 3 稳定性证明可信度 —— 数字自洽，provenance 未绑定（P2，见轴 5）

- 3 轮全量：`f02_fix_round1/2/3.log` ISO `03:10:53/03:10:56/03:10:57`，各自独立编译+运行，均 `34 passed; 0 failed` + `EXIT=0`。**三次运行时间戳与编译耗时（1.74s/0.35s/0.35s）与"三次独立调用"自洽。**
- 定向：`f02_fix_directed_loop.log:34-37` `f02_equal_size_rewrite_stability_loop ... ok`，`finished in 0.12s`（50 轮）→ **CI 超时风险可忽略**（每轮 ~2.4ms）；3 轮全量各含该 loop，`3×50=150` 场景的说法与日志一致。
- 单线程：`f02_fix_singlethread.log:70-72` `34 passed` + `EXIT=0`。
- **该 loop 是承重断言**（轴 6 合并）：它同时断言首请求 200 与二请求 400+`CONTENT_DIGEST_MISMATCH`（`main.rs:843-862`）；按轴 1 估算的单轮碰撞概率，对修复前代码 50 轮不红的概率 ≈1e-11，即"修复前必红、修复后必绿"，判别力足够。

### 轴 4 性能权衡 —— 数量如实，口径与外推需标注（P3）

- `342.0µs → 18424.5µs = 53.9x`（`f02_perf_prefix.log:30` / `f02_perf_postfix.log:34`）；另注 381.3→18606.0 = 48.8x（`verification-results.md:49-50`）。"~50x" 如实、不夸大，波动 ~11% 亦如实登记。
- release profile 明确 NOT_RUN（`handoff:75`），但同一段又断言"release 构建显著低于该量级"（`handoff:68`）——**该断言无实测支撑，应保持 unverified 标签**。
- 未写明的代价放大：`verify_and_serve` 对**每个 chunk 请求**都全量 hash 整文件（`:434`），16 MiB 分片拉取 256 MiB 资源 = 16 次全文件 hash ≈ 4 GiB 读。加上 `:440-441` 那次**结果被丢弃**的 chunk 读取、`:449` 的再读（该双读为修复前既有模式，非本次引入），单请求实际做"整文件 hash + 2 次 chunk 读"。
- **明显更优且更健全的替代（未评估，建议另立 Task）**：①单趟读：一次读文件同时累计 digest 并**捕获**目标 chunk，比对通过后再返回捕获字节——成本不高于现状（省掉两次 chunk 读），且把 digest→serve 的 TOCTOU 窗口彻底消除（现状 `:434` 校完再读 `:449`，对"预持写句柄"（M2-S2 T-16 威胁模型）仍有微秒级漏检窗口；该窗口修复前更大，属既有面、非本次回归）；②grant 携带 **per-chunk digest**，只验被服务的那个 chunk——安全性等价（响应体就是这个 chunk）而成本从 O(文件) 降到 O(chunk)，可消除 N× 放大；③真正的低成本变更信号是 **USN journal / 文件变更通知**（不依赖时间戳粒度），可作为未来大文件的旁路；④"mtime+size+内容抽样"**不健全且被 Task 明确禁止**（`Task:57`、`handoff:90`），不推荐。

### 轴 5 范围与证据纪律 —— 大体达标，三处纪律缺口（P2/P3）

- 范围：`raw/scope-and-diff-check.log:5-24` 的 name-status 在 `2b81f91c..fd31a7ad` 内只含 `main.rs`、`resource_protocol.rs` 两个源文件 + `doc/STATUS.md` + `doc/tasks/...` + `verification/**`；`git diff --check` 整树空 `DIFF_CHECK_EXIT=0`（`:26`）。`doc/STATUS.md`、`release-2b81f91c.md` 归因于编排者 release commit `0ef9155e`，与 Task `:45` 自述一致——**但该归因无法在本会话核对作者（not_verified）**。
- 探针处置：`TEMP-DIAG/TEMP-PERF`、`f02_diag_probe_loop`、`diag_entry_state_for_tests`、`f02_perf_probe_request_cost` 在 `src/` 内已全部不存在（grep 仅命中日志/文档）；保留的 `capture_facts_for_tests`（`resource_protocol.rs:547-552`）是**修复前既有**测试辅助（`verification/M2-RC1/run-log.md:32` 有历史引用），不是本次泄漏。**✓ 声明属实。**
- **P2 —— 证据未绑定交付对象**：所有 Rust 日志的 `HEAD` 戳是 claim `6a404c19`（诊断/性能/3 轮/定向/单线程），`f02_final_tip_verify.log:3` 也是 `6a404c19`（"交付候选"= 提交前工作树），`final-tip-bind-rerun.log:3` 是 `bf4b3dc0`（Handoff 自述为 amend 前）；**没有任何日志以 `fd31a7ad` 或回填 tip 为 HEAD**。AC5 字面要求"命令日志带固定 HEAD"虽满足，但"固定"的不是交付对象。缓解证据：这些日志的编译器诊断（`main.rs:30/421`、`resource_protocol.rs:67-68` 的行列号与字段形状）与交付源码**逐位对齐**，故"被编译的树 = 交付树"高度可信；但这是间接绑定，集成方仍需在集成 head 上重跑。
- **P3 —— 回填 tip 在范围证据之外**：`scope-and-diff-check.log` 停在 `fd31a7ad`，`scope-and-diff-check.log`/`final-tip-bind-rerun.log` 本身是回填 commit 新增（未出现在 name-status 列表内，自洽），即 `2b81f91c..3cef4831` 的最终范围/diff-check 从未跑过。
- **P3 —— 文档计数与日志头尾不齐**：Task `:45` 说"raw 日志 15 份"、Handoff `:22` 说"14 份"，交付时 raw/ 实为 14 份、回填后 16 份（三者不一致）；`raw/f02_py_core_full.log` **既无头部（shell/版本/HEAD/ISO）也无 `EXIT=` 尾行**，`f02_py_m2acceptance.log:1-5` 只有半截头（无 shell/HEAD）——与 `verification-results.md:76`"所有日志头部含 shell、cargo --version、`git rev-parse HEAD`、ISO；尾部 EXIT"的整体断言不符（其余 14 份确实齐）。
- **P3 —— Python 运行未记录 HEAD 且发生在主仓**：`f02_py_core_full.log:4-48` 输出路径为 `G:/CODEX/New Manga/src/ui/qml/...`（主仓而非本 worktree），且无 HEAD 戳。"Python 面零改动"本身由 name-status 佐证成立（无 `src/**` 条目），但回归号未绑定基线。

### 轴 6 测试语义保持 —— 未弱化 ✓

- `main.rs:798-826` 的 f02 原测试**断言与结构未动**：`400` + `{"code":"CONTENT_DIGEST_MISMATCH"}` 两条断言齐全（`:821-825`），本地 `use std::io::{Seek, SeekFrom, Write};`（`:814`）与修复前形态一致；旁证：修复前基线日志的 `warning: unused import: std::io::Write`（`f02_baseline_run1.log:254-258`）在修复后消失，恰好由新增 loop 只引入 `{Seek, SeekFrom}`（`:850`）而使用模块级 `Write` 解释——**即 main.rs 的改动就是"f02 之后追加 828-864 的 loop"，f02 本体未被改写**（无 Git 复核，属 indirect 但多点一致的证据）。
- 新增 loop 的断言承重（见轴 3），且都带 `round {round}` 上下文，失败可定位。
- `identity_change_invalidates_cache_entry`（`:716-732`）在缓存失去读取后仍有效（第二次请求由 `verify_and_serve` 的 identity 比对返回 `FILE_IDENTITY_CHANGED`），但**其测试名已名不副实**（不再验证任何"缓存条目失效"语义）——与 P2 同源，随缓存处置一并修。

---

## 二、分级问题清单

**P0**：无。

**P1**：无。（未发现安全语义弱化、未发现残留 mtime/digest 短路、未发现 f02 断言放宽、未发现允许范围外源文件改动。）

**P2**

1. `apps/desktop/src-tauri/src/resource_protocol.rs:67-69`、`:500-511`、`:517-526` —— 移除短路后 `CachedGrant.grant` 成为写入即弃的死字段，`GrantCache` 整体退化为只写结构；交付树因此产生**修复引入的** `warning: field 'grant' is never read`（`verification/.../raw/f02_fix_round1.log:21-29` 等 6 份日志），并被 Handoff `:16` 错误描述为"只 memoise Core resolve 结果"。理由：死状态是代码卫生/可维护性问题，且与交付文档陈述矛盾；建议按 AC2 的"最小清理"选项一并删除（或登记 follow-up）。
2. `doc/handoffs/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-owner-delivery.md:55-64`、`verification/.../raw/f02_final_tip_verify.log:3`、`raw/final-tip-bind-rerun.log:3` —— AC3/AC4 全部证据的 HEAD 为 claim `6a404c19`（tip 绑定复跑为 amend 前 `bf4b3dc0`），**无一份日志以 `fd31a7ad`/回填 tip 为 HEAD**；"交付树 = pre-delivery 树内容"仅是自述。理由：本仓库以"固定 HEAD + raw 日志"为验收纪律，本 Task 的交付对象恰在证据之外；缓解性对齐证据见轴 5。

**P3**

3. `raw/f02_py_core_full.log`（全 48 行）—— 无头部、无 `EXIT=` 尾行，且运行于主仓而非 worktree；`verification-results.md:76` 的"所有日志头尾齐全"断言对它不成立。
4. `doc/tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md:45`（"raw 日志 15 份"）vs `handoff:22`（"14 份"）vs 实际（交付 14 / 现 16）—— 计数不一致。
5. `raw/scope-and-diff-check.log:3` —— 范围/`diff --check` 只覆盖 `2b81f91c..fd31a7ad`，回填 commit（`3cef4831`）未纳入最终整树复算。
6. `handoff:42` —— 把 run 级"3/3 捕获"表述为"失败概率极高"；按 dump 轮次 0/2/5 推算单轮碰撞概率约 0.3–0.5（轴 1），措辞应改为"单轮高概率、运行内必捕获"。
7. `raw/f02_diag_run1/2/3.log` —— 缺负向对照：未做"跨 tick 写入后 mtime 必须变化"的判别实验，因此"系统 tick 粒度碰撞"与"LazyWriter 元数据延迟/缓存 FCB 未刷新"两种机理**未被区分**；`verification-results.md:30` 选定了前者而未证伪后者。两者都导向同一修复，故不影响判定，仅降低机理归因强度。
8. `resource_protocol.rs:434` + `:440-441` + `:449` —— 每请求"整文件 hash + 丢弃读 + 再读"的冗余路径与 digest→serve 的残留 TOCTOU 窗口（对预持写句柄；修复前更大，非本次回归）；未评估单趟 hash+capture 或 per-chunk digest 这两个**同成本/更低成本**方案（轴 4）。
9. `handoff:68` —— "release 构建显著低于该量级"为无实测断言（release 已声明 NOT_RUN），同段落里应显式标 unverified；且未写明按 `MAX_RESOURCE_BYTES`(256 MiB) 线性外推的绝对值（debug ≈4.7 s/request）。
10. `main.rs:836-864` —— loop 每轮 `env_with_fixture` 走 `std::mem::forget(dir)`（`:458`），单次运行泄漏约 50 个临时目录（既有模式、量级无害），可顺手改为带守卫清理。

---

## 三、not_verified 清单（需集成方代跑；本会话 shell 不可用，全部为 Git/运行级事实）

前置：`cd apps/desktop/src-tauri`；worktree `apps/desktop/frontend` 需先 `npm install && npm run build` 生成 `dist`（`handoff:71` 已登记该环境前置，gitignored）。

```bash
# 0) 交付对象确认（回填 tip 的 src 必须与 delivery_head 逐字一致）
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" rev-parse HEAD
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" diff --stat fd31a7ad..HEAD        # 期望：仅 docs/verification
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" diff fd31a7ad..HEAD -- apps/desktop/src-tauri/src   # 期望：空

# 1) 最终整树范围 + diff-check（含回填 commit）
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" diff --check 2b81f91c..HEAD        # 期望：空，EXIT=0
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" diff --name-status 2b81f91c..HEAD  # 期望：仅 src 两文件 + docs/verification

# 2) 作者归因（doc/STATUS.md、release-2b81f91c.md 是否为编排者 release commit 0ef9155e）
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" log --format='%H %an %ae %s' 2b81f91c..HEAD

# 3) 集成 head 上的稳定性复跑（补上 P2-2 缺的绑定）
cargo test --bin m2rc1-desktop                       # 期望 34 passed / 0 failed；请记录 HEAD 与 EXIT
cargo test --bin m2rc1-desktop f02_equal_size_rewrite_stability_loop   # 期望 1 passed（50 轮）
cargo test --bin m2rc1-desktop -- --test-threads=1    # 期望 34 passed

# 4) 修复引入警告的证据（P2-1 复核）
cargo build --bin m2rc1-desktop 2>&1 | Select-String "never read"    # 期望命中 resource_protocol.rs:68

# 5) loop 判别力（承重性）反证：只回退产品文件、保留新 loop，预期 f02 loop 变红
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" checkout 6a404c19 -- apps/desktop/src-tauri/src/resource_protocol.rs
cargo test --bin m2rc1-desktop f02_equal_size_rewrite_stability_loop   # 期望 FAILED（50 轮内命中同 tick 碰撞）
git -C "G:/CODEX/New Manga.worktrees/M2-FIX-F02-zcode" checkout HEAD -- apps/desktop/src-tauri/src/resource_protocol.rs   # 立即还原

# 6) Python 零回归（在可记录 HEAD 的状态下重跑，勿只依赖主仓旧日志）
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q   # 期望 35 passed
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/core -q            # 期望 77 passed
```

另有两条**本 Task 明确未做**、且交付树上不可复现的项，请集成方按需决策：
- **性能数字不可在交付树复现**：`TEMP-PERF` 已移除（`verification-results.md:43`），342/18424 µs 只能引用日志，无法重跑；release profile 未测（`handoff:75` 已如实登记）。
- **真实 Core sidecar 通道下的等长重写复放未做**（`handoff:76` 已声明；原 f02 亦不覆盖，非本 Task 收窄）。

---

## 四、结论与条件

**判定：approved_with_conditions。** 交付达成了 Task 的实质目标：AC1 用三份独立 dump 证明了"mtime 逐位相同 + 重写内容以 200 被放行"，把 f02 从"测试 flake"重新定性为**真实产品安全缺口**；AC2 的修复（移除 mtime 门控、每请求全量 digest 重验）在语义上是最强且正确的方向，f02 断言未弱化，F-01 未受影响，探针已如实移除，范围未越界；AC3/AC4 的日志数字经逐份核对自洽，50 轮 loop 对修复前代码具有近乎确定性的判别力。**不存在 P0/P1。**

放行条件（不含实现改动，均为集成期动作）：

- **C1（对应 P2-2）**：在集成 head（或最终 tip）上复跑并留存 HEAD 绑定日志：`cargo test --bin m2rc1-desktop`（3 轮）、`... f02_equal_size_rewrite_stability_loop`、`... -- --test-threads=1`、两条 pytest、`git diff --check 2b81f91c..<final-tip>`；日志须带 `git rev-parse HEAD` 与 `EXIT`。本 Task 现有证据全部止于 `6a404c19`/`bf4b3dc0`，该条件是 AC5 的收口动作。
- **C2（对应 P2-1）**：对"缓存死结构"给出明确处置之一——(a) 在允许路径内一并删除 `CachedGrant/GrantCache` 及其三处无观察效果的 map 操作（随后触发 C1 重跑），或 (b) 由 Integrator 在集成记录/Task 回填中**显式接受该 dead-code 并把 Handoff `:16` 的"只 memoise Core resolve 结果"更正为"缓存已无读取方、仅保留计数/驱逐副作用"**，同时把 `identity_change_invalidates_cache_entry` 的更名/收敛登记为 follow-up。任选其一即可，不得以"性能"为由恢复 mtime 门控。

**推荐下一步**：由 Codex（Integrator，保持 Owner≠Integrator）按 C1 在集成 head 上复跑并产出集成记录，同时选定 C2 的处置；集成通过后回填 `doc/tasks/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY.md` 的 `review`/`integration_merge` 并将 `status` 改 `done`（Review 报告建议落 `doc/reviews/M2-FIX-F02-RESOURCE-CHANNEL-FLAKY-fd31a7ad-dsh-r1.md`，本会话按只读约束未写盘）。另建议**新开一个 Task（本 Task 范围外）**：把 `verify_and_serve` 改为单趟"hash+capture 同一读"并在 grant 契约允许时评估 per-chunk digest，以消除冗余读、残留 TOCTOU 窗口与 N× 全量 hash 放大——该优化须经 Core 契约变更流程，不得弱化"等长重写必拒"。
