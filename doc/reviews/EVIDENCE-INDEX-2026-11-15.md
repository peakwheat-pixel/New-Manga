# 证据索引（本会话产出）

基线 `1ae427638`。本文件把本会话产生的 **verification 目录与评审文档**整理成一张**可导航的表**，
让读者不必翻 88 轮 checkpoint 就能找到每项主张的证据。

**使用方式**：每条主张后面的路径都可以直接打开；每份 `README.md` 内部都写明了**可复核的具体文件与行号**。

---

## 1. 按 Gate 条件索引

### 条件 1 —— 剩余 finding 处置并验证（**MET，8/8 逐项核实**）

| finding | 证据 | 关键点 |
|---|---|---|
| **L-R1-1 / L-R2-1**（阅读器 UI 四控件） | `verification/L-R1-1-UI-WIRING-VERIFY-1/` | 控件在 **`Views/Fluent/ReaderPageView.cs`（737 行，C# 代码构建 UI）**，含书签面板 `:279/:291/:295/:338`、整书进度 `:414/:419/:616`、reset 确认 `:424/:153/:154`、偏好持久化 `:275/:276/:393-395` |
| **L-F1-2** | `verification/CONDITION1-FINDINGS-RECHECK-1/` | `tests/core/test_font_wire.py:92` 测试存在，`:86` 注释明标 finding id |
| **L-L1-1** | `verification/CONDITION1-FINDINGS-RECHECK-2/` | UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md`；`CoreServiceClient.cs` 的 `record ChapterSummary(..., string? Kind = null, long? CustomRank = null)` |
| **L-L1-4** | `verification/CONDITION1-FINDINGS-RECHECK-1/` | `src/application/library/service.py:28-33`（`MAX_SQLITE_INTEGER`/`MAX_IMPORT_ORDER`）+ `:298` 注释标 `AC6 (R3-001)` |
| **L-AI1-6** | `verification/CONDITION1-FINDINGS-RECHECK-1/` | `reassign_references` 在 `src/**` **命中 0**；`tests/storage/test_prompt_templates.py:221` 有 `assert not hasattr(...)`（**能变红的反向断言**） |
| **L-L1-2** | `verification/L-L1-2-CONSTRAINT-VERIFY-1/` | commit 可达性 + SQL `ORDER BY c.sort_order,...` + 调用链 + 测试存在性，四项核实 |
| **L-F1-3** | `doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md` | ZCode 裁决接受替代判据 |

### 条件 2 —— 远端可见性（**MET，调查完成**）

- `doc/reviews/SEC-01` / `SEC-02`：结论"已确认可见"；处置四项均需 Owner 授权。
- `verification/SIGNING-PATH-AUDIT-1/` §6：**`gh auth status` → 未认证**、`GH_TOKEN`/`GITHUB_TOKEN` 均 unset（实测）。

### 条件 3 —— GUI/Core/Host 流程矩阵 + TestHost

| 主张 | 证据 |
|---|---|
| 矩阵盘点（经 3 轮独立复核） | `doc/reviews/GATE3-COVERAGE-MATRIX-*` |
| Host 2 个失败是**设计使然** | `verification/CRASHPOINT-FAIL-NATURE-1/`（驱动实测 `CRASH_POINT=PASS`，10 项 CHECK 全 1） |
| **真实设备 GUI 走查** | **`verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/`** —— 源码构建与**安装产物**上各 **5/5 页真截图**、`host.log` 实测 `core_service ready`+`host_bridge ready`、**逐张目视确认** |
| 阅读器 overlay（**仍未取得**） | `verification/GATE3-READER-OVERLAY-1/`（`PostMessage(WM_KEYDOWN, VK_F11)` 实测无效） |

### 条件 4 —— Windows 包 + install/启动/升级回退/四页/卸载矩阵

| 主张 | 证据 |
|---|---|
| **AC1–AC6**（0.1.0，可逐条复核） | `verification/INSTALLER-EVIDENCE-VERSION-AUDIT-1/` —— `install-phase.json` **37 条断言全 pass**、`uninstall-phase.json` **19 条全 pass**、`verify.json` |
| **AC7 四页** | `verification/GATE4-AC7-UPGRADE-VERIFY-1/`（`GATE4-PAGES-UPGRADE-1` 当时 3/4 页，如实标 `NOT_REACHABLE`）+ **`GATE3-FOUR-PAGE-WALKTHROUGH-1/`（5/5 页）** |
| **升级/回退** | `verification/GATE4-AC7-UPGRADE-VERIFY-1/` —— 6 步实测；**但只是"标签回退"**（0.1.0 包是复制 0.1.1 只改 version） |
| **0.1.1 包级核实** | `verification/INSTALLER-011-PACKAGE-AUDIT-1/` —— setup.exe sha256 三链一致；**但交付包缺 `yolo11s-seg.onnx`，`VERSION.json` 已自陈 `fails closed`** |
| **0.1.1 无原始断言** | `verification/INSTALLER-EVIDENCE-VERSION-AUDIT-1/` §7（workspace 也没有） |
| 补 0.1.1 断言的风险评估 | `verification/INSTALLER-011-ASSERTION-PLAN-1/` |
| 签名路径 | `verification/SIGNING-PATH-AUDIT-1/` —— **不需买证书**，有 SignPath 免费 OSS 通道；只差 P0-4 两步 |
| 模型恢复 | `verification/GATE4-MODEL-RECOVERED-1/` —— `yolo11s-seg.onnx` SHA 与 pin 逐位一致 + onnxruntime 实测 `LOADED OK` + **真实推理** `REAL_INFER_OK` |

### 条件 5 —— 代表性质量基线（**NOT_RUN**）

| 主张 | 证据 |
|---|---|
| **"需人工 GT"有书面依据** | `verification/GATE5-GT-AUDIT-1/` —— V1 审计 `05_OCR_SFX_TRANSLATION_REVIEW.md:20`：「Mock、合成素材或 fake engine 的成功结果……不是识别准确率、真实模型效果或付费服务通过证据」 |
| **③ UI 端到端的实物证据** | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` §10 —— 工位页右侧 `OCR 原文 / 机器翻译 / 人工译文 / 终端` **全部"能力待接入"**，底部 `流水线投影未接入 · NOT_WIRED` |

### 条件 6 —— 门禁 + 独立 Review（**MET**）

- 四件套：`check.ps1` PASS / `verify_pins.ps1` 18/18 / `generate_api_inventory.py` 87 / 三项目测试。
- 独立 Review 记录：`doc/reviews/E9-FILE-ROOT-RECOVERY-1-REVIEW.md`、`doc/reviews/THREE-DELIVERABLES-REVIEW-agent-8.md`、`doc/reviews/E9-UNLOCK-ADJUDICATION-zcode-2026-11-15.md`、`verification/READER-ENTRY-PATH-1/` §6。

---

## 2. E-9 专线（本会话最大的一条技术线）

| 环节 | 证据 |
|---|---|
| 产品影响裁决 | `doc/reviews/E9-PRODUCT-ADJUDICATION-*` |
| 可行性评估（**我的前提错了**） | `verification/E9-FEASIBILITY-2/` |
| **解锁方案裁决（方案 E）** | `doc/reviews/E9-UNLOCK-ADJUDICATION-zcode-2026-11-15.md` |
| 实现 + 验收（`crash-ack.ps1` → PASS） | `verification/E9-FILE-ROOT-RECOVERY-1/` |
| 负例测试（6 个，实测 5/6 变红） | `verification/E9-FILE-ROOT-RECOVERY-1/` §5 |
| 登记回退 | `doc/reviews/E9-KNOWN-LIMITATION-REGISTER.md`（顶部"已解锁"横幅） |
| **独立复核** | `doc/reviews/E9-FILE-ROOT-RECOVERY-1-REVIEW.md`（**ACCEPT_WITH_LIMITATIONS，未发现实质错误**） |

---

## 3. 两轮 Gate 评审文档

| 文档 | 内容 |
|---|---|
| `doc/reviews/RELEASE-GATE-RE-ASSESSMENT-2026-11-15.md` | **正式复评**：判定口径 + 六条逐项判定 + 依据 + 局限 |
| `doc/reviews/RELEASE-GATE-HANDOFF-2026-11-15.md` | **交接文档**：六条状态 + 四项阻塞四元组 + 5 次误判 + 独立复核记录 |

---

## 4. 我在本会话犯的错误（全部原样登记）

| # | 错误 | 登记位置 |
|---|---|---|
| 1 | `L-F1-3` 判"需真人定义口径" | `doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md` |
| 2 | `E-9` 判"需新增持久化"，前提"root==父目录"错误 | `verification/E9-FEASIBILITY-2/`（就地更正） |
| 3 | `yolo11s-seg.onnx` 判"全盘不存在"（只搜了 git 索引） | `verification/BLOCKED-ITEM-AUDIT-1/`（已证伪并改写方法论） |
| 4 | 签名判"需买证书" | `verification/SIGNING-PATH-AUDIT-1/` §4 |
| 5 | `reader` 判"必须按键"，实为 C# 构建的 UI | `verification/L-R1-1-UI-WIRING-VERIFY-1/` §2 |
| 6 | `INSTALLER-MATRIX-1` 未查实物就改状态 | `doc/tasks/INSTALLER-MATRIX-1.md`（横幅内登记两次失误） |
| 7 | 只搜 `.axaml` 断言"控件不存在" | `verification/L-R1-1-UI-WIRING-VERIFY-1/` §3 |
| 8 | **"GUI 无法启动，根因是窗口站"（诊断错误）** | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` §9.6 |
| 9 | 把"截图截早了"误判成"数据根不一致" | `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` §11.5 |
| 10 | 把"模型已就位"说得像**交付包也完整** | `verification/INSTALLER-011-PACKAGE-AUDIT-1/` §6 |

---

## 5. 本会话的方法论结论（可复用）

1. **"搜索"要明确范围** —— `git grep` 查不到 gitignore 的文件；`*.axaml` 查不到 C# 构建的 UI。
2. **"需人"之前先读关键那一行代码/原文**。
3. **下"做不到"结论前先做对照实验**（如 `cmd /c echo` 20 ms vs GUI 挂起）。
4. **推翻一个诊断后，必须回头清理所有传播它的文档**。
5. **截图类证据必须人眼过一遍** —— "哈希不同"不等于"内容正确"。
6. **卡片表格普遍陈旧** —— 看表格后必须再查 `verification/` 与 `workspace/task-envs/` 的实物。
7. **低估也是失真** —— 我三次把已完成的工作说成"未做"。

---

## 6. 一句话

**每一份证据都能被第三人独立打开复核；每一处"未完成"都写明了为什么；我自己的每一次误判都留在上面。**
