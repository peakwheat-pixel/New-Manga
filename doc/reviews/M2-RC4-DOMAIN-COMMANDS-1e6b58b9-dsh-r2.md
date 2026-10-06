# M2-RC4-DOMAIN-COMMANDS 非作者独立 Review（r2，静态只读）

```yaml
---
task_id: M2-RC4-DOMAIN-COMMANDS
round: r2
reviewer: DeepSeek Harness（非作者，静态只读）
reviewed_head: 1e6b58b975ae2132d69124f27be3157214bd5c4b  # = codex/rc4-integration
r1_report: doc/reviews/M2-RC4-DOMAIN-COMMANDS-5954bb4b-dsh-r1.md（decision=approved_with_conditions，RC4-01..13）
prior_heads: 0fba6079(base) → 5954bb4b(r1 审) → 2e9d9819(+e495910f) → 7c9d3a32(+7021d34c) → 1e6b58b9(+evidence commit)
decision: approved_with_conditions
new_findings: 2×P3（N-1 范围待追认、N-2 Gate git 原始日志缺档）+ 3×P4
---
```

## §0 固定事实与方法限制

| 项 | 值与证据 |
|---|---|
| 仓库 / worktree | `G:/CODEX/New Manga.worktrees/RC4-integration`（linked worktree，`.git:1` → `G:/CODEX/New Manga/.git/worktrees/RC4-integration`） |
| HEAD 静态确认 | `refs/heads/codex/rc4-integration` = `1e6b58b975ae2132d69124f27be3157214bd5c4b`（`.git/refs/heads/codex/rc4-integration:1`）；`.git/worktrees/RC4-integration/logs/HEAD:16` 记录 `7c9d3a32 → 1e6b58b9`，message=`commit: evidence(rc4): DSH r1 report, r1-fix combined Gate runs, RC4-05 ratification` |
| 上游链（reflog 实证） | `5954bb4b →(merge e495910f) 2e9d9819 →(merge 7021d34c) 7c9d3a32 →(evidence commit) 1e6b58b9`（`logs/HEAD:13-16`） |
| **方法限制（随结论携带）** | 本会话 **pwsh 仍不可用**：`pwsh -Command`（含 `echo hello`、`run_in_background`）第三次仍以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\RC4-integration)` 失败，命令未执行。故**未运行 git/pytest/npm/cargo，未修改任何文件**。所有动态数字均为**引用已入库 raw 日志**（逐条给文件:行），不是本次运行结果；`git diff/name-status` 类文件清单无法独立枚举（见 N-2/RC4-02/N-5） |

---

## §1 r1 全部 13 项逐项处置

### 1.1 三项 blocking

| 项 | r1 级别 | r2 裁决 | 证据 |
|---|---|---|---|
| **RC4-01** list/restore 零 wire 测试 | P2（blocking） | **闭合** | 新 `tests/core/test_rc4_revision_commands.py`（324 行，真实 `assemble_production_core` + 真实 `CoreServiceServer.dispatch_request` wire + 真实 SQLite/导入/PNG）：①**DTO**：`SUMMARY_FIELDS` 恰 10 字段并 `assert set(rev)==…`（`:37-48,117-118`）、升序（`:116`）、`is_current` 唯一（`:119-120`）、无快照/路径/bytes；②**TARGET_NOT_FOUND**：list 未知 region（`:129-142`）、restore 未知 region 与未知 revision（`:252-268`）；③**restore 全语义**：新 revision=5、`origin="restored"`、`review_state="needs_review"`、`is_pinned=false`、`restored_from_revision_id`、源 pin/历史保留、**不移动指针**、文字+锁回退（`:145-196`）；④**过期零写**：`INPUT_REVISION_CHANGED` + 版本数 5 + 无 restored（`:199-227`）；⑤**正整数校验**：0/str/float/bool/缺参/缺 region_id → `INVALID_REQUEST`（`:230-249`）；⑥**双连接竞态**：同一 data root 起两个 Core + `threading.Barrier`，恰一应用、败者 `INPUT_REVISION_CHANGED`、文件终态恰一条 restored（`:271-324`）；⑦**TOCTOU 守卫**：`expected` 先行、未知 revision 需当前 expected 才可达（`:257-261`）。执行证据：`raw/core-stdio-r1fix-1.log:5,12`（两文件 **8 passed**，= 该文件 7 用例 + stdio 1）、组合树复跑 `raw/combined-gate-r2fix-focused.log:4,21`（focused **408 passed**，含该目录） |
| **RC4-03** Gate 未绑定被审 head | P3（blocking） | **闭合（方式可接受，见 §2）** | 新 Gate 在 `7c9d3a32` 重跑并绑 head（6 份日志 `:3` 均写 `HEAD=7c9d3a32`）；Task:73 记录该 head 身份（`= merge Core e495910f + React 7021d34c`）；reflog 证明 `1e6b58b9` 是 `7c9d3a32` 之上**唯一**一个 commit，且 message 明确为 evidence/追认 |
| **RC4-05** `gen/schemas/**` 越 allowed_paths | P3（blocking） | **闭合（追认已登记）** | `doc/tasks/M2-RC4-DOMAIN-COMMANDS.md:72`「RC4-05 追认（Codex/集成方）：`gen/schemas/*.json` 4 文件系 build.rs 生成器对三命令权限条目的实质再生…按 M2-REGION-RETYPE-CORE P3-2 先例追认为授权范围内」。先例形态核对：`doc/reviews/M2-REGION-RETYPE-CORE-eaed7858-dsh-r1.md:51-52` 同类条目 + 该 Task 的 r2 收口表（同文件 r2 报告）确为「集成方追认」闭合。4 个文件实存（`gen/schemas/{acl-manifests,capabilities,desktop-schema,windows-schema}.json`），生成源 `build.rs:54-89` 确实声明 19 条命令（12 production + 4 probe + 3 AC1） |

### 1.2 五项非阻塞

| 项 | r1 级别 | r2 裁决 | 证据与残留 |
|---|---|---|---|
| **RC4-02** attempt-2→3 像素翻转无解释 | P3 | **部分闭合 → 降级接受（非阻塞，附 P3 残留）** | 已补：(a) diff 口径写入 Handoff（`doc/handoffs/…-core-58b3706d.md:39`：`git diff 37110749..58b3706d -- src/` 仅 `service.py`（+38/−16），全部落在 managed 读取 typed 化 / reports 白名单化 / skip-SFX 原图 bbox 恢复）；(b) **墨水显式断言**：`tests/core/test_rc4_stdio_render_preview.py:239-248`「并非裸背景」弱断言之上新增 `ink >= 400`（注释注明实测 1389，阈值≈29%），组合树已实跑通过（`combined-gate-r2fix-focused.log:12-14` 该测试在跑）。**未闭合部分（我独立核对推翻其因果说明）**：Handoff 称翻转「来自测试文件自身演进…非实现翻转」，但 attempt-2 的 traceback **逐行**复现了与当前文件**行号一致**的测试源码（`raw/core-stdio-preview-attempt-2.log:11-176` ↔ 当前文件 `:84-238`），fixture（含 NMFR clean 帧、两个 region、`"VISIBLE TEXT"`）逐字相同，唯一差异是 3 处 `.convert("RGB")`（`attempt-2:163` vs 当前 `:236-237`）——而**RGBA 全等 ⇒ RGB 全等**，该差异因果惰性（与 r1 判断一致）。且 attempt-3 日志头仍记 `commit: 37110749`（`raw/core-stdio-preview-attempt-3.log:3`，脏树运行），故翻转只能落在 **src 侧（即同一 commit 的 `service.py` 组合路径重构）**，而非测试演进。另：我无 shell，无法独立核对 `git diff` 的文件清单与 +38/−16（只能确认三处改动都在 `service.py` 内且与当前实现一致：`:162-165,201-217,221-267,261-278`）。**残留动作**：补一条 `git diff --stat 37110749..58b3706d -- src/` 原始日志（并入 N-2） |
| **RC4-04** 7 vs 1 skip 口径 | P3 | **闭合（附 P4 残留）** | Task:73 给出分解：`1 skipped=registry_readiness（dev venv 有意携带 ML 栈，用户批准）`；`Owner 轮 7 skipped…差异=PowerShell 驱动下 openssl 不在 PATH 的 6 个 TLS skip`。算术自洽（7 = 6 TLS + 1 registry），且 6 个 TLS skip 有仓库既证（`doc/reviews/M2-I2-86ecb94.md:35`：1 项 `tests/network/test_connection_tester.py:106` + 5 项 `tests/network/test_transport_tls.py:39,47,62,69,83`，原因 openssl 不可用）。基线口径核对：`verification/…/integration/baseline-full-300b4007.log:3,4,49,50`（HEAD=300b4007，`-q`，`1 failed`=test_catalog，7 skipped）。该 registry skip 本体实存：`tests/providers/test_registry_readiness.py:236-247`。**P4 残留见 N-3**（本轮日志头声明 `-rs` 却无 `SKIPPED [1] …` 行） |
| **RC4-06** revoke 失败分支无判别证据 | P3 | **闭合** | 注入口：`core_bridge.rs:318-321`（`pub fail_revoke_for: Mutex<Option<String>>`，理由注释点名 RC-4）、`:337`（初始化 None）、`:438-447`（命中即 `Err(CoreError::new("REVOKE_FAILED"))`）。测试：`main.rs:1858-1893` `rerender_fails_closed_when_previous_revoke_fails` 断言 `preview=Null`(`:1885`)、`PREVIEW_UNAVAILABLE`(`:1886`)、`current` 保留旧 key(`:1887`)、旧 grant 仍可 resolve(`:1888`)、新 grant `REF_REVOKED`(`:1889-1892`)。执行证据：`combined-gate-r2fix-cargo.log:67`（ok） |
| **RC4-07** 卸载窗口 object URL 泄漏 | P3 | **闭合** | `WorkbenchPage.tsx:315-324` 卸载 cleanup 内 `imageRequestRef.current += 1; operationRef.current += 1;`（`:321-322`，附 RC4-07 理由注释）；迟到预览闭包据此走 `:601-604` 分支（`URL.revokeObjectURL(url)` 后 return），不再 `replaceImageUrl`（`:605`）。React Handoff `:52` 已说明不新增 JSDOM 用例的理由（jsdom 无真实 blob 生命周期，判别力为零），我认可 |
| **RC4-08** 两种 wire 码 | P3 | **闭合** | page 级：`service.py:261-271`（`ValueError` → `BLOCKED/MISSING_REQUIRED_INPUT`，注释点明解码失败/尺寸不一致/box 越界）+ `:272-278`（`OSError` → `WRITE_FAILED/ARTIFACT_WRITE_FAILED`）；region 级同拆分 `:368-376`/`:377-383`。测试：新增 `tests/rendering/test_rerender.py:425-452`（page 级 ValueError→BLOCKED，且旧 current 保留 `:449-452`）、`:563-587`（region 级，并断言 `compose_page` 不被触达 `:579`）。**既有 OSError 用例语义仍一致**：`:402-423` 仍是「compositor 抛 OSError（磁盘/IO）→ WRITE_FAILED/ARTIFACT_WRITE_FAILED，旧 current 保留」，与「输入不可用」拆分后不冲突；另一处 `tests/storage/test_artifact_commit.py:172` 属 commit seam 的写失败，与本拆分无交集 |

### 1.3 五项 nit

| 项 | r1 级别 | r2 裁决 | 证据 |
|---|---|---|---|
| **RC4-09** 陈旧命名/注释 | P4 | **闭合（附 P4 残留 N-4）** | Core：`tests/core/test_core_detect.py:604` `test_ping_carries_protocol_minor_4`（断言 minor 4 `:614`，注释含 RC-4 出处 `:608`）；`tests/core/test_core_service_retype.py:132` `test_protocol_minor_bumped_to_four_with_rc4_surface`（`:136-137`）。Rust：`main.rs:897-900`「twelve production -- resource-channel, IPC1, settings, retype and RC-4」；`build.rs:37-41`「nineteen commands below (twelve production …)」。React：`ViewerPanel.tsx:1-23` 已删除 "Core has no restore/rerender runtime command yet (PROTOCOL_MINOR=3)…render disabled"，改写为「Since M2-RC4 … undo runs `restore_region_revision` …rerender calls `rerender_page` …」（`:17-22`）。Handoff 措辞：`doc/handoffs/…-core-58b3706d.md:60` 已把 ignored 用例改为 digest 性能探针（对应 `main.rs:1344-1351` `perf_chunk_request_digest_cost` `#[ignore]`） |
| **RC4-10** `MISSING_REQUIRED_INPUT` 的 category | P4 | **降级接受（登记可接受）** | 现状 `core_service.py:863-866`：`MISSING_REQUIRED_INPUT` → `category="not_found"`。C1 §8 语义更近 `unavailable`，但契约未冻结 category、UI 按 `code` 消费；Handoff `:47` 登记 deferred + 下一轮契约澄清建议。属 P4 口径项，**接受其延后**；建议把该条落到下一轮契约修订的候选清单，而非只留在 Handoff 表格 |
| **RC4-11** rotate 无等值短路 | P4 | **闭合** | `main.rs:347-361`：`let same_key = next.as_deref() == Some(previous_id); if !same_key && channel.revoke_resource(previous_id).is_err() {…}`（`:352-353`，含 RC4-11 理由注释）。测试 `main.rs:1895-1923`：对**同一 key** 注入 `fail_revoke_for`（`:1900-1903`）后仍断言 `preview_error` 为 Null（`:1920`）、current 不变（`:1921`）、旧 grant 可 resolve（`:1922`）——若移除短路该断言必红，判别力成立。执行证据 `combined-gate-r2fix-cargo.log:55` |
| **RC4-12** derived 预览无 GC | P4 | **降级接受（登记可接受）** | 现状核对无误：`render_preview.py:27` 每次 `preview-<uuid4>` 新键、`:39` `catalog.upsert`，失败路径只回收本次产物（`:40-44`），轮换/撤消失败后旧文件与旧 catalog 行不回收；`publish` 只读源（`:34` `open("rb")`）。契约未要求 GC，Handoff `:49` 登记为后续 Task 候选。**接受延后**；建议同步登记到 planning 候选清单 |
| **RC4-13** 冻结码判别力弱化 | P4 | **闭合** | 新用例 `WorkbenchPage.test.tsx:723-748`：fake 返回 `preview_error: "CORE_INTERNAL_PREVIEW_CODE"`（`:733`），断言 UI 仍含 `…预览不可用：PREVIEW_UNAVAILABLE`（`:742`）、**不含** Core 原值（`:743`）、rerender 入口仍在（`:744`）。UI 侧硬编码点 `WorkbenchPage.tsx:583-584,587`；旧用例保留（`:698-721`）。执行证据 `combined-gate-r2fix-frontend.log:20-23`（WorkbenchPage.test.tsx **24 tests**，全量 **118 passed**） |

**r1 汇总：13/13 有处置；11 项闭合、2 项（RC4-02 部分、RC4-04 附残留）以「降级接受 + 新 P4」口径收口；0 项未处置。**

---

## §2 组合 Gate 证据核对 + RC4-03 绑定方式裁决

**本轮 raw 集合**（`glob verification/M2-RC4-DOMAIN-COMMANDS/raw/*`，仅 6 份 r2fix 日志）：

| 日志 | 绑定 head | 关键数字（引用行） | 我核对的点 |
|---|---|---|---|
| `combined-gate-r2fix-focused.log` | `:3` `7c9d3a32` | `:4` 命令四目录；`:21` **408 passed**（2 warnings）；`:67` EXIT=0 | 与 Owner 轮 `core-focused-r1fix-1.log:3`（`58b3706d + r1-fix worktree changes`，408）等量；新增 9 测试（7 revision + 2 rerender）已计入 |
| `combined-gate-r2fix-cargo.log` | `:3` 同上 | `:18` running 54 tests；`:54` ignored=`perf_chunk_request_digest_cost`；`:74` **ok. 53 passed; 1 ignored**；`:76` EXIT=0；`:55,67` 两个新测试 ok | 非零 `#[ignore]` 已具名且为性能探针（`main.rs:1344-1351`）；另有 `:6-12` 一条既有 unused import 警告（`main.rs:816`，非本轮引入） |
| `combined-gate-r2fix-frontend.log` | `:3` 同上 | `:20` WorkbenchPage.test.tsx **24 tests**；`:22-23` 11 files / **118 passed**；`:27` EXIT=0 | 与 r1 期 117 tests 等量 +1（RC4-13 用例），`react-vitest-r1fix-1.log:4,21,24` 亦 24/118 自洽 |
| `combined-gate-r2fix-build.log` | `:3` 同上 | `:9` 50 modules；`:14` built；`:15` EXIT=0 | 与 React 轮 `react-build-r1fix-1.log:4,10` 一致 |
| `combined-gate-r2fix-full.log` | `:3` 同上 | `:4` 命令 `pytest tests -q -rs -rf --tb=short`；`:394-397` 3 failed / **1859 passed / 1 skipped**；`:398` EXIT=1 | 3 failed = `test_catalog`（`:394`）+ `ui_shell/repair13` 两例（`:395-396`）；与基线口径自洽（见下） |
| `combined-gate-r2fix-uishell-main-baseline.log` | `:3` `main@8c8e0eb4` | `:46,51` 同一文件 `test_repair13_import_entry.py:154,163` 同样失败；`:53-55` **2 failed, 3 passed**，EXIT=1 | 失败测试名与组合全量逐字相同 ⇒ 2 例属 main 既有环境敏感失败，非 RC-4 回归 |

**数字自洽复算（我独立算过）**：Owner 全量 1852+1sk+1failed（`raw/core-full-resume-1.log:408`）→ 组合唯一新增 pytest 用例 = 7（revision）+2（rerender）=9；两例 ui_shell 由 passed 转 failed（−2 passed/+2 failed）⇒ 1852+9−2 = **1859 passed**，1+2 = **3 failed**，总收集 1863，与 `:397` 完全一致。基线 300b4007 为 1841+7+1=1849（`integration/baseline-full-300b4007.log:50`）。

**RC4-03 裁决：该闭合方式可接受。** 理由：①r1 的条件是「现有日志绑定 78e4f24d/a1bd8acb/2f741407，未覆盖被审 head；须写明两 head 间仅 docs/evidence 差异，或在被审 head 复跑」。集成方选择的是**更强**的一条：在 r1 返修后的真实代码合并 head `7c9d3a32`（= e495910f + 7021d34c）**全量重跑**，而不是只补 diff 说明；②r2 的被审 head `1e6b58b9` 与 `7c9d3a32` 之间由 reflog 证明**恰有一个 commit**，其 message 与 Task:72-73 的内容（r1 报告入库、r1 返修 Gate 日志、RC4-05 追认）都属 docs/evidence 面；③故 `7c9d3a32` 上的 Gate 结果对 `1e6b58b9` 的代码树（src/tests/apps）成立。**残留（P4，见 N-5）**：Task:73 与 raw 都没有把「`1e6b58b9 = 7c9d3a32 + 仅 docs/evidence`」写成一句可核验记载，也无 `git diff --name-status 7c9d3a32..1e6b58b9` 日志；我无 shell，无法枚举该 commit 文件清单，故该等价性我按「reflog 单 commit + message + Task 记录」采纳，**不计为已实证**。

---

## §3 新 finding（r2 引入，按 P0–P4）

| ID | 级别 | 位置 | 触发与影响 | 证据 | 建议 |
|---|---|---|---|---|---|
| **N-1** | **P3**（范围/记账，需 Codex 权限，Reviewer 不能批准） | `apps/desktop/src-tauri/src/core_bridge.rs:318-321,337,438-447` | r1 返修在 **`src/core_bridge.rs`** 新增 `pub fail_revoke_for` 注入面，但 Task `allowed_paths`（`doc/tasks/M2-RC4-DOMAIN-COMMANDS.md:39`）只枚举 `src/library_bridge.rs`、`src/main.rs`、`build.rs`、`capabilities/**`、`permissions/**`，**未含 `core_bridge.rs`**。属 tracked 源码越界改动（与 RC4-05 同类，已如实披露）。功能影响为零：该结构体仅在 `#[cfg(test)] mod tests` 内使用（`main.rs:810-813`），生产路径不实例化、字段默认 `None` | 归属推断链：r1 在 `5954bb4b` 上记「`MockCoreChannel::revoke_resource` 恒 `Ok`，**无法注入失败**」（`doc/reviews/…-dsh-r1.md:29`）⇒ 当时无该注入点；Core Handoff r1 段自述「`core_bridge.rs` Mock 加 `fail_revoke_for` 注入口」（`doc/handoffs/…-core-58b3706d.md:43`）⇒ 改动属 r1 返修 commit（e495910f）。文件实存：`:321,337,438-447` | 由 Codex 按 RC4-05 同款在交付记录中追认，或把 `src/core_bridge.rs` 写入 allowed_paths（**不得**由 Owner/Reviewer 自行批准） |
| **N-2** | **P3**（证据完备性） | `doc/tasks/M2-RC4-DOMAIN-COMMANDS.md:73`；`verification/M2-RC4-DOMAIN-COMMANDS/raw/` | Task:73 断言两条 **git 侧事实**——「代码面 `diff --check` EXIT=0」与「`git diff 0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/` 为空」——但本轮 raw 只有 6 份 `combined-gate-r2fix-*`（focused/build/cargo/frontend/full/uishell-baseline），**无任何 diff 日志**；旧 `integration/combined-diffcheck-final.log` 只覆盖旧 head（且 r1 已指出其 range 面 EXIT=2）。同时 Task 断言的是 range `0fba6079..7c9d3a32`，而 Owner 轮日志头绑定的是 `58b3706d`，区间面缺少原始记录 | 目录清单（glob `raw/*` 共 48 项，r2fix 仅 6 项）；全目录 grep 无 `diff --check`/`name-status` 命中 | 集成收口 commit 内补三条原始日志：①`git diff --check <range>`（代码面，含 EXIT）；②`git diff --name-status 0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/`（期望空）；③`git diff --stat 37110749..58b3706d -- src/`（同时闭合 RC4-02 的残留口径） |
| **N-3** | P4 | `raw/combined-gate-r2fix-full.log:4` vs `:393-397` | 日志头声明命令含 `-rs`，但 `-q` 短摘要只列 3 条 `FAILED`，**无 `SKIPPED [1] …` 行**；本 Task 全 raw 目录内亦无任何 pytest `SKIPPED [n]` 摘要行（grep `^SKIPPED\|skipped` 的 19 处命中全是计数行或源码文本）。故那 1 条 skip 仍只在 Task:73 的散文中具名（其归属由 `tests/providers/test_registry_readiness.py:236-247` 与仓库历史佐证，实质可确认），但「命令头与原始输出不自洽」削弱本轮 Gate 日志的自证力 | `:4`、`:393-397`、`:397` | 重跑并保留 `SKIPPED [1] tests/providers/test_registry_readiness.py:237: …` 原行，或把命令头改为与实际执行一致 |
| **N-4** | P4 | `tests/core/test_core_service.py:149-152,234-237` | minor 注释链止于「`2 -> 3`」而断言为 **minor 4**（`:152,237`），缺「M2-RC4-DOMAIN-COMMANDS: `3 -> 4`」一行；被改名的两处测试（`test_core_detect.py:608`、`test_core_service_retype.py:136`）都有该行 ⇒ 属 RC4-09 同类残留的第五处，纯文案 | `:149-152`、`:234-237` | 各补一行 `# M2-RC4-DOMAIN-COMMANDS: 3 -> 4 (three domain commands)` |
| **N-5** | P4 | `doc/tasks/M2-RC4-DOMAIN-COMMANDS.md:73` | 未写出被审 head 与 Gate head 的等价关系（`1e6b58b9 = 7c9d3a32 + 仅 docs/evidence`），下游只读 Task 的人无法判定 Gate 覆盖被审 head；等价性目前只能由 `.git/worktrees/RC4-integration/logs/HEAD:15-16` 反推 | `logs/HEAD:15-16`；Task:73 全文无 `1e6b58b9` 字样 | Task:73 追加一句 + ②的 `git diff --name-status 7c9d3a32..1e6b58b9` 日志 |

**无 P0/P1/P2 新缺陷。** 另记两项观察（不计 finding）：① `MockCoreChannel` 非 `#[cfg(test)]` 门控但对生产不可达（见 N-1 影响面）；② `combined-gate-r2fix-cargo.log:6-12` 的 `unused import: CHUNK_SIZE`（`main.rs:816`）是既有告警，非本轮引入。

---

## §4 Architecture 与范围（r2 复核）

- **分层/安全面零回潮**：r1 已逐条核过的 DTO/typed error/fail-closed/锁与轮换/probe-AC1 零扩权，在本轮 head 未见反向改动；r1 返修引入的改动面（§1）全部是**加测试、加注入点（test-only）、加异常拆分、改注释/命名、卸载期版本递增**，无共享契约、ports、Schema、阈值 0.90、Legacy `src/ui` 触碰。
- **allowed_paths 判定**：r1 返修文件集合对照 Task `:36-43`——`tests/core/**`、`tests/rendering/**`（`:42` ✓）、`src/application/rendering/service.py`（`:36`，异常拆分属「RC-4 必要保护/错误修复」✓）、`src-tauri/src/main.rs`+`build.rs`（`:39` ✓）、`frontend/src/workbench/**`（`:40` ✓，含 `ViewerPanel.tsx`）；**唯一不符 = `src-tauri/src/core_bridge.rs`（N-1）**。
- **新契约面**：无新增 wire 字段/错误码；RC4-08 只是把同一物理条件从 `ARTIFACT_WRITE_FAILED` 归位到 `MISSING_REQUIRED_INPUT`（契约第 11 行），RC4-11 只是加宿主侧防御短路，均不改变冻结面。

---

## §5 Verification（我实际做的 / 明确 NOT_RUN）

**实际做的（纯静态：read/grep/glob，未运行任何命令、未改动任何文件）**
1. 逐项读 13 个 r1 finding 的处置点：`tests/core/test_rc4_revision_commands.py`（全文 324 行）、`tests/core/test_rc4_stdio_render_preview.py:190-249`（含墨水断言）、`src/application/rendering/service.py:100-299,352-386`、`tests/rendering/test_rerender.py:396-465,556-587`、`core_bridge.rs:312-351,432-456`、`main.rs:325-384,893-906,1344-1351,1845-1954`、`build.rs`（全文）、`WorkbenchPage.tsx:300-324,560-629`、`WorkbenchPage.test.tsx:690-749`、`ViewerPanel.tsx:1-30`、`tests/core/test_core_detect.py:604-616`、`test_core_service_retype.py:132-141`、`test_core_service.py:145-152,230-238`、`render_preview.py`（全文）、`core_service.py:840-914`。
2. 绑定链静态重建：`.git` 指针 → `.git/worktrees/RC4-integration/HEAD` → `.git/refs/heads/codex/rc4-integration` → `logs/HEAD`（merge/evidence 轨迹逐行核对）。
3. Gate 证据：6 份 `combined-gate-r2fix-*` 逐份读头+尾，独立复算 408 / 53+1ig / 118+build / 1859+1sk+3failed 与基线 1841+7+1 的差值自洽性。
4. 反例核对（r1 的关键判别）：`raw/core-stdio-preview-attempt-2.log` traceback 与当前测试文件逐行比对（行号/行数/fixture/断言），得出「测试演进不能解释翻转」。
5. 证据完备性反查：`raw/*` 全目录清单 + 全目录 grep `SKIPPED`/`diff --check`/`name-status`/`37110749..58b3706d`。

**明确 NOT_RUN / NOT_VERIFIED（不可记为通过）**
- 任何命令、测试、构建与 git 操作（本会话 shell 三次失败，与 r1 同）；
- `git diff --name-status/--stat` 的任何区间文件清单（N-1 的「仅该 commit 新增」为 r1 记录 + Handoff 自述的推断；N-2/RC4-02/N-5 的等价性与范围和统计）；
- 真实 WebView / 资产协议 / grant 生命周期（沿用 r1 与 React Handoff `:44` 的如实登记）；
- `1e6b58b9` 上任何独立复跑（本轮无任何日志绑定该 commit）。

---

## §6 结论

**verdict = `approved_with_conditions`（0×P0/P1/P2；r1 三项 blocking 全部闭合）。**

- **blocking 关闭**：RC4-01 由 `test_rc4_revision_commands.py` 的 wire/DTO/过期零写/双连接竞态/正整数/TOCTOU 七用例真实闭合（+`combined-gate-r2fix-focused.log:21` 408 passed）；RC4-03 由在 `7c9d3a32` 全量复跑 + reflog 单 commit 证据链闭合（方式可接受）；RC4-05 由 Task:72 的 Codex/集成方追认登记闭合。
- **非阻塞/ nit**：11/13 完全闭合；RC4-02 因 Handoff 因果说明与仓库内可读证据矛盾而**降级接受**（实质风险=断言判别力已由 `ink ≥ 400`（实测 1389）钉住），RC4-04/RC4-10/RC4-12 以「文字归因充分 + 登记延后」口径降级接受。
- **条件（均非功能缺陷，属证据/范围记账级）**：① **N-1**：`src/core_bridge.rs` 由 Codex 追认或写入 allowed_paths（Reviewer 无权批准范围）；② **N-2/RC4-02/N-5**：集成收口 commit 补三条 git 原始日志（`diff --check`、`0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/`、`37110749..58b3706d -- src/` 与 `7c9d3a32..1e6b58b9 --name-status`）；③ **N-3/N-4**：可选顺手修（Gate 日志 `SKIPPED` 原行 / `test_core_service.py` 注释补 `3 -> 4`）。
- **AC 层提示（供 Codex 判 done）**：r1 遗留的 **AC2** 证据面（history 摘要真实可追溯 + 事务内并发零写守卫）**现已满足**（RC4-01 闭合）；**AC5 仍未满足**——Integration Gate 证据已齐但 `integration_commit` 仍为 `null`（Task:15），merge 与 post-merge 回归未发生。本报告为静态审读，不构成实现批准，也不代表 Integration Gate 通过。

**推荐下一步（可直接转发）**
> 交 Codex（Integrator）：在 RC4-integration 集成收口前，①在 Task/交付记录中按 RC4-05 同款追认 `apps/desktop/src-tauri/src/core_bridge.rs`（`MockCoreChannel.fail_revoke_for`，test-only 注入口）属授权范围，或将其写入 `allowed_paths`；②在同一 commit 内入库四条 git 原始日志——`git diff --check 0fba6079..HEAD`（代码面，含 EXIT）、`git diff --name-status 0fba6079..7c9d3a32 -- src/ui/ tests/ui_shell/`（期望空）、`git diff --stat 37110749..58b3706d -- src/`（期望仅 `service.py`）、`git diff --name-status 7c9d3a32..1e6b58b9`（期望仅 docs/verification）；③在 Task:73 补一句「被审 head `1e6b58b9` = Gate head `7c9d3a32` + 仅 docs/evidence commit」；④可选：`combined-gate-r2fix-full.log` 补 `SKIPPED [1] tests/providers/test_registry_readiness.py:237: …` 原行，并给 `tests/core/test_core_service.py:149-152,234-237` 各补一行 `M2-RC4-DOMAIN-COMMANDS: 3 -> 4`。以上不含代码改动，落字后即可置 `done` 前跑 merge 与 post-merge 回归；若需终审，请另派非作者 Reviewer 复核该收口 commit（不要复用本报告对 `1e6b58b9` 之前 head 的结论）。
