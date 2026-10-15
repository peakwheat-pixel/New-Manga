已完成全部只读审查。以下为可归档 Review 正文（未写入任何文件；pwsh/Git 在本 worktree 因 DSH 沙箱 ACL 授权失败不可用，故 Git/hash 一律 object_binding=NOT_VERIFIED）。

```yaml
---
task_id: PROJECT-ROADMAP-RELEASE
title: 完整产品路线恢复、Gate裁决与下一实施切片释放
reviewer: DeepSeek Harness（非作者，独立只读）
author: Codex（Owner / Integrator）
base_commit: 0dcc94f3591b2837c91a6b3aa5b6dcce6c23aa64
reviewed_head: 657096b41042d7cfbbbee76baa856f96c28de24a
review_worktree: G:/CODEX/New Manga.workspace/worktrees/PROJECT-ROADMAP-RELEASE-REVIEW
date: 2026-10-15
mode: 只读；禁止修改文件；未执行 Build/Cargo/GUI/模型/sidecar/安装/OS/registry/ACL 操作
object_binding: NOT_VERIFIED
architecture_axis: PASS（文本层；附 P2）
verification_axis: PARTIAL / NOT_RUN
decision: APPROVED
decision_scope: 仅覆盖 AC1–AC3 的文本内容与 P22-REBASE-1 范围可接受性；不覆盖 AC4（未完成），不得以本 Review 作为 AC4 完成或任何测试 PASS 的证据
---
```

# PROJECT-ROADMAP-RELEASE 独立 Review

## 0. 审查对象、方法与能力边界

### 0.1 审查对象
- 固定 Review 对象 `reviewed_head=657096b4`，`base_commit=0dcc94f3`；任务文档 `doc/tasks/PROJECT-ROADMAP-RELEASE.md`、`doc/tasks/P22-REBASE-1.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/README.md`，证据目录 `verification/PROJECT-ROADMAP-RELEASE/**`（16 个文件），以及本轮明确指定的 SOURCE_PIN 快照 `inputs/doc/**`、`inputs/verification/P08/SCOPE_DRAFT.md`、`inputs/verification/P22/codex-p22-r10-review-adjudication.md`。
- 本 Review 不代表任何产品实现或运行时结论；本轮无产品代码修改、无 Cargo/产品测试运行（与 Task 自述一致）。

### 0.2 实际执行 vs NOT_RUN
| 项 | 状态 | 说明 |
|---|---|---|
| 文档/证据只读阅读 | **executed** | 上述全部文件逐份阅读，含 `git-verification.log` 内的 `main:` 源码 blob（1102 行日志中的 1039 行 C 代码） |
| 文本级交叉核对（见 §0.3） | **executed** | 仅文本层；未做字节/哈希比对 |
| `git`/`git cat-file`/`Get-FileHash` | **NOT_RUN** | pwsh 调用被 DSH 沙箱拒绝：`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.workspace\worktrees\PROJECT-ROADMAP-RELEASE-REVIEW)`（两次复现）。按策略未换路径重试 |
| `tools/governance/check.ps1` 运行 | **NOT_RUN** | 见 P2-8；且该脚本在 `reviewed_head` 不存在 |
| Cargo/产品测试/GUI/模型/sidecar/安装/OS/registry/ACL | **NOT_RUN** | 指令禁止，且无环境 |
| Task 表中 R-00…R-20 的 commit=`aa629c7c70eb33a9ec84bed4003f911dc73500ee` 与各 sha256 | **NOT_VERIFIED** | 未由我执行；Codex 的核验结果不冒称为我执行 |
| Plan/STATUS 字节预算（2500/3200 bytes） | **NOT_RUN** | 仅能确认行数：Plan 33 行、STATUS 21 行、README 9 行（工具报告值），字节数未测得 |

**object_binding=NOT_VERIFIED**：本 Review 的所有 Git 对象、祖先关系、blob、SHA-256 结论均来自文本引用，不来自我执行的 Git/hash。

### 0.3 我实际完成的文本级交叉核对（可复核、非哈希级）
1. `verification/.../git-verification.log` 中 `git show main:apps/desktop/src-tauri/src/library_bridge.rs` 的 blob 为 **1039 行**（log 行 61–1099），`reviewed_head` 工作区同名文件亦为 **1039 行**；抽检区域一一对齐（log 行偏移 +60），`StdioLibraryChannel` 字段仅有 `child/stdin/stdout/request_id_gen`（worktree 190–192 行、255–260 行），`round_trip` 确实是「先独立锁 stdin 写+flush，再独立锁 stdout 读」（283–303 行），**无 transaction lock**。→ 印证「main 仍有 stdin/stdout 分段锁」这一核心事实（文本级）。
2. 全文件检索 `transaction|ignore` 未发现 `#[ignore]` 测试；`real_core_sidecar_answers_startup_ping_on_fresh_catalog`（1009–1038 行）**未被 ignore**，会 `spawn` 生产 `bootstrap.core_service`（`M2RC1_SRC_ROOT` 默认回退到仓库 `src/`）。→ 支撑 P2-4。
3. `apps/desktop/src-tauri/build.rs:18–21` 以 `env!("CARGO_MANIFEST_DIR")/target/core-sidecar/core-sidecar` 为锚；该期望路径**不受 `CARGO_TARGET_DIR` 重定向影响**。→ 支撑 P2-2。
4. `doc/09_COLLABORATION.md` 在 `reviewed_head` 缺少快照版本 §4.2 的 `[Worktree Safety Inventory](WORKTREE_SAFETY_INVENTORY.md)` 链接；`doc/WORKSPACE_GOVERNANCE.md` 在 `reviewed_head` **不存在**（read 直接 not found）；全树 `**/check.ps1` **无匹配**，`tools/**/*` 只有 `tools/p02/*.ps1` 两个文件。→ 印证 SOURCE_PIN 的必要性，并支撑 P2-8。
5. 我以只读方式读取了 **root 工作区**（非固定 head、非 pin）的 `G:/CODEX/New Manga/tools/governance/check.ps1`（275 行），据其规则推导出 §8 的关闭条件；该文件本身**不在固定 head、也不在 source-manifest.json 的 pin 列表内**。

---

## 1. Architecture 结论：PASS（文本层，附 P2）

- **目标架构与分层不变**。AD-001 冻结的 `React/WebView → explicit Tauri IPC → Python Core → SQLite/Managed Copy` 未被本 Task 或 P22-REBASE-1 触碰。P22-REBASE-1 仅改 `apps/desktop/src-tauri/src/library_bridge.rs` 的**传输层单实例往返串行化**，不拥有 domain 业务逻辑、不写数据库、不改 React/任意 OS 路径/模型直连边界；禁止范围明确排除 `main.rs`/`build.rs`/`Cargo.toml|lock`/前端/Python Core/IPC/schema/依赖/模型。
- **依赖扩大可实现为 0**：`std::sync::Mutex` 已在文件顶部导入（第 10 行），per-channel 事务锁可用既有类型实现，无需新增 crate。AC1「不改 wire shape 或 request_id 合同」与现有 `version {major:1,minor:4}` 报文相容。**架构可接受**。
- **DOC Gate 处理正确**：REPORT §12–23 将 P09/P18/P20 映射记 NOT_RUN，Plan 以 `DOC` 依赖与 `P09 proposed` 如实体现；SCOPE_DRAFT §49/§71 原始要求（P09 释放前须完成 AC-DOC-001..003 目标架构 Gate；P18/P20 引用 stack-specific D08 条目前须先完成映射）与之一致。P22-REBASE-1 属既有 IPC 根因修复，不依赖 DOC Gate，理由成立。
- **架构侧缺口（P2，非阻断）**：
  - **P2-7**：DOC Gate **没有对应的可释放 Task**。REPORT §23 明确「另需冻结 Architecture Documentation Rebaseline Task」，SCOPE_DRAFT §71 记「该Task尚未登记或释放」，但恢复后的 Plan 只有 `DOC` 伪节点，没有 owner/AC/allowed_paths/状态。一个「未登记、不可释放」的依赖无法被 DAG 跟踪，P09 的「依赖全部 done」在形式上是不可判定的。
  - **P2-5**：REPORT 的「架构文档Gate结论」表把 **P16/17 格式**列为 NOT_RUN 行（REPORT:21），而 Plan 只在 P09/P18/P20 挂 `DOC`（Plan:15/24/26），P16/P17 无该边；SCOPE_DRAFT:58 又要求 P08-FMT-* 经该重基线 Task「转录至 D08 或 doc/13」。Plan 与 REPORT（自称 Plan 展开表）互相不一致。
  - **P2-6**：Plan:31 把 `verification/PROJECT-ROADMAP-RELEASE/REPORT.md` 声明为「本Plan展开表」。按 09_COLLABORATION §4.1，`verification/**` 是 task-scoped 当前证据，Task 终态后按 HISTORY 处置；把整条产品路线的依赖/Gate 语义唯一存放在其中，存在关闭后丢失或降级为历史的实际风险。

---

## 2. Verification 结论：PARTIAL / NOT_RUN

- 固定 Git 命令集**形式合格**：`git-verification.log` 含 argv、shell、Python 版本、cwd、EXIT 与原始 stdout，覆盖 `rev-parse HEAD`/`git-common-dir`、`merge-base --is-ancestor 92093792 main`=EXIT 1、`faea1a2c main`=EXIT 1、`92093792..4a707db8` 与 `faea1a2c..4a707db8` 的 name-status、`diff --check`、`main:library_bridge.rs`。P22/P04 未集成的结论与「main 无 transaction lock」可由这些原始输出直接支撑（见 §0.3.1）。
- **不可复核/未执行项**：sub-task 表中 15 条 canonical evidence 的 commit/sha256 我未复核（object_binding=NOT_VERIFIED）；`verification.json` 与 `git-verification.log` 存在 HEAD 口径冲突（P2-1）；`unknown_preserved` 与 REPORT 叙述口径不一致（P2-1b）；`helper_selftests: 127 passed/0 skipped` 的「helper」未标识（P3-8）；`tools/governance/check.ps1` 无运行 artefact（P2-8）。
- **P22-REBASE-1 运行时**：无实现、无 Cargo 运行、`dispatch_state=NOT_DISPATCHED`，与本轮「未派发/未开始实现」一致；不得解读为任何 PASS。

---

## 3. AC1：P01–P22 完整路线恢复（Plan 内容）

- Plan 表含 P01…P22 全 22 行，含 `P21 可选proposed`，且未把历史终态当授权：P02=`限定关闭`、P22=`in_review来源`、P22-REBASE-1=`拟释放，审查前 proposed`、`READY 节点：无。`。P03/P05/P08 `done` 与 P08 快照 `status: done` + `integration_commit: fe2224646…`（P08.md:5/16）一致。**结论：满足**。
- 历史隔离正确：Plan 只挂当前指针，未复制 190/196 节点历史台账；SCOPE_DRAFT §5「P01–P21 路线规划」与 Plan 的 P22/P22-REBASE-1 追加叙事无冲突。
- 记录级小缺口（P3-4）：Plan 未把 `M2-PAGE-NAV-PROJECTION-1` 登记为节点，而 P22/P04/P22-REBASE-1 均以它为 hard dependency（P04.md:13/68、P22.md:12/69、P22-REBASE-1.md:11）；该「已 done 且已集成」事实只能从快照 Task 记录取得，Plan 侧看不到该前置。

## 4. P19→P04 依赖与 P15 子范围

- **无环**：完整边集 P08→P02/DOC/P10/P11/P16; DOC→P09/P18/P20; P09→P12/P13; P11→P13; P13→P14/P15*/P16/P18; P16→P17; P10→P15/P18; P12/P14/P15/P17/P18→P19; P04→P19; P22-REBASE-1→P22→P04; P19/P03/P06→P20; P20→P21。DOC 的下游不回流到 P08；P04 的下游（P19→P20→P21）不回流到 P22。**P19 接收 P04（进而 P22→P22-REBASE-1）合理且无环**；P19 与 P20 保持 `proposed`，未因该新增边被误释放。
- AC1 表述「P19 明确接收 P04/P22 并发安全验收」在 Plan 中 P22 是**传递依赖**（P19←P04←P22）；Plan 的 P04 行已写依赖 P22，可追踪。可接受（P4-4 记录一处措辞精度）。
- **P15 停写子范围**：Plan:21 `P15 设置维护|P10/P13*/UI|proposed` + Plan:31 `P13*仅备份停写`，REPORT:27 `P15模型/维护/全库备份恢复（停写/排空子范围依赖P13）`，SCOPE_DRAFT:20（D4）/42 说明备份恢复须依赖 P13 停写/排空/连接回收。语义方向清楚；`*` 的作用域（仅作用于备份-停写子范围，不作用于 P15 的配置/模型下载部分）靠一行注记成立，可读但偏紧（P3-9：建议在 Plan 或 P15 Task 中把「子范围→依赖」逐条写死）。
- **四页分别设计**：Plan:31 `UI=四页分别经ZCode设计审查`，UI 边分别挂在 P12（书架）/P14（工作台）/P17（阅读器）/P15（设置），与 REPORT:27 与 SCOPE_DRAFT:71 一致。**清楚**。

## 5. AC2：P22/P04/架构 Gate 复核

- **结论正确且边界清晰**：REPORT §5–10 明确 `92093792`（P22 R2 代码）/`4a707db8`（R10 末端，仅 Handoff 修订）/`faea1a2c`（P04 R4 交付）三者**均未集成**，且 **R10 的 DSH `APPROVED_WITH_CONDITIONS` 只覆盖 Handoff 文本、`object_binding=NOT_VERIFIED`、不批准源码/集成/runtime**；`adjudication` 原文（对应 codex-p22-r10-review-adjudication.md:9/24–26）逐条支持。新时点 P02 许可不扩用为 P22 运行许可，旧 Technical Gate/13 项缺失不在本轮解除（STATUS:16、P22-REBASE-1.md:57）。**满足**。
- 证据精度问题：
  - **P2-1**：`verification.json:5` 记 `"head": "571d8970264d86c84c8fdedfd594af07fbe0342f"`、`cwd=G:\CODEX\New Manga`；`git-verification.log:3–6` 同 cwd 下 `rev-parse HEAD` = `0dcc94f3…`（= Task `base_commit`）。同一批 canonical 证据对「被观察 root HEAD」给出两个不同值，必须解释或修正，否则 AC2 的「固定基线」不可判定。触发：`verification.json:5` vs `git-verification.log:3–6` vs Task frontmatter `base_commit`。
  - **P2-1b**：`verification.json:9–10` `"protected_paths": 1525, "protected_bytes": "PASS", "unknown_preserved": []`，而 REPORT:61 写「CON 等不可读路径明确 PRESERVE_UNKNOWN」。1525 条仅以计数+PASS 字符串呈现，无逐路径 manifest 入库，且与 REPORT 的 PRESERVE_UNKNOWN 叙述口径未在同一处解释差值（09_COLLABORATION §6.12④ 要求）。
  - **P4-1/P4-2**：log 未直接执行 `merge-base --is-ancestor 4a707db8 main`（可由「92093792 非祖先 + 92093792..4a707db8 仅改 Handoff」推导）；`git diff --name-status A B` 本身不证明祖先方向，Handoff-only 结论依赖 P22.md:194 的 R9→R10 parent 记录。

## 6. AC3：P22-REBASE-1 切片冻结

**总体结论：范围可接受、判别力要求强、与 P04 分离正确**；逐项：
- AC1（单事务锁覆盖 write/flush+read；所有构造路径初始化；实例互不影响；保留 typed error/EOF/stop/drop/startup ping 回收；不改 wire/request_id）：精确且与 main 现状对得上——main 恰有 **2** 个构造点（`spawn_with_resource_roots`、`#[cfg(test)] adopt_child_for_test`），`wait_first_ping` 的「worker 只持 stdout 锁、协调者只持 child 锁」注释（worktree 351–355 行）说明新锁不得侵入该路径。**强**。
- AC2（必须调用生产 `round_trip`；双调用方差异化 payload/响应；channel/barrier 强制竞争；禁 sleep/概率；禁 ignore；去锁 mutation 必须失败；单实例必过；等待有上限；清理自有子进程）：直接继承 P04 AC2/R2-001 的真实错配机制与 P22 AC1/AC2 的措辞，**判别力充分**。`revisions.implementation=1` + `max_implementation_repairs=2` 与「不得以新ID重置既有返修预算」（P22-REBASE-1.md:35）自洽：P22 的源码返修确为 R1→R2 一次（P22.md:62–64），R3–R10 全为 Handoff-only，不构成新的源码返修。
- AC3/AC4：定向回归覆盖 EOF/写读失败/startup ping timeout 回收；「P04 常量精确断言与完整生产桥接并发验收留给 P04」；「R10 Handoff 批准不沿用」「P04 仍 blocked 直至其自身 AC 完成」。分离干净。
- **释放前置的具体缺口（P2，均为一两行文本修正）**：
  - **P2-2 allowlist 与执行步骤不一致**：`P22-REBASE-1.md:59` 指令把 `core-sidecar` bundle 复制到「本 worktree 期望路径」（= `apps/desktop/src-tauri/target/core-sidecar/core-sidecar`，由 build.rs:18–21 唯一确定），但 `:44–49` 的允许修改范围没有该路径，且未指明由 Owner 还是 Codex 执行复制（P04.md:69 先例是 Codex provision）。Owner 按「超出 allowed_paths 暂停」处置会停摆。
  - **P2-3 复用测试 sidecar 的输入未 pin**：`:47` 只说「复用旧 sidecar 设计，拷入本切片新路径后改」，未给路径/commit/sha256；而 Core bundle 有精确只读来源 + 逐项 hash（`:59`、environment-sources.json:3–6）。AC4 要求「输入源…验证」，此处会退化为 Owner 自行选源。
  - **P2-4 「不运行真实 Core」与「完整 library_bridge 测试集通过」未闭合**：`:63` 的 `cargo test --locked library_bridge::tests` 会连带运行 `real_core_sidecar_answers_startup_ping_on_fresh_catalog`（library_bridge.rs:1009–1038，spawn 生产 `bootstrap.core_service`），而 `:53/:57` 禁止「运行真实 Core」。AC3（`:41`）允许「skip 原因逐项分列」，但未列明**预期 skip 清单**；Owner 若按「完整测试集通过」字面执行即越权。
  - **P3-10**：「有界 Cargo 单测」未量化边界（建议写明 ≤2 次 `cargo test` + 1 次 temp 副本 mutation）。
- **P3-1 分支命名**：`branch: codex/p22-rebase-1`（`:14`）与 09_COLLABORATION §2 的 `agent/<owner>/TASK-slug` 约定不符（Owner=Antigravity；P04/P22 均为 `agent/antigravity/…`）。§2 允许由 Codex 实际分配，但会造成归属/清理歧义。
- **P3-2 预算字段语义**：`revisions: {implementation: 1}`（`:23`）与 `implementation_repairs_used: 1`（`:24`）重复，且 P22.md **没有** `implementation_repairs_used` 字段，继承关系只能从正文推导，机器不可判。
- **P3-3 缺 `launch_head`**：`:57/:67` 说「进入前由 Codex 固定 source_tree 与 launch HEAD」，但无对应 frontmatter 字段；REPORT:63 也说「具体启动 HEAD 由 release 记录给出」。建议释放时写入 `launch_head` 并声明 `library_bridge.rs` 在该区间的差量为 0。
- **P3-6 环境源**：environment-sources.json:9–12 pin 的是 P02 venv 的 `venv/Scripts/python.exe`（274,712 bytes），而 `:57` 把它当作「基础 Python exe 源」去创建独立 3.12 venv。任务已要求「创建后重验 exe/version/hash」，建议同时验证新 venv 的 `pyvenv.cfg`/`home` 确实指向真实基础解释器。

## 7. AC4：保护、治理检查与证据收口

- **用户文件保护**：Task 与 P22-REBASE-1 均禁止写用户源文件/真实 DB/旧 worktree/旧证据，禁止删除/归档/迁移/push（Task:42、P22-REBASE-1.md:53）；源快照以 `* -text`（`.gitattributes`）落盘避免换行改写；source-manifest.json 逐项记 `git_status`（M/??/clean）与 `authority=SOURCE_PIN_NOT_NEW_IMPLEMENTATION`。方向正确。
- **AC4 未完成（本轮不可完成，属正常 in_review 状态；但必须在关闭窗口补齐）**：`canonical_evidence_status: pending`、`resource_closeout_status: pending`、`integration_commit: null`、Closeout Record 空、Resource Manifest 空、四类 AC 复选框全为 `[ ]`；`verification/PROJECT-ROADMAP-RELEASE/` 下 16 个文件中有 **1 个（`verification.json`）未列入 Canonical Evidence 表**。
- **P2-8 治理检查 = NOT_RUN 且工具不在固定 head**：Task:46 明确要求运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PROJECT-ROADMAP-RELEASE.md`，但 (a) `reviewed_head` 与本 worktree **不存在** `tools/governance/check.ps1`（全树无匹配），(b) `source-manifest.json` 未 pin 它，(c) 证据目录内**没有**其 argv/EXIT/输出 artefact。按 09_COLLABORATION §6.12②「artefact 缺失即记 NOT_RUN」，AC4 的「治理检查…完成」当前为 **NOT_RUN**。附带事实：该脚本若在 `reviewed_head` 运行会立即 FAIL（其 staticFiles 含 `doc/WORKSPACE_GOVERNANCE.md`，该文件在固定 head 不存在，check.ps1:61/69）；它只能在 root 工作区（未提交治理文档所在处）获得 PASS。
- **P2-9 `SOURCE_PIN`/`CANONICAL` 分类与正文不一致**：Task:57–71 把 `inputs/**` 与 `environment-sources.json` 全标 `CANONICAL`，而 Task 正文与派发口径称其为 SOURCE_PIN；checker 两者都接受，但语义应分清「本轮结果」与「外部来源快照」。

---

## 8. 生命周期元数据变更可行性（明确答复）

**可以按所述方向推进，但「仅生命周期元数据变更」这一表述不成立**——按 root 的 `check.ps1` 规则，`done` 还要求同批补齐下列元数据，否则治理检查必然 FAIL：

| 触发（check.ps1 行） | 强制要求 |
|---|---|
| :227 | `status: done` 必须有非空 `integration_commit`（当前 `null`） |
| :228 | `done` 必须 `canonical_evidence_status: complete` |
| :229–231 | 终态必须 `resource_closeout_status: complete` |
| :233 | `done` 不得保留任何 `- [ ]` 未完成 AC（当前 AC1–AC4 全未勾选） |
| :235/237–264 | `done` 必须逐项填写 Resource Manifest（≥1 行、6 列、合法 disposition、目标路径存在、integrity 为 sha256 或 manifest 路径、检查结果非空） |
| :217 | `done` 时 evidence_dir 不得含未登记文件 → **`verification.json` 必须加入 Canonical Evidence 表**（它是 16 个文件中唯一未登记项） |
| :145 | STATUS 不得再指向终态 Task → 必须同时把当前指针改为 P22-REBASE-1 |
| :152/155 | Plan 的 READY 声明必须保留 `READY 节点：` 精确前缀；**不可写成 `READY=[P22-REBASE-1]`**，否则报「缺少 READY 节点声明」 |
| :160–162 | READY 列表中的 id 必须有 `doc/tasks/<id>.md` 且其 `status` 必须为 `ready` → **Plan READY 与 P22-REBASE-1.md 的 `proposed→ready` 必须同一提交**，否则「READY DAG 只允许 status: ready」FAIL |
| :166/167 | 非终态 Task 必须出现在当前 DAG；`status: ready` 的 Task 必须在 READY 列表中 |
| :74 | STATUS 当前 Task 必须保持 `[X](tasks/X.md)` 可解析形式 |

其余答复：
- **P22-REBASE-1 ready 的条件已实质满足**（owner/reviewer/base/branch/worktree/allowed+denied/执行环境/判别测试均已冻结；依赖 P08 与 PAGE-NAV 已集成）。建议把 P2-2/P2-3/P2-4 三项低成本修正折入同一 release commit，再置 ready。
- **不是自动调用 Antigravity**：置 ready + `dispatch_state: NOT_DISPATCHED` 只登记 READY，§3.3 仍需 Owner 认领；符合 §5.1「建议不等于释放、不自动启动」。
- **不宣称测试通过**：本 Review 不改变 P22-REBASE-1 的 `NOT_DISPATCHED` 与 Cargo=`NOT_RUN` 事实。
- `integration_commit` 与 AC 勾选会改动 Task 文件本身，存在「文件不能含自身 commit」的顺序问题（09_COLLABORATION §5）；`done` 后需**再跑一次 check.ps1** 并以 artefact 入库（放 `verification/PROJECT-ROADMAP-RELEASE/**` 时同步补 evidence 行）。
- **导航同步（P4-3）**：除用户列出的四处外，§4.2 还要求更新 `doc/tasks/README.md`（Task 索引），该文件在本 Task 允许范围内。

---

## 9. Findings 汇总（P0–P4）

**P0：无。**

**P1：无。** 未发现阻断本 Review 批准的对象级缺陷（无虚假 PASS、无越权运行、无用户数据风险、无对固定 head 的错误断言）。

**P2（应在 release/关闭窗口内修正；不阻断本 Review 的 APPROVED）**
| ID | 触发/文件位置 | 问题与建议 |
|---|---|---|
| P2-1 | verification.json:5 vs git-verification.log:3–6 vs Task frontmatter `base_commit` | root HEAD 记录冲突（571d8970 vs 0dcc94f3）。修正或在同一处解释时间顺序，再 pin |
| P2-1b | verification.json:9–10 vs REPORT:61 | 1525 受保护路径仅计数+PASS，`unknown_preserved: []` 与「CON…PRESERVE_UNKNOWN」口径未解释 |
| P2-2 | doc/tasks/P22-REBASE-1.md:59 vs :44–49；build.rs:18–21 | sidecar 复制目标不在允许修改范围，且未指派执行者 |
| P2-3 | doc/tasks/P22-REBASE-1.md:47（对比 :59） | 复用测试 sidecar 的输入未 pin 路径/commit/sha256 |
| P2-4 | P22-REBASE-1.md:63/:41 vs :53/:57；library_bridge.rs:1009–1038 | 「完整 library_bridge 测试集」会 spawn 生产 Core；须列明预期 skip 清单 |
| P2-5 | REPORT:21 vs Plan:15/24/26；SCOPE_DRAFT:58/71 | P16/17 格式转录的 DOC 映射在 Plan 中无对应边 |
| P2-6 | Plan:31（REPORT 作「展开表」）；09_COLLABORATION §4.1 | 整条产品路线的范围/Gate 语义只存在于 task-scoped `verification/**` |
| P2-7 | REPORT:23；SCOPE_DRAFT:71；Plan:31 | DOC Gate 无可释放 Task（无 owner/AC/allowed_paths/状态） |
| P2-8 | Task:46；`tools/governance/check.ps1` 不在固定 head 与 pin 中；证据目录无运行 artefact | 治理检查 = NOT_RUN，且脚本无法在固定 head 复现 |
| P2-9 | Task:57–71 | `inputs/**`、environment-sources.json 的 evidence class 标 `CANONICAL`，与正文 SOURCE_PIN 表述不一 |

**P3（可留 backlog）**：P3-1 分支命名 `codex/p22-rebase-1` 不符 §2 约定；P3-2 `revisions.implementation` 与 `implementation_repairs_used` 语义重复、P22 侧无对应字段；P3-3 缺 `launch_head` 字段；P3-4 `M2-PAGE-NAV-PROJECTION-1` 未进 Plan DAG；P3-5 evidence_id 编号空洞（R-03/04/09/14/15/17 缺）、Plan 33/35 行仅余 2 行、字节预算需复测（已达 80% 会 WARN）；P3-6 环境源为 venv 内 `Scripts/python.exe`；P3-7 允许范围未含 `doc/00_INDEX.md`，而 §3.6 将其列为 Codex 默认元数据维护面；P3-8 `helper_selftests` 的 helper 未标识；P3-9 `P13*` 子范围注记偏紧；P3-10「有界 Cargo」未量化。

**P4（观察项）**：P4-1 未直接验证 `4a707db8` 非 main 祖先（可推导）；P4-2 `git diff --name-status` 不证明祖先方向；P4-3 README 导航更新未列入拟定变更清单；P4-4 AC1「P19 接收 P04/P22」中 P22 仅为传递依赖。

---

## 10. 结论

- **Architecture：PASS（文本层）**。目标架构/分层/依赖方向未被触碰；P22-REBASE-1 为最小传输层串行化，无需新增依赖，`不扩大共享契约`成立；DOC Gate 对 P09/P18/P20 的 NOT_RUN 保留正确。存在 DOC Gate 无 Task（P2-7）、P16/17 映射边缺失（P2-5）、范围定义寄居 `verification/**`（P2-6）三项架构治理缺口。
- **Verification：PARTIAL / NOT_RUN**。Git 证据形式合格，但 `object_binding=NOT_VERIFIED`（我无法运行 Git/hash）；`verification.json` 自身存在 HEAD 与统计口径问题（P2-1/P2-1b）；治理检查无 artefact 且工具不在固定 head（P2-8）。
- **AC 判定**：AC1 满足；AC2 内容满足（证据自洽性待修）；AC3 主体满足，四项释放前置缺口待补；**AC4 未完成**，且不得被本 Review 视为已完成。
- **decision：APPROVED**（限定范围：Plan 恢复、P22/P04/架构 Gate 结论、P22-REBASE-1 范围冻结与释放可行性）。**无未解决 P0/P1**，故按 09_COLLABORATION §6.8 可批准。
- **批准附加强制条件（不满足则 `done` 不成立）**：按 §8 表格补齐 `integration_commit`、`canonical_evidence_status/resource_closeout_status=complete`、AC 勾选、Resource Manifest 逐项、`verification.json` 入 evidence 表、STATUS/Plan/README 导航同步，并让 `check.ps1` PASS 且以 artefact（argv/EXIT/输出）入库；Plan 的 READY 行保持 `READY 节点：` 精确前缀；P22-REBASE-1 的 `proposed→ready` 与 Plan READY、STATUS 指针同一提交。
- **建议（低成本、不阻断）**：把 P2-2（allowlist 补 `apps/desktop/src-tauri/target/core-sidecar/**` 仅只读复制）、P2-3（pin 测试 sidecar 来源）、P2-4（列明预期 skip：`real_core_sidecar_answers_startup_ping_on_fresh_catalog`）、P2-1（统一 HEAD 口径）折入 release commit，再置 ready/dispatch。
- **未执行声明**：本轮未修改任何文件；未运行 Cargo/产品测试/GUI/模型/sidecar/安装/OS/registry/ACL；未执行 Git/hash。Codex 的 Git/hash/helper 结果与本 Review 的文本结论相互独立，不得互相冒称。

**推荐下一步**：Codex 按 §8 清单完成一次「关闭窗口元数据提交」（含 P2-1/P2-2/P2-3/P2-4/P2-8 修正 + `verification.json` evidence 行 + Resource Manifest/Closeout + check.ps1 PASS artefact），随后将 `PROJECT-ROADMAP-RELEASE` 置 `done`、`P22-REBASE-1` 置 `ready`、Plan `READY 节点：P22-REBASE-1`、STATUS 当前指针改为 P22-REBASE-1（READY/NOT_DISPATCHED），并复跑 `tools/governance/check.ps1 -TaskPath doc/tasks/P22-REBASE-1.md`；通过后由 Antigravity 凭已冻结范围认领，Codex 记录 `launch_head`。在该清单完成前，**不派发、不置 done**。