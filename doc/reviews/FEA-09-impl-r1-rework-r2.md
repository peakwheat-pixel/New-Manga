<!-- FEA-09 implementation rework review r2 (final) -->
# FEA-09 实现 Review r1-rework 返修复核（r2，最终）

- Reviewer：ZCode 独立会话（GLM-5.3），session `sess_8fd2ec28-cf80-4fd0-94ee-6c25ae58a1ca`；未参与 FEA-09 实现/返修、I001 裁决、UNFREEZE 起草。
- 只读：未修改仓库/commit/push；reviewed_head `de773236834423da341f1404c694d3436e2b8bbf`。
- 结论：**approved，P0=0/P1=0/P2=2（closeout 前置）**。

---

全部证据链已闭合。以下为最终复核报告。

---

# FEA-09 实现 Review r1-rework 返修复核（r2）

## 0. 元信息

- Reviewer：ZCode 独立会话（GLM-5.3）；未参与 FEA-09 实现/返修、I001 裁决、UNFREEZE 起草。
- **只读声明**：未修改仓库任何文件、未 add/commit/push、未触碰用户数据；plan-mode 约束下未运行任何测试/构建/门禁（静态审查 + 3 个只读 Explore 子代理定位）。
- reviewed_head：`de773236834423da341f1404c694d3436e2b8bbf`（main，工作树 clean）；对照 `doc/reviews/FEA-09-impl-r1-rework-r1.md`（reviewed_head `59ad0b9fe`）。
- 契约边界：C-05 v1.2/C-15 v1.1/C-16 v1.1 未动（本轮 5 commit 范围均为 src/tests/doc/verification，无 `doc/contracts/**`）。

## 1. Verdict

**`approved` — P0=0／P1=0／P2=2（残留+新发现各 1，均可 closeout 前置闭合）；I011 收敛成立。**

## 2. 逐项判定

| 项 | verdict | 证据 |
|---|---|---|
| P1-1 PDF 密码接线 | **CLOSED** | 端口 `open(data, password)`（ports.py:66）；bytes→utf-8 str、非文本 typed ENCRYPTED（importing.py:333-340）；`pdfium.PdfDocument(data, password=…)`（:341）真正到达 Pdfium；ENCRYPTED→REQUIRED/INVALID（reader.py:139-145）；cache-miss 仍先 claim 后 render（core_service.py:3424-3444，consume-before-read 防重放系设计），但 REQUIRED 码现与 Host 重试条件对齐（HostRuntime.cs:592，本轮抽查在位）→ 死锁链断；无 Secret-G 两面均 typed REQUIRED（reader.py:83-87/:140-145 + 测试断言） |
| P1-1 e2e 真实性 | **成立** | `encrypted_pdf()` 为 stdlib 手写 RC4/MD5 R2/V1 真加密（test_document_import.py:120-203，"exercises PDFium's production password gate"）；测试注入生产 `PdfiumDocumentRaster` 非 mock；断言 rendition 发布+secret 一次性消费+cache-hit 免 Secret-G（test_i005_encrypted_pdf_resolve.py:111-142）；`page_size`/`RenderedDocumentPage(png,w,h)` 与 R1-I007 端口一致（ports.py:51、reader.py:151-157 先 page_size→预算→render） |
| P2-1 解压预算 | **CLOSED** | `info.file_size` 检查在 `archive.read` 前（reader.py:75-80）；test_reader_decompress_budget.py 超限拒/预算内读两测在 |
| P2-2 PageView | **CLOSED** | entities.py:107-109 仅剩一个 `deleted`，重复定义已删 |
| P2-3 | **a/c CLOSED，b 未补** | a) test_source_grants_unittest.py:94/:111（三元组精确+revoke、unbound+错 version 均 `SOURCE_ACCESS_DENIED`）；c) 处置表 I005 行已刷新为返修后 CLOSED、frontmatter reviewer 行同步；**b) I009 book 改挂负测仍缺**（全树 `SOURCE_PLAN_STALE` 仅 2 处，均非改挂分支；代码路径 runtime.py:212-216 在）——frontmatter“P2-1/2/3 已修”表述与事实不符 |
| P2-4 债务 | 可接受 | RenditionCache 装配失败仍静默降级（core_service.py:6271-6290，legacy 路径加密源 typed REQUIRED 不静默失败）；上轮处置路径即“DSH 裁决登记”，现仅 frontmatter:11 一句提及，正式登记未落 |
| I011 EV 收敛 | **成立（附 1 前置）** | 唯一 ID EV-001…057、主表 0 PENDING；旧台账原字节归档（history/EV-2026-11-03.md，HISTORICAL 行 EV-002）；合成目录去跟踪+.gitignore:27-30+工作树 clean；历史缺失约 50 条单列。**残留**：台账生成于 `59ad0b9fe`（头部 HEAD 字段停滞），且 `verification/FEA-09/tools/rebuild_ev.py`（实存于此，Task:269 写 `tools/…` 系相对路径歧义）已跟踪（clean 树+无 ignore 规则可证）却不在 57 行表内 |

## 3. closeout 前置条件（DSH）

1. 在最终集成 head 重跑 `verification/FEA-09/tools/rebuild_ev.py` 刷新 EV.md（补自身行+刷新 HEAD/commit 列）。
2. 补 I009 book 改挂负测（约 15 行：plan 后 chapter 改挂另一 book → `SOURCE_PLAN_STALE`），或如实改 frontmatter 表述并登记遗留（推荐前者）。
3. DSH 裁决并正式登记 P2-4 债务候选（落债务台账/Task 债务小节，非仅 frontmatter 一句）。
4. 变更记录表补 r1-rework 返修批次行（`59ad0b9fe`/`bc90b467f`/`de7732368`），与 2/3 同次 doc 更新。
5. 加密 PDF Host↔Core **真实 IPC** e2e 仍 NOT_RUN（上轮即知）：DSH 集成验证时以 `NEWMANGA_FEA09_IPC=1` 变体复跑，或按 AC-4/AC-6 现状如实登记限制。

## 4. NOT_RUN（本轮未执行，不据此判级）

- Python/.NET 全量测试、build、`check.ps1`、`verify_pins.ps1`：处置表所记数字均系作者记录，未复现。
- 加密链路真实跨进程 IPC、folder 真实 IPC；C-05/C-15/C-16 契约全文逐字节比对（以 commit 范围+clean 树间接确认）。

## 5. 结论

P1-1 死锁链已实质闭合（端口→编码→Pdfium→typed 码→Host 重试全链在位，真加密 e2e 非 mock）；P2-1/2/3a/3c 闭合；I011 可作 closeout 证据台账。仅余 2 个 P2 与债务登记，均列入前置。**FEA-09 可进入 closeout，前置条件闭合前不得置 done。**

> **DSH**：请原字节归档本报告为 `doc/reviews/FEA-09-impl-r1-rework-r2.md`，登记 approved（P0=0/P1=0/P2=2+债务）。返修实现质量由原会话交付、本会话未改仓库。前置 1–5 可并入 closeout 单次处理；不重开 UNFREEZE，不 push。