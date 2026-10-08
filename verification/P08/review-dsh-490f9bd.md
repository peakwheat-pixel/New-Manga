# P08 正式独立 Review 报告

**Reviewer**：DeepSeek Harness（DSH，非作者；本 Task Owner=Codex）
**Task**：P08「完整产品范围与验收冻结准备」（`doc/tasks/P08.md`，status=blocked）
**base_commit**：`ab2f813c0ce311a6712002cafd852b9e7a258380`
**reviewed_head**：`490f9bd9637de0812a3ef3d9bbfa754868d5c15f`
**source delivery branch**：`main`（本次位于 detached Review worktree）
**Review worktree**：`G:\CODEX\New Manga.worktrees\P08-dsh-review-490f9bd`
**结论**：**changes_requested**（0×P0、4×P1、6×P2；P1 未闭合，不得批准、不得声称集成或 done）
**Qoder**：已退出项目，本报告中不作任何 Owner/Reviewer/设计角色引用；其历史署名仅作历史事实。

---

## 1. 工作区与 Git 核验

### 1.1 DSH 自身可执行的核验（只读文件层，已执行）

| 核验项 | 方式 | 结果 |
|---|---|---|
| worktree 独立性 | 读 `.git`（文件）= `gitdir: G:/CODEX/New Manga/.git/worktrees/P08-dsh-review-490f9bd` | 独立 linked worktree，非独立仓库、非复制源码 |
| common dir 共享 | 读 `.../worktrees/P08-dsh-review-490f9bd/commondir` = `../..` | 指向 `G:/CODEX/New Manga/.git`，与主仓共享 common dir ✅ |
| 反向绑定 | 读 `.../worktrees/P08-dsh-review-490f9bd/gitdir` | 指回本 worktree 的 `.git`，绑定一致 |
| HEAD == reviewed_head | 读 `.../worktrees/P08-dsh-review-490f9bd/HEAD` = `490f9bd9637de0812a3ef3d9bbfa754868d5c15f` | **严格相等** ✅（detached，无分支名） |
| reflog | 读 `.../worktrees/P08-dsh-review-490f9bd/logs/HEAD`：`0000…0000 490f9bd963… peakwheat-pixel 1791465087 +0800` | 该 worktree 自创建起唯一 HEAD 指向 `490f9bd…`，无后续提交/rebase |
| commit 是否存在/范围/状态 | git 命令 | **NOT_RUN / BLOCKED（见 §2）** |

### 1.2 调用方（Codex）独立实测结果（引用，非 DSH 实测）

调用方已在本精确 worktree 实测并告知：`HEAD=490f9bd9637de0812a3ef3d9bbfa754868d5c15f`；`status clean`；`common-dir=G:/CODEX/New Manga/.git`；`base=ab2f813c0ce311a6712002cafd852b9e7a258380`；并用 **PowerShell 7.6.6 / Python 3.14.6（`C:\Python314\python.exe`）** 实跑三条命令均 `EXIT=0`（见 §2.2）。

**归属声明**：以上 `status clean`、`base..head` 范围与三条命令的 `EXIT=0` 属**调用方实测**；DSH 自身 shell 测试仍记 `NOT_RUN`。我据调用方结论继续审查，未把它写成 DSH 执行结果。

> 残余边界（诚实披露）：DSH 无法自行执行 `git status`/`git diff`。因此本报告的**内容判断**建立在两个前提上：①worktree HEAD 严格等于 `490f9bd`（DSH 已从 `.git` 管理文件直接读证）；②工作树内容等于该 commit 内容（由调用方 `status clean` 结论支撑）。若该前提失效，则被审字节可能有非交付改动——此风险已列入 §8。

---

## 2. 验证执行记录

### 2.1 DSH 侧（本会话）

**实际 shell**：DSH `pwsh -Command` 调用器。**解释器**：未执行任何 Python（版本未知）。

- 现象：每次调用（共 4 次，含一次以 `workdir=G:\CODEX\New Manga` 的等价重试）在**进入会话前**失败：
  `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga.worktrees\P08-dsh-review-490f9bd)`
- `Win32 5 = ERROR_ACCESS_DENIED`，发生在 harness 为 `workspace-write` 授予工作区写 ACL 的阶段，早于任何 git/python 命令 → 无 stdout/stderr/EXIT 可记录。
- 沙箱提权重试一次：`sandbox escalation to "danger-full-access" requires approval, but no approval channel is available` → 关闭。
- 独立子代理复跑同一失败，确认属 DSH 环境限制而非命令错误。
- **因此本会话**：`python -B -X utf8 verification/P08/verify_scope.py`、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`、`git diff --check ab2f813c… 490f9bd… -- doc verification/P08 verification/PROJECT-ROADMAP-20261008`、`git rev-parse/status/diff` 全部 **NOT_RUN**；PSVersion、Python 版本亦 NOT_RUN。**不推断 PASS。**

### 2.2 交付内既有证据（文件层读取，非本次执行）

`verification/P08/validation.log`：
- `:3 input_HEAD=d44cb5cc05820a36804e3e4d1434ad23b1f2ea87`；`:4 tested_state=input_HEAD + allowlisted working-tree document edits` → **未绑定 `490f9bd`**；
- `:5/:15 command=python -X utf8 …`；`:6-11/:17-22` 两脚本逐项 PASS；`:14/:25 EXIT=0`；`:26` 为 `git diff --check` 的显式 14 文件清单，`:29 EXIT=0`；
- 全篇**无 shell 类型、无解释器路径/版本**（见 Finding P1-1）。

---

## 3. 总体结论与理由

**changes_requested**。理由（按协议 `doc/09_COLLABORATION.md:169/:172`「没有运行环境时不能批准未核实的关键路径」「P0/P1 未解决不能批准」）：

1. 交付自带的验证证据未绑定冻结 head、且缺 §6.12①（`09_COLLABORATION.md:177`）要求的 shell/解释器头 → 该证据按协议口径「按未提供处理」，而 DSH 侧本环境又无法复现 → **Verification 轴无法批准**（P1-1）。
2. 该交付在 D08 验收结果面上与既有权威追踪文档 `doc/13_ACCEPTANCE_TRACEABILITY.md` 存在结果真值/责任路由冲突，未对账（P1-2）。
3. 6 条 **[P1]** AC（AC-WIN-001..006）在已确认范围内**没有实现工作包**（实现方写成 "P20 packaging"），直接冲击 §5「P1=100% PASS」的发布判定（P1-3）。
4. `07/08`（含 D08）按 `AD-001:9` 仍是 **legacy production baseline** 表述、须由「separately released Architecture Documentation Rebaseline Task」更新；本交付把 D08 整表映射到 React/Tauri 新产品并把 stack-specific 条目按「维持D08现行要求」列入，未落任何处置（P1-4）。

正面结论同样明确：**193 条编号 AC + AC-SMOKE + §68–79 十二项 Gate 的映射是完整、有序、无重复的**，D1–D7 七项用户裁决完整保留且未被重新裁决，P0/P1 无一条被降级或延期，全部结果为 `NOT_RUN`，无伪造 PASS/done（详见 §5、§7）。

---

## 4. Architecture / Verification 覆盖声明

**Architecture 轴（executed）**：核对了产品边界（四页不变，`AD-001:26`）、新架构依赖方向（`React/WebView → Tauri IPC → Python Core → Domain/Ports → Infra`，`AD-001:21-24`、`09_COLLABORATION.md:168`）、冻结 wire 边界（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.8 / 协议 minor 6，`§12:414-416`）、Sidecar 生产装配与 15 命令面、Managed Copy/Lock/current/pinned 保护语义落点、以及 P09–P20 拟议 allowlist 与真实目录的一致性。结论：**未发现要求修改已冻结 wire 行的写法**；发现的架构面问题集中在 legacy/新架构口径混用（P1-4）与路径不可执行（P2-2）。

**Verification 轴（NOT_RUN，DSH 侧）**：见 §2.1。以下由文件层读证完成，不等同运行级验证：`verify_scope.py:12-20` 的断言设计（`actual == expected`、Gate 集合 68..79、行数 `len(expected)+1+12`、全行 `NOT_RUN`）、`validation.log` 内容与现行文档的自洽性、以及 As-Is 代码断言（由独立子代理逐条 grep/read 复核，见 §7）。

---

## 5. 逐项处置（对应派发重点 1–5）

### 重点 1：编号 AC / AC-SMOKE / §68–79 映射完整性 —— **满足（附 P1-2 对账要求）**

- D08 编号 AC 实测 **193 条**（104×P0、81×P1、8×P2，与 `doc/13:3` 一致）。我独立从 `doc/08_ACCEPTANCE_CRITERIA.md` 的 `^## AC-` 标题枚举得 193 条；`AC_COVERAGE.md:7-212` 恰 **206 行** = 193 编号 + `D08-AC-SMOKE`(1) + `D08-GATE-68..79`(12)，**数目闭合、无缺项**。
- §68–79 十二项逐项在内（`:201-212`，其中 `GATE-78` 排在末尾，见 P3 观察）；`D08-AC-SMOKE`（`:200`）与 §53 步骤逐字对应（D08:2513-2527）。
- P0/P1 行全部 `INCLUDED`、无 `DEFERRED`（`:7-191`、`:200-211`）；`DEFERRED` 恰 6 条且全部为 §78 的 P2 扩展（`:194-199`）——与 D6 延期清单**精确一致**；§78 另 2 条 P2（`AC-EXT-IMPORT-003/004`）按 D2 选入 PDF 输入，分类自洽。
- 完整主流程（§53）、clean Windows（`AC-PKG-002 [P0]`、`GATE-76`、P20）、备份/恢复（`AC-BACKUP-001..004`）与用户数据保护（源 hash 零变化、无静默覆盖人工/Lock/pinned、失败无半提交、secret 零容忍，`SCOPE_DRAFT:62-67`）**均完整保留**。

### 重点 2：D1–D7 与新增格式验收 —— **满足（附 P2-4/P2-5 精确性要求）**

- D1：基础 Reader 已选入（分页 RTL/LTR、Webtoon、独立进度恢复、PNG/ZIP 导出 → `AC-READ-*`、`AC-WEBTOON-*`、`AC-EXPORT-001`）；跨页联动/页缩略图延期已记录（`SCOPE_DRAFT:17/:33`）。D08 **无缩略图编号 AC**（`doc/08` 全文仅 `:2328 Thumbnail Cache`，属清缓存保护），`AC-PROGRESS-002 [P0]`（D08:1632-1649）清单**不含**缩略图 → 延期不与任何 P0 冲突 ✅。
- D2：PDF/MOBI 输入（`AC-EXT-IMPORT-003/004` + `P08-FMT-MOBI`）、PNG/ZIP/CBZ/PDF/文本输出（`AC-EXPORT-001` P0，D08:2054-2064 原文即 `单图/ZIP/CBZ/PDF/文本`）均落盘。
- 新增 `P08-FMT-MOBI/CBZ/PDF/TEXT`（`SCOPE_DRAFT:51-58`）逐项给出受控来源/页序/Managed Copy/损坏与加密拒绝/无半成品/源零写/取消与失败清理/安装包实际导出/编码与缺失策略留待契约冻结 → **可执行、无格式混淆**；`P08-FMT-PDF`（输出）与 `AC-EXT-IMPORT-003/004`（输入）职责分离清楚；D08 原文「只验收 PDF，不代表 MOBI 解析契约已确定」（D08:3173）被正确继承，MOBI 单列 ✅。
- D3：RG1 净化基线、JA/KO 分别实测、Win10「实测后声明」（`SCOPE_DRAFT:19/:43/:67`）✅；D4：全库 DB＋Managed Copy、停写/排空/连接回收/reassemble/rollback、DB-only 不可替代（`SCOPE_DRAFT:20/:42`，`AC-BACKUP-*` 行）✅；D5：§73/§76 门槛原样保留 ✅；D6：模型下载保留（`AC-MODEL-001/002`），Plugin/Hook、字体上传、Sakura 监控、Plugin Agent 首发延期且**非 PASS/N/A** ✅；D7：设置/回收站/TM 及维护按现行 P0/P1 ✅。
- 未重新裁决 D1–D7：未发现任何以历史文档推翻用户确认的条款 ✅。

### 重点 3：数据安全 / Secret / 损坏逃逸 / 恢复回滚 / Lock·current·pinned / 质量阈值边界 —— **满足（附 P2-5 引用精度）**

源文件 hash 零变化、无静默覆盖人工/Lock/pinned、版本冲突显式返回、失败无半提交、secret 零容忍（`SCOPE_DRAFT:62`）；`AC-SEC-001..005`、`AC-LOCK-*`、`AC-REV-*`、`AC-CACHE-001..003`、`AC-CLEAN-001..003`、`GATE-72`（源/人工/Revision/Stop/Crash/Migration/Secret，任一失败 BLOCK RELEASE）逐项在位；损坏/加密/逃逸/重复/中断/Unicode 与部分失败写入 P09/P12 Gate（`SCOPE_DRAFT:32/:75`）；备份失败回滚与连接回收写入 P15（`:42`、`AC-BACKUP-003`）。质量阈值缺口**明确不编造**：`SCOPE_DRAFT:65` 拒绝把 BJ13 0.90 当整体质量分数、缺失真值/阈值留待 P18 资格方案独立审定；`P18` 行（`:84`）要求真值/阈值/样本/版本冻结且「缺失数值不得编造」；所有行 `NOT_RUN`、未执行不标 PASS ✅。

### 重点 4：P09–P20 依赖 / Owner / Reviewer / allowed_paths 与协议一致性 —— **基本满足（附 P2-2）**

- 逐条对照 `doc/REBASELINE_PLAN.md:40-52`：10/12 依赖一致，**2 处缺失/弱化**（P15 漏 P10 与 ZCode 设计门；P12/P14/P17 设计门泛化）→ P2-2。
- **Owner≠Reviewer 全部满足**（`09_COLLABORATION.md:17`）：P09/P10 契约=Codex→Antigravity（Reviewer DSH）；P11=Codex（DSH）；P12/P13/P17=ZCode（DSH）；P14/P15/P16 契约→实现（DSH）；P18/P19=DSH（Codex 或 ZCode 非作者，符合「DSH 自己的实验由 Codex/ZCode 审」）；P20=ZCode（DSH；Codex 集成）。
- **Qoder 未出现在任何当前 Owner/Reviewer/设计位**（`SCOPE_DRAFT:9` 明示「Qoder不参与」；`:75-86` 无 Qoder）✅；ZCode 承担 UI/UX/React、Codex 承担契约/协调/集成、Antigravity 承担一般实现，与 `09_COLLABORATION.md:11-14`、`AGENTS.md` 一致 ✅。
- **未释放边界未被越过**：P09–P20 全部标「proposed/未释放/尚无正式Task」（`SCOPE_DRAFT:69/:71/:102`、`AC_COVERAGE:3`、`STATUS.md:7/:14`、`PLAN:28`）；P09–P20 无任何 PASS/已认领声明 ✅。
- 拟议 allowlist 与真实仓库核对（glob 实测）：`src/application/{library,importing,tasks,reading,export,editing,settings,maintenance}`、`src/bootstrap/core_service.py`、`apps/desktop/src-tauri/src/main.rs`、`packaging/**`、`doc/contracts/**` 均存在；三处写法与实际不符 → P2-2(c)。

### 重点 5：内部矛盾 / 遗漏 / 重复 / 不可操作 / 可能误导发布判断 —— 见 §6

---

## 6. Findings

### P0（阻断发布/批准）：无

### P1-1（P1）交付验证证据未绑定冻结 head，且缺 §6.12① 要求的 shell/解释器头 —— open

- **位置**：`verification/P08/validation.log:3-4`（`input_HEAD=d44cb5cc…`、`tested_state=input_HEAD + allowlisted working-tree document edits`）、`:5/:15`（`command=python -X utf8 …`）、`:16`（`live HEAD=d44cb5cc…`）；`doc/tasks/P08.md:49-53`（测试要求表以「见validation.log」为证据）；`doc/09_COLLABORATION.md:177`。
- **触发条件**：任何人（Reviewer/集成者/发布审计）试图把 `validation.log` 的 5 项 PASS 与 `EXIT=0` 归因到 `reviewed_head=490f9bd`；或按 §6.12① 复核该日志。
- **影响**：`validate.log` 自陈被测态为「`d44cb5cc` + 未提交工作树编辑」，而交付 head 是 `490f9bd`；其内两条断言依赖 git（`verify_scope.py:46-53` 的零生产差量与 Plan/Status 历史段落不变）——**无法从日志本身证明被验证字节等于被交付字节**。§6.12① 明确「无 shell 类型与解释器路径/版本…的日志不可复核，按未提供处理」。叠加 DSH 侧全量 NOT_RUN（§2.1），本交付的 Verification 轴目前**没有可归属、可复核的证据**；按 `09_COLLABORATION.md:169/:172` 不能批准，且不得在 Task/STATUS/台账中把它记为通过。
- **最小修订建议**：在 `490f9bd` 上重跑两脚本 + `git diff --check`，日志首部固定 `shell / PowerShell 版本、解释器绝对路径与版本、repo、branch/worktree、HEAD、命令、EXIT`，逐次入库；同步把 `P08.md:49-53` 的证据列指向新日志，并写明「旧 `d44cb5cc` 工作树日志仅作历史」。

### P1-2（P1）AC 结果真值与责任路由与 `doc/13_ACCEPTANCE_TRACEABILITY.md` 冲突且未对账 —— open

- **位置**：`verification/P08/AC_COVERAGE.md:3`（「所有状态均NOT_RUN」）与全表；`doc/13_ACCEPTANCE_TRACEABILITY.md:9`（结果真值只在本文件或绑定固定 commit 的 Handoff/Review 中维护）、`:45-48/:50/:64-65/:75-76/:197-199`（12 条 `PASS`：AC-REGION-001..004、AC-OCR-002、AC-TRANS-001/002、AC-REV-003/004、AC-DOC-001/002/003，均带 `verification/TASK-008/integration-06ba2e7.md`、`Review f9e5977` 等固定证据）、`:217-226`（§51/§56/§57/§59/§60/§62/§63/§64/§67 以 `ACG-*` 追踪）、`:242`（「§74/§75 为建议性章节，**不作为独立验收项**」）、`:248-257`（§78 剩余 5 条草稿 AC：AGENT-001/002、FONT-003、SAKURA-002/003）；`doc/00_INDEX.md:59`（把 `13_ACCEPTANCE_TRACEABILITY.md` 列为「D08 条目到计划 Task 的映射」）、`:95`（同一结论只维护一个权威位置）。
- **触发条件**：P19/P20 归集发布证据、或用户/审计按「D08 AC 当前结果」提问时；以及 P09（Schema/契约）启动前需核对 §67 AC-SYNC Gate 时。
- **影响**：同一 193 条 AC 上出现**两个互斥结果面**（12×PASS vs 全量 NOT_RUN）与**两套责任路由**（legacy TASK-0xx vs P09–P20）；`AC_COVERAGE.md:207-208` 把 §74/§75 当作独立 Gate 行（含实现/验收责任），与 `doc/13:242` 的既有裁决直接相反；`AC_COVERAGE.md:191` 将 §66「正式开发前必须通过文档一致性检查」（D08:2819-2821）的 AC-DOC-003 记 NOT_RUN 并路由到 P11/P13/P19（开发之后），而 `doc/13:197-199` 记 PASS；§51/§56/§57/§59/§60/§62/§63/§64/§67 与 §78 剩余 5 条草稿 AC 在本索引中**完全未出现**，读索引者会误以为 D08 只有这些验收面。上述任一条都可能**误导发布判断**（以哪份为准、哪些是独立验收项、pre-dev Gate 是否已闭）。
- **最小修订建议**（不新增产品决定、不改 D08）：在 `AC_COVERAGE.md` 头部增补一段 3–6 行对账声明：①本表 `NOT_RUN` 是**新架构 To-Be 路由**，不覆盖 `doc/13` 中绑定固定 commit 的 12 条 legacy PASS（逐条列 AC ID 与证据去向）；②未编号 `ACG-*`（§51/§56/§57/§59/§60/§62/§63/§64/§67）与 §78 剩余 5 条草稿 AC 仍由 `doc/13` 追踪，不在本表重复；③§74/§75（及 §79 建议性章节）按 `doc/13:242` 口径标注「建议性、非独立验收项」，若因本 Task 要求必须列为行，则在「决策处理」列写明该定性；④AC-DOC-001..003 属 §66「正式开发前」Gate，须在 P09 前单独闭合，不由 P11/P13/P19 承接。

### P1-3（P1）6 条 [P1] AC-WIN-001..006 没有实现工作包（实现方写成 "P20 packaging"） —— open

- **位置**：`verification/P08/AC_COVERAGE.md:10-15`（实现工作包列 = 「P20 packaging；平台不兼容另立Task」）；`verification/P08/SCOPE_DRAFT.md:86`（P20 = 「fresh Windows Gate…自有packaging/verification冻结范围」）；对应 AC：`doc/08_ACCEPTANCE_CRITERIA.md:286/303/325/333/351/366`；对应用户流程：`doc/04_USER_FLOW.md:56-70`（§1.3 关闭语义）、`:1746`（§45 无保存修改时关闭）、`:1769`（§46 双屏/悬浮窗）。
- **触发条件**：P19 组装「四页完整 E2E + 安装包」验收、或 P20 逐格提交 §73 证据时。
- **影响**：D08 §5（D08:171）要求 **P1 = 100% PASS** 才可 Release。这 6 条 P1（固定面板优先、编辑窗 Dirty Close、查看类外部关闭、悬浮窗内容不溢出、双屏拖动、第二屏消失恢复）在已确认范围内**没有任何实现 Owner**：P20 被本交付定义为打包/验证 Gate，不能承担 UI 行为实现。结果是二选一：要么被永久挂起而阻塞 §5/§76 READY，要么由 P19/P20 在无实现的前提下产出 PASS（伪 PASS 风险）。此外 `AC-WIN-002`（编辑窗 Dirty Close）与 `AC-CLOSE-001/002`（D08:2794/2804）属同一关闭语义族，未说明是否共用实现与验证边界。
- **最小修订建议**：把这 6 行的**实现切片**改指 UI 工作包（P12/P14/P15/P17 中按页面归属，ZCode React/Tauri 主责），平台相关部分（多屏/DPI/窗口恢复）实现留 P17/P20、验证留 P20+DSH；并在行内注明 AC-WIN-002 与 AC-CLOSE-001/002 的共用实现及各自证据，避免同一行为两处验收口径不一。

### P1-4（P1）legacy-baseline 冲突未落处置：D08 被整表当作新产品验收，而 AD-001 声明 07/08 仍是 legacy production baseline —— open

- **位置**：`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:9`（「The existing 02 technical architecture, QML mappings, nonfunctional requirements and acceptance criteria still describe the **legacy production baseline until a separately released Architecture Documentation Rebaseline Task** updates them」）、`:13`、`:36`（「a PyInstaller/QML PASS cannot be copied into a Tauri packaging PASS」）；`doc/00_INDEX.md:44-45`（D07/D08 为 To-Be「什么算达标」）与之并存；本交付：`verification/P08/AC_COVERAGE.md:175/177/202`（`AC-PKG-001` PyInstaller、`AC-PKG-003` **Qt DLL**、`D08-GATE-69` **ViewModel** 均记 `INCLUDED：…维持D08现行要求`）、`AC_COVERAGE.md:209`（§76 READY 含 clean Windows）、`SCOPE_DRAFT.md:43/:49/:67`；`doc/REBASELINE_PLAN.md:32-52`（P01–P21 中**没有**该 Architecture Documentation Rebaseline Task）。
- **触发条件**：P18/P20 执行打包/平台/UI 验收并引用这些 AC 作为新架构证据时；或用户/审计追问「D08 到底是 legacy 还是目标验收」时。
- **影响**：`AC-PKG-003 [P0]` 在 Tauri/React 产品上语义错位（校验 PySide6 Qt DLL/Qt plugin 缺失），`AC-PKG-001 [P0]` 需依赖其中「等价方案」条款才成立，`§6`（D08:188 `PySide6 Version`）与 `§69`（D08:2926 `UI 自动化 / ViewModel`）在新架构下无对应物；三者都以「维持 D08 现行要求」出现在发布 Gate 面上。按 §5 P0/P1=100% 判定，它们要么以**空洞证据**被记 PASS（误导发布判断），要么被永久卡住。D5 已确认保留 D08 门槛，因此需要的是**表述/处置对账**，而非改门槛。
- **最小修订建议**：在 `AC_COVERAGE.md`（或 `SCOPE_DRAFT.md` 的「D08发布口径」段）增补一行「legacy-baseline 表述处置」：列出 stack-specific 条目（`AC-PKG-001`、`AC-PKG-003`、`§6 PySide6` 字段、`§69 ViewModel`、`§51`/`§69` 的旧命名），声明①用户 D5 已确认的门槛数值与 P0/P1 级别不变；②其**新架构等价表述**须由 AD-001 所指的、单独释放的 Architecture Documentation Rebaseline Task（或 P08 之外的另一项单独授权）产出后，才能作为 P18/P20 证据；③在此之前这些行只能记 `NOT_RUN`，不得以 legacy 语义或空洞检查记 PASS。同时把该 rebaseline 依赖写进 P18/P20 行的依赖位（若它不在 P01–P21 内，则在 P08 明确记为待 Codex/用户登记的前置，不新增产品决定）。

### P2-1（P2）`STATUS.md` 同日状态自相矛盾 —— open

- **位置**：`doc/STATUS.md:20`（「P08范围草案已准备但blocked**等待D1–D7**和DSH正式Review」）vs `:3`/`:7`/`:10`（「D1–D7全部确认…用户决策已收齐」）。
- **影响**：`STATUS.md` 是运行状态唯一事实源（`00_INDEX.md:81`）。恢复工作的 Agent 读到 `:20` 会误判仍有待用户裁决，与 P08 的 checkpoint/RESUME 主张冲突。
- **最小修订**：把 `:20` 的「等待D1–D7和DSH正式Review」改为「D1–D7已确认；等待DSH正式Review」。

### P2-2（P2）P09–P20 的依赖、职责与拟议允许路径存在错配/不可执行项 —— open

- **位置与内容**：
 - (a) `SCOPE_DRAFT.md:81`（P15）依赖位**未声明 P10 与 ZCode 设计依赖**，而 `REBASELINE_PLAN.md:46` 为「P10＋ZCode设计；备份恢复需P13停写/排空设计」；
 - (b) `SCOPE_DRAFT.md:78/:80/:83`（P12/P14/P17）设计门泛化为「设计Review」，未点名 `PLAN:43/:45/:48` 的「P08 的 ZCode 设计通过」；
 - (c) 路径与实际不符：`:75` 的 `core_assembly.py`（实际 `src/bootstrap/core_assembly.py`，与并列书写的 `src/bootstrap/core_service.py` 不同层）；`:78` 的 `frontend/library与路由最小切片`（仓库根**无** `frontend/`，实际 `apps/desktop/frontend/src/library/`，且未标「拟议」）；`:83` 的 `frontend拟议reader/export目录`（已标拟议 ✅，但实际根为 `apps/desktop/frontend/src/`，该目录下确无 reader/export）；`:84` 的 `自有experiments/verification`（实际是根级 `experiments/` 与 `verification/` 两个目录，`verification/experiments` 不存在）；
 - (d) `AC_COVERAGE.md:175-179`（AC-PKG-001/002/003、AC-OPTIONAL-001/002）把实现工作包写作「P18/P20」，而 P18 定义为 JA/KO 真实质量资格（`PLAN:49`），不含打包/可选依赖职责。
- **影响**：这些正是未来 Task 冻结 `allowed_paths` 的输入；按 `09_COLLABORATION.md:51`（「允许路径具体化」）与 `doc/templates/TASK.md`（不存在的代码路径必须标为拟议），现写法会产出不可执行或误导的 allowlist；P15 依赖缺 P10 会让凭据/设置链在错误次序上启动；P18 承担打包职责会稀释其资格实验定位。
- **最小修订**：按实际目录改写并统一标「拟议路径」；P15 补 `P10＋ZCode设计` 依赖并保留「恢复必须 P13 停写排空」；P12/P14/P17 的设计门改指「P08 产出、单独释放的 ZCode 设计 Task 通过后」；AC-PKG-*/AC-OPTIONAL-* 的打包职责改指 P20（及 P03/P06 补证）。

### P2-3（P2）新增格式验收条目没有入权威文档的通道，且 P08-FMT-TEXT 行缺安装包级验证字样 —— open

- **位置**：`SCOPE_DRAFT.md:51-58`（P08-FMT-* 仅存在于该草案）；`:56`（TEXT 行「必须验证」列止于「受控输出/失败清理/源零写」，未含其余三行均有的「安装包实际导出」）；`doc/tasks/P08.md:41`（allowlist：doc/01–08 类共享需求文件只读）。
- **影响**：P08 集成后，这 4 条**有约束力的新验收项**仍只存在于 `verification/P08/**`（Task 级材料），而 `doc/13` 声明「结果真值/路由只在本文件或固定 commit 报告中维护」；P16/P17 Gate 引用它们时缺乏权威落点，未来修订易漂移。TEXT 行还弱化了「安装包实际导出」这一与 CBZ/PDF/MOBI 同级的发布证据要求。
- **最小修订**：在 FMT 表下加一句「P08-FMT-* 为 P16/P17 契约与 Gate 的临时权威来源，须由单独授权的文档冻结/rebaseline Task 转录进 D08 或 `doc/13`」；TEXT 行补「生产安装包实际导出」与其余三行对齐。

### P2-4（P2）易误读措辞与未声明的格式等价关系 —— open

- **位置与内容**：
 - (a) `SCOPE_DRAFT.md:49`「§53完整主流程全部PASS；§68–79总Gate逐项保留；§73 Backup/Restore PASS及P0/P1 100%」——转述门槛，但脱离上下文可被读成「已 PASS」（同一文档 `:27` 与 `AC_COVERAGE.md:3` 已声明全部 NOT_RUN，属措辞风险）；
 - (b) `SCOPE_DRAFT.md:18/:40`、`AC_COVERAGE.md:142` 把 D08/D04 原文的「单图」（D08:2059、D04:1467）写作 **PNG**，等价关系未声明；`AC-EXPORT-001 [P0]` 的格式面因此可能被窄化为「仅 PNG」或反之；
 - (c) `SCOPE_DRAFT.md:66`「已冻结Workbench刷新≤300ms」在 D07/D08 中无对应条文可检索对应：`AC-PERF-002`（D08:2154）为「一级页面切换 P95≤300ms」，`TaskProgressPanel` 刷新为 `250 ms / 4 Hz`（D07:286、:2772）。
- **影响**：三类都直接面向发布判断（是否已 PASS、P0 格式集合边界、性能口径），可造成审计歧义。
- **最小修订**：分别改为「§73 要求 Backup/Restore PASS 与 P0/P1 100%（当前未执行）」；「PNG 即 D08『单图』的具体形态，由 P16 契约冻结（D08 原文为『单图』）」；性能句改引实际条文（AC-PERF-002 / D07 §6）并去掉未定义来源的「已冻结」。

### P2-5（P2）D04 来源引用编号真实但 6 处内容不支撑/无法核实 —— open

- **位置**：`SCOPE_DRAFT.md:31-42`（「当前缺口/来源」列）。
- **已核实事实**：11 条 D04 小节编号（§3–10、§8、§9/33–36、§11–14/22/30–31/51、§18/27–29/32、§20–22、§38–42、§17/19/23–26、§37、§43/44、§38）**全部存在、无错位**；但：①「四个一级页面」定义在 `doc/04:29-36`（§1.1），不在 §3–10；②§20–22 无「TM 管理」流程（§21 仅「翻译时/写入时」）；③D04 全文无「诊断」（§44:1709 实为「错误处理用户流程」），诊断对应 D08 `AC-LOG-003`；④备份/恢复在 D04 仅 `:1499` 一个分区名，无流程小节（实体要求为 `AC-BACKUP-001..004`）；⑤`current` 在 D04 全文 0 命中（§29 只有 `:1113 固定（Pin）重要版本`、`:1114 清理旧版本`）；⑥`§8` 含缩略图（`:332 生成缩略图`、`:1216 建议附小缩略图`），而该行未标注与 D1 延期的关系（D1 延期已在他处记录，不构成 P0 冲突）。
- **影响**：来源列是 Reviewer/未来 Task 判断「需求出处」的唯一指针；6 处会把追溯引向不存在的内容，削弱 To-Be 与实现缺口的对应关系。
- **最小修订**：逐条校正（四页→§1.1；TM 管理→§20–22+AC-TM-*；诊断→AC-LOG-003；备份恢复→AC-BACKUP-*，D04 仅设置分区名；`current` 标为「D04 无对应条目，语义见 D08 AC-REV-*/AC-CLEAN-001」；导入行补注缩略图延期）。

### P2-6（P2）`verify_scope.py` 的零差量与 whitespace 断言覆盖不足 —— open

- **位置**：`verification/P08/verify_scope.py:46-48`（零差量路径 = `src apps tests packaging doc/contracts doc/reviews verification/…/task-inventory.csv`，**不含 `doc/01_…`–`doc/08_…`**）、`:49-53`（仅断言 Plan/Status 历史段不变）；`validation.log:26`（`git diff --check` 只覆盖 14 个显式文件，未含 `verification/P08/DSH-REVIEW-PROMPT.md`、`preliminary-review.md`、`validation.log`）。
- **影响**：`SCOPE_DRAFT.md:49`「D08源文件本轮不变」与 `doc/tasks/P08.md:41`「共享契约…本来产品需求文件仅只读」是本交付的核心边界声明，但**未被任何断言机器验证**；whitespace 检查存在同类盲区。在 git 不可用（本次）时，这两条声明只能记 `NOT_VERIFIED`。
- **最小修订**：把 `doc/01_FUNCTIONAL_ARCHITECTURE.md`～`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`、`doc/AD-001_…` 加入零差量路径集合，并把 `verification/P08/**` 全部纳入 `git diff --check`；重跑并入 `validation.log`。

### P3 / 观察（不阻断，建议一并收口）

1. `AC_COVERAGE.md:3` 写「§68–77/79 也单列」，但表内含 `D08-GATE-78`（`:212`）——措辞陈旧，易被读成 §78 未覆盖。
2. `AC_COVERAGE.md:86`（P20 行）把「Codex 集成」与 Reviewer 并列在同一列；集成是 Codex 职责（`09_COLLABORATION.md:11/:173`），建议分列，避免与「非作者 Reviewer」混淆。
3. `AC_COVERAGE.md` 列名含「Owner」，虽 `:3` 声明为「尚未释放的建议」，仍可能被读成已认领；建议改为「建议实现切片（未认领）」。
4. `SCOPE_DRAFT.md:100-102`「下一步可转发指令」未含 `09_COLLABORATION.md:100-111` 的 7 项字段，且指向的 `DSH-REVIEW-PROMPT.md:5` 自陈「尚未填 base/reviewed_head」——交付内**没有任何文件固定 `reviewed_head`**（`RESUME.md:5` 亦推给「下一份 Handoff」）。P08 未 done、§5.1 未强制，但冻结交付宜自带 head/Handoff 记录，避免复审时基线悬空。
5. `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:45` 的 open decision 仍写「Qoder owns existing UI/UX and QML design」，与 2026-10-08 Qoder 退出裁决不一致；`doc/13` 的多行主责任 Task 亦为 Qoder 时代署名。两者均**先于本交付存在**且不在 P08 allowlist 内，P08 正确地未据此恢复 Qoder 资格；建议由 Codex 另立治理切片处置，不计入本 Task 缺陷。

---

## 7. 已核实的正面结论（避免被 findings 掩盖）

1. **193 条编号 AC + AC-SMOKE + §68–79 十二项 Gate 映射完整、顺序一致、无重复**：`AC_COVERAGE.md:7-212` 恰 206 行 = 193+1+12，与我从 D08 `^## AC-` 独立枚举的 193 条（104 P0 / 81 P1 / 8 P2）逐数吻合；`verify_scope.py:12-20` 的 `assert actual == expected` 在顺序层进一步保证一致性（该断言由调用方在 `490f9bd` 实跑 `EXIT=0`，DSH 侧 NOT_RUN）。
2. **P0/P1 零降级**：无一条 P0/P1 被标 DEFERRED；`DEFERRED` 恰为 §78 的 6 条 P2（Plugin/Hook 3、字体 2、Sakura 1），与 D6 精确一致；另 2 条 PDF 输入 P2 按 D2 选入。
3. **D1–D7 完整且未被重新裁决**：基础 Reader 解冻（含分页/Webtoon/独立进度/PNG·ZIP 导出）、跨页联动与页缩略图延期（D08 无对应 P0，不冲突）、PDF/MOBI 输入、PNG/ZIP/CBZ/PDF/文本输出、RG1 基线、JA/KO 分别实测、Win10 实测后声明、全库 DB＋Managed Copy 备份与停写/排空/回滚、D08 现行 P0/P1 与 §53 完整主流程、模型下载保留 vs Plugin/Hook/字体/Sakura/Plugin Agent 延期（非 PASS/N-A）、维护范围按现行 P0/P1——逐项在位。
4. **数据安全与失败语义覆盖到位**：§72 八项（源 hash、人工保护、current、pinned、Stop 不回滚、Crash 不误判、Migration 可恢复、Secret 不入库/日志）在 `GATE-72` 与 `AC-SEC/LOCK/REV/CACHE/CLEAN` 行逐项映射；`SCOPE_DRAFT:62-67` 给出「不以总测试数量替代、逐入口与故障注入、mock/静态测试不得代替真实生产链」的口径。
5. **NOT_RUN / NOT_VERIFIED 纪律良好**：全表结果一律 `NOT_RUN`；质量阈值缺失项明确不编造（拒绝把 BJ13 0.90 作为整体质量分），P18 要求真值/阈值/样本/版本冻结；P08 状态 `blocked`、`reviewer: null`、`integration_commit: null`，无任何 PASS/done/已释放声明。
6. **As-Is 代码断言经独立复核成立**（11/11，逐条带 `文件:行号`）：生产侧车 decoder 恒 1×1（`src/bootstrap/core_service.py:313-318,:369`）、生产命令面恰 15 条且无 Import/CreateBook/StartRun/ReaderProgress/Export（`apps/desktop/src-tauri/src/main.rs:53-77,:1021-1048`）、React `TaskProgressPanel` 静态占位（`TaskProgressPanel.tsx:1-8,:24-29`）、PDF composer 未注入（`core_assembly.py:1149`、`export/service.py:423-429`）、`CredentialRef` exchange 缺失（`M2-C1:144,:370`，`src/` 零命中）、style analyzer 为空 stub（`core_service.py:321-324`）、learned inpaint `implements=False`（`runtime.py:615-634`）、React Reader 缺失（`frontend/src/**` 无 reader）、`PipelineService`+九步 handler 可复用但无 StartRun 命令、Trash/Diagnostics 已装配未接命令、备份服务零引用且新架构无 backup/restore 命令面。→ 「代码只证 As-Is」的边界被正确执行。
7. **未越界**：`SCOPE_DRAFT:75/76/82` 对 M2-C1 只承诺「自有修订/自有契约」，所涉 `CreateBook/CreateChapter/ImportPages/GetReaderProjection/SaveReadingProgress/StartExport/CancelExport` 在 M2-C1 §5 全为 PROPOSAL/UNKNOWN（`:123/125/126/143/145`），与 §12「freezes design only…successor implementation Task must reference this contract」（`:414-416`）相容；P09–P20 全部未释放，无 Qoder 当前角色。

---

## 8. 未覆盖风险与 NOT_VERIFIED

| 项 | 状态 | 说明 |
|---|---|---|
| DSH 侧三条验证命令 | **NOT_RUN / BLOCKED** | pwsh 沙箱 `grantWrite` 失败（`SetNamedSecurityInfoW Win32 5`），提权无审批通道；未推断 PASS |
| `git status clean`、`base..head` 全量 diff、`merge-base --is-ancestor`、`branch --contains` | **NOT_RUN（DSH）**；调用方实测 clean/HEAD/common-dir 一致 | DSH 无法验证交付是否含 allowlist 之外改动（例如 D08/doc/13 是否被动过）；`SCOPE_DRAFT:49`「D08源文件本轮不变」仅由 `P08.md:41` 声明 + `verify_scope.py` 的**不含 doc/01–08** 的差量断言支撑 → 记 `NOT_VERIFIED`（见 P2-6） |
| `git show 8617e184`（checkpoint 元数据对比） | **NOT_RUN** | 本次依据任务指令所述「current metadata at checkpoint 8617e184」与 head 内 `doc/tasks/P08.md` 内容审查；未做 commit 级对比 |
| 产品 pytest / cargo / vitest / GUI / build / 模型推理 | **NOT_RUN**（P08 为文档任务，交付自陈 NOT_RUN） | 不属于本交付范围 |
| 质量真值/阈值（检测、OCR、翻译相似度、无字页 F4、复杂背景修复） | **NOT_VERIFIED**（正确保留） | `SCOPE_DRAFT:65` 明确缺失，须在 P18 资格方案独立审定后才可定 |
| P08 交付内 `reviewed_head` 记录 | **缺失** | 仅存在于本派发与调用方实测；交付内 `DSH-REVIEW-PROMPT.md` 为占位（见 P3-4） |
| Win10 / 独立干净 Windows / 多 build | **NOT_RUN** | D3 已约束「实测后声明」，不得外推 |
| 未被 DSH 覆盖的文档面 | — | `doc/02`、`doc/03`、`doc/06`、`doc/10`–`doc/14` 及全部历史 `verification/**` 未逐一通读；本次聚焦派发指定材料、D08 全文、`doc/13`、Plan/Status/协作协议、AD-001、M2-C1 与真实代码断言 |

---

## 9. 最小修订清单（仅限固定交付范围，不扩产品范围、不新增产品决定）

1. 在 `490f9bd` 重跑并入库**带 shell/解释器/HEAD/EXIT 头**的验证日志；同步更新 `doc/tasks/P08.md` 测试表证据指向（P1-1）。
2. `AC_COVERAGE.md` 头部增补「与 `doc/13_ACCEPTANCE_TRACEABILITY.md` 的对账声明」：结果真值、12 条 legacy PASS 不覆盖、`ACG-*`/5 条草稿 AC 归属、§74/§75/§79 建议性定性、AC-DOC-* 的 §66 pre-dev 时点（P1-2）。
3. 将 `AC-WIN-001..006` 的实现切片改指 UI 工作包并说明与 `AC-CLOSE-001/002` 的共用边界（P1-3）。
4. 增补 legacy-baseline 表述处置行（stack-specific AC 清单 + rebaseline 依赖 + 未完成前只记 NOT_RUN）（P1-4）。
5. `STATUS.md:20` 同步为「D1–D7 已确认」（P2-1）。
6. `SCOPE_DRAFT.md:75-86` 修正依赖（P15 补 P10＋设计门）、设计门具名、路径按实际目录并标「拟议」、AC-PKG-*/AC-OPTIONAL-* 打包职责归 P20（P2-2）。
7. `P08-FMT-*` 加权威转录通道说明；TEXT 行补「安装包实际导出」（P2-3）。
8. 修正 `:49` PASS 措辞、PNG↔单图等价、`:66` 性能口径引用（P2-4）。
9. 校正 `:31-42` 的 6 处 D04 来源指向，并标注 D04 §43.4 回收站自动清理（`doc/04:1690-1705`，默认「永不自动清理」`:1704`）在 D08 无编号 AC 的处置（P2-5）。
10. 扩展 `verify_scope.py:46-48` 零差量路径至 `doc/01`–`doc/08`+`doc/13`+`AD-001`，并把 `verification/P08/**` 全量纳入 `git diff --check`（P2-6）。

以上均为**文档级最小修订**：不改 D08、`doc/13`、冻结 wire、Schema、依赖或产品取舍；P09–P20 仍保持未释放。

---

## 10. 推荐下一步

1. **Codex（Owner）**：按 §9 逐条返修 P08 自有文档（仅 `doc/tasks/P08.md`、`verification/P08/**` 及 allowlist 内 Plan/STATUS/派生索引），在返修后的新固定 head 上重跑并入库带环境头的验证日志。
2. **Codex（Integrator）**：返修提交后重新派发 **DSH 非作者正式复审**并固定新的 `reviewed_head`（`09_COLLABORATION.md:155`：分支变化不延用旧批准）；本报告仅对 `490f9bd` 有效。
3. **边界提醒**：本报告不代表 P08 done，不代表 Codex 已完成集成；P08 仍需在 findings 闭合 + Codex 集成检查通过后才可标 done，P09 及以后必须分别释放。
4. **无需本会话其他下一步操作**；不写入任何报告文件（原始输出由调用方保存）。

---

### Findings 处置表（Disposition）

| ID | 级别 | 状态 | 类别 |
|---|---|---|---|
| P1-1 | P1 | **open（需 Owner 返修）** | 证据纪律 / Verification |
| P1-2 | P1 | **open（需 Owner 返修）** | 验收权威与结果真值对账 |
| P1-3 | P1 | **open（需 Owner 返修）** | P1 实现责任缺口 / 发布判定风险 |
| P1-4 | P1 | **open（需 Owner 返修；可能需另立治理切片）** | Spec 内部矛盾 / legacy-baseline |
| P2-1…P2-6 | P2 | open（建议同轮收口） | 状态同步 / 依赖与路径 / 权威落点 / 措辞与等价 / 来源精度 / 验证器覆盖 |
| P3-1…P3-5 | P3/观察 | open（非阻断） | 措辞、列名、head 记录、既有治理不一致 |

DSH 本会话未修改、未 stage、未 checkout、未 commit、未删除或清理任何文件；未运行任何写操作或产品测试。
