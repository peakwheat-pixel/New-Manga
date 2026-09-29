## approved_with_conditions

**评审对象**：worktree `G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`，分支 `agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`，HEAD=`ea07b4b1`；delivery=`b4baf7c2`；实现 head=`9fa92475`；base=`d1a4b406`。
**评审方式**：**只读静态评审 + 只读取证**。我的沙箱 `pwsh` 全部不可用（`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），**未能复跑任何 cargo/git 命令**；因此所有 `cargo`/`clippy`/`git` 的 EXIT 与输出均取自入库日志（作者自述证据），我另行做了**可独立核验的交叉取证**：`.git/worktrees/**/logs/HEAD` reflog、主工作区 base 版源码逐区对照、日志内部算术与行号一致性核算。

---

## P0

无。

## P1

无。

## P2

### P2-1｜AC1 的「大 offset（≥2^31）语义正确」缺少判别性 artefact，却记为 PASS
- **文件/位置**：`apps/desktop/src-tauri/src/resource_protocol.rs:341-345`（前置 guard）、`:609-617`（`read_through_rejects_offset_beyond_i32_seek_range`）；Task `:28`、Handoff `:38`。
- **问题**：`2^31 = 2 GiB > MAX_RESOURCE_BYTES = 256 MiB`，**所有 ≥2^31 的 offset 都被新增的前置 guard 短路**，永远到不了 `SetFilePointerEx`。因此 `read_through_rejects_offset_beyond_i32_seek_range` 判别的是「guard 存在」而非「seek 位宽 64 位」：只加 guard、保留旧的 `SetFilePointer(offset as i32)`，该测试同样会绿。红证 `r1-red-large-offset.log:26` 的 `Ok([48,49,50,51])` 也正是 guard 缺失的表现，不是 FFI 位宽被证明。按本仓库证据纪律（`doc/templates/REVIEW.md:51` Q-009「判别力 artefact 缺失即记 `NOT_RUN`，不得以散文或 `N passed` 代替」），AC1 的该子句当前应为 **NOT_RUN**，而 Task/Handoff 整体记 PASS。
- **补充事实**：低 32 位路径**确实**被覆盖——`:353-354` 的 `landed != offset as i64` 每次界内调用都断言了 `SetFilePointerEx` 的实参与落点，故「FFI 参数错序/错位」类缺陷会被界内测试捕获；真正未覆盖的只有 **LARGE_INTEGER 高 32 位**。
- **建议**：在现有 `#[cfg(test)] mod tests` 内补一个直接判别用例（约 6 行）：
  `let (dir, opened) = open_fixture(b"..."); let mut landed = 0i64; let ok = unsafe { win32::SetFilePointerEx(opened.handle, 0x1_0000_0000, &mut landed, FILE_BEGIN) }; assert!(ok != 0 && landed == 0x1_0000_0000);`（Windows 允许 seek 越过 EOF）。若因「不可达即不测」而决定不加，则必须在 Task/Handoff 把 AC1 拆成「FFI 结构 PASS（静态核对）+ ≥2^31 行为 NOT_RUN」如实落字。

### P2-2｜AC2 明确列出的「seek 失败/落点不符」分支零测试
- **文件/位置**：`resource_protocol.rs:351-359`（新分支），`resource_protocol.rs:576-636`（测试模块无对应用例）。
- **问题**：新分支 `OPEN_FAILED:seek_to=… landed_at=…` 完全未被任何测试触发；交付的 4 个测试只覆盖 guard 两个分支与两个界内回归锚。我核对了 Task `:30`（AC3 只要求「大 offset fail-closed + 常规路径回归」），故**不构成 AC 违约**，但「新 fail-closed 分支被验证」在证据层是空白。
- **建议**：补一个用例传无效句柄（如 `std::ptr::null_mut()`）调 `read_through(handle, 0, 4)`，断言 `error.code.starts_with("OPEN_FAILED")`（预期 SetFilePointerEx 失败 → `ok == 0` → `landed_at=-1`）；成本极低且不依赖文件系统行为。

### P2-3｜交付/文档 commit 未被范围审计覆盖（b4baf7c2、ea07b4b1）
- **文件/位置**：`verification/M2-FIX-DIGEST-SEEK-2GIB/raw/s2-delivery-range-audit.log:3-12`。
- **问题**：s2 的 `git diff --name-status d1a4b406..9fa92475` 只覆盖到实现 head。reflog（`G:/CODEX/New Manga/.git/worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode/logs/HEAD:5-6`）证明其后还有 `b4baf7c2`（Task 回填 + Handoff）与 `ea07b4b1`（补 s2 日志）。这两个 commit 的文件集合**没有任何入库证据**审计（提交内容与 Task/Handoff 所述一致是我从工作区读取推断的）。
- **建议**：补一条 `git diff --name-status d1a4b406..ea07b4b1`（或 `b4baf7c2..ea07b4b1`）日志入库，把 AC5 的审计范围钉到最终 tip。

## P3

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| P3-1 | Task `:11` vs Handoff `:5`、reflog `logs/HEAD:655-656` | Task frontmatter `base_commit: 915cea99`，但实际 release/claim base 是 `d1a4b406`（reflog 显示 `915cea99 → d1a4b406`，`d1a4b406` 才是 "release M2-FIX-DIGEST-SEEK-2GIB" 的 commit）。frontmatter 与正文 `:71`「claim 298aa24b（base d1a4b406）」自相矛盾，容易被集成方按错 base 复算 | 把 frontmatter 改 `d1a4b406…`，或注明「release commit = d1a4b406（parent 915cea99）」 |
| P3-2 | Task `:44`、`:60` | 禁止/风险条款引用「f02/f05 断言语义」，但**本树不存在 f05 测试**（`src/**` 全量 grep 无命中，仅 f01/f02 存在）；该禁改项是空引用 | 改为实际测试名（`f02_equal_size_rewrite_after_first_verify_rejected`、`full_chunk_serving_matches_bytes_and_digest_check`、`chunk_offset_beyond_size_rejected` 等） |
| P3-3 | Handoff frontmatter `:6-7` 与正文章节 | 未按 `doc/templates/HANDOFF.md` 字段：用 `implementation_head`/散文 `delivery_commit` 而非 `delivery_head`；缺模板的「验证证据」五列表（逐行含「环境与被测 commit」）、「接收方式」章节、以及**必填**的「下一任务建议」章节（§5.1 的下一任务建议义务在 `done`/切片关闭时由交付者承担，当前 `in_review` 可延后给集成方，但字段应对齐） | 对齐模板字段与章节；「下一任务建议」可留给集成 commit 补齐 |
| P3-4 | `raw/s1-scope-audit.log:10`、`raw/s2-…:12` | 与 r1/g1/c0/c1 不同，s1/s2 无统一 `# EXIT=` 尾行（用内联 `DIFF_CHECK_EXIT=0`），AC4「日志带 EXIT 码」在执行口径上成立、格式上不统一 | 统一为末行 `# EXIT=n`；或在 Task 中明确 s1/s2 用内联 EXIT 口径 |
| P3-5 | `resource_protocol.rs:355-357` | seek 失败复用 `OPEN_FAILED`（`status_for` 落到默认 **400**），但 seek 失败本质是宿主/IO 侧错误，400 语义偏「客户端错误」；且错误串未带 `GetLastError()`（对比 `:322` 的 `open_once` 会读 last_error），排障信息弱 | 至少把 `win32::last_error()` 拼进 code（`:355` 的 `landed_at` 旁），或后续统一把 IO 类失败映射 5xx |
| P3-6 | Task `:31` | 「（42 passed/1 ignored 基线既有，EXIT=0）」措辞易误读为 42 passed 是基线；实际基线 39 passed + 1 ignored，修复后 39+4=43 total → 42 passed + 1 ignored（红证 `:42` 的「39 filtered out」可反推）。`:52`/`:68` 的表述是正确的 | 删去「基线既有」或改「42 passed（含新增 4）/1 ignored（基线既有）」 |
| P3-7 | `resource_protocol.rs:631-635` | `read_through_at_limit_offset_yields_empty_tail` 把 `offset == MAX_RESOURCE_BYTES` 的**静默空读**固化为「期望语义」。与 AC 字面（`>` 为越界）一致、且生产不可达（调用链恒 `offset < size ≤ MAX`，见 `:406-408`），但与本次修复「不再静默空读」的叙事边界相冲 | 在注释/AC 中明确「`== MAX` 为界内且不可达」，避免后人误读为边界防御缺口 |
| P3-8 | `verification/M2-FIX-DIGEST-SEEK-2GIB/` | 目录内仅 `raw/` 6 份日志；同类 Task 惯例还有 `verification-results.md`、`release-<hash>.md`/`checkpoint.md`（见 `verification/M2-FIX-*-*`）。§5 允许「Handoff 完整承载时复用」，故不阻塞 | release 记录属编排侧产物；建议集成 commit 时补/声明 |
| P3-9 | `raw/c0-clippy-baseline.log:1` | 基线 clippy 以「stash 回退 resource_protocol.rs」测得，日志内**没有 stash/checkout 命令回显**，方法与状态不可自证（结论 6 error 集合与 c1 一致，我逐条比对确认无新增） | 日志头补命令回显，或在 Task 中注明该方法口径 |

## 我认为通过静态核对、无需修改的部分（供集成方记录）

- **B｜FFI 正确性**：`extern "system"` = x64 下 C 约定，与 `BOOL SetFilePointerEx(HANDLE, LARGE_INTEGER, PLARGE_INTEGER, DWORD)` 原型一致；`BOOL→i32`、`LARGE_INTEGER→i64`（8 字节值类型，x64 传参与 `__int64`/`LARGE_INTEGER` 同槽）、`PLARGE_INTEGER→*mut i64`、`dwMoveMethod: u32` 均正确；`FILE_BEGIN=0` 语义为「距文件头绝对位置」，故 `landed == offset` 是合法不变量。`offset as i64` 在 guard 之后无回绕；`landed` 初值 `-1` 在失败时不会被 API 覆写，错误串如实反映。旧 32 位声明已删，全仓 grep 仅剩注释与 `:353` 唯一调用点（AC1「全仓唯一调用点」成立）。
- **C｜fail-closed 与 wire**：`CoreError::new(&format!(...))` 与既有 `CORE_SPAWN_FAILED:{error}`（`core_bridge.rs:142,158`）风格一致；`typed_error`（`resource_protocol.rs:112`）`split(':').next()` 保证 wire code 仍为 `RESOURCE_TOO_LARGE`（→ 403，`status_for:104`）/`OPEN_FAILED`（→ 400，默认），与既有一致，**后缀不外泄、wire 语义未变**——作者的评估如实。
- **D｜行为不变性（我自己做了行级重建，不依赖作者 diffstat）**：以主工作区 base 版（`G:/CODEX/New Manga/apps/desktop/src-tauri/src/resource_protocol.rs`，确认 `:332` 为旧 `SetFilePointer(offset as i32, null_mut(), FILE_BEGIN)`，548 行）逐区对照工作区版（636 行）：`1..228` 无位移（`:136` clippy 命中行号在 c0/c1 相同），FFI 块 `+5`，`read_through` `+21`，新增 `mod tests` `+62`，**5+21+62 = 88 = 548→636**，与 s1 的 `+93/-5` 精确吻合；`verify_and_serve`/`stream_digest_and_capture`/`handle_m2res_request`/`parse_request`/`status_for`/`typed_error` 与 base 逐行同构（整体 +26 位移）。故 issue 校验、digest 逻辑、256 MiB 内 seek 语义均未被误改；guard 在生产调用链上不可达（`served < expected_size ≤ MAX`）。f02 两条 + f01 两条 + `full_chunk_serving…` 在 g1 中全绿。
- **E｜测试真实判别性**：`MAX_RESOURCE_BYTES+1` 用例在修复前返回 `Ok([])`、`2^32` 用例返回文件头 `[48,49,50,51]`，与旧代码 `as i32` 截断（`2^32→0`；`[2^31,2^32)` 为负偏移 → `ERROR_NEGATIVE_SEEK` 被忽略、指针停留 0）的理论值完全一致，红证**真实且对应缺陷**；`r1` 的「39 filtered out」与 g1 的 43 total 反推出基线 39 测，算术自洽。
- **F｜范围纪律**：s2 `--name-status` 仅 `resource_protocol.rs` + Task + `verification/**`；无 `Cargo.toml`/`Cargo.lock` 变更（`LOCK_CLEAN=1`），无新依赖（i64 内联）。`gen/`、`permissions/` **未在 .gitignore 中**（`.gitignore` 仅 `dist/`、`frontend/node_modules/`、`frontend/dist/`）→ 属 tracked，s1 的 `git status --porcelain` 未列出它们，即无未提交改动；我抽样比对 `permissions/autogenerated/core_ping.toml` 主工作区/工作区一致。`src/**`（Python）、`frontend/**`、`packaging/**` 零命中。
- **提交链**：reflog 与交付说明一致（`d1a4b406 → 298aa24b claim → 9fa92475 实现 → b4baf7c2 交付 → ea07b4b1 补 s2 日志`），分支 ref = `ea07b4b1`。
- **G｜证据纪律**：6 份日志均带 `# shell: cwd=… cmd=…` 头与日期；r1/g1/c0/c1 带 `# EXIT=` 尾行（101/0/101/101）；红绿对同一命令口径一致。

## 缺失证据（明确清单）

1. **64 位 seek 高 32 位的判别性 artefact** → 该子句应按 Q-009 记 `NOT_RUN`（P2-1）。
2. **seek 失败/落点不符分支的测试证据** → 无（P2-2）。
3. **`b4baf7c2`/`ea07b4b1` 的范围审计** → 无（P2-3）。
4. **release 记录**（`verification/<Task>/release-d1a4b406.md`）→ 缺失（P3-8，编排/集成侧）。
5. **产品级端到端套件**（`tests/m2_acceptance`、vitest）→ 未复跑；AC4 只要求 `cargo test`，且 Rust 层 `real_core_sidecar_round_trip`/`full_chunk_serving…` 已覆盖服务路径，故不判缺失，仅记录。
6. **无法由我复核的项**：所有 `cargo`/`git` 实跑（沙箱 `pwsh` 不可用）；上述 EXIT 码与 diff 输出均为**作者入库日志自述**，我仅核验了其格式、内部算术与结构一致性。
7. **未复核的断言**：Task/Handoff 对 clippy 余留项「均基线既有」——我逐条比对 c0/c1 六条 error 的集合与位置**完全一致**，此项成立。

## AC 逐项裁定

| AC | 裁定 | 依据 |
|---|---|---|
| **AC1** 64 位 seek | **PASS（结构）+ 条件性 NOT_RUN（≥2^31 行为）** | 静态：旧声明删除、唯一调用点改 `SetFilePointerEx`、`offset as i64` 无截断、原型/约定/FILE_BEGIN 语义正确、返回值+落点双判（`:234-239`、`:351-359`）。动态：≥2^31 全部被 guard 短路，无判别性测试（P2-1）。不判 FAIL，但 Task/Handoff 需补字或补测 |
| **AC2** fail-closed 纵深 | **PASS** | `:341-345` / `:351-359` 与 AC 指定字符串逐字一致，均 typed `CoreError`；`typed_error` 冒号截断已验证（`:112`），wire code/status 与既有一致。seek 失败分支未测（P2-2），AC3 未要求故不影响判定 |
| **AC3** 测试 | **PASS** | `:594-635` 4 测；红证 2 failed（EXIT=101）、绿证 43 total 全绿（EXIT=0）；界内行为回归锚成立 |
| **AC4** 回归与证据 | **PASS（附 P3-4）** | `g1` 42 passed/0 failed/1 ignored EXIT=0；`c0` vs `c1` 6 error 集合一致无新增；日志带 shell 头与 EXIT（s1/s2 格式不统一）。**我未复跑**，数字取自入库日志并核对内部一致性 |
| **AC5** 范围纪律 | **PASS（附 P2-3）** | s1/s2：仅允许路径、`diff --check` EXIT=0、`Cargo.lock` 无变化；我以 base 版行级重建独立复算 `+5/+21/+62=+88` 与 `+93/-5` 吻合、`main.rs` 行号不变、`gen/`+`permissions/` tracked 且 s1 状态干净。范围审计未覆盖交付/文档 commit（P2-3） |
| 无 NOT_RUN 记为 PASS？ | **部分问题（P2-1）** | 唯一以 PASS 记录但实际无执行判别力的是 AC1 的「大 offset ≥2^31 语义正确」子句 |

## 结论与推荐下一步

代码层**未发现 P0/P1**；修复方向正确、FFI 原型与 fail-closed 构造经我独立静态核验无误，256 MiB 内行为可证不变，范围纪律与红绿证据真实（红证与 i32 截断理论值逐字节吻合）。判 `approved_with_conditions`：集成前建议由 Owner 以**同一允许路径内的小修 commit** 关闭 **C1 = P2-1（补 64 位高 32 位判别测试，或在 Task/Handoff 把该子句如实改记 NOT_RUN）**、**C2 = P2-2（补 seek 失败分支测试）**，并由集成方补 **C3 = P2-3（`d1a4b406..ea07b4b1` 范围审计日志）**；P3 项可随集成 commit 一并落字。

**基于当前仓库状态的推荐下一步**：Owner（ZCode，worktree/branch 不变）在 `apps/desktop/src-tauri/src/resource_protocol.rs` 的 `#[cfg(test)] mod tests` 追加上述两个用例（不新增依赖、不动 wire），复跑 `cargo test`（期望 44 passed/1 ignored，EXIT=0）并在 `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/` 追加带 `# shell:` 头与 `# EXIT=` 尾行的日志，然后生成新的 handoff/head 交付复审；随后由 Codex（代行）在集成时补 `d1a4b406..<新tip>` 的 `git diff --name-status` 与 `--check` 证据、回填 `integration_commit` 并按需更新 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（这两份不在本 Task 允许路径内，须由集成方改）。
