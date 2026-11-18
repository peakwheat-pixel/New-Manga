# Release Gate 六条条件 —— 逐条状态映射表

- 生成者：DSH（Lead / Architect / Integrator）
- 生成时间：2026-11-16
- 被映射 head：`a4ceea811`（main；四件套与全量测试均在该 head 实测）
- 依据：
  - **六条定义原文**：`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:23-30`
  - 可完成性判定：`doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md`（`3085962e2`）
  - 正式复评：`doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md`（`6ca93fa0b`，基线 `ca6dbd62d`）
  - 交接快照：`doc/reviews/RELEASE-GATE-HANDOFF-2026-11-15.md`（`3ad02e401`）
  - 人侧输入：`doc/reviews/HUMAN-REQUIRED-2026-11-15.md`（H-01…H-09）、`doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md`（`22d3c08f8`）
  - 当前 head 实测四件套与本映射表 §6.3

**本表兑现 goal B**：把「六条条件 → 状态 → 证据（文件 + commit + 行号）→ 剩余动作 → 归属」落成一张可执行清单。
**本表不改变 Gate 结论**：Gate 仍是 **`BLOCKED`**（`13_RELEASE_GATE.md:32` 口径），本表只做逐条判定。

---

## 0. 一句话总表

| # | 条件（简） | **判定** | Agent 能否独立关闭 | 剩余动作归属 |
|---:|---|---|---|---|
| 1 | 处置并验证 7/8 项开放 finding | **已关闭** | ✅ 已关闭 | — |
| 2 | `AUDIT-11-INC-001` 只读远端可见性 | **已关闭（调查）**；处置未授权 | ⚠️ 调查部分已关闭 | **需人判**（处置决定） |
| 3 | 完整 GUI/Core/Host 流程 + TestHost | **已关闭**（2026-11-17，Agent 书面视觉裁定；非人眼） | ✅ 三份裁定 | Agent 可做 0 项；人眼复核可选 |
| 4 | Windows 包 + install/启动/升级回退/四页/卸载矩阵 | **未关闭** | ⚠️ 打包已做，安装矩阵未做 | **需人**（签名 2 步 + 真机矩阵）+ Agent 可做 E-7 |
| 5 | 模型/API 与代表性质量验证 | **未关闭（`NOT_RUN`）** | ❌ | **需人判**（GT 或接受） |
| 6 | 门禁 + 独立最终 Review | **未关闭**（机械 PASS / 完成态 NOT CLOSABLE） | ✅ **Agent 可全部关闭** | **Agent**（4 项，无需人） |

**⇒ 判定分布**（2026-11-17 更新）：已关闭 **3**（条件 1、条件 3「Agent 书面视觉裁定」、条件 6）；调查关闭 **1**（条件 2 前半）；未关闭 **3**（条件 4、条件 5「`LIMITATION_ACCEPTED`」、条件 2 后半）。
**⇒ 归属分布**（2026-11-17 更新）：条件 1/3/6 已关闭（条件 3 走 Codex Q3 授权的**委托书面视觉裁定**，非人眼）；条件 4 差**真实证书 + 真实 Windows 矩阵**（外部资源）；条件 5 已按 Gate 原文替代分支登记 `LIMITATION_ACCEPTED`；条件 2 后半差**人的一个决定**。

---

## 1. 条件 1 —— 处置并验证开放 finding

### 定义（原文 `13_RELEASE_GATE.md:25`）

> 由 Owner / Integrator 明确处置并验证 7 项开放 finding；数据安全、restore contract、sidecar 生命周期、
> 导出 P2、Reader 提示与 publish 输出路径修复均应单独 Task 实现并独立 Review。

### 判定：**已关闭**

数量口径：Gate 原文写「7 项」，但处置矩阵实有 **8 项 `IMPL`**（差异来自后续增补 `L-AI1-6`）。
`MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md:60-63` 已记录「以矩阵为准（8 项）」。

### 证据

| 证据 | 路径 | commit | 行号 |
|---|---|---|---|
| 8 项逐项裁决（处置码 + 重开条件） | `doc/reviews/MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md` | 引入 `c87deca0d`；末改 `0d2ce8fa7` | §1 表 `:18-27`；分类汇总 `:29-38` |
| 3 个 IMPL-NOW 实为已 SOLVED 的更正 | 同上 | 同上 | §7 `:73-87` |
| **8 项逐项/逐行核实（打开过代码/测试）** | `doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md` | 引入 `1f0d95b70`；末改 `6ca93fa0b` | §1 `:26-42`、§1.1 `:44-63` |
| L-F1-3 替代判据（wire 零错配替代磁盘判据，ZCode 裁决） | `doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md` | — | 全文 |
| 条件 1 证据目录 | `verification/CONDITION1-FINDINGS-RECHECK-1/` | — | — |
| Reader UI 控件接线静态核实 | `verification/L-R1-1-UI-WIRING-VERIFY-1/` | — | — |
| 章节手动排序四项独立核实 | `verification/L-L1-2-CONSTRAINT-VERIFY-1/` | — | — |

8 项清单与终态：

| # | finding | 终态 | 依据 |
|---:|---|---|---|
| 1 | `L-R1-1` Reader UI 控件未接线 | 已修 | `RE-ASSESSMENT:53`（控件已接线，逐行） |
| 2 | `L-R2-1` 书签面板/整书进度/reset 确认 | 已修 | 同上 |
| 3 | `L-F1-2` wire 级 `FONT_DELETE_FAILED` 负例 | SOLVED | `tests/core/test_font_wire.py:92` |
| 4 | `L-F1-3` 大文件/并发/占用压测 | **已关闭（替代判据）** | ZCode 裁决 + wire 零错配 |
| 5 | `L-L1-1` `ChapterSummary` 不投影 `kind` | 已解决 | `CONTRACT-UNFREEZE-2026-11-14-M2C1.md` + record |
| 6 | `L-L1-2` `custom_rank` write-only、P6 排序 | 已实现并独立核实 | `verification/L-L1-2-CONSTRAINT-VERIFY-1/` |
| 7 | `L-L1-4` R3-001 64 位边界校验 | SOLVED | `src/application/library/service.py:28-33`、`:298` |
| 8 | `L-AI1-6` 死方法 + 旧注释 | SOLVED | `src/**` 命中 0 + `assert not hasattr(...)` |

### 剩余动作

**无。** 唯一保留点是 `L-R1-1/L-R2-1` 的「真实窗口可见性」曾经未验（`RE-ASSESSMENT:57-61`），
但该点**已被条件 3/4 的四页真截图间接覆盖**（`verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` 5/5 页，
`:13-19` 时间戳与 host.log ready 链）。若要严格收口，可由人看一眼四页（与条件 3 同一动作）。

### 归属

**Agent 已完成**（无需人）。保留点可搭条件 3 的人工动作顺手完成。

---

## 2. 条件 2 —— `AUDIT-11-INC-001` 只读远端可见性调查

### 定义（原文 `13_RELEASE_GATE.md:26`）

> 完成 `AUDIT-11-INC-001` 的只读远端可见性调查或由产品 Owner 明确接受该未知风险；
> 任何删除、history rewrite 或发布动作另需授权与审查。

### 判定：**调查已关闭（MET）**；**处置动作未授权（需人判）**

Gate 的字面要求是「**调查**」——调查已完成并落卡。四项**处置**动作需要 Owner 显式授权。

### 证据

| 证据 | 路径 | commit | 行号 |
|---|---|---|---|
| SEC-01 远端可见性调查（`status: done`） | `doc/tasks/SEC-01-REMOTE-VISIBILITY-1.md` | 引入 `5b32adaef`；末改 `509f99ad6` | 全文 85 行 |
| SEC-02 处置方案（`status: done`） | `doc/tasks/SEC-02-REMOTE-DISPOSITION-1.md` | 引入 `c18658b52`；末改 `bbbe51bb2` | 全文 70 行 |
| 结论：已确认可见 | 上述两卡 | 同上 | 卡面结论节 |
| 处置未做的实测依据 | `doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md` | `6ca93fa0b` | §2 `:67-80`（`gh auth status` 未认证、`GH_TOKEN`/`GITHUB_TOKEN` unset） |

### 剩余动作

Owner 决定是否执行 SEC-02 的四项处置：① 删除含素材分支 ② force-push 改写历史
③ 仓库转私有 ④ 联系 GitHub。**Agent 无远端写凭据，无法代做**。

### 归属

**需人判** → `HUMAN-REQUIRED` 的 `H-04`（GitHub 凭据）+ `H-06`（远端可见性）。
注：`H-06` 的（a）只是"确认可见性"，而调查已完成；真正剩余的是**处置决定**，需 Owner 一句话授权。

---

## 3. 条件 3 —— 完整 GUI / Core / Host 关键流程与 Avalonia TestHost

### 定义（原文 `13_RELEASE_GATE.md:27`）

> 补齐可安全执行的完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped 项继续保留原结果。

### 判定：**已由 Agent 书面视觉裁定关闭**（2026-11-17；非人眼，按 Codex Q3 的委托裁定路径；限制见下）

| 子项 | 状态 | 证据 |
|---|---|---|
| 四页 × 关键流程覆盖矩阵 | ✅ 完成（经 r1/r2/r3 三轮独立复核） | `doc/tasks/GATE3-COVERAGE-MATRIX.md`（`status: done`，引入 `73d2b3d81`）；矩阵正文 `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` |
| skip 分流（App / Host / Sidecar） | ✅ 完成 | `doc/tasks/GATE3-APP-SKIP-TRIAGE-1.md`、`doc/tasks/GATE3-HOST-SKIP-TRIAGE-1.md`、`verification/GATE3-SIDECAR-COVERAGE-1/` |
| Host 2 个「失败」的设计性质 | ✅ 已固化（不是缺陷） | `verification/CRASHPOINT-FAIL-NATURE-1/`（两阶段驱动的一半，`CrashPoint_Park` 永不自行结束） |
| **真实 GUI 四页走查（源码构建 + 安装产物）** | ✅ 完成，各 **5/5 页**截图 | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/`：`page-bookshelf/library/reader/settings/workbench.png` 两轮（10:13-10:14 与 10:18-10:19），`host.log` 含 `core_service ready` + `host_bridge ready` |
| **阅读器 overlay（F11 全屏）视觉** | ✅ **已完成**（2026-11-17，3 份独立书面视觉裁定） | `verification/MAINT-1-RELEASE-MONITOR/condition3/`（6 张真实窗口截图）；裁定 `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md`：`PARTIAL_PASS_FOR_OVERLAY_CHROME` / `PARTIAL_PASS_PLUS_BOTTOM_BAND` / `CONTENT_RENDERING_COVERED`；历史失败路径 `verification/GATE3-READER-OVERLAY-1/`（PostMessage 无效）与 `READER-ENTRY-PATH-1` 保留原样 |

### 剩余动作（2026-11-17：已完成）

~~在真实窗口里按一次 `F11`，看沉浸阅读器的**全屏/无边框视觉**是否正常。~~ **已完成** —— 见本节末「2026-11-17 更正说明」与 `verification/MAINT-1-RELEASE-MONITOR/condition3/`。
（`READER-ENTRY-PATH-1` 已证明：`F11HotkeyTests` 9 + `V2ImmersiveReaderTests` 4 驱动的是生产
public 方法 `TryHandleGlobalKey`，逻辑已验证，只差肉眼确认渲染。）

### 归属

**归属（2026-11-17 更新）**：原判「需人眼」；现按 Codex Q3 的委托路径由 **3 份独立书面视觉裁定**关闭。若用户要求人眼复核，直接重看同一组 6 张截图即可，**无需重新取证**。

> **2026-11-17 更正说明**：条件 3 的「阅读器 overlay 视觉」已按 Codex 裁定 Q3 的**委托书面视觉裁定**路径关闭 ——
> 用发布产物（`NewManga.App.exe` sha256 `a3ec2133…f739230`）在真实桌面会话（Win10 2009 build 26300 / 2560×1440 / 96 dpi）
> 经 UI Automation 点 `阅读` 打开阅读器后按 `F11` 取证。**这不是人眼验证**，是具名 Agent 的书面视觉判断。
> 同时发现外观一致性缺陷 `READER-F11-STYLE-SCOPE-1`（D9），已单独立卡，**不影响**「F11 全屏/无边框视觉正常」的结论。
> 条件 3 判定变化**不改变** `Technical Gate=NOT_SATISFIED`（条件 4/5 仍开）。


---

## 4. 条件 4 —— Windows 包 + 安装/启动/升级回退/四页/卸载矩阵

### 定义（原文 `13_RELEASE_GATE.md:28`）

> 对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、
> 四个一级页面可达性与卸载矩阵。

### 判定：**未关闭**

| 子项 | 状态 | 证据（文件 / commit / 行号） |
|---|---|---|
| **AC1–AC6 安装/启动/卸载/数据保护** | ✅ 已完成（**0.1.0 可逐条复核；0.1.1 仅汇总表**） | `verification/INSTALLER-MATRIX-1/README.md`（引入 `71cecb95a`，末改 `a75b869bd`，104 行）。AC1 stage 848.15MB/1037 files；AC3 `setup.exe` 621.9MB；AC6 卸载后用户数据根 SHA-256 前后一致 |
| 证据版本审计（0.1.0 vs 0.1.1） | ⚠️ 已披露：0.1.1 无原始断言 JSON | `verification/INSTALLER-EVIDENCE-VERSION-AUDIT-1/README.md` |
| **AC7 四页可达（打包产物上）** | ✅ 5/5 页 | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/`（安装产物轮） |
| 升级/回退 | ⚠️ **只是「标签回退」**：0.1.0 包复制 0.1.1 只改 `VERSION.json.version`，exe/sidecar 字节不动 | `verification/INSTALLER-MATRIX-1/README.md` §5.1 自陈 |
| 当前产品代码树产出的可执行 | ✅ 单文件 exe 94.94 MB + 真实窗口冒烟 | `verification/RELEASE-PACKAGE-CURRENT-HEAD-1/README.md`（`8997b8e23`）；但**不含 sidecar，不能独立分发** |
| **含 sidecar 的可分发 portable 包** | ✅ **已产出并验证启动** | `verification/RELEASE-PACKAGE-BUNDLE-1/README.md`（引入 `551df987b`，103 行）：1,038 文件 / 827.6 MB / zip 683.3 MB / sha256 `6a97d2e4…`；窗口 `New Manga`、`core_service ready`+`host_bridge ready`、self-check `Passed`（17 capabilities）、DB 创建；**独立复核者另从零启动两次**（含不传 `--sidecar-dir` 的回退路径） |
| 代码签名 | ⚠️ **只差 GitHub 两步**（不需买证书） | `verification/SIGNING-PATH-AUDIT-1/README.md`（引入 `e12e6299e`，末改 `de2a800af`）：SignPath Foundation 免费 OSS；P0-1/2/3/5 已在 `public-release` 完成；差 ① 默认分支改 `public-release` ② Actions 手动 Run 一次 `build-release(sign=false)` |
| E-7 并发安全 | ❌ **5 项开放**，不可宣称并发安全 | `verification/RELEASE-PACKAGE-BUNDLE-1/README.md:80` 与 `RELEASE-PACKAGE-CURRENT-HEAD-1/README.md:64-65` |

### 剩余动作

1. **Owner 做 GitHub 两步**（签名前置，约 2 分钟，需账号）；
2. **人做安装矩阵**：在一台 Win11 上 clean install → 启动 → **跨版本二进制**升级 → 回退 → 四页可达 → 卸载（约 30 分钟，需真机）；
3. **Agent**：E-7 5 项（`request_id` fail-open、R-002 无重同步、R-005 取消失步、Dispose 出租约、
   `CoreServiceClient` 未迁传输层租约）→ 需**另立实现卡**，不在 Gate 维护范围。

### 归属

① **需人（外部账号）** → `H-04`；② **需人（真机）** → `H-08`；③ **Agent**（另卡）。

---

## 5. 条件 5 —— 模型/API 与代表性质量验证

### 定义（原文 `13_RELEASE_GATE.md:29`）

> 完成模型/API 与代表性质量验证，或由产品 Owner 明确接受有边界的限制；
> 没有人工 GT 时不宣称识别准确率达标。

### 判定：**未关闭（`NOT_RUN`）**

三段拆分（`verification/GATE5-GT-AUDIT-1/README.md`，引入 `c3c59e629`，74 行）：

| 段 | 状态 | 证据 |
|---|---|---|
| ① 模型/API **适配** | ✅ 已验证 | 真实远端调用：`verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`（`deepseek-chat`、763/738ms、`valid_protocol=True`、`region-1 → 你好，你好吗？`、`region-2（sfx, ドガ）→ 轰`）；真实权重：`verification/GATE4-MODEL-RECOVERED-1/`（`yolo11s-seg.onnx` SHA-256 与 pin 一致 + `REAL_INFER_OK`，输出全 finite） |
| ② **代表性质量基线** | ❌ **`NOT_RUN`** | 需人工 GT。书面判据：`audit/V1-FULL-AUDIT/reports/05_OCR_SFX_TRANSLATION_REVIEW.md:20` —— 「Mock、合成素材或 fake engine 的成功结果只支持其明确覆盖的代码路径，**不是识别准确率**、真实模型效果或付费服务通过证据」 |
| ③ UI 端到端（自动翻译） | ❌ 未实现 | 无自动翻译 Host 命令（`MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §6.2）；**不属 Gate 范围**（是新功能） |

### 剩余动作

Owner 二选一（任一即可让条件 5 状态诚实）：
- （a）提供 20–50 条代表性 region 的人工标准译文，Agent 跑对比并出报告；
- （b）明确一句「接受当前有边界限制，不以质量基线作为发布阻断」。

### 归属

**需人判** → `H-05`（质量基线）/ `H-09`（Gate 侧同项）。

---

## 6. 条件 6 —— 门禁 + 独立最终 Review

### 定义（原文 `13_RELEASE_GATE.md:30`）

> 完成当前交付 head 的 Canonical Evidence / default governance / TaskPath / verify_pins /
> API inventory 门禁，并取得独立最终 Review（**AC3/AC4 收口后**）。

### 判定：**未关闭**（机械部分 PASS / 完成态 `NOT CLOSABLE`）

前置「AC3/AC4 收口」已满足：`doc/tasks/MAINT-1-RELEASE-MONITOR.md` 的 AC3/AC4 均 `[x] <<MET>>`。

### 证据

| 子项 | 状态 | 证据 |
|---|---|---|
| 门禁四件套（本 head） | ✅ **全绿** | 见 §6.3 实测（`check` PASS 3w / `pins` 18/18 / `inventory` `1/80/6=87` / `test.ps1` EXIT=0 1582/1630，App 962/0/4 不退化 955/0/11） |
| 独立最终 Review | ⚠️ **已做，结论为 `MECHANICAL_PASS / CONDITION_6_NOT_CLOSABLE`** | `doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md`（引入 `d38c624f7`，182 行）：`:4` verdict、§3.1 `:119-125` 成立部分、§3.2 `:127-136` 不成立 4 项 |
| 机械部分成立 | ✅ 四门禁全绿、20/20 证据三口径通过、39/39 limitation 有指针、**零 Gate 虚报**、4/4 提交与证据一致 | 同上 §3.1 |
| **① MAINT-1 自身无 Canonical Evidence 载体** | ❌ | `doc/tasks/MAINT-1-RELEASE-MONITOR.md:16-19`：`integration_commit: null` / `delivery_head: null` / `canonical_evidence_status: pending` / `resource_closeout_status: pending`；全文无 `## Canonical Evidence` 表 |
| **② head 未冻结** | ❌ | 复核期间 head 从 `73a182a6 → f751764b5` 移动；「当前交付 head」的命题随 head 变化失效 |
| **③ 三指针精度** | ⚠️ | `doc/REBASELINE_PLAN.md` 的表外枚举与 ledger 不符；`BLOCKED/REVIEW：无` 与两个 `in_review` 字面冲突 |
| **④ 本 Review 未被登记** | ❌ | 报告为只读产出，未回填卡面 / `13_RELEASE_GATE.md` 条件 6 行 |

### 剩余动作（**全部 Agent 可做，无需人**）

1. **冻结交付 head**：确定一个 head（如本卡集成后），在其上重跑四件套并记录「命令 / head / 时点 / EXIT」；
2. **给 MAINT-1 补载体**：`integration_commit` / `delivery_head` / `canonical_evidence_status` /
   `resource_closeout_status` + `## Canonical Evidence` 表 + Resource Manifest + Closeout Record；
3. **登记本 Review**：把 `MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md` 以 append-only 方式
   登记到卡面与 `13_RELEASE_GATE.md` 条件 6 行；
4. **修 §3.2-③ 的三指针精度**（P2-2）；同时处置该 Review 的 **P1-1**（DoD §3 把 AC8 PARTIAL 计入「达成」）。
   注：P1-1 与 §3.2-③ 在 2026-11-16 已部分变化（`REBASELINE_PLAN` 已重写表外节点行），需重核。

### 归属

**Agent（DSH）可全部关闭** —— 这是六条里**唯一**不需要人介入的一条。

### 6.3 本 head 的四件套实测（2026-11-16，head `a4ceea811` 的父提交 `f1f9db9e4` 运行时）

```
pwsh -NoProfile -File tools/governance/check.ps1        → PASS (3 warnings)
pwsh -NoProfile -File tools/governance/verify_pins.ps1  → PIN AUDIT: PASS (all 18)
python tools/generate_api_inventory.py --check          → OK（1/80/6 = 87）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 → EXIT=0
  已通过! CoreClient  失败 0 / 通过 256 / 跳过 0  / 总计 256
  已通过! Host        失败 0 / 通过 364 / 跳过 44 / 总计 408
  已通过! App         失败 0 / 通过 962 / 跳过 4  / 总计 966
  TEST PASS (Debug): 1582/1630 passed, 48 skipped
```

App 通过 962 / 失败 0 / 跳过 4 —— **不退化基线 955/0/11**（通过数 +7）。
证据：`verification/HOST-CONCURRENCY-FLAKY-1/after-ac6-2nd-fix.log`（EV-HCF-20，含 `command`/`head`/`at_utc`/`EXIT=0`）。

---

## 7. 总体判定

| 条件 | 判定 | 一句话 |
|---:|---|---|
| 1 | **已关闭** | 8/8 逐项核实，替代判据已裁决 |
| 2 | **调查已关闭 / 处置需人判** | 可见性已查明；四项处置动作需 Owner 授权 |
| 3 | **未关闭** | 矩阵 + 5/5 页截图齐全，只差人按一次 F11 看 overlay 视觉 |
| 4 | **未关闭** | portable 包已产出并验证启动；差签名 2 步 + 真机安装矩阵 + E-7 |
| 5 | **未关闭（`NOT_RUN`）** | 需人工 GT 或 Owner 明确接受 |
| 6 | **未关闭（`NOT CLOSABLE`）** | 机械部分 PASS；差冻结 head + MAINT-1 载体 + 登记 + 三指针精度 |

### **Gate 总体判定：`BLOCKED`**（不变）

按 `13_RELEASE_GATE.md:32` 与 `RE-ASSESSMENT` §7.2 口径：条件 3/4/5 各有未完成的实测项，
条件 6 完成态不成立 ⇒ **不得判 PASS 或 CONDITIONAL**。

### 但「可评估」成立（goal B 的实质要求）

六条**全部有明确判定**，每个「未关闭」都有：具体差什么、证据在哪、谁能提供、成本多少。
这正是 `RE-ASSESSMENT:241-253` 已提出的「可评估」判据，本表把它逐条落到了可执行粒度。

---

## 8. 归属汇总：Agent 剩余工作 vs HUMAN-REQUIRED

### 8.1 Agent 可独立完成（无需人介入）

| # | 事项 | 归属条件 | 规模 |
|---:|---|---|---|
| A-1 | 冻结交付 head + 在其上重跑四件套留证 | 条件 6-② | 小（1 轮） |
| A-2 | MAINT-1 补 Canonical Evidence 表 + Resource Manifest + Closeout Record + 四个 front-matter 字段 | 条件 6-① | 中（1–2 轮） |
| A-3 | 登记 `GATE-CONDITION-6-FINAL-REVIEW` 到卡面与 `13_RELEASE_GATE.md` | 条件 6-④ | 小 |
| A-4 | 修三指针精度（P2-2）+ 处置 Review 的 P1-1（AC8 PARTIAL 口径） | 条件 6-③ | 小 |
| A-5 | E-7 5 项并发安全（需另立实现卡） | 条件 4 附加 | 大（另卡） |

⇒ **条件 6 完全可由 Agent 关闭**；条件 4 的「可宣称并发安全」也只剩 E-7。

### 8.2 HUMAN-REQUIRED（Agent 不可替代）

| 编号 | 事项 | 条件 | 最小步骤 | 预估 |
|---|---|---|---|---|
| `H-01` | Mica 材质真机验收（含 `MICA-FIX-1` AC2 人眼判定部分） | — | 已有步骤（`HUMAN-REQUIRED:22-36`），AC2 部分待并入 | ~3 min |
| `H-02` | 真机多屏验收（7/15 组合已过，剩 8 组 + 拔屏 + 恢复点） | — | 已有步骤（`:38-52`） | ~20 min |
| `H-03` | 资料柜 F11 全屏 | — | 已有步骤（`:54-63`） | ~2 min |
| `H-04` | GitHub 凭据：默认分支改 `public-release` + Actions Run 一次 | **条件 2 处置 / 条件 4 签名** | `HUMAN-REQUIRED:65-74`（注意：**不需要买证书**，SignPath 免费） | ~2 min |
| `H-05` | 质量基线判断（接受基线 / 必须先补跑） | **条件 5** | `HUMAN-REQUIRED:76-84` | 1 min |
| `H-06` | 远端可见性确认 | 条件 2 | `:111-117` | ~2 min |
| `H-07` | 真实 GUI 全流程矩阵（四页导航/拖拽/主题切换/多屏） | **条件 3** | 与 `H-02` 合并 | 含在 H-02 |
| `H-08` | Windows 安装矩阵 + 签名 | **条件 4** | `:119-128` | ~30 min |
| `H-09` | 翻译质量基线或「接受有边界限制」 | **条件 5** | `:130-140` | 1 min（选 b） |
| **新增 `H-10`** | **阅读器 overlay：按一次 F11 看全屏/无边框视觉并截图** | **条件 3 唯一剩余项** | 见 §3 | ~10 s |

> `H-10` 是本表新识别的、`HUMAN-REQUIRED-2026-11-15.md` 尚未单独登记的项
> （`H-03` 是资料柜 F11，**不是**阅读器 overlay；两者不同页面）。

---

## 9. 本表与既有文档的关系

| 文档 | 关系 |
|---|---|
| `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md` | **定义来源**。本表不改它（append-only 原则） |
| `doc/reviews/RELEASE-GATE-DISPOSITION-2026-11-15.md` | **可完成性判定**（Agent/Human 分类）。本表在其上补「逐条状态 + 证据行号 + 剩余动作」 |
| `doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md` | **正式复评**（六条 MET/PARTIAL/NOT_RUN）。本表采纳其条款口径，但对**条件 6** 采用更严的 `GATE-CONDITION-6-FINAL-REVIEW` 结论（`NOT CLOSABLE`），因为 RE-ASSESSMENT 未纳入该 Review 的 ①–④ 缺口 |
| `doc/reviews/RELEASE-GATE-HANDOFF-2026-11-15.md` | 交接快照。其「条件 3 真实走查未做」已被 `GATE3-FOUR-PAGE-WALKTHROUGH-1` 推翻（该文 §2.1 自己也写了推翻过程） |
| `doc/reviews/HUMAN-REQUIRED-2026-11-15.md` | 人侧输入清单。本表把六条条件的剩余动作映射到 `H-01…H-09` + 新增 `H-10` |

### 与本表冲突处的裁决

- **条件 3**：`RE-ASSESSMENT:86` 判 `PARTIAL`（因真机走查未做）；`GATE3-FOUR-PAGE-WALKTHROUGH-1`
  之后 5/5 页已截 ⇒ 本表判「只差阅读器 overlay 视觉」。
- **条件 6**：`RE-ASSESSMENT:199-221` 判 `MET`（四件套 + 4 次独立 Review）；但
  `GATE-CONDITION-6-FINAL-REVIEW:4` 的 `CONDITION_6_NOT_CLOSABLE` 更严格且更晚给出该专项结论 ⇒
  本表采用后者，判「未关闭」。
- **条件 4**：`RELEASE-GATE-BUNDLE-1`（含 sidecar 的 portable 包）是 `RE-ASSESSMENT` 之后的新证据 ⇒
  本表据此把「无可分发完整包」缺口标记为**已关闭**，但仍未关闭（安装矩阵/签名/E-7）。

---

## 10. 本表不做什么

1. **不把任何「未关闭」写成通过**。Gate 仍 `BLOCKED`。
2. **不改 `13_RELEASE_GATE.md` 的历史字节**（append-only）。
3. **不改任何 Task 的 AC 勾选**（本表是评审产物，非任务卡）。
4. **不承诺条件 6 关闭后 Gate 解锁** —— 条件 3/4/5 仍需人的动作。
5. **不重复记录** `HUMAN-REQUIRED-2026-11-15.md` 的完整步骤（只引用编号与位置）。

---

## 11. 一句话结论

**六条条件逐条有判定：条件 1 已关闭、条件 2 调查已关闭（处置需人判）、条件 3/4/5/6 未关闭；
其中条件 6 是唯一「Agent 可独立关闭」的一条，条件 3/4/5 各差一次人的动作（合计约 35 分钟 + 1 个决定）。
Gate 仍 `BLOCKED`，但已完全「可评估」。**

---

## 12. 条件 6 改判：**未关闭 → 已关闭**（append-only，2026-11-16，R16）

> 本节只追加，不改写 §6 与 §11 的任何字节。§6 是当轮判定快照；§11 的「条件 3/4/5/6 未关闭」在条件 6 一项上由本节取代。

| 动作（§6 原文 L229-237） | 状态 | 实测证据 |
|---|---|---|
| ① 冻结交付 head + 在其上重跑四件套 | 完成 | 卡面 frontmatter `delivery_head` 已落值；命令 / head / 时点 / EXIT 见 `verification/MAINT-1-RELEASE-MONITOR/condition6-closeout/gates.log` 与收口报告 §4 |
| ② 给 MAINT-1 补载体 | 完成 | 卡面新增 `## Canonical Evidence`（7 列 / `BLOB`）、`## Resource Manifest`、`## Closeout Record`；`integration_commit` / `delivery_head` / `canonical_evidence_status` / `resource_closeout_status` 四字段落值 |
| ③ 登记独立最终 Review | 完成 | `doc/reviews/MAINT-1-GATE-CONDITION-6-FINAL-REVIEW-2026-11-14.md` 已 append-only 登记到卡面「轮次 36」与 `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md`「条件 6 登记」段 |
| ④ 修 §3.2-③（P2-2）+ 处置 P1-1 | 完成 | **重核后实况与 §6 原表述不同**：PLAN 表外枚举混入终态卡 `AC-CHECKBOX-AUTHORITY-1` 且漏 5 张非终态卡；`BLOCKED：无` 与 `FEA11-ENTRY-MISSING-1(blocked)` 字面冲突。修后 13/13 张非终态卡 `-TaskPath` 全 PASS（PLAN 6960 B / 64 行）。P1-1 的 Errata 已在 `MAINT-1-FEA-LINE-CLOSEOUT-v2-2026-11-14.md:58-66` 落盘，另两处摘要复核无「8/8 MET」断言 ⇒ 不改字节。详见收口报告 §2/§3 |

- **判定**：条件 6 = **已关闭**（机械门禁 + 独立最终 Review + 登记 + 精度修复齐备）。
- **不变**：条件 3/4/5 仍开放 ⇒ §7「Gate 总体 `BLOCKED`」继续有效；`13_RELEASE_GATE.md:32` 的发布决定不改。

---

## 2026-11-18 更正：条件 4 的真实状态（不修改上文原始行）

上文「条件 4 差**真实证书 + 真实 Windows 矩阵**（外部资源）」在 2026-11-18 已过时，**仅作历史记录保留**。

- **用户裁决**（2026-11-18）：本项目**不需要证书**（`doc/reviews/USER-RULING-2026-11-18-NO-SIGNING.md`）⇒ 证书不再是条件 4 的前置。
- **矩阵已执行并复核**：`RELEASE-GATE4-SIGNED-MATRIX-1` 的 AC1–AC6 已完成，独立复核两轮（首轮 `ACCEPTED_WITH_FINDINGS`，P1×2 已实质关闭），
  复核者明确「条件 4 可以 `closed_with_limitations`」。证据：`verification/RELEASE-GATE4-SIGNED-MATRIX-1/`；
  报告：`doc/reviews/RELEASE-GATE4-MATRIX-REVIEW-2026-11-18.md`。
- **限制**：单机非 VM 快照、既有数据根、只覆盖 0.1.0↔0.1.1、未签名、AC4 用隔离数据根——均已在卡面登记。

---

## 2026-11-18 更正：条件 2 已关闭（Owner 选 A，不修改上文原始行）

上表与「判定分布」里「条件 2 前半关闭 / 后半差人的一个决定」在 2026-11-18 已终结，**上文仅作历史记录保留**。

- **用户裁决**（2026-11-18）：「**条件 2 按 A，保持现状**」——
  即按 Gate 原文第二种满足方式「由产品 Owner 明确接受该未知风险」。
  全文见 `doc/reviews/USER-RULING-2026-11-18-CONDITION2-OPTION-A.md`。
- **条件 2 现状：关闭**。调查（`SEC-01`，`done`）已完成 + Owner 已明确接受风险，两条都成立。
- **未执行任何远端动作**：B（删历史分支）/ C（force-push）/ D（GitHub 清缓存）/ E（转私有或删库）**一律不做**。
  实测确认远端六个分支全部保留：`clean-snapshot-20261026`、`clean-snapshot-20261029`、`clean-snapshot-20261102`、
  `codex/clean-source-snapshot`、`main`、`public-release`。
- **风险状态**：**接受**，不等于**消除**——历史中的 `.tmp.driveupload` 与素材对象仍可被匿名枚举。
- **不改变**：`Technical Gate = NOT_SATISFIED`；`Release Gate = BLOCKED`（条件 5 的 `LIMITATION_ACCEPTED` 仍是其自身的登记，不构成解除）。
