# New Manga · 项目状态一页纸（2026-11-18，DSH）

> 用途：给下一个会话/下一位 Agent 一个**不超过两分钟**的现状快照。详细历史见 `doc/handoffs/NEXT-SESSION-STARTER.md`（130 KB，按轮次 R1–R28 累积）。
> 本文件由 DSH 每轮体检时更新；**它不替代** `STATUS`（当前阶段）、`REBASELINE_PLAN`（DAG）、`TASK_LEDGER`（卡片统计）。

## 1. 一句话

产品侧（C# Avalonia + Python Core + SQLite + ReferencedSource）已能**干净产出合规的 models 安装包**；
Release Gate **仍 BLOCKED**，唯一硬阻塞是**真实代码签名证书**，其余条件已关闭或已按书面裁定登记。

## 2. 指针（以仓库为准）

| 项 | 值 |
|---|---|
| HEAD | `8b1648d84`（main，`0 0`，工作树干净） |
| 非终态 v3 卡 | **2**：`MAINT-1-RELEASE-MONITOR`（in_progress，伞位）、`RELEASE-GATE4-SIGNED-MATRIX-1`（proposed） |
| v3 卡统计 | `done` 551 / `closed_with_limitations` **77** / `cancelled` 21 / `superseded` 10 / `historical` 11（另有 `doc/tasks/README.md` 与旧格式卡不计入 v3 统计） |
| 旧格式卡（v3 前） | `UIUX-FUSION-IMPL-1`（正文写 in_progress、不在 v3 台账）—— 已于 2026-11-18 追加状态澄清，**不推进** |
| Technical Gate | `NOT_SATISFIED`（未变） |
| Release Gate | `BLOCKED` |

## 3. 六条 Gate 条件现状

| # | 状态 | 依据 |
|---|---|---|
| 1 | **已关闭**（8/8） | `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` |
| 2 | 前半调查完成；后半需**人的一个决定** | 同上 |
| 3 | **已关闭**（3 份独立书面视觉裁定，**非人眼**） | `doc/reviews/MAINT-1-GATE-CONDITION-3-VISUAL-ADJUDICATION-2026-11-17.md` |
| 4 | **未关闭** —— 只差**真实证书** | `doc/reviews/RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md`（照着做即可） |
| 5 | `LIMITATION_ACCEPTED`（无代表性质量基线，**不宣称准确率**） | `MAINT-1` 卡 |
| 6 | **已关闭** | `45af57007` |

## 4. 当前可发布的包（未签名）

| 项 | 值 |
|---|---|
| 变体 | `models`（含 3 个 ONNX，632,552,582 B） |
| 包级许可 | **GPL-3.0-or-later**（两变体相同；随包权重上游声明 Apache-2.0，随包附 Apache 全文） |
| 安装包 | `NewManga-0.1.1-setup.exe` **652,081,157 B / sha256 `3c9984b2…`**（**未签名**） |
| 护栏 | `verify-package-manifest.ps1` → `OK / EXIT=0`（含许可一致性检查） |
| 包内合规文件 | 6 份与仓库**逐字节相同**（NOTICE / THIRD_PARTY / LICENSE_AUDIT / LICENSE / Apache / AGPL） |
| 向导文案 | 实拍：欢迎页「models 变体（含模型权重，按 GPL-3.0-or-later 分发）」；许可页中文正常 |
| **不得** | 作为发布候选或条件 4 证据（未签名） |

## 5. 唯一阻塞与解封步骤

**阻塞**：无代码签名证书；本机无 `signtool.exe`（`Cert:\CurrentUser\My`、`Cert:\LocalMachine\My` 均无 `-CodeSigningCert`）。

拿到证书后按 `RELEASE-GATE4-EXECUTION-CHECKLIST-2026-11-17.md`：
S1 签 `app/NewManga.App.exe` → 重出安装包 → 签 `setup.exe` → 验签；
S2 干净安装；S3 四页可达；S4 跨版本升级/回退；S5 卸载 + 用户数据保护；S6 不虚报。
**完成后必须交独立上下文复核，不得自审。**

## 6. 已知限制（不隐瞒）

1. 三项权重（rtdetr / manga-ocr encoder+decoder）的许可**只以上游声明为依据**（HF 模型卡 / nixpkgs / 百度 / Roboflow），
   本地 ONNX **无可读许可元数据**；本仓库**不做法律认定**。
2. 安装向导只实拍了欢迎页/许可页；安装过程页、完成页、卸载向导、跨版本升级页**未实拍**（属条件 4 内容，需签名后的最终包才有意义）。
3. 条件 3 是**Agent 书面裁定**关闭，不是人眼验证；若要人眼复核，直接看 `verification/MAINT-1-RELEASE-MONITOR/condition3/` 的 6 张图即可。
4. 历史 `INSTALLER-MATRIX-1` 的 stage/`setup.exe` **不可发布、不可作条件 4 证据**（元数据不自洽 + 许可声明非法，见 L-IM-8/9/10）。

## 7. 治理工具与基线

- 四件套：`check.ps1`（PASS，3 warning）/ `verify_pins.ps1`（18/18）/ `clean_workspace.py --audit-declarations`（0 error）/ `audit_evidence_pins.py`（FAIL 0，7,195 行 / 674 卡）。
- 预算：`STATUS` ≤ 3200 B（当前 3,160）、`REBASELINE_PLAN` ≤ 7000 B（当前 6,724）。
- 本轮体检发现并修正：STARTER 头部指针仍停在 `f475ea155`、旧格式卡 `UIUX-FUSION-IMPL-1` 状态未澄清。
