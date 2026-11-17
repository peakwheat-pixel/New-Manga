# 新会话启动包 — New Manga 目标续接

- 生成时间：2026-11-16 15:45 (+08:00)（本版为 R16 之后更新 —— **Release Gate 条件 6 已关闭**）
- 生成者：DSH（lead）
- **当前 head：`b18a2ef90`**（main）；R16 收口链 = `45af57007`（内容，含四件套实测）→ `3cc4e1186`（证据）→ `b18a2ef90`（载体落值）→ 本文件所在提交
- 工作区：干净（`git status --porcelain` 为空）
- **R1**：`9ce819ae7` → `dd029b73f`（7 commit，目标 A/B/D 达成）
- **R2**：`dd029b73f` → `5f2664c2e`（8 commit）—— 目标 C 闭合 10 条
- **R3**：`5f2664c2e` → `bfbf95a82`（3 commit）—— 目标 C 再闭合 2 条
- **R4**：`bfbf95a82` → `8900dcbdb`（5 commit）—— 闭合 `MICA-FIX-1` AC2；**AC7 书面裁决落盘 + 开清理卡**
- **R5**：`8900dcbdb` → `a8ffd8a3d`（2 commit）—— 闭合 `V11R-A-3` AC4（该卡 **6/6 全闭合**）
- **R6**：`a8ffd8a3d` → `759b49730`（4 commit）—— 闭合 `RUN-IPC-1` AC4；**该卡门禁首次全绿**（顺带据实更正资源行）
- **R7**：`759b49730` → `650b2605e`（4 commit）—— 闭合 `V11R-C-1` **AC1/AC6/AC7**（该卡 **7/7 全闭合**）并补齐结构性表格，**门禁转全绿**
- **R8**：`650b2605e` → `b11689068`（3 commit）—— 闭合 `V11R-B-5` **AC1/AC2**（补 SCREEN_SPECS §6.5 + 上下文保留断言 + 结构性表格）
- **R9**：`b11689068` → `26519c9fd`（2 commit）—— 闭合 `V11R-B-5` **AC3**（六态显式映射 + 两条变红验证）；**该卡 7/7 且门禁全绿**
- **R10**：`26519c9fd` → `2e575c8f6`（3 commit）—— 闭合 `GATE3-COVERAGE-MATRIX` **AC2/AC4**；**该卡 6/6 且门禁全绿**
- **R11**：`2e575c8f6` → `691753f9d`（3 commit）—— 立 `FEA-04-IMPL-1` 实现卡 + 闭合 `M2-SFX` **AC4**；目标 C 41 条全部有处置
- **R12**：`691753f9d` → `bfa74707e`（4 commit）—— 推翻 R11 的判断：`FEA-04` 实现早已交付，8 条 AC 依据既有证据闭合；撤销 `FEA-04-IMPL-1`
- **R13**：`bfa74707e` → `dd7619675`（3 commit）—— 闭合 `GOV-RESIDUAL` **AC6**（补第 7 类「保护集合回退」负例 + 变红验证）。目标 C → 闭合 40 / 仅剩 1 BLOCKED
- **R14**：`dd7619675` → `df2f7aef6`（2 commit）—— 三项 Ruling A/B/C 落盘 + Ruling A 执行（L1 清除）；清理卡 AC1 闭合
- **R15**：`df2f7aef6` → `74b2a704a`（5 commit）—— **Ruling D 新出 + Ruling C 实施**；清理卡 **AC2/AC4/AC5** 闭合；**`GOV-RESIDUAL` AC7 经独立复核 approved 后闭合（7/7）⇒ 目标 C 41/41**
- **R16（本轮）**：`74b2a704a` → `45af57007`（+ 证据 `3cc4e1186`、载体 `b18a2ef90`）—— **Release Gate 条件 6 关闭**：冻结 head 上四件套实测 + MAINT-1 三节载体 + 独立最终 Review 登记 + §3.2-③ 三指针精度修复（13/13 卡 PASS）+ P1-1 处置

> 本文是**给下一个会话的唯一起点**。不要重读历史对话；按「下一步队列」推进即可。

---

## 0. 三十秒状态快照

| 项 | 状态 |
|---|---|
| HEAD | `b18a2ef90`（main；R16 收口链见上） |
| 四件套 | **全绿**（head `45af57007` 实测）：`check.ps1` PASS(3w) / `verify_pins` 18/18 / `api_inventory` 1/80/6=87 / `test.ps1` EXIT=0 **1591/1639 passed, 48 skipped**（App 969/0/4；skip 未增） |
| Release Gate 条件 6 | ✅ **已关闭**（R16）—— 见 `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md`；Gate 总体仍 `BLOCKED`（条件 3/4/5） |
| 上一 goal | 已用尽 100 轮（见 `GOAL-WRAPUP-R100.md`） |
| 本 goal | 60 轮上限 |
| 目标 C | 可行动项 41 → **闭合 41 / 0 剩余** ✅ |

复跑四件套：

```powershell
cd "G:\CODEX\New Manga"
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1
python tools/generate_api_inventory.py --check
$env:NEWMANGA_WORKSPACE_ROOT = "G:\CODEX\New Manga.workspace"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1
```

⚠️ **`test.ps1` 会改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/{immersive-reader.png, render-info.md}`**
（测试副作用）。跑完必须 `git checkout -- verification/READER-OVERLAY-HEADLESS-PNG-1/` 再提交。

---

## 1. 原目标与达成情况（R3 更新）

| 目标 | 状态 | 缺口 |
|---|---|---|
| **A** 四件套持续通过 | ✅ **达成** | — |
| **B** Release Gate 六条逐条判定 + 映射表 | ✅ **达成（R1）** | — 见 `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| **C** 已登记技术债清零 | ⚠️ **未达成（R2+R3 推进 41→20 闭合 / 21 open）** | 剩 **21 条**：`FEA-04` 8（需另立实现卡）+ `V11R-B-5` 3 + `GOV-RESIDUAL` 2 + `GATE3-COVERAGE-MATRIX` 2 + `V11R-C-1` 2 + 其余 4 条各 1 |
| **D** 剩余仅 HUMAN-REQUIRED 登记 | ✅ **达成（R1，R2 又收窄 H-02）** | `MICA-FIX-1` AC2 判定并入 `H-01`；新增 `H-10`（阅读器 overlay）；`H-08` 签名表述更正；**`H-02` 由 3 大项收窄为 3 小项**（ADJ §7.21） |

---

## 2. 下一步队列（按建议顺序，可直接接手）

### 队列 0 —— **`GOV-DECLARATION-SCAN-CLEANUP-1` AC3：154 → 0**（进行中：已 154→147）

**进度（R23，最新）**：`GOV-DECLARATION-SCAN-CLEANUP-1` **已关闭（status: done）**——AC6 独立复核 `ac6-reviewer` 三轮收敛后
两项 P1 全 PASS；卡片补齐 `## Canonical Evidence`（17 行 BLOB 基准）/`## Resource Manifest`/`## Closeout Record`。
最终读数（关闭后复测）：**errors 0 / declarations 6828 / protected_roots 5629 / warnings 823**（比冻结 head 多的 +18 根，
来自卡片自身 Resource Manifest 被解析为声明表）。仓内 `ac3-after-audit-2026-11-16.json` 记录这一最终轮（sha `8318bdda`）。

**进度（R22）**：复核 P1（FEA-15 误配）与 P2（13 处未闭合反引号等）已返修 —— 45 个文件整体还原到 `23e8d7152`
后用**严格匹配**（完整单元格键 + ≥60 字符前缀容忍 + 整格重建）重放；实测 errors **0**、declarations 6800、
protected_roots 5611、warnings 822（+1 是恢复真实的 `DECL_SOURCE_NOT_A_PATH`）；`ac7-allowed-cells` 改为**由 diff 反向生成**
（99 单元格 / 45 文件）。⚠️ 教训：**audit=0 不能替代语义正确性** —— 短键前缀匹配会把 `G:/CODEX/New Manga` 误吸成更长路径。

**进度（R21）**：**`errors 154→0`**（AC3 与 AC7 均 `[x] <<MET>>`）。B1 64 / B3 11 清零；16 条活 pin B2 转可审计保留态
（`DECL_PINNED_DEFECT_RETAINED`，新增 HIE-R016 覆盖 `LEGACY-SHELL-ARCHIVE-1` 的 archive 证据行，WORKTREE 通道）；
其余 64 条未钉住 B2 按 `ac7-allowed-cells-2026-11-16.md` 做单元级修复（45 张卡、48 文件、+121/−84 行），
`protected_roots 5593→5611`、`declarations 6765→6800`。**剩 AC6**（固定 head + 上下文独立 Review + 前后两轮 JSON 回填）。

**进度（R20）**：`errors 154→65`；B1 64 / B3 11 已清零，**15 条活 pin B2 转可审计保留态**
（`DECL_PINNED_DEFECT_RETAINED` 警告保留原始错误码 + pin 卡片/证据/commit/sha），剩 **65 条未钉住 B2** 待 AC7；
`protected_roots 5593→5601`。**新登记的治理缺陷**：`doc/tasks/FEA-11-HOST-AUTH-2.md` 的 `EV-11` 对
`doc/tasks/FEA-11-HOST-AUTH-3.md` 的 pin **已失效**（钉 4a7e1ca8…，实测 worktree 6b540148… / blob 21818135…）⇒ 不作活 pin 处理，
单独登记，修它需动终态证据行（另立治理动作）。

**进度（R19）**：**B1 64 与 B3 11 已全部清零**，`errors 154→80`（只剩 B2 80）、`protected_roots 5593→5601`。
batch 3 新增顶层 `table_bindings`（64 条，逐表：section + table_start + block_sha256（原始字节含 CRLF）+ header/第二行/行数
+ 该表精确诊断），代码按 (origin, section, start) 定位唯一表并只移除该表诊断，另加 `PROTECTION_REGRESSION` 超集断言；
`HISTORICAL_EVIDENCE_DIGEST` 再重批。逐条处置映射见 `ac3-disposition-map-2026-11-16.md`（154 行，带机制）。
⚠️ 新坑：任何「原始字节」哈希必须 `read_bytes()`，`read_text()` 会做换行转换 ⇒ block 哈希全崩、HIE 整体 RECORD_DRIFT（errors 反弹到 160）。

**进度（R18）**：**B3 11 条已全部清零**，`errors 154→144`、`protected_roots 5593→5601`。
batch 2 把 HIE 层的绝对计数耦合改成成员不变量（`HISTORICAL_EVIDENCE_BINDING_IDS` / 派生 `removed`/`pending` /
`HISTORICAL_EVIDENCE_KEEP`），新增 HIE-O04（NUL markdown）与 HIE-O05/O06（不可解析 JSON）三条 `raw_non_declaration_bindings`，
JSON 绑定带「一旦变合法 JSON 即 RECORD_DRIFT」的 fail-closed 条件，`HISTORICAL_EVIDENCE_DIGEST` 已重批；
新测试 `test_historical_binding_policy.py`（10 项）。证据 `ac3-batch2-raw-bindings-2026-11-16.log`。
⚠️ 踩坑：`test_architecture_assertions` 会往 `doc/STATUS.md` 追加一段散文再跑 check.ps1 ⇒ STATUS 必须留 ≥17 B 余量
（我一度涨到 3190 B 使该测试转红，已压回 3161 B）。

**进度（R17）**：裁定已由 **Codex** 出（`APPROVED_WITH_CONDITIONS`，见
`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-CODEX-RULING-2026-11-16.md`）；
归属表已冻结（`verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-baseline-disposition-2026-11-16.md`，154 行逐条
带 err_id/桶/活 pin）；**batch 1（Q3 封闭别名表）已实施**：`errors 154→147`、`warnings 732→740`、
`protected_roots 5593→5598`、`declarations 6755→6762`，`DECL_UNKNOWN_DISPOSITION 8→0`；
证据 `verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-batch1-alias-2026-11-16.log`。
**下一步**：**AC6 集成复验**（唯一剩余 AC）——固定 head → 交上下文独立 Reviewer（Codex 或 DSH 派的新子 agent）→
回填 baseline/after 两轮 `--audit-declarations` JSON → 回填 `GOV-RESIDUAL` 的 AC6/AC7。
> 历史（已完成）：**AC7 单元修复**。
**修复计划已落盘**：`verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac7-repair-plan-2026-11-16.md`
（46 条机械可执行 + 19 条需判定；每条含 ERR-id / 文件 / locator / 字段 / 现值 / 拟改为 / 拟 disposition / 置信与说明）。
下一轮照该表逐文件应用（只改值匹配的单元格），每批后重跑 audit 记录单调下降，65→0 后进 AC6
（固定 head + 上下文独立 Review + 前后两轮 JSON 回填）。
**卡已加 AC7**（`<<PARTIAL>>`）与 AC5 追加式窄例外。剩余 errors = **80 = B2 80**（其中 12 条活 pin 只登记）。

### 队列 0 附录 —— 原 R16 评估（保留）

R16 已在 A2 head 上复核并重推归属表（**不要再用 Ruling B 的 166 条旧数**）：

- **权威基线（R16 实测，head `45af57007`）**：`python -B tools/governance/clean_workspace.py --audit-declarations --out <workspace>` →
  `154 error / 732 warning / 6751 declaration / 5589 protected root`；code 分布与 `6a408e5aa` 的 154 条**逐项一致**
  （本轮新增 22 declaration、4 protected root，**零新增 error** —— 新表若写错会立刻计入，务必 parser-clean）。
- **按 Ruling B 的 code→桶冻结映射重推**：**B1 64**（`TABLE_SCHEMA_INCOMPLETE` 53 + `TABLE_DELIMITER` 10 + `TABLE_ROW_ARITY` 1）/
  **B2 79** / **B3 11**（`DECL_UNKNOWN_DISPOSITION` 8 + `JSON_PARSE` 2 + `FILE_UNREADABLE` 1）。
- ⚠️ **B2 里有 12 条被"活 pin"钉死**：分布在 8 个 `verification/**/RESOURCE-MANIFEST.json`，且每份都被其终态卡的
  Canonical Evidence 以 sha256 钉住（例：`doc/tasks/FEA-07-RESIDUAL-3.md` 的 `EV-R4B-10`）。按 Ruling B 硬约束 2 ⇒ **只登记、不修改**。
  ⇒ **AC3 无法靠纯数据修复把 errors 降到 0**，必须先出一道书面裁定，明确「活 pin 文件的 B2 走 B1 式解释层绑定（逐 origin + 行号 + raw sha）」。
- 其余 **67 条 B2** 全在 `doc/tasks/*.md`（约 46 张历史卡的 Resource Manifest 表），可修但**需要 scope 冻结**（改历史卡字节）。
- B3 11 条是**规则**问题（`DECL_UNKNOWN_DISPOSITION` 多为 `PRESERVE` 这类裸 disposition、`JSON_PARSE` 2 份不可解析 JSON），出规则裁定而不是改数据。
- 估时：3 批（B3 规则 1 轮 → B1 绑定 1–2 轮 → B2 67 处 2–3 轮）+ 独立复核 1 轮；**每批后 `errors` 必须单调下降**，且 `protected_roots >= 5582`（现 5589，不得缩小）。

### 队列 1 —— ~~目标 C：剩余 21 条可闭合 AC~~（**R15 已 41/41 全部闭合，本表保留为历史素材**）

素材：
- `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`（41 条可行动项）
- `verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md`（384 行，**逐条明细 + 判定依据**）
- `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md`

**已闭合 12 条**（不要再做）：
R2：`RELEASE-PACKAGE-1` AC6 / `CHAPTER-MANUAL-SORT` AC10 / `M2-REGION-RETYPE-CORE` AC6 / `MICA-FIX-1` AC4 /
`FEA-07-AC5-NATIVE-1` AC-N2 + AC-N5 / `V11R-B-3` AC4 / `V11R-B-4` AC4 / `V11R-B-5` AC4 / `V11R-C-1` AC4。
R3：`V11R-C-3` R1（补 tag 存在后的 `-DryRun` + limitation L-C3-1）/ `V11R-B-4` AC3（补 partial/loading 断言 + 变红验证）。

⚠️ **进度统计的教训（R2 踩过、R3 又需注意）**：**不要信 `classification-v2.md` 的行号**——
它已漂移，且部分条目早已 `[x]`。统计必须**逐卡读真实 checkbox**（R2 因此把 23 报成 33）。

**剩余 21 条，按可动手性排序**：

| 优先 | 卡 | 未勾 AC | 性质 | 已核实的入手点 |
|---:|---|---|---|---|
| 1 | `FEA-04` | AC1–AC8（8） | **实现** | **需另立实现卡**；范围已冻结（`:88-97`，8 条均 `- [ ] **ACn …**`） |
| 2 | `V11R-B-5` | AC1 / AC2 / AC3（3） | DOC + IMPL | AC1 = `doc/plan/V11R_SCREEN_SPECS.md`（102 行）缺导出预检/术语章节；**AC2/AC3 是 Export/Terms 页**（Tools overlay），需针对该子 VM 取证——可仿 `V11R-B-3` 的 `ContextRetention_PageBatchSwitch_*`（`V2StudioPageTests.cs:508`）与 `V11R-B-4` 的六态写法 |
| 3 | `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | AC6 / AC7（2） | IMPL + RERUN | AC7 **实际不可闭合**：需清理 160 处历史声明错误（7 处裁定身份必须保留），会碰历史证据字节 ⇒ 建议改判 `BLOCKED` 并写明；AC6 = 第 7 类「保护集合回退」负例测试 |
| 4 | `GATE3-COVERAGE-MATRIX` | AC2 / AC4（2） | DOC（大） | AC2 已有 progress 稿 `verification/GATE3-COVERAGE-MATRIX/ac2-four-cells-progress.md`（4 格已补），但整张矩阵仍缺逐行断言说明；AC4 需核 100 项 NOT_RUN 归因 |
| 5 | `V11R-C-1` | AC6 / AC7（2） | IMPL+DOC | 引擎卡；AC6 = 单测/截图，AC7 = 证据目录整理 |
| 6 | `MICA-FIX-1` | AC2（1） | RERUN | 需跑 `--diagnostics` 留原始日志（会起 GUI，Agent 可用 `[System.Diagnostics.Process]::Start`）；人眼判定已并入 `H-01` |
| 7 | `V11R-A-3` | AC4（1） | IMPL | `CommandParityContractTests` 66 条 parity 断言 |
| 8 | `RUN-IPC-1` | AC4（1） | IMPL | typed 拒绝单测（`ControlRun` 非法 action → `INVALID_REQUEST`；`StartRun` 幂等键复用 → `IDEMPOTENCY_KEY_REUSED`）+ allowlist 断言；AC4-3 成功往返仍 NOT_RUN（缺夹具） |
| 9 | `M2-SFX-CORRECTION-EXPORTER` | AC4（1） | IMPL | T1b 批量产物尚不存在，需先生产 |

⚠️ **R2/R3 发现的重要事实**：
- `RELEASE-PACKAGE-1.md` **实测 NUL=0** ⇒ 队列 5 的「NUL 字节」债项**不存在**，已结案；
- **225 张终态 lifecycle v2 卡没有 `## Canonical Evidence` 节**（实测 `doc/tasks/*.md` 中
  `status: done|closed_with_limitations` 共 608 张，其中 225 张无该节）。`check.ps1 -TaskPath <某张这类卡>`
  因此会报 `EVIDENCE_BASIS_HEADER_INVALID` / 「必须列出 canonical evidence」/「必须逐项填写 Resource Manifest」。
  **不要把这类 FAIL 当成本轮引入的回归**：治理 §4.3 明确 v1/v2 Task「保持原状，不回溯补标」，
  且**全局 `check.ps1` 不受影响（PASS）**。⇒ **不要逐卡补表**（225 张不现实），本卡族已多次踩到这个噪音。
- 裸值类 AC 的准确口径是「**无未登记**的裸间距」，由两个可执行测试守护
  （`V2StudioConformanceTests` 白名单 + `R14ContractTests`），不是「零裸值」。
- **Studio 证据落点**：`StudioEvidence.Write` 默认写 `%TEMP%/newmanga-evidence/<task>/`，
  只有设 `NEWMANGA_EVIDENCE_SYNC=1` 才写 `verification/<task>/`。
  ⇒ 想让测试直接产出到仓库，跑测试前设该变量；否则要手动 copy（R3 是手动 copy 的）。

### 队列 2 —— ~~目标 B 的延伸：条件 6~~（**R16 已完成**）

条件 6 已关闭，逐项证据见 `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-2026-11-16.md` 与
`verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/`。**不要再重做**这四项。
Gate 剩下的是条件 3（人眼目视 overlay）/ 4（签名 + 真机安装矩阵）/ 5（人工 GT 质量基线），均需人。

### 队列 3 —— 队列 5 小债（低优先）

- ~~`doc/tasks/M2-REGION-RETYPE-CORE.md` 重复 `integration_commit` 键~~ → **R24 已删除**（保留真实值 d8019810）
- `doc/REBASELINE_PLAN.md` 第 56/58 行漂移（**R16 已修**：表外枚举补齐 9 张非终态卡、`BLOCKED：FEA11-ENTRY-MISSING-1`、
  `SIDECAR-REBUILD-1` 行改 `in_progress`；现 6972/7000 bytes、64/64 lines，**加行前必须先压缩**）
- ~~`test.ps1` 改写 `verification/READER-OVERLAY-HEADLESS-PNG-1/`~~ → **R15 已修**（`GOV-TEST-SIDE-EFFECT-1`）：
  该测试改为从 `NEWMANGA_READER_OVERLAY_EVIDENCE_DIR` 取输出目录，`test.ps1` 非 `-CanonicalEvidence` 时指向 workspace 证据根；
  实测全量 `test.ps1`（1591/1639 passed, 48 skipped, exit 0）后 `git status --porcelain verification/READER-OVERLAY-HEADLESS-PNG-1` **为空**；
  证据：`verification/GOV-TEST-SIDE-EFFECT-1/ac3-no-side-effect-2026-11-17.log`。
- ~~**EOL 前提**~~ → **R24 已根治**：Codex 裁定 `doc/reviews/GOV-EOL-PIN-1-EXT-CODEX-RULING-2026-11-16.md`
  （`APPROVED_WITH_CONDITIONS`，Q1=A/Q2=C）→ `.gitattributes` 只给 `doc/REBASELINE_PLAN.md` / `doc/STATUS.md`
  加 `text eol=lf`（未扩大、未提预算）；实测新鲜 clone：6939 B / 3156 B、0 个 CRLF 行、`check.ps1` PASS。
  同时按 Q2=C 给 14 条 WORKTREE 口径保留态登记「经验证的对照摘要」（`sha256_alt` + `alt_kind`），
  校验只接受这两个精确摘要且告警写 `pin_basis`。证据：`verification/GOV-EOL-PIN-1-EXT/eol-execution-2026-11-16.log`。
  **仍建议**：恢复 doc 字节优先用 `git cat-file blob` + 二进制写（LF 规则只覆盖这两份）。
- ~~`doc/tasks/RELEASE-PACKAGE-1.md` 含 NUL 字节~~ → **R1 实测 NUL=0，已不存在**

### 队列 3b —— **`GOV-EVIDENCE-PIN-REPAIR-1`（R24 释放，R14 已 `done` 收口）**

> **收口摘要（2026-11-17）**：AC1–AC7 全 `<<MET>>`；四轮上下文独立复核（REJECTED ×3 → APPROVED）；
> 证据 pin 待判 **445 → 4**（2 条带 class 的占位行 + 2 条多路径行仅巡检工具建模限制）；33 张有登记项的卡全部 PASS；
> 例外通道 13 项 + 批量证据 8 项 + EOL 7 项测试全过；全局门禁 PASS。以下为过程记录，保留备查。

- 来由：Codex 裁定（`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-CODEX-RULING-2026-11-16.md`，`APPROVED_WITH_CONDITIONS`）
  Q1=D：先建独立修复卡、再对终态卡 **append-only** 追加 `EV-11-supersede`；Q3 要求提供只读巡检。
- **已完成（AC1/AC2）**：`tools/governance/audit_evidence_pins.py`（只读，12 项测试，`judge()` 纯函数）；
  全仓基线 **7,080 行 / 445 FAIL / 103 卡**（SHA_MISMATCH 110、SHA_NOT_64_HEX 214、PATH_MISSING 109、
  COMMIT_NOT_FOUND 12），4 类各抽样 1 条均为**真实失效**；全仓耗时 183.4 s ⇒ **不并入 check.ps1**。
  证据：`verification/GOV-EVIDENCE-PIN-REPAIR-1/ac1-ac2-baseline-2026-11-16.log`。
- **已完成（AC3 内容部分）**：`FEA-11-HOST-AUTH-2` 追加 `EV-11/12/13-supersede`（完整 commit + 64 位 sha256 = blob、
  与工作树逐字节一致；git diff 11 insertions / **0 deletions**）；巡检新增 supersede 语义 + 2 项测试。
- **新裁定（门禁例外通道）**：`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-GATE-RULING-2026-11-16.md`
  （`APPROVED_WITH_CONDITIONS`，**Q1=B**：不让 check.ps1 自动识别 supersede，改**逐行受控 allowlist**；
  资格基线冻结 `8db997f9…`；一行一指纹；替代行仍严格校验；Resource 不受豁免；卡片转非终态即失效）。
  ⇒ 巡检工具的 `SUPERSEDED` 只是**诊断**，不构成门禁通过。
- **AC4 分诊已出**（`verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-triage-2026-11-16.{md,json}`）：
  T1 122 / T2 211 / T3 109 / T4 3（共 445 / 103 卡），只用于排期，**不构成豁免**。
- **事实更正**：`check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-2.md` 在本次改动**之前**就已是 7 errors
  （5 条 SHA 不匹配 + 2 条 Resource「—」），全局 check 的 15 文档作用域从未覆盖它。
- **已完成（AC6）**：受控例外通道落地 —— `tools/governance/evidence-pin-exceptions.json`（schema_version 1，
  资格基线 `8db997f9…`，当前 entries 为空）+ `check.ps1` 精确匹配降级（资格校验在门禁内执行：基线终态卡 + 行逐字存在 + 字段全等；
  不满足即 `EVIDENCE_EXCEPTION_INELIGIBLE` 并仍报错）。9 项测试全过；全量 118 tests OK；
  `check.ps1` 1.18 s（改动前 1.19 s，< 10 s 要求满足）。证据：`verification/GOV-EVIDENCE-PIN-REPAIR-1/ac6-exception-channel-2026-11-16.log`。
- **AC4 进度（R6）**：口徑修訂後全仓 FAIL **445 → 310**。关键发现：我在 batch 1 两次把「记录值不可复现」写进例外理由，都是因为只 hash 了**原始 blob**；实测 130 条「路径已清理/摘要不符」的行，记录值恰好等于 commit blob 的 **CRLF 形态**（EV-01/EV-03 就是 closeout 提交 f7016d3fb 下 blob 的 CRLF 形态）⇒ 它们是**有效的 worktree 口径 pin**。巡检工具已接受 blob 的原始/LF/CRLF 三种精确形态（`BLOB_EOL_MATCH`），五条例外理由全部改写为已核实事实。
- **教训（写进 STARTER 供后续复用）**：断言「某摘要不可复现」之前，必须穷举所有登记表示（原始/LF/CRLF × blob/工作树）；只查一种就会把有效 pin 判成缺陷。
- **新裁定（EOL 门禁）**：`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-EOL-GATE-RULING-2026-11-16.md`（`APPROVED_WITH_CONDITIONS`，Q1=A）：
  六列历史行接受 commit blob 的**原始/LF/CRLF 三种精确形态**；七列显式 basis 不变；新行必须七列；
  行尾推断仅限冻结基线中已存在且字段未变的行；三种都不匹配仍报错。**实现与 3 正 4 负测试未开始（卡片 AC7）**。
- **已完成（AC7，R7）**：门禁接受 blob 行尾形态 —— `check.ps1` 六列历史行现在按「工作树原始 → blob 原始 → 行尾形态」顺序判定，
  行尾推断仅限冻结基线中已存在且字段未变的行；**混合行尾不产生派生形态**；七列显式 basis 不变；
  命中行尾形态会输出可见 warning。7 项测试全过（3 正 4 负），全局门禁 **1.10 s**。
  效果：`HOST-CORECLIENT-1` FAIL 55 → PASS(60w)；`FEA-11-HOST-AUTH-2` 只剩 3 条 registry 例外。
- **第三次口径修正（重要）**：旧六列 schema 的语义是「commit **或** sha256」，所以 `sha256=null` 而 commit 有效的行
  是**合法 pin**；我的工具此前判 FAIL。修正后全仓待判 **445 → 98**（SHA_MISMATCH 31 / PATH_MISSING 53 /
  无摘要且无 blob 2 / commit 不可解析 12，34 张卡；集中在 P02PRE-R1H-H2-COLLECTOR 27、P02-NEW-TIME-X6 15）。
- **教训（三次同类）**：判「证据失效」前必须先把该 schema 的**合法表示集**穷举完（原始/LF/CRLF × blob/工作树；commit-only 也是合法形态）。
- **AC4 batch 2（R8）**：`P02PRE-R1H-H2-COLLECTOR` 31 errors → **PASS**(41w)（27 条仓外产物逐条例外 + 5 处 Resource 单元改 ALREADY_ABSENT）；
  并对全仓逐行登记 67 条（理由四类：历史可复现但 commit 列缺记载 3 / 仓外已清理 17 / 仓内已删 45 / 仓内漂移 6），
  登记表共 **99** 条。同时修掉指纹比较的两处实现缺陷（未剥离反引号、空 commit 与 `-` 不等价；非十六进制 commit 统一记 `-`）。
  现巡检 FAIL **51** / EXEMPTED 50（门禁与工具一致）。
- **已知未完成**：51 条待判（多在 `P02-NEW-TIME-X6`(15, superseded)、`GOV-EVIDENCE-UNIQUE-1`(4)，其余每卡≤3）；
  4 条无摘要行因登记表 schema 要求 64 位摘要而**无法登记**（需 schema 扩展或改行，后者被 append-only 禁止）；AC5 复核未做。
- **AC4 batch 3（R9）**：按新裁定（`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-EXCEPTION-HOOKS-RULING-2026-11-16.md`，
  Q1=A/Q2=A/Q3=结构非法）新增两个例外钩子 **COMMIT_FORMAT**（散文 commit，逐字记录才降级）与 **SHA_MULTI**（有序摘要列表），
  并把整行 `-` 判为「行结构非法」且不进例外通道；同时修掉「单元格反引号未剥离导致条目永不命中」的实现缺陷。
  登记表 97 条（PATH_MISSING 51 / SHA_MISMATCH 34 / COMMIT_FORMAT 12）。
- **AC4 batch 4（R10）**：9 张卡收口（`FEA-GOV-4/5/6/7/8/9/10`、`FEA-05-PORT-1`、`FEA-05-WIRE-1` 全部 PASS）。
  手法：12 条散文 commit 行登记 COMMIT_FORMAT+SHA_MISMATCH 双指纹；2 条多路径/多摘要行登记 SHA_MULTI+COMMIT_PATH_MISSING；
  9 张卡补 Resource Manifest 表格；FEA-GOV-5 AC1 补勾选与 verified 注释；3 张卡按当前 blob 追加新证据行。
  本轮 9 张卡全部 PASS（**注意**：33 张有登记项的卡里仍有 16 张因 Resource Manifest/证据目录等问题 FAIL，见 AC5 复核）（2 条多路径行仅巡检工具建模限制、2 条空壳行按裁定 Q3 保留）。
  登记表 **114** 条；例外通道测试 10/10、EOL 测试 7/7 全过。
- **AC4 batch 5（R11）**：33 张有登记项的卡 **32 PASS / 1 FAIL**（更早一轮 16 FAIL，上一轮 1 FAIL）。手法全是元数据修正：
  PRESERVE_* 目标已消失 → ALREADY_ABSENT；DELETE_SAFE 声明不实 → PRESERVE_USER_DATA；manifest 指针改指仓内可验证文件；
  补 Resource Manifest 表格；integration_commit/closeout 补齐；两处摘要漂移更新并把原值留在末列。
  连带修：改别人的卡导致 FEA-DOC-RECONCILE-1 的钉失配 → 逐条例外；批量脚本误改表头 → 已恢复。
- **AC4 batch 6（R12）**：按裁定实现 `evidence_dir/EVIDENCE-MANIFEST.json` 批量证据机制（仅 research；门禁递归枚举并重算，精确集合相等；8 项测试全过），`DISPLAY-PERF-DECISION-1` 以 245 文件清单收口（1 个 .pyc 编译缓存移到 workspace archive，见复核处理） ⇒ **33 张有登记项的卡 33 PASS / 0 FAIL**。
  注意：`ALREADY_ABSENT` **不是**允许的 disposition（实测被门禁拒绝），已消失资源应写 `PRESERVE_UNKNOWN`；
  其他卡上遗留的 ALREADY_ABSENT 用法需统一（虽当前通过）。
- **待做（AC5）**：第二轮整卡独立复核
- **待做（旧清单）**：剩余按卡处理 —— ①同一行还需补登记 SHA_MISMATCH；②`FEA-GOV-10` 等卡缺 `## Resource Manifest` 整节；
  ③2 条多摘要行应登记 SHA_MULTI，2 条空壳行按裁定保留错误。余 **51** 条（SHA_NOT_64_HEX 214 / PATH_MISSING 53 / SHA_MISMATCH 31 / COMMIT_NOT_FOUND 12）按类逐条归因 → 逐条登记或修 pin → 上下文独立复核；另需就「check.ps1 是否接受 blob 的 EOL 形态」取得裁定（当前门禁只比对原始 blob 与当前工作树，会把这些有效 pin 判红）。
- ⚠️ 已更正事实（2026-11-17 第二次更正）：EV-11 的值是 **64 位**合法 sha256；此前的「本仓无任何字节表示能复现」是**错的** ——
  记录值恰等于 closeout 提交 `5cbec0e8` 下该文件 blob 的原始字节（已逐字核实），原行的问题是 commit 列缺记载。

### 队列 3c —— 带 class 占位行 + superseded 卡口径（R16 已裁决定案）

- 裁定：`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-PLACEHOLDER-RULING-2026-11-17.md`（Codex，Q1=D/Q2=A）。
- 实现：门禁在 Canonical Evidence **原始行**上检查必填字段；缺字段行**不计作证据**，
  本卡另有完整行时只报 warning，全卡无完整行则报 error；分隔行判定要求至少三个连字符（避免把 `| - | …` 当分隔行）。
- 实测：`FEA-05-WIRE-1` / `FEA-GOV-6` PASS(4w)（其中一条 warning 即该无效行）；例外通道测试 13/13。
- `superseded` 卡的 15 条：门禁不校验，巡检标 `NOT_ENFORCED`，逐条可见、不进失败计数。

### 队列 3d —— `GIT-CLEAN-RUST-CAPACITY-DESIGN-1`（ZCode 设计已交付）

- **已完成（R17-R18）**：ZCode 交付设计 → 独立复核三轮（v1 BLOCKED 4 P1 → v2 BLOCKED 2 P1 → **v3 RELEASABLE，P1=0**）；
  DESIGN.md 现为 v2 正文 + DSH 附记 v3/v4；量测：`verification/GIT-CLEAN-RUST-CAPACITY-DESIGN-1/DESIGN.md`（37.9 KB）。
- 卡片 AC1-AC4 全 MET，`status: in_review`（**设计可释放，但未实施**：产品源码零改动、压力测试未跑）。
- **待做**：①DSH 集成裁决（approve / 立实施 Task，实施须重新冻结范围并新 Appointment）；②P2 三条随实施处理
  （补 `GuardFinishReport` 结构定义、修正「Drop 不会重入」措辞、评估 `cleaned=true` 后 panic 路径）。


### 队列 5a —— 复核者改派（2026-11-17 用户确认，Lead 执行）

- **决定**：`reviewer: Antigravity` 的非终态卡，一律改派 **ZCode 或上下文独立的新子 agent**；不再使用 Antigravity（2026-10-31 裁决已令其退出 Owner/Reviewer/派发名单）。
- **适用范围（当前 2 张）**：`GIT-CLEAN-PUBLICATION-1`（in_review）、`GIT-CLEAN-CORE-ENV-2`（proposed，释放时同步改派）。
- **执行方式**：在**真正指派复核的那一刻**改 `reviewer:` 字段并记录复核者来源（子 agent 名/会话 ID，或 ZCode sessionId）；
  不得先改字段后补复核。
- **历史卡不动**：已 `done`/`closed_with_limitations` 卡上的 Antigravity 署名按 2026-10-31 裁决**保持原字节**，不改写。

### 队列 4 —— HUMAN-REQUIRED 等待项（不阻塞 Agent）

`doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 现有 `H-01`…`H-10`，
六条 Gate 条件的剩余动作已逐条映射（见 `RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` §8.2）。
**不要因等待人回复而停顿。**

---

## 3. R1 本轮完成的事（避免重复劳动）

| # | 事项 | 结果 |
|---|---|---|
| 1 | **`HOST-CONCURRENCY-FLAKY-1` AC6 二次+三次复核** | 三轮独立上下文复核：`reviewer-hcf`（CHANGES）→ `reviewer-hcf2`（CHANGES，代码侧放行）→ `reviewer-hcf3`（**ACCEPTED**）；定案 **`closed_with_limitations`**，AC1–AC6 全 MET，保留 L-1…L-4 limitation |
| 2 | 新增回归测试 | `HostFileIdNormalizationTests`（3 facts）——固定 53 位常量与 wire 口径；**做过回退红测**（`:414` 改回 raw ⇒ 红 ⇒ 还原绿）；`%TEMP%` 探针拿不到 `raw > 2^53` 样本时**直接 FAIL**（拒绝假绿） |
| 3 | 三次复核 P2 清扫 | 行号**第三次**同步（`:414/:638`、`TileChannel.cs:457`）、AC5 双数、控制字符 18 处、旧「并行」叙述四处作废标注 |
| 4 | **目标 B** | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md`（六条逐条：定义/判定/证据 commit+行号/剩余动作/归属） |
| 5 | **目标 D** | `HUMAN-REQUIRED` 更新：AC2 并入 H-01、新增 H-10、更正 H-08 签名表述 |
| 6 | 证据卫生 | 该卡 22 行 EV 全量校验（`git cat-file blob` + sha256，22/22 匹配）；发现并修复「`core.autocrlf=true` ⇒ 工作区 sha ≠ blob sha」的陷阱 |

---

## 3b. R2（本轮）完成的事 —— 目标 C 闭合 10 条 AC

| # | AC | 卡 | 依据要点 |
|---:|---|---|---|
| 1 | AC6 | `RELEASE-PACKAGE-1` | 五判据全满足：`check -TaskPath` PASS / `test.ps1` EXIT=0 / pytest 3569P·0F·10S vs 基线 3360P·10S / 9 条 pin / Handoff 已有。**并澄清** B1-DOC-CLOSE-1 那次 3 failed 是 sidecar schema v6 vs 数据根 v14 的**环境问题**，非代码回归 |
| 2 | AC10 | `CHAPTER-MANUAL-SORT` | App 962/0/4 + CoreClient 256/0/0 + pytest 3569P/0F/10S，skip 未增 |
| 3 | AC6 | `M2-REGION-RETYPE-CORE` | pytest 三套件 **1665P/0F/4S**（基线 650/1）+ `m2_acceptance` **37**（要求 35）；cargo/vitest 旧壳退役 ⇒ NA |
| 4 | AC4 | `MICA-FIX-1` | `test.ps1` 1582/1630 0 failed；pytest **failed 3→0**；旧壳 vitest ⇒ NA（`apps/desktop/package.json` 不存在） |
| 5 | AC-N2 | `FEA-07-AC5-NATIVE-1` | **新增 `V2KeyDispatchOnceTests`（3 facts）+ 变红验证**：注入重复全局手势 ⇒ 3/3 红且报「按键冲突 Ctrl+1」 |
| 6 | AC-N5 | `FEA-07-AC5-NATIVE-1` | **独立复核 `reviewer-fea07b` ACCEPTED（带 limitation）**；并修掉该卡 3 类 pin 缺陷（commit 错配 / WORKTREE 口径 / 旧版 README） |
| 7–9 | AC4 ×3 | `V11R-B-3` / `V11R-B-4` / `V11R-B-5` | 由**两个可执行一致性测试**守护（`V2StudioConformanceTests` 白名单 + `R14ContractTests`），裸值均在**已登记白名单**内 |
| 10 | AC4 | `V11R-C-1` | 引擎卡无 `.axaml` ⇒ 子项 NA；唯一 hex `#1F1F1F` 经核为**冻结 Fluent baseline 的 theme-layer 常量**（注释明写故意不入 token 字典） |

**R2 踩到并更正的错误（务必记住）**：
1. 我先按「分类行的行号」统计，报出 **33 条 open**，实际逐卡核对后是 **23 条** ——
   分类文档的行号已漂移、且部分条目早已 `[x]`。**统计必须逐卡读真实 checkbox，不能信派生快照。**
2. 我写的 `UnboundGesture_DispatchesNothing` 断言「Ctrl+D1 在 Studio/Batch 不匹配」**实测红** ——
   因为 `Ctrl+D1` 声明为 `Space=null`（**全局**），每个作用域都绑定。**是断言错，不是产品 bug**；
   已改为正确口径的 `GlobalShortcuts_ResolveInEveryScope_SpaceScopedOnesDoNotLeak`。
3. 一度把 `FEA-07` 的 `EV-AC5-03/04/05` 判为「sha 错」，实为 **WORKTREE 口径**（CRLF）；
   同一文件工作区哈希 = 声明值，而 blob 哈希不同 —— **又一次 `core.autocrlf` 陷阱**。

---

## 3o. R16（本轮）完成的事 —— **Release Gate 条件 6 关闭**

### 结果一句话
条件 6 由「未关闭 / `CONDITION_6_NOT_CLOSABLE`」改为 **已关闭**；Gate 总体仍 **`BLOCKED`**（条件 3/4/5 未开放完）。
提交链：`45af57007`（内容 + 四件套实测所在 head）→ `3cc4e1186`（证据）→ `b18a2ef90`（卡面落值）。四件套全 EXIT=0（`1591/1639`，48 skipped）。

### 四个剩余动作怎么做的（逐项）
| 动作（§6 L229-237） | 处置 |
|---|---|
| ① 冻结交付 head + 重跑四件套 | head `45af57007`，工作区 clean；`check` PASS(3w) / `verify_pins` 18/18 / `inventory` 1/80/6=87 / `test.ps1` EXIT=0；原始日志 `condition6-closeout/gates.log` |
| ② 给 MAINT-1 补载体 | 卡新增 `## Canonical Evidence`（7 列 / BLOB，8 行）/ `## Resource Manifest` / `## Closeout Record`；frontmatter 四字段落值 |
| ③ 登记独立最终 Review | `MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md` append-only 登记到卡面「轮次 36」+ `13_RELEASE_GATE.md`「条件 6 登记」 |
| ④ 修 §3.2-③ + 处置 P1-1 | 见下两节（**都与原文描述不同，是重核后才发现的**） |

### ⚠️ §3.2-③（P2-2）原文已过期，实际缺陷更重
CI 复核发现：PLAN 的 `表外节点` 枚举里混着**已终态**的 `AC-CHECKBOX-AUTHORITY-1`，同时**漏掉 5 张非终态卡**
（`DOC-CTRLCHAR-FIX-1` / `GATE3-MATRIX-EXPAND-1` / `GATE3-SETTINGS-SHORTCUT-1` / `INSTALLER-MATRIX-1` = `in_progress`，
`FEA11-ENTRY-MISSING-1` = `blocked`），且 `BLOCKED：无` 与之字面冲突 ⇒ 5 张卡 `-TaskPath` 实测 FAIL。
修后：`BLOCKED：FEA11-ENTRY-MISSING-1`，表外枚举 = 全部「无 DAG 行」的非终态卡（9 张，含 `GOV-DECLARATION-SCAN-CLEANUP-1`），
**13/13 非终态卡 PASS**。PLAN 6990→6960 B（压缩 8 处历史行冗余措辞，状态与 hash 未变，留 40 B 余量）。

### ⚠️ P1-1 的处置是"登记指针"，不是"改口径"
`MAINT-1-FEA-LINE-CLOSEOUT-v2` 的 Errata（`:58-66`）早已把 §3 收窄为「8 项实现 + AC8 PARTIAL ≠ 8/8 MET」；
本轮另核 `POST-ROADMAP:8` 与 `MAINT-2/README:5` —— 两处**没有**「8/8 MET」断言（后者原文即写 AC8=PARTIAL），故**不改字节**。
卡内「轮次 24」的历史记录按 Errata 读，不重写。

### 独立复核结果（`c6-reviewer`，新上下文、只读、未参与实施）
- **`APPROVED_WITH_FINDINGS`（P0=0 / P1=2 / P2=7）**，报告 `doc/reviews/MAINT-1-GATE-CONDITION-6-CLOSURE-REVIEW-2026-11-16.md`。
- 两条 P1 已处置：① 交付 head 与载体错位 ⇒ `integration_commit` 改为载体完成提交 `b18a2ef90`，`delivery_head` 仍为被测树
  `45af57007`，卡面写明「提交无法自证 ⇒ 逐代回填」；② PLAN 压缩误删 4 处披露字样 + 2 个 `done` ⇒ **已全部恢复**（PLAN 6972 B / 28 B 余量）。
- P2 摘要：`render-info.md` 副作用已复原（净零）；CoreClient 数字改为 **258/0/0**；GATE4 指针改为证据目录；
  **PLAN `SIDECAR-REBUILD-1` 行原写 `done` 而卡/台账为 `in_progress`，已改正**；余下 1 条 **EOL 前提** 见队列 3。
- ⚠️ 复核还实测出一条**仓库级风险（未修）**：`core.autocrlf=true` 下 fresh checkout 会把 `doc/REBASELINE_PLAN.md` 写成
  7024 B、`doc/STATUS.md` 写成 3205 B，**双双超预算**（本轮工作树是 LF 所以 PASS）。要根治需 `.gitattributes`
  给 `doc/**` 定 `text eol=lf` —— 属仓库级改动，下一轮若要动需先立卡。

### 本轮新踩的两个坑（已写进 §5）
1. **`git checkout` 恢复 doc 会写出 CRLF**：`core.autocrlf=true` 下 `git checkout -- doc/REBASELINE_PLAN.md`
   让工作树变成 7054 B，`check.ps1` 直接判预算超限。恢复 doc 字节要用 `git cat-file blob` + 二进制写，或写完立刻核字节数。
2. **新写的 Resource Manifest 会立刻进声明审计**：`%TEMP%`/`*`/`原路径`/`DELETE_SAFE（可重建）` 这类写法各产生 1 条
   `DECL_*` error（本轮先加 3 条、修净后归零）。新表必须用：占位符 `—` + `NOT_APPLICABLE`（两者同时才被跳过）、
   绝对路径、或 `DELETE_SAFE`/`ALREADY_ABSENT`/`PRESERVE_*` 这类**精确 token**。

## 3n. R15（本轮）完成的事 —— **目标四点全部达成**

### 结果一句话
`GOV-RESIDUAL` 的 **AC6/AC7 双 BLOCKED 全部解除**，该卡 **7/7 全闭合**；目标 C 由 40/41 → **41/41**。

### 本轮做了什么（按发生顺序，含两次「以为做完了其实没完」）

1. **Ruling A 之后又冒出两处同源漂移**（三层模型比裁决书写的更深）：
   - `clean_workspace.py:1848-1850` 把「第 4 条必须 untracked」**硬编码**在扫描器里 = policy 之外的第二份真值；
   - policy 里声明的那条错误 **message 文本**也写着 `untracked markdown …`（实际已 `tracked markdown …`）。
   ⇒ 同一个事实（tracking 状态）被复制在**三个地方**，`ee755d4bb` 一次入库就三连漂移。
2. **新出 Ruling D**：Ruling A 修好后 audit 报 `residual identity origin changed: doc/tasks/P19.md`。
   实测 RRI-01/02/03 同时绑整文件 sha（18443 B）与行级 :112/:113/:114；该卡被 `0e7bc1fc5`
   合法追加到 21306 B ⇒ 整文件 sha 失效，**而行级三份 sha 全部仍匹配**。
   裁定：**带行级身份时以行级为权威** —— 整文件 sha 对活卡是**过宽绑定**，不是更严的保护。
3. **Ruling C 实施**：`:2177` 去掉 `and len(index.errors) == 7`；`:2194` 的 `not staged.errors`
   （同样是绝对零耦合）换成「7 条裁定身份确实被移除」。
4. **结果**：`errors` 167→**154**、residual **0→7**、`protected_roots` 5582→**5585**、
   `PRESERVE_USER_DATA` 18→**21**；APPDATA 三根**按路径核验**回到保护索引。
5. **独立复核**（`gov-residual-ac7-reviewer`，DSH fresh 上下文独立，只读）：
   **`approved`（P0=0 / P1=0 / P2=5）**，报告 31332 B。复核席位亲自复跑三条命令并另用独立探针
   验证「守卫替换不是绿洗」。

### ⚠️ 本轮最该记住的两件事

**(1) 复核抓到我一条「假证据」。** 我交付的证据日志里「测试原始输出」段**是空的** ——
因为 `unittest` 把报告写到 **stderr**，而我的生成脚本只捕获了 stdout。复核用
`git grep "Ran 13 tests"` 全仓零命中把它揪出来。
⇒ **教训：任何「原始输出」类证据，必须 grep 回来确认它真的在文件里**，不能因为脚本没报错就以为抓到了。
（这与 R13「注入范围偏了测试会以绿的形式说谎」是同一类错误：**工具没报错 ≠ 结果正确**。）

**(2) 我给的被审 head 是错的。** 我告诉复核 `54b1167ee`，但那是我 `git commit --amend` **前**的悬空 commit
（其 HIE digest 常量与同 tree 政策不自洽，以它为 head 时 HIE 层必然 `POLICY_DIGEST_MISMATCH`）。
复核把 `reviewed_head` 固定为 **`983243488`** 并警告不可引用悬空 hash。
⇒ **教训：`--amend` 后必须立刻 `git rev-parse` 取新 hash 再对外引用；记录 head 前先确认它可达（`git branch --contains`）。**

### 未处置的 3 个 P2（已登记，非阻塞）
- **P2-2**：两处替换守卫在当前控制流下**不可触发**（dead guard，不是 fail-open；真正防线是 `:2133`），
  且 `:2187` 注释行号写错。
- **P2-3**：Ruling D 未覆盖风险 —— P19.md **非绑定行**漂移不再被本层拦截；
  RRI-01..03 的 `origin_raw_sha256`/`byte_length` 成了**不被校验的旧值**（18443 vs 实际 21306）；
  缺「尾追加应通过 / 无行级整文件绑定的整文件漂移应失败」两个测试。
- **P2-1** 已处置（head 统一记 `983243488`）。

### 目标四点状态（本轮后）
| 目标 | 状态 |
|---|---|
| A 四件套 | ✅ check.ps1 PASS(3w) / verify_pins 18/18 / api_inventory 1/80/6=87 / 本轮**未动 .NET**，App.Tests 基线 969/0/4 不受影响 |
| B Gate 六条映射表 | ✅ `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md`（23532 B），六条逐条显式判定（已关闭 1 / 调查关闭 1 / 未关闭 4，标注需人判·需人眼·Agent） |
| **C 技术债清零** | ✅ **41/41 闭合** |
| D HUMAN-REQUIRED | ✅ `HUMAN-REQUIRED-2026-11-15.md`(13896 B) + `HUMAN-VS-AGENT-SPLIT-2026-11-16.md` |

### 剩余可做（不属于原 41 条，属后续增量）
- `GOV-DECLARATION-SCAN-CLEANUP-1`：**5/6**（AC3 = Ruling B 的 154 条分类处置，多天级；AC6 = 集成复验）
- Release Gate **条件 6** 的 4 项「Agent 可全部关闭」项（映射表 L28 明确标注无需人）
- 3 个 P2 跟随项

---
## 3m. R14（本轮）完成的事 —— 三项 Ruling 落盘 + Ruling A 执行（L1 清除）

### 1) 三项书面裁定已落盘
`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-RULING-ABC-2026-11-16.md`（署名 DSH / Lead）：

- **Ruling A = 方案 (i)**：`HIE-O03.expected_tracking` → `tracked` + 重批 `HISTORICAL_EVIDENCE_DIGEST`
  （`3f4cae13…4b7d` → `5cc68358…aadd`）。
  否决 (ii)：`git rm --cached` 会反悔 `ee755d4bb` 的 406 文件入库决策 —— **应让政策追上事实，不是让事实退回政策**。
  否决 (iii)：tracking-agnostic 会把真实 fail-closed 削弱成 fail-open。
- **Ruling B = 按 error code 冻结三分类**：B1 历史形态 **64** / B2 真实缺陷 **86** / B3 规则误报 **16** = **166**。
  两条硬约束：先冻结归属表再实施；B2 修数据前须实测是否被**活 pin** 引用（被引用者只登记不修）。
- **Ruling C = 批准重写为「成员不变量」**：保留 `len(removed)==7`，把 `len(index.errors)==7` 换成
  「7 条裁定错误身份必须全部存在」的三元组成员检查，缺失仍 `ERROR_MISMATCH`（**fail-closed 不变**）。
  附 §4.4 两项实测：受影响调用面（精确形式全仓仅 `:2172`；生产调用点仅 `:2303`）+ 基线错误矩阵。

### 2) Ruling A 已执行 —— 且发现了**第二处真值重复**

**只改政策字段不够**：改完后 `SOURCE_DRIFT` 换成了同义错误 `POLICY_INVALID`
（"historical source tracking policy changed"）。

根因：`clean_workspace.py:1848-1850` 把「第 4 条必须 `untracked`」**硬编码**在扫描器里 ——
这是 policy 之外的**第二份真值**，必然随 `ee755d4bb` 过期，且与 `read():1718` 的检查**功能重复**。
处置：改为政策驱动的取值合法性校验（`expected_tracking in ("tracked","untracked")`），
字段值与真实状态的比对仍由 `read()` 负责 ⇒ **fail-closed 不变，仅去重**。

**三步实测（同一条命令，逐步收窄）**：

| 步骤 | `SOURCE_DRIFT` | `POLICY_INVALID` | `ERROR_MISMATCH` | residual warning | `protected_roots` |
|---|:--:|:--:|:--:|:--:|:--:|
| 基线 | **1** | 0 | 0 | **0** | 5582 |
| 改 policy + digest | **0** | **1** | 0 | 0 | 5582 |
| 完整执行 | **0** | **0** | **1** | 0 | **5582（未缩小）** |

⇒ **L1 已彻底清除；L3 成为唯一剩余阻塞**（`ERROR_MISMATCH` = `:2172` 的绝对计数耦合，正是 Ruling C 要改的）。
**这精确验证了裁决书的三层模型**，并实证「L1 确实是第一层」：清掉它之后才暴露出 L3。

### 3) ⚠️ 诚实更正：A 单独**不能**解 AC2
原设想「做 Ruling A 就能恢复 residual 层」经实测**不成立** —— residual warning 仍为 0，
因为 `ERROR_MISMATCH` 在 residual 层可应用**之前**就把它挡住了。
按 §4.4「核验结果与假设不符则假设作废」，已在裁定文中更正为：
**A 是必要不充分条件；A + C 才解 `GOV-DECLARATION-SCAN-CLEANUP-1` AC2。**

### 4) 字节保留核验（硬约束，可机械核对）
`git status` 实测只有 `clean_workspace.py` 与 `historical-evidence-interpretation.json` 两个治理文件被改；
`verification/**` 与 `doc/tasks/*` **零改动**；4 条绑定 `raw_sha256` **仍全部匹配**
⇒ Ruling A 全程**未触碰任何历史证据字节**。

### 5) 进度
- `GOV-DECLARATION-SCAN-CLEANUP-1`：**AC1 闭合（1/6）**；AC2 需 A+C，AC3 需 Ruling B 实施，AC4 需 C 实施。
- 目标 C：仍 **40 闭合 / 1 BLOCKED**（`GOV-RESIDUAL` AC7 未闭合），但**解锁路径已从「未开工」变为「A 完成、C 待做」**。

### 下一轮建议（明确、可执行）
**做 Ruling C 的实施**（`clean_workspace.py:2172` 成员不变量 + 两条新负例）。
理由：① 它是 AC2 的最后一块；② 改动面收敛（`git grep` 实测精确形式全仓仅 1 处、生产调用点仅 1 处）；
③ 完成后 residual 层应恢复（warning=7 + APPDATA 三根回归），即 **AC2 可判**，并可能连带解除
`GOV-RESIDUAL` AC7（其测试文件 3 条 ProductionScan 失败正是靠 residual 层恢复才可能转绿）。
**注意**：实施 C 时必须同步复核 `tests/test_residual_runtime_identity.py:184/191/197/203/217/266/275`
的 `len(index.errors) == 8/9` 期望值 —— 它们是绝对计数断言，正是 C 要改掉的那类耦合。

---
## 3l. R13（本轮）完成的事 —— `GOV-RESIDUAL` AC6（目标 C 只剩 1 条）

### AC6 的唯一缺口：第 7 类负例「保护集合回退」

原 blocked：「7 类负例中 6 类有测试（`test_residual_runtime_identity.py:182/220/187/194/200/206`），
第 7 类『保护集合回退』缺负例：`clean_workspace.py:2191-2195` 的 `PROTECTION_REGRESSION` 守卫
只有 `:149` 的**正面**断言」。

新增 `FixtureBehaviour.test_protection_set_regression_fails_closed`：
断言两条 `PROTECTION_REGRESSION` 守卫会 fail-closed（最终错误数 8、末项 code = `PROTECTION_REGRESSION`）。
**7 类负例现已全部有测试**，`FixtureBehaviour` **9/9 绿**（rc=0）。

### 变红验证（已做并还原）
把两条守卫条件改成恒真 `require(True, ...)` ⇒ 测试 FAILED，报 `AssertionError: 0 != 8`
⇒ 证明用例**真的依赖这两条守卫**而非空转；还原后产品源码 `git diff` 为空。

### ⚠️ 本轮最有价值的踩坑（写进了测试注释与证据）

**第一版测试跑绿了，但它是空的。** 我在全局范围让 `_register_protective` 丢根 —— 守卫**没触发**（错误数 0）。

实测根因：`_register_protective` **也被更早的声明扫描阶段调用**。全局丢根先把 **pre-stage 索引本身**弄坏了
（residual 阶段拿到的 `protected` 由 37 变 36，被丢的根根本不在里面）⇒ 守卫看的是「被污染的输入」，
自然拦不住，**那样测的是错的东西**。

修法：用 active 开关把退化**严格限定在 `_apply_residual_runtime_identity` 执行期间**，
且丢的是**该函数自己收到的 pre-stage 保护集合**里的根。

⇒ **教训：注入式负例测试必须核对「注入的范围」是否只在被测守卫的作用域内；
范围偏了，测试会以「绿」的形式说谎。**（本轮靠 `dropped_in_index=False` 的调试输出才发现。）

### 与 AC7 的边界（不要混）
`ProductionScan` 有 3 条失败（`test_protection_set_did_not_shrink` 报 `167 != 7`、缺 `catalog` 保护等）。
**已用 HEAD 版本测试文件（不含本轮改动）复跑，同样 3 条失败** ⇒ 预先存在，属真实仓库声明漂移，
**归 AC7 的 blocked 范围**，不影响 AC6 的负例覆盖判定。

### 目标 C 现状：**41 → 闭合 40 / 仅剩 1 条 BLOCKED**

| 处置 | 条数 |
|---|---:|
| 已闭合 | **40** |
| 已裁决 BLOCKED | **1**（`GOV-RESIDUAL` AC7） |
| 合计 | 41 |

**A / B / D 三项目标均已达成。** 唯一未达的是 C 的最后 1 条，它的解锁前提只有一条：**Ruling A**
（P22 快照被 `ee755d4bb` tracked 化后，冻结的 HIE 绑定怎么办 —— 三选一）。

### 下一轮建议（重要）
**要么出 Ruling A，要么写「无需下一步操作」并停。**
除 Ruling A 外，已无任何可由 Agent 在现有授权内推进的目标项。
**不要再去找 blocked AC「顺手修」** —— R11/R12 两次教训说明，那类动作最容易撞上过期注释或已完成的实现；
若真要碰，先核「代码 / 测试 / 证据 / 复核」四者。

---
## 3k. R12（本轮）完成的事 —— **推翻我自己的判断**：FEA-04 早已实现

### 我上轮错在哪

R11 我建 `FEA-04-IMPL-1` 时，依据是 `FEA-04` 卡面写「AC1–AC8 一律标 `blocked: 实现未开始`」，
推断「实现还没开始，需要一张实现卡」。**我没有先核实实现是否已交付。**

### 核实结果：代码 / 测试 / 证据 / 复核 **四者全在**

| 项 | 位置 |
|---|---|
| 代码 | `Shell/V2/Frontends/CurrentFrontend.cs`(12493 B)、`CurrentSessionMemento.cs`(4112 B)、`Views/V2/Route/CurrentRouteAdapter.cs`(1642 B) |
| 测试 | `tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs`(16804 B，17 项) |
| 证据 | `verification/FEA-04/`：baseline-comparison / preflight-blocker-matrix / lifecycle-assertions / sln-test-results / build-test-raw.log(176 行) / git-diff-check / governance-check / verify-pins |
| 复核 | **`doc/reviews/FEA-04-r3.md` = approved（P0=0 / P1=0）**，r3 `:105`「AC1–AC7 在 head 均有实测/证据支撑（独立复跑 931/0/60、0 failed）」 |

⇒ `FEA-04` 的 8 条 AC **逐条依据既有证据闭合**（`-TaskPath` 转 **PASS**）。

### 两处必须诚实登记的措辞矛盾（都写进了 AC 注释）

1. **AC2 基线 commit 不一致**：AC 写 `91be6c134`，但该 commit 的 build 因 **NuGet 路径问题 BLOCKED（14 errors）**，
   基线测试 NOT_RUN；**实际基线改用 `68c72ba57`**（914/0/60，App 396/403）vs 实现 931/0/60（App 413/420）。
   实质判据（同命令、同 runsettings、逐工程 ≥ 基线、failed=0、skipped 不变、无删除弱化）成立，但替换原因必须载明。
2. **AC8 点名 `FEA-04-r1.md` approved，而 r1 实为 `changes_requested`**：
   其意图（实现面独立复核、P0/P1=0）由 **r3 approved** 满足（r1→r2→r3 收敛）。
   r3 的边界声明（不构成集成批准、不覆盖 A0/B 类未执行项）一并保留。

### `FEA-04-IMPL-1` 已撤销（保留痕迹，不删）

`status: closed_with_limitations`；卡首**撤销横幅**写明「本卡前提是错的、我未核实实现是否已交付」；
8 条 AC 记 `NOT_APPLICABLE`；原始 AC 文本以「原拟｜」保留不改；
`verification/FEA-04-IMPL-1/RETRACTION.md` 记录原因 + 核实证据表 + 教训。
`FEA-04` 内我上轮加的指针**已划掉并更正**（append-only 留痕）。

### ⚠️ 这是**同一类错的第二次**

| 轮次 | 场景 | 我的错 |
|---|---|---|
| R11 | `M2-SFX` AC4 | 相信「T1b 产物不存在」，实际存在 |
| R12 | `FEA-04` AC1–AC8 | 相信「实现未开始」，实际早已交付 |

⇒ **铁律（已写入队列第 0 条）：处理任何 blocked AC 前，先核「代码 / 测试 / 证据 / 复核」四者是否已存在，
再决定是「补证据」还是「立新卡」。blocked 注释是线索，不是事实。**

### 目标 C 现状（本轮的最大成果）

**41 条 → 闭合 39 / 仅剩 2 条已裁决 BLOCKED**（`GOV-RESIDUAL` AC6/AC7）。
**无「无路径项」、无「未处置项」。** 那 2 条的唯一解锁前提是 **Ruling A**（HIE P22 tracked 化三选一）。

---
## 3j. R11（本轮）完成的事 —— 目标 C **41 条全部有处置**

### 1) 立 `FEA-04-IMPL-1`：把 8 条「无路径项」变成有路径项

`doc/tasks/FEA-04.md` 是**范围冻结卡**，它自己写着（`AC-CHECKBOX-AUTHORITY-1`，2026-11-15）：
> `status: done` 表示**范围冻结与 scope 复核完成**，**不代表 AC1–AC8 已满足** —— 那些是**下游实现**的验收条件。

⇒ 这 8 条不是欠账，是**缺一张实现卡**。新卡 `doc/tasks/FEA-04-IMPL-1.md`（`proposed`，`depends_on: [FEA-04]`）：
- **不重开范围**：规则一律引用 FEA-04（R-CURRENT/R-STATE/R-SWITCH/§15.3/Q-16…Q-20），不复制第二份定义；
- **AC1–AC8 逐条承继**（语义不变、不新增不弱化），每条标注依据的规则编号；
- **建议 6 批 B0–B5**，B0 = 先在 `91be6c134` 上量出逐工程基线（**否则 AC2 无法判定**）；
- **禁止 6 条**：不重开范围 / 不实现 wire / 不做切换执行与 Fluent 启动 / 不新建工程不改 sln /
  不弱化既有断言 / 不硬编码用户路径；
- **关账口径**：FEA-04 的 AC1–AC8 继续 `[ ]`（实测 8/8 未变），只有实现卡达成 + 独立复核 approved 后
  **依据其证据**依次翻。

### 2) `M2-SFX-CORRECTION-EXPORTER` AC4 收口 —— 原 blocked 前提**不成立**

原 block：「T1b 产物尚不存在，「与 T1b 产物同构、训练侧零适配」无法验证」。
**实测：T1b 产物就在本机** —— `training_data/sfx-v1/manifest.train.json`（216280 B，
`kind=sfx-data-infra/manifest@1`）、`manifest.full.json`、`sfx-v1/` 下四个子目录。

**「同构」是构造性成立，不是碰巧像**：T1b 产物与本导出物都由 `sfx_data_infra.atomicio.write_manifest` 写、
由同一个 `SampleRecord.to_dict()` 产出，训练侧读取走同一个 `load_manifest` ⇒ 同一套 IO 模块。

**新增判别力测试** `test_manifest_is_structurally_identical_to_the_shared_writer`：
容器形状 / 每样本键集合 == `SampleRecord.to_dict()` / 辅助册同构 / **跨产物逐一相等**。
缺失 T1b 产物时 `pytest.skip` —— 因为 `training_data/` 被 `.gitignore:13` 排除，**刻意不把 gitignored 产物做成硬依赖**。

**变红验证**：往 `to_dict()` 注入 `red_proof_extra` ⇒ FAILED，报
`T1b-only=[] exporter_only=['red_proof_extra']` —— **`T1b-only=[]` 反证了原状下两者键集合完全相同**。
还原后 **12 passed**，产品源码零改动。

### 3) 目标 C 的最终记账（这是本轮最重要的一句话）

| 处置类别 | 条数 | 说明 |
|---|---:|---|
| **已闭合** | **31** | 逐条有证据 + 独立复核/实测 + 变红验证（多数） |
| **已裁决 BLOCKED** | **2** | `GOV-RESIDUAL` AC6/AC7；解锁 = **Ruling A**（HIE P22 tracked 化三选一），书面裁决已落盘 |
| **已移交实现卡** | **8** | `FEA-04` AC1–AC8 → `FEA-04-IMPL-1`（`proposed`，路径已建立） |
| **合计** | **41** | **无「无路径项」残留** |

⚠️ **口径必须说清**：目标 C 的原文是「AC blocked 剩余 33 条可闭合项**处置完**」。
现在的状态是「**41 条全部有处置**」（闭合/裁决/移交三类），**不是「全部闭合」** ——
8 条在实现卡里仍 open、2 条是 BLOCKED。**不得写成「目标 C 清零」**。

### 4) 判据来源提醒（本轮踩过）

`M2-SFX` AC4 的原 block 说「T1b 产物不存在」，实际存在 —— **blocked 理由也会过期**。
⇒ 处理任何 blocked AC 前，**先实测它声称缺的前提**，不要直接相信注释；本轮靠这一点直接关掉了 1 条。

---
## 3i. R10（本轮）完成的事 —— `GATE3-COVERAGE-MATRIX` AC2/AC4（该卡 **6/6 全闭合 + 门禁全绿**）

### AC4：把「类名推断」换成**权威口径**

原 blocked 三条主张逐条处理，落盘矩阵新增 **§16**：
1. 「100 项 NOT_RUN 归因仍是未核实的类名推断」→ 改为「**实测 SKIP 行 + 源码 fact attribute + gate 变量反查**」；
2. §16.2 给出 **Host 44 个 skip 的全部 13 类 × 12 种 gate attribute × 具体门禁变量**；
   §16.3 给出 App 4 个 skip 的逐条门禁；
3. **r3 R3-006 的「3 处性质错标」实测结论是「表过期」而非「attribute 写错」**：
   `GrantIssuerTests`/`StartupSelfCheckTests`/`Fea11WatchHostRuntimeTests` **当前 skip 数均为 0**
   （实测 attribute：`[HostSidecarFact]` / 普通 `[Fact]` / `[HostSidecarFact]`）⇒ §4.2 那 3 行是过期残留。

**更大更正：旧「100 项」口径作废** —— 实测 **48**（Host 44 + App 4 + **CoreClient 0**，后者 26→0）。
性质统一为「按设计 gated」（需环境开关或交互桌面），不是缺覆盖。

### AC2：8 处【摘要】格**全部升级为【核对】**

每格给 `测试名 (文件:行)` + **该测试具体断言了什么（精确到断言行号）**：
错误态·工作台 / 只读·工作台 / 只读·阅读器 / 导入·工作台 / 阅读进度·书架（4 条逐条）/
主题·外观·设置（2 处）/ 快捷键·阅读器 / 焦点·a11y（2 条）。
同时修正 §7 两条已过期的自述限制（「仅 12 格【核对】」、「§4.2 未核实 attribute」）。
⇒ 全文【摘要】只剩 §1 的**图例定义**一处，不再有「类摘要+方法名」格。

### 本轮最重要的方法论

**「矩阵自述的限制」比矩阵本身更容易过期。** 上一版 §7 写着「仅 12 格核对」，
但 §8–§15 已经补了大量内容为前提的更新，§7 从未回改 ——
⇒ **结论：任何「本文件尚未核实/仅 N 格」的自述，都必须在下次补内容时同步回改，
否则它会变成一份自我否定的证据**（AC2/AC4 的 blocked 理由正是引用了这些过期自述）。

### 本次会话已有四张卡走通「补 AC + 补结构性表格 ⇒ 门禁全绿」

`RUN-IPC-1`（R6）、`V11R-C-1`（R7，7/7）、`V11R-B-5`（R9，7/7）、`GATE3-COVERAGE-MATRIX`（R10，6/6）。

### ⚠️ 目标 C 只剩 11 条，且**都不在「补断言/补文档」路径上**

| 卡 | 未勾 | 性质 | 唯一前提 |
|---|---|---|---|
| `FEA-04` | **8** | **实现** | **必须先立实现卡**（范围已冻结 `doc/tasks/FEA-04.md:88-97`） |
| `GOV-RESIDUAL` | 2 | 已裁决 BLOCKED | **必须先出 Ruling A**（HIE P22 tracked 化三选一） |
| `M2-SFX-CORRECTION-EXPORTER` | 1 | IMPL | 需先生产 T1b 批量产物 |

⇒ **下一轮的正确动作不是继续找 AC 补，而是二选一：**
(a) **写 `FEA-04` 实现卡**（一次解锁 8 条 = 剩余 73%）；或
(b) **出 Ruling A**（解锁 `GOV-RESIDUAL` 2 条 = 剩余 18%，且是 Release Gate 条件 6 的唯一路径）。

推荐 **(a)**，因为 8 条体量最大且完全在 Agent 权限内（不需要改冻结政策）。

---
## 3h. R9（本轮）完成的事 —— `V11R-B-5` AC3（该卡 **7/7 全闭合 + 门禁全绿**）

### 做法：**先把映射口径写死，再断言**

Export 面**不用** DESIGN_SYSTEM §7 的六态字面词表（它用 `StudioExportPhase`），
所以测试注释里**先写明映射**才断言 —— 后来人能核对口径而不是猜：

| §7 态 | Export 表征 | 就地呈现 |
|---|---|---|
| `idle` | `Phase=Idle` | 「预检未加载」 |
| `loading` | `Phase=Loading`（瞬时，从 **PropertyChanged 发布序列**观察） | 「正在读取预检数据…」 |
| `ready` | `Phase=Ready` | 「预检就绪 · 可导出 N 页」 |
| `empty` | `Phase=Ready` 且 `ExportablePageIds` 空 | 「可导出 0 页」+ `HistoryEmptyText`「还没有导出记录」 |
| `error` | `Phase=Failed`（StartExport 被拒） | 「导出失败」+ `HasError`/`ErrorText` 含「StartExport 被拒绝」 |
| `partial` | `Phase=Ready` 但未确认/过期**无读取面** | `—` + **非空 tooltip**，计数为 `null` **不伪造 0** |

### 为什么从发布序列读 `loading`（重要方法论）

`loading` 是瞬态。若靠「阻塞读取」观察，测试就绑到了**帧内 await 次数**上；
从 `PropertyChanged` 序列读，钉的是**状态机**。
⇒ **这正是 R3 在 `V11R-B-4` 踩过的坑**（当时我写「settle 必须是 Ready」而实测是 Partial，
原因就是读次数变了）。本轮刻意避开，并且变红验证证明它真的依赖状态机。

### 变红验证（两条，均已还原，产品源码零改动）

1. 删掉 `Phase = StudioExportPhase.Loading` 赋值 ⇒ 红：`Assert.Contains() Failure: Item not found in collection`
2. 把「StartExport 被拒」分支的 `Phase = Failed` 改成 `Ready` ⇒ 红：`Expected: Failed / Actual: Ready`

### 至此本次会话已有三张卡「补 AC + 补结构性表格 ⇒ 门禁全绿」

`RUN-IPC-1`（R6）、`V11R-C-1`（R7，7/7）、`V11R-B-5`（R9，7/7）。
**这条路径已被验证三次，可放心用于剩余的 open AC 卡。**

### ⚠️ 目标 C 剩余 13 条的真实结构（下一轮据此排期）

| 卡 | 未勾 | 性质 | 备注 |
|---|---|---|---|
| `FEA-04` | 8 | **实现** | 必须另立实现卡；范围已冻结（`doc/tasks/FEA-04.md:88-97`） |
| `GATE3-COVERAGE-MATRIX` | 2 | DOC（大） | AC2 逐格断言说明 / AC4 100 项 NOT_RUN 归因 |
| `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | 2 | **已裁决 BLOCKED** | 解锁前提 = **Ruling A**（HIE P22 漂移三选一）；不做 A 全白做 |
| `M2-SFX-CORRECTION-EXPORTER` | 1 | IMPL | 需先生产 T1b 批量产物 |

⇒ **能靠「补断言 + 补表格」推掉的只剩 `GATE3-COVERAGE-MATRIX` 的 2 条（大文档）**；
其余要么需另立卡（`FEA-04`）、要么被 Ruling 阻塞（`GOV-RESIDUAL`）、要么缺前置产物（`M2-SFX`）。

---
## 3g. R8（本轮）完成的事 —— `V11R-B-5` AC1/AC2

### AC1：原 block 是「**无章节可核对**」，缺口在**被我冻结的规格文件**里

原 blocked 理由：SCREEN_SPECS 无导出预检/术语章节（`grep '预检|术语'` 0 命中）⇒ AC1 无从核对。
**这是 2026-10-30 冻结 `V11R_SCREEN_SPECS.md` 时的遗漏**（我冻结的）。

本轮增补（**additive，不改既有章节字节**）：
- `## 6.5 导出预检 + 术语与约束（ui-studio）`（`:86`）—— 表头明写「冻结时遗漏该工作面……按其已交付实现**如实回填**，不新增需求」；
- 文末 `## 修订记录`（`:126`）。

**内容全部来自本卡已交付实现**（逐项对照源码写的，不是凭空设计）：
`StudioExportFormat`=Zip/Pdf、`StudioPdfContentMode`=ImageOnly/SearchableDualLayer、
`StudioExportScope`=Chapter/SelectedPages、`StudioStalePolicy`=Abort/ContinueExisting、
`StudioExportPhase` 8 态、`StudioTermsSection`=Terms/DoNotTranslate/Conflicts、
NOT_WIRED 时**零伪造行 & 搜索禁用**、预检未确认/过期显示 `—` 且**禁止伪造 0**。

### AC2：补「模式切换不重建 VM / 不丢状态」的实证

新增 `ExportSurface_KeepsViewModelSelectionAndOptions_AcrossStudioModeSwitches`：
**Page → Batch → Page 两次真实切换**后断言 `Assert.Same(export, vm.Export)` +
`Phase` 仍 Ready + `TranslatedPageCount` 不变 + `Format`/`PdfContent`/`Scope` 保留 + selection 逐项保留。

**变红验证**：临时让 `RequestMode` 切模式时重置导出态 ⇒ 测试红，报 `Expected: Ready / Actual: Idle`；还原后绿。

### 两处 Lead 扩权（都是**范围缺陷**，不是我想扩）

1. `doc/plan/V11R_SCREEN_SPECS.md` —— AC1 的**前置文档**，此前不在卡内；
2. `apps/desktop-avalonia/tests/NewManga.App.Tests/V2StudioExportTermsTests.cs` ——
   **本卡自己的测试文件**，由交付提交 `e3e928869`/`b309606aa` 引入，但当时 `allowed_paths` 漏列。

⇒ 教训：**AC 引用的前置文档/测试文件必须出现在 `allowed_paths`**，否则 AC 会卡在「无可核对/无可修改」。
冻结规格文件缺章节时，正确的做法是**additive 回填 + 修订记录**，而不是把 AC 判 NA 或改写既有字节。

### 结构性表格配方再验证

按 R7 配方给 `V11R-B-5` 补 `## Canonical Evidence`（13 行）+ `## Resource Manifest`：
`-TaskPath` 由 **5 条 FAIL → 1 条**（仅剩 AC3 未闭合，属实）。
⇒ 配方在第二张卡上同样一次成功，可直接用于批量。

### 踩坑记录（本轮）

- **Python 脚本里用「整文件锚点 + replace」时，锚点必须与文件的真实行尾一致**；
  本轮 `patch_b5_ac2.py` 的锚点因行尾/格式不匹配而 `AssertionError`，
  但我此前已被 *同一脚本的前一步* 打印「成功」，导致误以为 `allowed_paths` 已改。
  ⇒ **凡「改结构」的补丁，改完必须回读文件确认**（本轮之后我在每次 flip 后都 `Get-Content` 回读）。
- 一次 `write` 误把脚本落到仓库根（`workspace_dummy_ignore.py`），已 `Move-Item` 到 workspace 并确认仓库 `git status` 干净。
  ⇒ **派生脚本一律直接写到 `G:\CODEX\New Manga.workspace\`，不要先落到仓库再搬。**

---
## 3f. R7（本轮）完成的事 —— `V11R-C-1` 三 AC 收口 + 结构性表格补齐（**该卡门禁转全绿**）

### 1) AC6/AC7：两张卡此前都只卡在同一件事 —— 证据目录 0 个 `.png`

| 部分 | 结论 |
|---|---|
| AC6 单测覆盖 + `dotnet test` 绿 | **已满足**。本轮实跑 `tests/NewManga.ThemeEngine.Tests` → **失败 0 / 通过 253 / 跳过 0 / 总计 253**，EXIT=0（历史日志记 203/203，说明套件之后继续增长且仍全绿）；10 子系统逐项对照见 `verification/V11R-C-1/README.md` §3 |
| AC7 构建/测试日志 + 偏差清单 | **已满足**。`build.log`（0 warning/0 error）、`dotnet-test-full.log`（586 通过/0 失败）、`generator-check.log`、`DEVIATIONS.md`（16 条）+ README §5 |
| 「关键屏截图」 | **NOT_APPLICABLE（无对象）** —— 见下 |

**为什么截图无对象**（口径与该卡 AC1 完全一致，AC1 的 blocked 理由原文即「屏幕验收面无对象：本卡为 headless 库卡」）：
- `allowed_paths` 仅 `src/NewManga.ThemeEngine/` + `tests/NewManga.ThemeEngine.Tests/` + `verification/V11R-C-1/`
  —— **不含任何视图/截图测试目录**；
- 引擎不渲染像素：`Preview/ThemePreviewEngine.cs` 是**预览会话状态机**，产出令牌解析结果与变更事件，不是可截图的窗口；
- SCREEN_SPECS §1–§6 无引擎章节。

⇒ 要截图必须往 `tests/NewManga.App.Tests/` 加 Theme Studio 用例，**超出本卡 scope**。
屏幕/截图义务由消费方卡履行（`V11R-B-3` design-system-usage、`V11R-B-4` `screenshots.json` + 1600x1000/1280x800 真帧、
`V11R-B-5` Tools overlay），已在各自卡内履行。**不把未做写成 PASS、不伪造截图。**

### 2) AC1：应用本卡**既有裁定**，不是新裁决

AC1 的 blocked 理由由**原作者**写成完整的 NA 结论（headless 库卡 + SCREEN_SPECS 无引擎章节）。
本轮只按 §4.3 把它落成 `[x]` + `not-applicable` 标记，**未新增或改变任何判定**。
⇒ **`V11R-C-1` 现在 7/7 AC 全部 `[x]`。**

### 3) ⭐ 关键发现：pin 口径有**双通道**，225 张存量卡因此**可以脚本化补齐**

`check.ps1` 的哈希校验接受**二者之一**：

1. `worktreeSha == sha`（磁盘口径），**或**
2. `Get-GitBlobSha256 $commit $repoRel == sha`（**BLOB 口径**，但要求 `commit` 列是**真实含该 blob 的提交**）

⇒ 按项目规则用 **BLOB sha**、`commit` 取 `git log -1 --format=%h -- <path>`（其 blob 即当前内容），
**两条通道同时可验证**，且**不需要改任何历史文件字节**。

这**直接解决了 R6 踩到的困境**：R6 时我的证据文件是 CRLF、磁盘 sha ≠ blob sha，只能靠把**新**文件规范化成 LF 绕过；
但**对存量历史证据不能这么做**（会改历史字节）。现在不必了。

**可复用配方（供批量处理那 225 张结构性欠账卡）**：
```
对每张卡：
  files  = verification/<id>/ 下全部文件
  每文件：
    sha    = sha256(git cat-file blob HEAD:<path>)   # BLOB 口径
    commit = git log -1 --format=%h -- <path>         # 含该 blob 的真实提交
  生成旧六列 Canonical Evidence 表 + 一行 NOT_APPLICABLE 资源清单
  插到卡尾（`## 交付与运行记录` 之前或最后一节之前）
```
本轮在 `V11R-C-1` 上验证：13 个文件一次生成，`-TaskPath` 由 **FAIL(4) → PASS(3 warnings)**。

---
## 3e. R6（本轮）完成的事 —— `RUN-IPC-1` AC4（**该卡门禁首次全绿**）

### 核心结论：AC4 的 blocked 理由**三项主张全部已过期**

| 原 blocked 主张 | 实测结论 |
|---|---|
| ① allowlist 断言缺（含原始日志） | **静态复核通过**：`main.rs:290-297` 恰为那 6 条；6/6 全在 `PRODUCTION_COMMANDS`（`:70-165`）；6/6 在 `probe_surface.rs`/`ac1_bridge.rs` **各 0 命中**；`command_allowlist(probe,ac1)`（`:321-345`）逐族过滤且含 `!RUN_PRODUCTION_ONLY_COMMANDS.contains(...)` ⇒ 结构上不可能进 probe/AC1；钉住它的 Rust 测试仍在（`:2748`/`:2606`）。cargo 运行面 **NA**（AD-002 退役 Tauri，`package.json` 不存在） |
| ② 缺 host 层 typed 拒绝单测 | **全部已有并实测通过**：`INVALID_REQUEST`、`TARGET_NOT_FOUND`×5、`CANCELLED`、**`IDEMPOTENCY_KEY_REUSED`**、**`INVALID_RUN_TRANSITION`**、冻结转移表、缺 key 本地拒绝、只读面拒绝 |
| ③ 成功 Run 往返 NOT_RUN（无夹具） | **NOT_RUN → PASS**：`[RunBookFixtureFact]`（真实 sidecar + BOOK-FIXTURE）**实跑 6s 通过**，C056→真实 RunId、同键复用同一 RunId、C059 targets==pages、C060 rows==pages 且 StepFlow 非空 |

**本轮实跑**：`RunControllerHostIntegrationTests` 3/3 + 补充 2 条 2/2，均 EXIT=0。

### 顺带修掉一处**陈旧的资源记录**（`check.ps1` 因此转全绿）

资源清单原先写 worktree `PRESERVE_REFERENCED` 于
`G:/CODEX/New Manga.workspace/worktrees/RUN-IPC-1`，但该目录**已不存在**：
`Test-Path` = False、不在 `git worktree list`、系 `ad7ce5047`
（"prune 41 orphaned worktree admin entries"）清掉的孤儿管理项。
**交付未丢**：`git merge-base --is-ancestor 5642b2a72 HEAD` = 0。
⇒ 据实改为 `DELETE_SAFE` / destination `-`，并同步更正 Closeout Record。
**结果：`check.ps1 -TaskPath doc/tasks/RUN-IPC-1.md` 由 FAIL(1) 变 PASS(3w) —— 该卡首次全绿。**

### ⚠️ R6 最重要的方法论教训：证据文件必须 **LF-only**

第一版证据用 PowerShell here-string 写成 **CRLF**，于是 worktree sha 与 blob sha 不同：
- worktree `91c77c4a…`（CRLF）
- blob `dd78a0af…`（`core.autocrlf=true` 转 LF）

我按项目规则填了 **blob sha**（正确），但 `check.ps1` 在**这条 v2 卡路径上按磁盘/工作区字节取哈希**
⇒ 报 `Evidence SHA-256 不匹配`。
**解法**：把证据文件规范化为 **LF-only**，使 worktree 与 blob 哈希相同，两种口径同时成立。
（FEA-07 / MICA-FIX-1 之所以能一次过，正是因为那些文件本来就是 LF。）
⇒ **今后写证据文件一律 LF-only**，尤其是用 PowerShell 生成时。

### 另一个坑：PowerShell here-string 会吞反引号后的字符

我用 `python -c "@'...'@"` 时，`` `verification/...` `` 里的反引号是 PowerShell 转义符，
结果路径被写成 `erification/...`（吃掉 `v`）⇒ `Canonical evidence 路径缺失`。
**结论：改仓库文件一律用 Python 脚本文件（`write` 工具落盘后 `python <script>`），不要用 `pwsh -c` 内联 Python。**

---
## 3d. R5（本轮）完成的事 —— `V11R-A-3` AC4（该卡 6/6 全闭合）

| # | 事项 | 结果 |
|---:|---|---|
| 1 | **Lead 裁决 AC4 口径** | 原 blocked 理由明写「**口径待 Lead 裁决**」。裁决：AC4 的实质要求是「66 条有 parity 断言（含参数特判与 minor 预期）」，**不是**「必须改 `CommandParityContractTests` 这个文件名」——该文件的 66→76 改造归 `V11R-F0-1`（已完成），本卡由 `CommandContractV11RTests` 承载属合理分工 |
| 2 | **补唯一真实缺口「参数特判」** | 给 `ContractRow` 加 `Params`（契约表第 7 列）；新增 2 个 fact：**(a)** 66 行逐行断言参数契约非空且归入 **5 种文档化形态**（pass-through 12 / typed 39 / no-params 5 / host-local 6 / core-fieldset 4，词表由代码派生，第 6 种即 fail）；**(b)** 从契约派生「带 `!` 的必填参数」（typed `name!: type` 与 core-fieldset `{name!, x?}` 两种都收），逐条发**空 payload** 断言**一律被拒且无一静默接受**，并记录拒在哪层 |
| 3 | **实测结果** | **39** 条命令声明必填 → **37** 条 dispatcher 边界拒（`INVALID_ARGUMENTS`，断言**发帧数不变**）+ **2** 条 Core 拒（`INVALID_REQUEST`，断言**恰好 1 帧**）+ **0** 条静默接受 |
| 4 | **变红验证（两个都做了）** | (i) `parameters` 改 `string.Empty` ⇒ fact (a) 红，报 `C001 settings_get does not declare its parameter contract`；(ii) 移除 dispatcher 对 `list_region_revisions` 的 `region_id` 强制 ⇒ fact (b) 红。**均已还原**，`git diff` 证实产品源码零改动 |

### finding A-1（登记，不掩盖）

`C040 library_delete_book_permanently` / `C041 library_delete_books_permanently` 的契约单元格写「由 Core field-set 校验」，
但实测 **dispatcher 先拒**（无害的双层加固）⇒ 是**契约描述精度**问题，不是行为缺陷。
契约 `V11R_COMMAND_CONTRACT_V1.md` 是**冻结件**，本轮**不改其字节**；测试对**反向漂移**
（typed 声明却只有 Core 拒 = dispatcher 漏检）仍硬失败并点名命令。

### R5 的方法论教训

- **`.md` 文件的行尾不统一**：`V11R-A-3.md` 是 **LF**，而 `.cs` 文件是 **CRLF**。
  用 `\r\n` 切分的补丁会静默失败 —— 打补丁前先测行尾（`ReadAllBytes` 数 CRLF/LF）。
- **PowerShell 里做多行文本替换很脆**（引号/括号转义）；改用 Python 脚本做仓库文件的精确改写，
  并且**先断言锚点存在**再写盘，避免「静默无操作」。
- 一次失败的补丁曾把 `ContractDocument` 整块切掉；**止损方式是 `git checkout -- <file>` 从零重打一个合并脚本**，
  而不是在坏状态上继续叠补丁。

---
## 3c. R4（本轮）完成的事

| # | 事项 | 结果 |
|---:|---|---|
| 1 | **`MICA-FIX-1` AC2 收口** | 用仓库内构建产物**真实启动**（全隔离 `--data-root/--log-dir/--theme-home/--mutex-name` + `--exit-after=15000`，`exit_code=0`、16s 自然退出），捕获 `window-material.log` 原文 `material=Mica; requested=Mica,Blur,None; actual=Mica` ⇒ 确证拿到 **Mica 而非回退 None**。证据 `verification/MICA-FIX-1/ac2/{window-material.log,startup.log,host.log}`（EV M5/M6/M7）。**limitation L-MICA-1**：该文件由 **legacy 壳**的 `MainWindow` 写出（**V2 默认壳不写**），故取证用 `--shell=legacy`；V2 壳 Mica 的**视觉**仍需人眼（`H-01`），**不宣称 AC1 已验** |
| 2 | **`GOV-RESIDUAL` AC7 书面裁决** | 派 `adjudicator-decl`（全新上下文、只读）出裁决 → **BLOCKED**，落 `doc/reviews/GOV-RESIDUAL-AC7-ADJUDICATION-2026-11-16.md`（34943 B，署名，末行 FINAL） |
| 3 | **卡面裁定** | AC7 重写 blocked 理由（三层阻塞 + 三条路径裁决 + 点名缺口）；AC6 补记「裁决确认其为真」并注明**不能**用 `test_protection_set_did_not_shrink` 替代；`status: done → closed_with_limitations`（解决 frontmatter 与「集成复验后才 done」的冲突） |
| 4 | **新卡 `GOV-DECLARATION-SCAN-CLEANUP-1`** | `proposed`；写死三层定位 + 三选一 Ruling A / B(1/2/3) / C(相对不变量) + **硬禁止四条** + 建议拆三张子卡；附带登记 R-1 / **R-2（路径硬编码跨机必红）** / EV-03·EV-04 复现性疑点 |

### ⚠️ R4 最重要的认知更正（务必内化）

我派发裁决时把 AC7 描述成「需清理 160 处历史声明错误」。**裁决者实测推翻了它**：

> **第一层阻塞不是 160 条历史错误**。`tools/governance/historical-evidence-interpretation.json` 把
> `verification/P22/codex-p22-task-r4-malformed-snapshot-7ebd7d40.md` 绑定为 **untracked**，但提交
> `ee755d4bb`（2026-10-22「406-file evidence backlog」）把它入库成 **tracked** ⇒ 产出唯一一条 `SOURCE_DRIFT`。
> 而 `clean_workspace.py:1986-1988` 见 HIE 政策错误就让 **residual 层整段早退**
> （7 条裁定身份未降级、APPDATA 三根未注册、`DECL_RESIDUAL_RUNTIME_PRESERVED` warning=0）。
> **仅这一条就足以让 3 个测试全红。先清 160 条是错的顺序，会白做一轮。**

⇒ **前进顺序必须是 L1（HIE 漂移）→ L2（159 条分类）→ L3（不变量重写）**，且 L1 前必须先有 Ruling A。

### R4 另外两条实测事实

- **`test_user_data_root_is_now_protected` 不是独立缺陷**：裁决者做受控实验（字节相同 origin + 真实 APPDATA
  目标 + 内存 patched digest）→ `errors=0 / residual warnings=7 / 三根各命中 1` ⇒ 它是 L1 的下游症状，
  修 L1+L2 后自动绿，**不要为它单独立卡**。
- **AC6 与 AC7 同属性**：AC6 缺的第 7 类「保护集合回退」负例，正好是 L3 不变量重写的产物 ⇒
  清理卡 Ruling C 顺带把 AC6 一起解掉。

---
## 4. 关键技术事实（R1/R2 累积）

### 4.1 file identity 53 位契约（已闭环）

- 权威定义：`src/application/importing/referenced/identity.py:3-9/16/20`
- C# 已修点（**行号已稳定**）：
  - `NewManga.CoreClient/Issuer/HostIssuer.cs:563`（file）/ `:596-597`（dir）
  - `NewManga.Host/Sources/SourceReadCoordinator.cs:414` / `:638`（写 wire facts 两处）
  - `NewManga.Host/Sources/SourceSecurity.cs:138`（`CoreFileIdMask`）/ `:154`（`NormalizeFileId`）
- **`SourceSecurity.Identity` 本体保持 raw**（`registry.v1.dat` 兼容），**不要**在里面 mask
- `TileChannel.cs:457` 的 raw index **不参与跨语言比较**（同进程同源自比），无需修；已加契约注释

### 4.2 `core.autocrlf = true` 的两条硬约束

1. **证据 sha256 必须用 BLOB 口径**：`git add` 后 `git cat-file blob :<path>` 算，
   **不能用工作区文件**（工作区是 CRLF，blob 是 LF，哈希不同）。
2. 提交后用 `git cat-file blob <commit>:<path>` 复核（本卡 22/22 就是这么验的）。

### 4.3 新回归测试的「可红性」是硬要求

`HostFileIdNormalizationTests` 的探针建在 **`%TEMP%`**（实测 12/12 的 raw id > 2^53），
**不是** `G:\CODEX\New Manga.workspace`（实测 0/6）。
若把探针放 workspace 卷，强断言永远不触发 ⇒ **绿但什么都没测到**。
这是本卡最贵的教训之一，写测试时务必确认「样本真的能落进回归区间」。

### 4.4 诊断优先读仓库自带 wire log，不要自造 probe

`SidecarFixture.cs:312` 一直配着 `WireLogPath`，`test.ps1` 每次自动写 NDJSON 到
`G:\CODEX\New Manga.workspace\task-envs\HOST-RESOURCE-SECURITY-1\evidence-rerun\wire\`，
字段名是 `request` / `response`（小写）。

⚠️ **但该 test 目录每次全量运行都被覆写**（`results-*.trx`、`summary.json` 的 `at_utc`），
依赖旧 `.trx` 的哈希声明**不可复验** ⇒ 证据要么「当日跑当日验」，要么按 run 分目录。

---

## 5. 陷阱区（累计，务必内化）

| # | 错误 | 代价 |
|---|---|---|
| 1 | 把测试夹具副本错认成产品 bundle | 一轮 |
| 2 | 从 `weights not found` 警告推断 `pending` 原因 | 一轮 |
| 3 | probe 用点号命令名 ⇒ 误判「settings 域未挂载」 | 一轮 |
| 4 | probe 自己传 `null` ⇒ 误判「发现 payload bug」 | 一轮 |
| 5 | 给测试插诊断块时把 `return` 放到断言前 ⇒ **断言被跳过、测试假通过** | 一轮 |
| 6 | **把 `dotnet test` 的 `EXIT=0`（含 skipped）当成 passed** | **3 轮方向错误** |
| 7 | 修完 `HostIssuer` 就宣称「唯一产品缺陷已修」 | 一轮 |
| 8 | **写行号引用后改了被引用代码，不重新核实行号** | R1 又犯 2 次（三轮复核各抓一次） |
| 9 | **回归测试探针放错卷 ⇒ 强断言不触发（假绿）** | R1 自查抓到 |
| 10 | **用 `git checkout` 恢复 doc 字节**（autocrlf 下写出 CRLF ⇒ 预算/行数判据假超限） | R16 |
| 11 | **新写的 Resource Manifest 直接进声明审计**（`%TEMP%`/`*`/描述性 disposition 各产生 DECL_* error） | R16 |
| 12 | **把「文档里的旧结论」当现状**（§3.2-③ 原文说漏 1 张卡，实测漏 5 张 + 混入 1 张终态卡） | R16 |

**纪律**：

1. 判断测试通过要看**具体结果行**（`已通过`/`失败`/`已跳过`）；`EXIT=0` 只说明没有失败。
2. 诊断零侵入；优先读仓库已有证据。
3. 修 producer 前先 `grep` 查**有几处**。
4. 改持久化数据的 producer 前先想兼容。
5. 证据 pin 的 `commit` 必须是**实际引入该文件当前内容**的 commit
   （`git log --diff-filter=A` 对新增文件；`git log -1 -- <path>` 对修改过的文件）。
   `check.ps1` **不校验** blob 是否存在，要自己 `git cat-file blob <commit>:<path>` 验。
6. 跑完 `test.ps1` 先恢复 `verification/READER-OVERLAY-HEADLESS-PNG-1/`（该测试会改写 `render-info.md` 与 png）；
   恢复后核 `git diff 6a408e5aa -- <该目录>` 为空，**不要**用 `git checkout` 去恢复 `doc/**`（会写 CRLF）。
7. 「测试全绿」≠「没 bug」：opt-in 路径（`NEWMANGA_FEA11_IPC=1`）不跑时，绿是假的安全感。
8. 写行号引用后若改了被引用代码，**必须重新核实**；更稳的是「函数名 + 语句特征」而非纯行号。

---

## 6. 治理约束（不可绕过）

- **仓库**：`G:\CODEX\New Manga`（唯一事实来源）；派生**一律**进 `G:\CODEX\New Manga.workspace`
- **可用 Agent**：仅 DSH / Codex / ZCode。**`subagent_agy` 禁用**（Antigravity 已退出）
- **Review 独立性**：按**上下文独立**，不要求非作者。作者可派新子 agent 只读审查
- **AC 标记**（lifecycle v3）：`<<MET>>` / `<<PARTIAL: 原因>>` / `<<BLOCKED: 原因>>` / `<<NOT_APPLICABLE: 原因>>`，
  **严格在行末**；`[x]` 只允许 `MET`/`NOT_APPLICABLE`，`[ ]` 只允许 `PARTIAL`/`BLOCKED`；
  `MET` 不得带原因。门禁在 `in_review/approved/done/closed_with_limitations` 生效
- **DAG**：`ready`/`in_progress`/`blocked`/`in_review`/`changes_requested`/`approved` 六态须登记 DAG；
  终态与 `proposed` 不检查
- **预算**：`doc/STATUS.md` ≤3200 bytes / 45 lines（现 3177/29，余 23 B）；
  `doc/REBASELINE_PLAN.md` ≤7000 bytes / **64 lines（现 6960/64，余 40 B；加行前必须先压缩）**
- **提交**：长中文 commit message 用 `git commit -F <file>`

---

## 7. 本次 goal 的关键文件索引

| 用途 | 路径 |
|---|---|
| 本文（启动包） | `doc/handoffs/NEXT-SESSION-STARTER.md` |
| 上一 goal 总账 | `doc/handoffs/GOAL-WRAPUP-R100.md` |
| **Gate 六条映射表（目标 B 交付）** | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| **HUMAN-REQUIRED（目标 D）** | `doc/reviews/HUMAN-REQUIRED-2026-11-15.md`（H-01…H-10） |
| 目标 C 素材 | `doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`、`verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md` |
| 人侧甄别 | `doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md` |
| 已关闭的 HCC 卡 | `doc/tasks/HOST-CONCURRENCY-FLAKY-1.md`（含三轮复核结论 + L-1…L-4） |
| 三轮复核报告 | `verification/HOST-CONCURRENCY-FLAKY-1/review-ac6{,-2nd,-3rd}.md` |
| 当前 DAG | `doc/REBASELINE_PLAN.md`（**行数已满 64/64**） |
| 当前状态 | `doc/STATUS.md` |

---

## 8. 一句话交接

**R15 后目标四点全部达成（含目标 C 41/41）；R16 已把 Release Gate 条件 6 关闭**（六条里唯一 Agent 可独立收口的一条），
四件套在 head `45af57007` 全 EXIT=0（`1591/1639`，48 skipped），Gate 总体仍 `BLOCKED`（条件 3/4/5 需人）。
**最高优先 = §2 队列 0（`GOV-DECLARATION-SCAN-CLEANUP-1` AC3）**；但它**不能直接开工**：154 条里 12 条被活 pin 钉死，
必须先出「活 pin B2 走解释层绑定 + B3 规则口径 + scope 扩到 doc/tasks」的裁定。估时 4–6 轮（B3 1 → B1 1–2 → B2 2–3）。
评估已落盘：`doc/reviews/GOV-DECLARATION-SCAN-CLEANUP-1-AC3-BASELINE-REDERIVATION-2026-11-16.md`。

---

## 3p. R17（本轮）—— AC3 开工：Codex 裁决 + Q3 别名批

- **裁决**：Codex（`codex-cli 0.162.0` / `gpt-6-luna` / xhigh，会话 `01a1e3fd…`）出 `APPROVED_WITH_CONDITIONS`，
  四问逐条：Q1 逐表 `template_bindings`；Q2 逐文件 `raw_non_declaration_bindings`（带 `expected_diagnostics`）；
  Q3 **封闭别名表**（5 个精确 token）；Q4 AC5 追加式窄例外 + 新增 AC7（单元级 `allowed_cells`）。
  ⚠️ 裁决者自述其 Windows 进程被 **错误 740** 拒绝启动 ⇒ **未独立复核字节**，只按请求文事实裁定；已在采纳记录里如实保留。
- **归属表冻结**：`verification/GOV-DECLARATION-SCAN-CLEANUP-1/ac3-baseline-disposition-2026-11-16.md`，
  按审计 JSON 原始顺序 154 行（ERR-001…154），带 code/桶/位置/活 pin；锚定 `report_sha256`。
- **batch 1（Q3）**：`DISPOSITION_ALIASES` + `DISPOSITION_ALIAS_APPLIED` 警告 + 9 项测试（含「未列 token 仍 fail-closed」、
  「大小写不折叠」负例）。实测 **154→147**，`protected_roots` **不缩反增 5**。
  同时**暴露** 1 条被错误 disposition 掩盖的真实缺陷（Credential Manager 描述文本当路径）⇒ 转 B2，不做消音。
- **顺带发现（登记，不在 AC3 桶内）**：`tools/governance/tests/test_canonical_evidence_basis.py` 在
  **HEAD 未含本轮改动** 时同样 **9 failures**（用 `git stash` 复现）⇒ 既有债务，非本轮回归。
- **AC 变更**：新增 **AC7**（B2 单元级修复，`<<PARTIAL>>`）+ **AC5 追加式窄例外**（不追溯改写原核验）。

### 队列 5 —— 剩余非终态卡清单（R18 实测，11 张）

| 卡 | 状态 | 剩余工作 | 谁可做 |
|---|---|---|---|
| `MAINT-1-RELEASE-MONITOR` | in_progress | 伞形哨位；Gate 3/4/5 待人类输入 | 人工 |
| `SIDECAR-REBUILD-1` | in_progress | AC5/AC6 未勾；capabilities 17 / 13 失败拆 E-6 | Agent 可续 |
| ~~`GATE3-MATRIX-EXPAND-1`~~ | **done（R19）** | 三轮独立复核（REJECTED→REJECTED→ACCEPTED）；更正 80→79、951→962 两个实测数字；终态材料补齐 | 已完成 |
| `GATE3-SETTINGS-SHORTCUT-1` | in_progress | 同上（AC1–AC6 全勾） | Agent 可续 |
| `DOC-CTRLCHAR-FIX-1` | in_progress | AC1–AC6 全未勾 | Agent 可续 |
| `INSTALLER-MATRIX-1` | in_progress | 安装矩阵/签名，属 Gate 条件 4 | 人工（签名/GT） |
| `FEA11-ENTRY-MISSING-1` | blocked | 依赖 FEA-11 入口缺失 | 待裁定 |
| `GIT-CLEAN-PUBLICATION-DIAG-1` | approved | 待集成 | Agent 可续（需先看卡） |
| `GIT-CLEAN-PUBLICATION-1` / `GIT-CLEAN-RUST-ISOLATION-1` | in_review | 待复核/集成 | Agent 可续 |
| `GIT-CLEAN-CORE-ENV-2` | proposed | 未激活 | 需 DSH 释放 |

**结论**：Agent 侧仍有可执行项（上表标「Agent 可续」的 6 张），但每张都要按终态要求整理证据 + 独立复核 + 收口，单轮只能推进 1–2 张。

### 队列 6 —— R20 终局核验（四件套 + 证据巡检）

| 项 | 命令 | 结果 |
|---|---|---|
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)** |
| 声明审计 | `python -B tools/governance/clean_workspace.py --audit-declarations --out <dir>` | **0 error**；6,870 declarations；**protected_roots 5,657**（要求 ≥5593） |
| Pin 审计 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)** |
| 证据巡检 | `python -B tools/governance/audit_evidence_pins.py` | **FAIL 0** / EXEMPTED 84 / NOT_ENFORCED 15 / WARN 273（7,113 行 / 667 卡） |
| 治理测试 | `python -B -m unittest tools.governance.tests.{test_evidence_exceptions,test_bulk_evidence_manifest,test_audit_evidence_pins,test_evidence_eol_forms}` | 全过（13 + 8 + 15 + 7） |

**R20 修掉的回归**：我此前批量脚本改坏了 21 张卡的 Resource Manifest 表头/行形状，导致声明审计
23 error；已恢复表头、补尾 `|`、合并第 7 列（未动任何 Canonical Evidence 行），审计回 0。
证据：`verification/GOV-DECLARATION-SCAN-CLEANUP-1/declaration-audit-{2026-11-17-post-repair.json,repair-2026-11-17.log}`。
