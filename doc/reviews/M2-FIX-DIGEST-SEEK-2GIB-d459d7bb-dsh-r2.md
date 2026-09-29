approved_with_conditions

**评审方式声明（与 r1 同）**：本环境 `pwsh` 全部不可用（`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`，实测 3 次），**未复跑任何 cargo/git**。以下结论全部来自 read/glob/grep + `.git` 明文取证，并逐条标注「我独立核验」与「取自作者入库日志」。

**我独立完成的取证**：`.git/worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode/logs/HEAD`（reflog 链）、`HEAD`、`.git/refs/heads/agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`（=`d459d7bb79d1daad8a940e1c06a6037f76924f3d`，即被审 tip）、worktree `index`（二进制，用于确认 r2 日志已入库）、**mtime 升序 glob 全树序列（8932 路径）**。

---

## 1. 被审对象身份（独立核验）

| 项 | 核验结果 | 证据 |
|---|---|---|
| r2 commit / parent | `d459d7bb` commit msg = `fix(...): address DSH r1 conditions C1/C2 + P3 doc fixes`，其前一条 reflog 记录为 `ea07b4b1` → **parent=`ea07b4b1` 成立** | `logs/HEAD:7` |
| 分支 ref = 被审 tip | `refs/heads/agent/zcode/M2-FIX-DIGEST-SEEK-2GIB` = `d459d7bb` | refs 文件 1 行 |
| r2 日志已入库 | `index` 内命中 `r2-cargo-test-full.log`、`r2-scope-audit.log`（01:31 快照时为 `??` 未跟踪 → 必由 d459d7bb 收编） | `.git/worktrees/**/index` grep |
| r2 代码改动早于 r2 日志与文档 | mtime 升序序列：`resource_protocol.rs`(#8873) → target 编译产物(#8874-8893) → r2 两条日志(#8894/8895) → Task/Handoff(#8896/8897) | glob 全树 #8820-8932 |
| r2 日志与当前测试清单自洽 | r2 日志 `running 45 tests / 44 passed / 1 ignored`；我逐文件数 `#[test]`：resource_protocol 6 + main 31 + library 5 + ac1 3 = **45** | r2 log:23/70；grep `#[test]` |
| r1→r2 增量 = +2 测 | g1（r1）= `running 43 tests / 42 passed / 1 ignored` | `g1:22/67` |

---

## 2. 条件闭合逐项表

| 条件 | 判定 | 依据与我的独立核验 |
|---|---|---|
| **r1-C1/P2-1** 64 位高位判别测试 | **closed** | `resource_protocol.rs:629-641` 真实落盘：`SetFilePointerEx(opened.handle, 0x1_0000_0000i64, &mut landed, FILE_BEGIN)`，`assert!(ok != 0)` + `assert_eq!(landed, target)`。判别力**成立**：①该断言在旧 `SetFilePointer(i32, high=null)` 绑定下根本无法通过（高 32 位写不进 `LARGE_INTEGER`）；②回退旧 API 会使 FFI 声明自身消失、`read_through` 编译失败；③越 EOF seek 在 Windows 是合法操作（若被拒则 `ok==0`）。r2 日志 `:45` 该用例 `ok`。**残余限制**（见 P3-10 说明）：它钉的是 FFI 位宽，不是 `read_through` 调用点——因为 `:341` 的 guard 使 ≥2^31 永远到不了 FFI，调用点只能静态核对 |
| **r1-C2/P2-2** seek 失败分支测试 | **closed（执行覆盖）／判别力不成立 → 见新条件 C4** | `:646-655` 真实落盘，`read_through(null_mut(), 0, 4)`：guard 放行（0 ≤ MAX）→ **必然**执行 `:353` 的 seek 调用 → `:354` 失败分支返回。分支确实被触发。但断言仅 `starts_with("OPEN_FAILED")`：**若把 `:354` 的 `ok == 0 \|\| landed != …` 整行删掉**，裸 null 句柄随后在 `ReadFile`（`:368-379`）同样返回 `OPEN_FAILED`，该用例**照样绿** → 对「seek 失败检查存在」零判别力 |
| **r1-C3/P2-3**（Owner 侧）交付 commit 范围审计 | **closed** | `raw/r2-scope-audit.log:4-14`：`--name-status d1a4b406..ea07b4b1` 仅 `resource_protocol.rs`+Task+Handoff+`verification/**`，`--check` `# EXIT=0`（`:34`），与 r1 要求一致 |
| **r1-C3**（集成方侧，覆盖 r2 tip） | **open** | 无任何入库证据覆盖 `ea07b4b1..d459d7bb`（`raw/` 8 份日志已逐一读完）；见 P3-11 |
| **P3-1** frontmatter base | **closed（本轮范围）** | Task `:11` = `d1a4b4067a2222732867d16fc42ee0b6e4bfa228`，与 Handoff `:5` 一致；reflog 证实 claim 自该 base 切出。**但** `REBASELINE_PLAN:76`、`STATUS:14`、`tasks/README:7` 仍写 `base=915cea99` → P3-14（不在 Owner 允许路径） |
| **P3-2** f05 空引用 | **closed** | Task `:45` 改为 `f02_equal_size_rewrite_after_first_verify_rejected`/`f02_equal_size_rewrite_stability_loop`/`full_chunk_serving_matches_bytes_and_digest_check`/`chunk_offset_beyond_size_rejected`；Task 文件内 `f05` 零命中（仅 Handoff `:42` 作为「已修说明」提及，属正常） |
| **P3-3** Handoff 模板 | **closed** | `delivery_head` 字段（Handoff `:6`）、验证证据**五列表**含「环境与被测 commit」(`:63-70`)、「接收方式」(`:76-92`)、**必填**「下一任务建议」(`:94-100`)、「风险与遗留」(`:102-117`)、「未运行项」(`:72-74`) 齐备；残余见 P3-13 |
| **P3-4** 日志 EXIT 口径 | **closed（声明式）** | 两条 r2 日志均带 `# shell:` 头 + 末行 `# EXIT=0`（r2 log `:2/:72`、scope `:2/:34`）；s1/s2 的历史格式在 Handoff `:112-113` 明确登记 |
| **P3-5** `last_error` 拼接 | **closed（wire 未被破坏）** | `:358-361` `OPEN_FAILED:seek_to=… landed_at=… last_error={error}`；`typed_error:112` `split(':').next()` → wire code 仍 `OPEN_FAILED`，`status_for:107` 默认 → **400 与 r2 前完全一致**；我另行 grep 全仓消费者：resource_protocol 内除 `typed_error` 无其他 `.code` 解析点，main.rs 的 `map_err(\|e\| e.code)` 不经过 `read_through`；`HttpResponse::error` 只把 code 放进 body → **后缀不上 wire、无新泄漏**。文档漂移见 P3-12 |
| **P3-6** 计数表述 | **closed** | Task `:32` 改「44 passed（含新增 6）/1 ignored（基线既有）… ；r1 时点 42 passed（含新增 4），基线 39+1」。算术独立复核：基线 39+1=40 → r1 43 total（g1 实读 42+1）→ r2 45 total（r2 实读 44+1）✓ |
| **P3-7** at-limit 注释 | **closed** | `:666-671` 明写「`== MAX` 为 INSIDE the limit… this exact call is unreachable in production」，与 `:341` 的 `>`、`:548` 的 `offset < size` 一致 |
| **P3-8** release 记录 | **open（集成方）** | `verification/M2-FIX-DIGEST-SEEK-2GIB/` 仍只有 `raw/` 8 份日志；Handoff `:114-115` 已声明归属集成侧 |
| **P3-9** c0 基线方法不可自证 | **closed（口径已注明）** | `c0-clippy-baseline.log:1` 补「resource_protocol.rs stashed back to pre-fix」，Handoff `:69` 五列表写「基线经 `git stash` 回退…复测」；仍无 stash 命令回显，属可接受口径 |

**关于 C1 的残余限制（不构成新条件）**：C1 只能钉绑定/宽位，无法钉 `read_through` 的调用点，这是 guard 带来的**固有可观测性上限**（≥2^31 在生产与测试都不可达）。静态面已足以闭合：全仓 `SetFilePointerEx` 唯一调用点 `:353`、旧声明已删、`landed != offset as i64` 在每次界内调用都校验实参与落点。

---

## 3. 新问题（P 级）

**P0：无。P1：无。P2：无（r2 未引入新缺陷）。**

| ID | 位置 | 问题 | 建议 |
|---|---|---|---|
| **P3-10（= 新条件 C4 的依据）** | `resource_protocol.rs:646-655`；Handoff `:67` 结果列 | 两处证据层缺陷：①断言只查前缀，删掉 `:354` 的 seek 失败检查后仍绿（见上表），故「seek 失败分支被**验证**」这一强表述无判别性 artefact（Q-009 同类问题）；②同一行的「错误串含 `last_error=` 原始码」在 `r2-cargo-test-full.log` 中**不可能被看到**（该用例未 `--nocapture`，日志只有 `ok` 一行），纯静态阅读结论 | 用例补一行 `assert!(error.code.contains("landed_at=") && error.code.contains("last_error="), "{}", error.code)`（seek 分支专属标记 + 让 P3-5 由测试输出支撑；null 句柄下 `last_error=6` 稳定），复跑 `cargo test` 并追加带 `# EXIT=` 的日志 |
| **P3-11** | `raw/r2-scope-audit.log:15-32`；glob 全树 #8898-8932 | 范围审计**未覆盖 r2 交付 commit 自身**。另：r2 快照已显示 14 个 `gen/**`+`permissions/**` 文件处于 ` M`；我按 mtime 升序看到这批文件（#8900-8913，含 `gen/schemas/*.json`）**晚于** Task/Handoff（#8896/8897）被写入 → 提交前后还存在一次构建（与派发说明「集成方已复跑 cargo test」相符），故「这批构建改动是否进入 d459d7bb」我**无法在只读轮核实** | 集成方执行：`git diff --name-status ea07b4b1..d459d7bb`（应仅 `resource_protocol.rs`+Task+Handoff+`verification/**`）、`git status --porcelain -- apps/desktop/src-tauri/gen apps/desktop/src-tauri/permissions`（应为空或如实声明为环境产物不入库）；并入 C3 的集成记录 |
| **P3-12** | Task `:30` vs 代码 `:358-361` | AC2 括注仍写 seek 失败串为 `OPEN_FAILED:seek_to=<n> landed_at=<n>`，**缺 `last_error=<n>`**，与同一 commit 引入的实现不一致（Handoff `:38-40` 是对的） | Task AC2 括注补 `last_error=<n>`，或显式注明「后缀仅供诊断，wire 只取 code」 |
| **P3-13** | Handoff `:6`；`doc/reviews/` | `delivery_head` 的值是 `git log --grep …`/「本 fix commit」描述而非 hash（自引用所致，reflog 可解）；且 r1/r2 评审报告都未入库 `doc/reviews/`（对照 `doc/reviews/M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF-5d7cff11-dsh-r1.md` 先例） | 集成 commit 回填 hash；由集成方（`doc/reviews/**` 不在 Owner 允许路径）归档 r1/r2 报告 |
| **P3-14** | `REBASELINE_PLAN.md:76`、`STATUS.md:14`、`doc/tasks/README.md:7` | 三处仍 `base=915cea99`、状态 `ready`，与 Task/Handoff 的 `d1a4b406`、`in_review` 不一致（Codex/集成方路径） | 集成时一并修正 |

备注（不单列 P 级）：`c1-clippy-deny-warnings.log` 为 r1 期产物、未随 r2 重跑；因记录命令是 `cargo clippy --bin m2rc1-desktop`（不编译 `cfg(test)`），而 r2 只动 `read_through` 实现与 `#[cfg(test)]`，其「6 error 无新增」结论对 r2 仍成立（`c1:227` 命中 `resource_protocol.rs:136`，与 `c0` 同行号，独立复证 `:136` 未位移）。建议集成记录登记该口径。

---

## 4. r2 是否引入新缺陷（复核点 4）

**未发现**。逐项：`read_through` 改动仅 guard（`:341-345`）+ 64 位 seek 与落点校验（`:351-363`），`offset as i64` 在 guard 之后无回绕；`:364-386` 读取循环、`:401-434` 单遍 digest+capture、`:446-506` verify_and_serve、`:510-556` 请求流与 `typed_error` 均未见改动（`c1` 与 `c0` 的 `:136` 命中行号一致，佐证 230 行前零位移）；新增测试只用 `#[cfg(test)]` 内 `win32::SetFilePointerEx`/`read_through`，无新依赖、无新 FFI、无 wire/状态码变化；`Cargo.toml/lock` 未动（`raw/r2-scope-audit.log` 与 s1 `LOCK_CLEAN=1`）；句柄/TempDir 释放顺序（`:584-593`）正确，无泄漏。

---

## 5. 结论与推荐下一步

代码层 r2 是**严格改进**，r1 的 C1 判别性 artefact 已真实获得，P3-1/2/3/4/5/6/7/9 均落实，C3 的 Owner 侧证据补齐；未发现 P0/P1/P2。判 **approved_with_conditions**，唯一 Owner 侧动作为 **C4（P3-10）**：一行断言强化 + 复跑日志，属证据判别力问题，不动实现语义、不影响 Codex 对代码本身的采信。

**推荐下一步**：Owner ZCode 关闭 C4（同一 worktree/branch，`d459d7bb` 之上追加一个小 fix commit），随后由 Codex 集成。

可直接转发给 ZCode 的指令：

> 你是 ZCode（M2-FIX-DIGEST-SEEK-2GIB 作者，worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-DIGEST-SEEK-2GIB-zcode`，branch=`agent/zcode/M2-FIX-DIGEST-SEEK-2GIB`，被审 tip=`d459d7bb`）。DSH r2 结论 `approved_with_conditions`（报告对象 HEAD=`d459d7bb`）。请在允许路径内关闭 C4=P3-10：(1) 在 `apps/desktop/src-tauri/src/resource_protocol.rs` 的 `read_through_invalid_handle_fails_closed_with_open_failed`（`:646-655`）把断言从仅前缀改为同时校验 seek 分支专属标记，例如 `assert!(error.code.contains("landed_at=") && error.code.contains("last_error="), "{}", error.code)`——理由：现状下把 `:354` 的 `ok == 0 || landed != offset as i64` 删掉，裸 null 句柄会在 `ReadFile`（`:378`）同样返回 `OPEN_FAILED`，用例仍绿，故对「seek 失败检查存在」无判别力；同时该断言可让 Handoff `:67`「错误串含 last_error」由测试输出支撑（该日志未 `--nocapture`，现无可见证据）。(2) 同步 Task `:30` AC2 括注补 `last_error=<n>`，并如实区分「seeki 分支执行覆盖」与「判别性 artefact」口径。(3) 复跑 `cargo test`（期望 44 passed/1 ignored，EXIT=0），追加带 `# shell:` 头与 `# EXIT=` 尾行的 `verification/M2-FIX-DIGEST-SEEK-2GIB/raw/` 日志，更新 Task/Handoff 的 r2→r3 轨迹。禁止改 wire 语义、`gen/**`、`permissions/**`、`Cargo.toml/lock`。完成后交 Codex 集成。

集成方（Codex）在集成 commit 需一并收口：`git diff --name-status ea07b4b1..d459d7bb`（并复核 14 个 `gen/**`+`permissions/**` 构建改动**未入库**）、`integration_commit` 回填、r1/r2 报告归档 `doc/reviews/`、`release-<base>.md`、`REBASELINE_PLAN:76`/`STATUS:14`/`tasks/README:7` 的 `base`/状态修正。若需一个独立下一 Task，**clippy 6 个基线既有 error 清理**是唯一登记在案的候选，但需由 Codex 显式释放后才可实施（不在本 Task 范围，我无权释放）。
