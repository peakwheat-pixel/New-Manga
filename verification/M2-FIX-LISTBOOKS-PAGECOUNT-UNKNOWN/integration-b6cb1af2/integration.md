# M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 集成记录（integration-b6cb1af2）

- 集成者：Codex（子 agent 代行，用户授权 2026-09-28；Owner=ZCode 另一子 agent，Owner≠Integrator 保持）
- 集成日期：2026-09-29（本地 +0800）
- base：`6199df48`；release commit：`a2380706`（main 集成起点，集成前 HEAD 已核实）
- Owner 分支：`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`；Owner worktree：`G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode`
- **最终 r2 tip（被验树/被并树）：`b6cb1af2299b887461e1e7b2914b7577f8a6871c`**（worktree `git rev-parse HEAD` 集成前实测一致，`git status --porcelain` 空）
- **integration merge：`699610291f1536a1a1dbda62ba73f2587def1d91`**（`git merge --no-ff`，ort 策略，无冲突，merge diff 23 文件 +1023/−40）
- 契约修订：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` `1.1 → 1.2`（§5 ListBooks `BookSummary.page_count: int | null` widening + §3.2 授权例外指针 + Revision history 日期 2026-09-29）
- 验收套件终态：`tests/m2_acceptance` **35 passed, 0 xfailed**（F-2 xfail 移除转 PASS，无 XPASS）

## 0. Review 链（双轮，报告已归档）

| 轮次 | 对象 | 判定 | 归档（原字节复制） | SHA256 |
|---|---|---|---|---|
| DSH r1 | 交付 `852a92ae`（回填 tip `bee7bf59`） | `approved_with_conditions`（0×P0/P1；4×P2；6×P3；C1/C2 归 Owner 返修，C3/C4 归集成方） | [doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-852a92ae-dsh-r1.md](../../reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-852a92ae-dsh-r1.md) | `aba657b1ddb80af2b2ce0ac8bc9cd03003067ba375a17886e677e63ede8efd01` |
| DSH r2 | r2 tip `b6cb1af2` | `approved_with_conditions`（**C1=通过、C2=通过，无需 Owner 返修，可进入集成**；新增 1×P2（tip 绑定/amend 轨迹）+4×P3（文档指针级）；新条件 C5 归集成） | [doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-b6cb1af2-dsh-r2.md](../../reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-b6cb1af2-dsh-r2.md) | `16c97ef1afa6b546cd8eff66b78afbb7aaefe2d42405a4d0973e636f1fb9b3d0` |

两份归档均经 `sha256sum` 与 `/tmp/m2fixpc-review/` 原件比对一致（原字节复制）。

## 1. C3 —— 集成 head 四套复跑 + commit 绑定（关闭）

集成 head = integration merge `69961029`（集成修正 commit 仅改 doc/verification 文件，测试面与 `69961029` 完全一致；两组 hash 一并绑定于此）。另：Owner 侧 tip 级复跑在 `b6cb1af2` 上完成（见 §3 代跑表 A1-5a/b/d），Handoff 表注「交付 tip」表述经复核已是修正后版本（「工作树等价于 `852a92ae`，日志 head 戳 `2210d642`（交付前）」），无需再改。

| 套件（cwd） | 结果 | EXIT | postmerge 日志 |
|---|---|---|---|
| `$py -m pytest tests/m2_acceptance -q` | **35 passed, 0 xfailed**（9.18s） | 0 | [raw/postmerge-pytest-m2-acceptance.log](raw/postmerge-pytest-m2-acceptance.log) |
| `$py -m pytest tests/core -q` | **77 passed**（7.38s；尾段 QML TypeError 为 QML smoke 测试既有 stderr 噪声） | 0 | [raw/postmerge-pytest-core.log](raw/postmerge-pytest-core.log) |
| `cargo test --bin m2rc1-desktop`（`apps/desktop/src-tauri`，默认线程） | run1 **32 passed; 1 failed**（f02，见 §2 裁定 1）EXIT=101 → run2/run3 均 **33 passed** EXIT=0 | 0（终态） | [raw/postmerge-cargo-test.log](raw/postmerge-cargo-test.log) / [-run2](raw/postmerge-cargo-test-run2.log) / [-run3](raw/postmerge-cargo-test-run3.log) |
| `npm test`（`apps/desktop/frontend`，vitest run） | **5 files / 31 tests passed**（LibraryPanel.test.tsx **8 tests**） | 0 | [raw/postmerge-npm-test.log](raw/postmerge-npm-test.log) |

解释器：`"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"`（Python 3.12.3）；node v24.15.0 / npm 12.0.1；cargo 1.98.1。所有日志带头（shell/解释器或工具版本/HEAD/ISO 时间戳/目的/命令）带尾 EXIT。

## 2. C4 —— 三项裁定（关闭）

**裁定 1｜f02 flaky 复跑口径与判定**：按 r1 §2-6 协议在 Owner tip `b6cb1af2` 连跑 3 次 `cargo test --bin m2rc1-desktop`（默认线程）——run1 **FAILED**（`f02_equal_size_rewrite_after_first_verify_rejected`，panicked `src/main.rs:821`，`left: 200, right: 400`，32 passed，EXIT=101；[raw/a1-5c-cargo-run1.log](raw/a1-5c-cargo-run1.log)）、run2/run3 **33 passed** 全绿（[raw/a2-f02-run2.log](raw/a2-f02-run2.log) / [a2-f02-run3.log](raw/a2-f02-run3.log)）；因已复现，补单线程对照 `-- --test-threads=1`：**33 passed** 全绿（[raw/a2-f02-single-thread-control.log](raw/a2-f02-single-thread-control.log)）。集成 head postmerge 三连同模式：run1 FAILED（f02 同点同值）→ run2/run3 绿（§1 表）。
**判定**：f02（资源通道 equal-size 原地重写 mtime/digest 判定，`main.rs:798-826`）为**默认线程并发下的既有潜伏 flake**——间歇触发（每侧三连均为首跑红/后续绿）、单线程稳定，与 `library_bridge.rs` page_count 类型改动**零代码路径交集**（r1 §0 轴 5 静态评估 + 本轮两侧 6 次默认线程跑中 library_bridge 5 测试全绿佐证）。**不计本 Task 回归**。**另立 flaky Task 建议**（留 planning 池，非本 Task 范围）：对 M2-S2 资源通道 equal-size 重写 mtime/digest 重验证判定做并发稳定化（如显式序列化该测试组或修 mtime 粒度依赖），Task 命名建议 `M2-FIX-F02-RESOURCE-CHANNEL-FLAKY`。

**裁定 2｜`LibraryPanel.test.tsx` 范围解释**：Task §允许修改范围（`:57`）字面仅列 `types.ts`、`LibraryPanel.tsx`（r1 P3-5）。该文件的修改（r1 期 None 用例 + r2 期 known-0 用例）是 **AC1（「vitest 用例锁定不渲染 0」）与 DSH r1 条件 C1 的必然要求**——AC 文本本身点名了 vitest 用例，无测试文件则 AC1 不可验收。属「AC 必然要求」的范围解释，与 r1 P3-5 定性一致；后续 Task 冻结允许路径时建议把测试文件与产品文件成对列明。

**裁定 3｜NOT_RUN 裁定**（对应 Handoff NOT_RUN 小节逐项）：
- **Rust 真通道 unknown-page 端到端：未覆盖，留 P3-1**——`real_library_sidecar_round_trip_and_eof` 仅对空库断言；「Python 真进程 `json.dumps` 发出 `"page_count":null` 被 Rust `Option<u32>` 接住」无判别用例。登记为**后续增强候选，不阻断集成**（现有三侧单测 + serde 往返 + 35/77/33/31 全绿已覆盖本 Task 冻结语义；若未来 Rust 退回 `u32`，该缺口会使回归逃逸——见 §5 增强候选 1）。
- TS known-0 正向渲染：已由 r2 C1 新用例闭合（非 NOT_RUN）。
- 交付 commit 级绑定复跑：已由 r2 `raw/r2-final-bind-rerun.log`（Owner）+ 本记录 §1/§3（集成方）双重闭合。
- f02 flaky 复跑口径：已按裁定 1 执行并闭合。
- `Any` 导入来源：已比对闭合（见 §4）。

## 3. 集成方代跑证据表

（全部在 Owner worktree `b6cb1af2` 执行，除注明 postmerge = 集成 head；日志于 [raw/](raw/)，均有头尾纪律）

| # | 组 | 命令/检查 | 结果 | EXIT | 日志 |
|---|---|---|---|---|---|
| A1-1 | r2§5-1 r2 delta 面 | `git diff --name-status/--stat bee7bf59..b6cb1af2` | **10 文件全为测试/文档/日志，`src/` 零改动**（`LibraryPanel.test.tsx` +27、契约 4 行、Handoff 27 行、Task 2 行、验收测试 docstring 8 行、4 raw 日志 + verification-results.md 新增） | 0 | [a1-1-…log](raw/a1-1-r2s5-diff-bee7bf59-b6cb1af2.log) |
| A1-2 | r2§5-2 amend 轨迹 | `git diff --stat` 三段 | 见 §6 C5 | 0 | [a1-2-…log](raw/a1-2-r2s5-amend-trajectory.log) |
| A1-3 | r2§5-3 P3-1 | `git log --diff-filter=A --format='%h %cI' -- …/final-tip-rerun.log` | **首次加入 = `b6cb1af2`（2026-09-29T02:35:19+08:00）**，即随 r2 落盘而非随 `bee7bf59`（日志头时间 02:17:45 > bee7bf59 ref 时间 02:17:38，互证）——verification-results.md §1 #3 括注已按此修正 | 0 | [a1-3-…log](raw/a1-3-r2s5-final-tip-log-added-at.log) |
| A1-4 | r2§5-4 洁净 | `git status --porcelain` + `git diff --check 6199df48..b6cb1af2` | porcelain 空；diff --check 空 | 0 / 0 | [a1-4-…log](raw/a1-4-r2s5-status-diffcheck.log) |
| A1-5a | r2§5-5a | `$py -m pytest tests/m2_acceptance -q` | 35 passed（9.04s） | 0 | [a1-5a-…log](raw/a1-5a-pytest-m2-acceptance.log) |
| A1-5b | r2§5-5b | `$py -m pytest tests/core -q` | 77 passed（7.13s） | 0 | [a1-5b-…log](raw/a1-5b-pytest-core.log) |
| A1-5c+d | r2§5-5c/d | cargo / vitest | 见 §1 同款命令在 tip 的三连与单跑；vitest 5 files / 31 tests（LibraryPanel 8） | 见 §2/0 | [a1-5c](raw/a1-5c-cargo-run1.log) / [a1-5d](raw/a1-5d-npm-test.log) |
| A2-1 | r1§2-1 契约最小性 | `git diff 6199df48..852a92ae`（及 `..b6cb1af2`）契约文件 | r1 交付口径 = 头部版本行 + Revision 1.2 段 + §5 行；r2 tip 口径 = 上三者 + **§3.2 授权例外指针行** + 日期修正 2026-09-29（共 4 处）；命令名/payload/错误码/命令清单零改动 | 0 | [a2-1](raw/a2-1-contract-minimality.log) / [a2-1b](raw/a2-1b-contract-minimality-tip.log) |
| A2-2 | r1§2-2 范围 | `git diff --name-status 6199df48..852a92ae` | **实测 18 条路径**（10 M + 8 A），与 Owner 自检 [raw/scope-and-diff-check.log](../raw/scope-and-diff-check.log) 清单逐条一致；r1 报告所述「11 条」系其口径笔误（18 = release 3 条 + owner delivery 15 条；scope decomposition 见 Owner 日志）。全部落允许路径，唯一字面缺口 `LibraryPanel.test.tsx` 见裁定 2 | 0 | [a2-2-…log](raw/a2-2-scope-name-status.log) |
| A2-3 | r1§2-3 diff 面 | `git diff 6199df48..852a92ae -- apps/desktop/frontend apps/desktop/src-tauri` | 全部为 page_count 相关（TS 类型+注释、`?? "—"` 一行、None 用例；Rust `Option<u32>`+注释+serde 测试），无其他语义改动 | 0 | [a2-3-…log](raw/a2-3-frontend-rust-diff-surface.log) |
| A2-5 | r1§2-5 变异红证复现 | 临时把 `core_service.py:169` 改回 `page_counts.get(book.book_id, 0)` → 跑 F-2 场景 → 还原 | **1 failed @ `presented_unknown` 断言**（`E assert False`，Python 腿 `||` 类变异即 `get(...,0)` 默认 0 变异），PYTEST_EXIT=1；`git checkout --` 还原后 `RESTORED_LINE` 无默认 0、零残留（日志尾部 porcelain 中 gen/schemas 与 permissions/autogenerated 的 M 行为 cargo 构建副产物，非变异残留，已按路径还原，见日志集成方括注） | 1（预期红）/0 | [a2-5-…log](raw/a2-5-f2-mutation-red.log) |
| A2-7 | r1§2-7 Any 来源 | `git show 6199df48:tests/core/test_core_service.py \| grep typing` vs 当前 | **base 亦无 `from typing import Any`**（两侧 grep `typing` 均 EXIT=1；`Any` 用例在 `:394` `fail_execute` 注解）——既有潜伏项，非本 Task 引入；`from __future__ import annotations` 下运行期无碍（77 passed 实证），留待套件 lint 化时统一处理 | 0 | [a2-7-…log](raw/a2-7-any-import-provenance.log) |

## 4. `Any` 导入比对结论

base `6199df48` 与 r2 tip `b6cb1af2` 的 `tests/core/test_core_service.py` 均无 `typing` 导入行（`grep -n "typing"` 双侧 EXIT=1），`Any` 仅用于 `:394` 函数注解；`from __future__ import annotations`（`:7`）使注解不求值，运行期无影响。**裁定：既有潜伏项，非本 Task 引入，不阻断**；候选后续项：套件引入 lint/mypy 时统一补导入。

## 5. 遗留与后续增强候选（均不阻断）

1. **P3-1（r1）Rust 真通道 unknown-page 端到端 seed 1 条**：在 `real_library_sidecar_round_trip_and_eof` seed 一本无合格页书、断言 Rust 侧 `page_count == None`——登记为后续增强候选（可并入 flaky Task 之后的资源通道测试整理，或独立 micro-task），不阻断本 Task。
2. **f02 flaky Task 建议**：`M2-FIX-F02-RESOURCE-CHANNEL-FLAKY`（M2-S2 资源通道 equal-size 重写 mtime/digest 并发判定稳定化），证据 §2 裁定 1。
3. `Any` 导入（§4）与 r1 报告「11 条路径」口径勘误（§3 A2-2）已登记，无需动作。

## 6. C5 —— r2 amend 轨迹与 final tip 落档（关闭）

reflog（DSH r2 §0 已核对）+ 本轮 `git diff --stat` 实证（[raw/a1-2-r2s5-amend-trajectory.log](raw/a1-2-r2s5-amend-trajectory.log)）：

| amend 段 | 差集 |
|---|---|
| `f4f77808`（r2 初版，run-at hash）→ `c3f8bb3a` | **+`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/raw/r2-final-bind-rerun.log`（新增 167 行）**——tip 绑定复跑日志并入 |
| `c3f8bb3a` → `b6cb1af2`（最终 r2 tip） | **`verification-results.md` 1 行（1 insertion, 1 deletion）**——§6 括注修正 |
| 合计 `f4f77808 → b6cb1af2` | 2 文件，+168/−1 |

**最终 r2 tip hash = `b6cb1af2299b887461e1e7b2914b7577f8a6871c`**，已落档：
- `verification-results.md` §1 #4（集成方修正，含完整 hash 与本 amend 轨迹指针）；
- `doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md` frontmatter `delivery_head` 与正文 ledger（集成方修正）；
- 同时修正 `verification-results.md` §1 #3 `final-tip-rerun` 括注（P3-1，实随 #4 `b6cb1af2` 落盘）与 §5「零残留…见日志尾」指针（P3-2，改指 `raw/r2-final-bind-rerun.log` diff --check 实证），均标注集成方修正。

## 7. 集成操作与工作区保护

- merge 前核实：main HEAD = `a2380706`（release commit）；Owner worktree HEAD = `b6cb1af2`、porcelain 空。
- merge：`git merge --no-ff agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`，ort 策略无冲突。
- 主 repo 既有未提交改动（`apps/desktop/frontend/package*.json`、`apps/desktop/src-tauri/gen/schemas/**`、`apps/desktop/src-tauri/permissions/autogenerated/**`、`verification/M2-RC2/**` 等）与分支 delta 无交集，**未被 add/checkout/覆盖**，继续归原作者所有。
- cargo 复跑在 Owner worktree 与主 repo 产生的 `gen/schemas` / `permissions/autogenerated` 构建副产物：worktree 侧已 `git checkout --`（仅限这些路径）还原至 porcelain 空；主 repo 侧此类文件本就处于未提交状态，未纳入任何 commit。
- 本记录与归档报告、raw 日志、`verification-results.md` 修正、Task 回填、REBASELINE_PLAN 行更新一并进入集成修正 commit（`integration(M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN): …`）。不 push、不删分支；`doc/STATUS.md` 留主会话收口。
