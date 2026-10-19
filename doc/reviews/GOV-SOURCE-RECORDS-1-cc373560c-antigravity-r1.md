---
task_id: GOV-SOURCE-RECORDS-1
reviewer: Antigravity
reviewed_head: cc373560c
verdict: APPROVED
conversation_id: 4b1a0e16-a7ba-4f76-ba8f-d80a8440de3f
note: 逐项核对 12 个补勾均有书面依据；AC4 保留未勾判为「非常恰当」；确认既有缺陷与本次改动无关；明确意见为「绝不应当顺手修」
---
# Review 报告：Task GOV-SOURCE-RECORDS-1

- **审查对象**：[`doc/tasks/GOV-SOURCE-RECORDS-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-SOURCE-RECORDS-1.md)
- **Handoff**：[`doc/handoffs/GOV-SOURCE-RECORDS-1-d8ad739d2.md`](file:///G:/CODEX/New%20Manga/doc/handoffs/GOV-SOURCE-RECORDS-1-d8ad739d2.md)
- **交付 Commit**：`d8ad739d2` / Handoff 提交 `cc373560c`（Pin 修正 `5ed5fde21`）
- **审查结论**：**`APPROVED`**

---

## 逐条评议结论

### 1. 每一个补勾是否真有依据（逐项核对 12 个补勾）

核对结果：**补勾的 12 项全部在各自 Task 的 Canonical Evidence 表（`AC/Gate` 列）、测试要求表、交付与运行记录或 Closeout Record 中有明确书面依据，没有一项是从 `status: done` 反推的。**

#### 1.1 [`EXPORT-REVEAL-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md)（补勾 6 项）

- **AC1（先契约后实现）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L119](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L119)）：`EXPORT-REVEAL-CONTRACT` 的 `AC/Gate` 列明确标注为 **`AC1`**（对应 [`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`](file:///G:/CODEX/New%20Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md)）。
    2. 测试要求表（[L85](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L85)）：场景/AC 为 `AC1`，记载“PASS：§5.8 与合并前文本在换行归一后完全相同；R1 批准只绑定旧 head”。
    3. 交付与运行记录（[L107](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L107)）：“contract rev 2.4 与 production-only host command 实现先于测试完成；实现固定 commit `5f95aac0f`”。
    4. 独立审查（[L130](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L130)）：`EXPORT-REVEAL-REVIEW-R1` 覆盖 `AC1-AC7`。
- **AC2（实现）** → **`MET`，补勾**
  - **依据位置**：
    1. 交付与运行记录（[L107](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L107)）：“官方 `tauri-plugin-opener = "2"` 是唯一新增依赖；Rust 侧直接 opener API，无 shell 字符串及 WebView opener capability”。
    2. Closeout Record（[L144](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L144)）：“逐处做三方并集：三方功能全部保留；`gen/schemas/*` 由 tauri-build 重新生成后核对（34 条权限含 6 条 Run + reveal + 2 条事件）；RUN-IPC-1 的 `PRODUCTION_COMMANDS.len()` 断言由 24 更新为 25（REVEAL 合法新增一条命令）”。
- **AC3（依赖）** → **`MET`，补勾**
  - **依据位置**：
    1. 交付与运行记录（[L107](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L107)）：“官方 `tauri-plugin-opener = "2"` 是唯一新增依赖”。
    2. Closeout Record NIT（[L147](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L147)）仅记载 rustfmt 格式差异，确认未引入任何未授权或非官方依赖。
- **AC5（不越界）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L118](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L118)）：`EXPORT-REVEAL-POST-MERGE-RESOLUTION`（`verification/EXPORT-REVEAL-1/merge-resolution.md`）明确核验 §5.8 未变及冲突解决。
    2. 交付与运行记录（[L110](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L110)）与 Closeout Record（[L144](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L144)）详细记载三方并集与越界检查结果。
- **AC6（不回归）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L121-L122](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L121-L122)）：`EXPORT-REVEAL-CORE-TESTS` 标为 `AC6`；`EXPORT-REVEAL-RUST-PACKAGED` 标为 `AC4-③/AC6`。
    2. Closeout Record（[L145](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L145)）：“合并后重跑（Coordinator 亲自执行）：source 88 passed / 0 failed / 1 ignored、frozen 打包 10 passed / 0 failed、`tests/core` 405 passed，三条 exit 0。三族测试在同一二进制内全绿”。
- **AC7（固定交付）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L126](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L126)）：`EXPORT-REVEAL-POST-MERGE-HANDOFF` 明确标注 `AC/Gate = AC7`。
    2. Closeout Record（[L140-L143](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L140-L143)）：记录交付集成 `c9b113f96`（`--no-ff` 三方合并）、冻结 delivery_head `13ac5b30f`。

#### 1.2 [`P15.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md)（补勾 6 项）

- **AC1（布局与分类）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L94](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L94)）：`E6 布局/分类/禁用断言源`（`SettingsPage.test.tsx`）的 `AC/Gate` 列明确标注为 **`AC1/AC2`**。
    2. 测试要求表（[L65](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L65)）：场景 `AC1` PASS（十二分类顺序=冻结数组、200px nav + content panel、切换本地状态无子路由）。
    3. Closeout Record（[L112](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L112)）：独立 Reviewer 复跑前端 28 files / 274 tests passed。
- **AC2（可编辑范围）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L94](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L94)）：`E6` 标为 **`AC1/AC2`**。
    2. 测试要求表（[L66](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L66)）：场景 `AC2` PASS（11 分区逐项可见 + 控件 disabled + 无输入元素 + 原因含「等待 section schema 冻结」）。
    3. Closeout Record（[L113](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L113)）：“只开放契约 §7 清单内 4 个面（Provider+Capability / Network / SFX），11 个禁用分区逐条『可见/不可操作/有原因』”。
- **AC3（数据面与 Secret 边界）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L95](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L95)）：`E7 wire/Secret 反例断言源`（`client.p15.test.ts`）明确标注为 **`AC3`**。
    2. 测试要求表（[L67](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L67)）：场景 `AC3` PASS（单节 null/空对象/已设置三态区分；Secret 不入 DTO；§9 封闭错误投影）。
    3. Closeout Record（[L113, L115](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L113-L115)）：“Secret 四处零暴露（三层反例测试）”，并判定 `Error.message` 不构成泄露（RV-P15-01）。
- **AC4（状态矩阵）** → **`MET`，补勾**
  - **依据位置**：
    1. 测试要求表（[L68](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L68)）：场景 `AC4` PASS（五态完整，保存失败 draft 保留）。
    2. Closeout Record（[L113](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L113)）：“状态矩阵五态且保存失败保留输入”。
- **AC5（范围与证据）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L89-L93](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L89-L93)）：`E1`（AC1–AC5）、`E2`（AC5）、`E3`（AC5）、`E4`（AC5）、`E5`（AC5）共 5 项直接标注 `AC5`。
    2. Closeout Record（[L112, L117](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L112-L117)）：独立复核亲跑全套套件（前端 274 passed、Core 407 passed、cargo source 95/0/1、cargo packaged 12/0），且明确记载“GUI e2e = NOT_RUN（无头 WebView2 0x80070578）”。
- **AC6（交付）** → **`MET`，补勾**
  - **依据位置**：
    1. Canonical Evidence 表（[L97](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L97)）：`E8 独立 Review` 标注 `AC1–AC6`。
    2. Closeout Record（[L107-L111](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md#L107-L111)）：独立 Reviewer（dsh），BL-17 包含性逐条成立，修正 RV-P15-04 并在主仓库复算全部 pin；交付由 Coordinator 集成 `--no-ff`，Owner 未自行合并。

---

### 2. `EXPORT-REVEAL-1` AC4 保留未勾是否恰当

**判断：处理非常恰当，坚决支持保留未勾选。**

- **理由**：
  1. **标准整体性**：验收标准（Acceptance Criteria）是对功能契约的完整检验。AC4 包含 3 个明确子项，其中子项 ③（真实 GUI 往返）在 Closeout Record（[L146](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md#L146)）中明文记录为：
     > `AC4-③ = BLOCKED（原样保留）——真实"成功导出 → reveal → 文件管理器打开"未跑通：测试 fixture 无有效 book，且无头 Windows 无法取得 WebView2 窗口句柄（0x80070578）。`
  2. **诚实性底线**：AC4 原文特别警示“严禁伪造”。三分之二的达成不能等同于整体达成。若勾选为 `[x]`，哪怕追加注记，也会在各种自动化工具和宏观统计中被归为已完成，属于事实上的过度声明。
  3. **契约合规**：本 Task（`GOV-SOURCE-RECORDS-1`）自身 AC2（[L86](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-SOURCE-RECORDS-1.md#L86)）明确规定：“`BLOCKED` 项必须保持不勾选”。交付方严格执行了该规定。

---

### 3. 两个 Task 的检查错误是否与本次改动无关，以及既有缺陷的处置

#### 3.1 错误分类与归因独立复核

经执行 `tools/governance/check.ps1` 对当前文件与基线 commit `32f95fdf9` 的比对复核：

| Task | 改动前（基线 `32f95fdf9`） | 改动后（当前交付） | 变动原因 |
|---|---:|---:|---|
| [`EXPORT-REVEAL-1.md`](file:///G:/CODEX/New%20Manga/doc/tasks/EXPORT-REVEAL-1.md) | **3 errors** | **3 errors** | 错误类型与内容完全一致，零变动 |
| [`P15.md`](file:///G:/CODEX/New%20Manga/doc/tasks/P15.md) | **4 errors** | **3 errors** | 补勾消除了既有的“DONE 不能保留未完成 AC”错误，错误数净减 1 |

当前剩余的 3 类错误均为既有缺陷，完全与本次改动无关：
1. **Evidence SHA-256 不匹配**：
   - `EXPORT-REVEAL-1` 的 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：该契约在后续 commit 演进到了 rev 2.11，导致磁盘当前内容与历史交付时的 pin 哈希不同。
   - `P15` 的 `apps/desktop/frontend/src/settings/SettingsPage.test.tsx`：后续提交 `528c6289c` 修改了该测试文件，导致磁盘当前内容与交付时的 pin 哈希不同。
2. **evidence_dir 含未登记文件**：历史遗留的过程日志（如 `post-merge-packaged-capture-error.log`、`cargo-test-unfiltered-first-run.log` 等）未在各自 Task 的 Canonical Evidence 表中登记。
3. **缺 Resource manifest**：`P15` 引用的 `verification/P15/resource-manifest.json` 在仓库中确实不存在。
4. **`EXPORT-REVEAL-1` 的未完成 AC 报错**：由于 AC4-③ 真实阻塞而保留未勾选，触发了检查器的规则，反映的是真实情况。

**结论：交付方“没有引入新错误”的说法完全成立。**

#### 3.2 明确意见：是否应该在同一 Task 里顺手修掉这些既有缺陷？

**明确意见：绝对不应该在同一 Task 里顺手修掉，必须严格保持现状，由 Codex 统一评估另立专项治理 Task。**

- **理由**：
  1. **严守授权范围与禁止事项**：本 Task（`GOV-SOURCE-RECORDS-1`）属于 Codex r19 裁定的有限表单维护 Task。其 AC4（[L90-L92](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-SOURCE-RECORDS-1.md#L90-L92)）与禁止事项（[L106-L107](file:///G:/CODEX/New%20Manga/doc/tasks/GOV-SOURCE-RECORDS-1.md#L106-L107)）明文禁止：“不改两个 Task 的任何其它字段、正文、Closeout Record。不改任何证据文件、pin、Review”。在同一 Task 中擅自修复构成严重的跨范围越界（Scope Creep）。
  2. **不能破坏历史事实与证据链**：历史 Task 的 pin 记录的是当时的提交快照与磁盘状态。后来的提交修改了契约或测试文件，不能直接粗暴更新历史 Task 的 SHA-256（否则篡改了历史验收依据），需要系统设计（例如如何处理已合入 Task 面对主线演进时的证据有效性）；未登记文件清理和缺失 manifest 补齐也需要严密的前后依赖审查。
  3. **事实准确性高于检查器绿灯**：检查器的红灯客观反映了历史技术债（行尾改写、过程文件遗留、悬空引用等），“把勾选纠正为事实”与“治理检查器判定证据完整性”是两个独立维度。掩盖或顺手修改历史交付物只会引入新的不可控风险。

---

## 治理检查验证

执行以下两条命令，结果均 **PASS**：
```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-SOURCE-RECORDS-1.md
# Governance check: PASS (1 warnings: doc/STATUS.md 达到预算 80%)

pwsh -NoProfile -File tools/governance/check.ps1
# Governance check: PASS (1 warnings: doc/STATUS.md 达到预算 80%)
```

---

## 总体结论与推荐下一步

- **审查结论**：**`APPROVED`**
- **推荐下一步**：交付方本次表单维护严谨合规、依据充分。建议将该 Review 结论提交给 **Codex**，由 Codex 执行终态集成裁决并关闭 Task `GOV-SOURCE-RECORDS-1`。剩余的既有检查错误（历史 pin 失配、未登记过程文件、缺失 manifest）建议作为 Governance Debt 记录在 Backlog 中，另行立项处理。
