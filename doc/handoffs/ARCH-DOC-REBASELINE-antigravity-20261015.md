---
task_id: ARCH-DOC-REBASELINE
author: Antigravity
recipient: DeepSeek Harness, Codex
base_commit: 4ef92f3daa527adac752b8fc52d492176697a292
delivery_head: b2e198239c486af220439e44795e1b48d85a9901
status: ready_for_review
---

# Handoff：ARCH-DOC-REBASELINE 架构文档重基线交付报告

## 交付结果

本任务作为新架构需求、验收及输出格式映射 Gate，把既有产品要求映射至 [AD-001](doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md)（Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy），为下游任务 P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）提供前置 Gate 输入。

### 核心合规与红线执行
1. **主仓保护与来源 Pin**：主仓当前存在未提交（dirty）文档，严格禁止原位覆盖主仓。已在只读扫描主仓工作区 10 份架构文档后，将 SHA-256、字节数与 mtime 记录于 `verification/ARCH-DOC-REBASELINE/source-pins.json`。主仓 dirty 版本未被覆盖，仅作来源追溯参考。
2. **严格遵守 allowlist**：仅在本 worktree（`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`）内修改了 allowlist 允许的文件（`doc/02`, `05`, `07`, `08`, `13`, `doc/tasks/ARCH-DOC-REBASELINE.md`, 本 Handoff 及 `verification/ARCH-DOC-REBASELINE/**`）。`doc/01, 03, 04, 06, AD-001` 严禁落笔，产品代码、Schema、依赖零修改。
3. **不降低产品范围与任何阈值**：所有功能、安全与 NFR 阈值全部完整保留。
4. **历史 PASS 零继承与诚实评定**：历史 PySide6 PASS 结果一律不继承至新架构，全部如实评定为 PARTIAL 或 NOT_RUN。

---

## 验证证据与 AC 逐项对照

| AC 编号 | 核心要求与覆盖内容 | 结论 | 证据路径 | 说明与后续责任 Gate |
|---|---|---|---|---|
| **AC1** | 01–08 逐份覆盖核验；新技术架构、权限边界与 UI 映射的正式来源确立 | **PARTIAL** | [ac1-coverage-and-sources.md](../../verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md) | 架构分层职责与权限隔离铁律已确立，旧 QML 映射标为参考。Tauri IPC 代码级 Schema 编译与前端通信验证待 **P09（AC1–3）** |
| **AC2** | 领域模型、Pipeline、版本、受控来源、持久化、错误语义 6 大维度跨文档一致性对照 | **PARTIAL** | [ac2-cross-document-consistency.md](../../verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md) | 跨文档 6 大核心维度业务逻辑与状态机完全一致。新架构端到端持久化与错误恢复自动化测试待 **P09（AC1–3）** |
| **AC3** | 四个同级一级页面、默认书架、基础 Reader、延期项与 01/04/05/08 一致性；四页设计独立释放声明 | **PARTIAL** | [ac3-four-pages-and-deferred.md](../../verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md) | 页面信息架构与延期项范围完全锁定。明确四页设计由 ZCode 主责并在独立设计 Task 中审查，待 **P09（AC1–3）** |
| **AC4** | P18 的 JA/KO、无字页、质量 AC 对应新链；7 维全证据责任规范；旧结果不继承 | **NOT_RUN** | [ac4-p18-quality-and-responsibility.md](../../verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md) | 建立了真实样本、真值、阈值、version、device、model、endpoint 7 维证据责任规范。新架构实测基准待 **P18（AC4）** 运行 |
| **AC5** | P20 NFR 在 Tauri/WebView2/Python sidecar/Windows 下对旧条目逐项保留且不降阈值；新证据 Gate | **NOT_RUN** | [ac5-p20-nfr-stack-rebaseline.md](../../verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md) | 保留冷启动 <= 2.0s、进程树内存总和 <= 350MB、滚动 60 FPS、故障隔离等阈值。新二进制实测基准待 **P20（AC5）** 测量 |
| **AC6** | P08-FMT 5 大格式（PNG/ZIP/CBZ/PDF/文本）长期验收追踪表与安全异常矩阵 | **NOT_RUN** | [ac6-p08-fmt-traceability.md](../../verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md) | 格式导入解析标准、导出生成规范与 Zip Slip/XXE 安全防御用例已冻结。消费前置 Gate 移交 **P16/P17** |

---

## 接收方式

- **工作区坐标**：`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`
- **分支**：`codex/arch-doc-rebaseline`
- **Base Commit**：`4ef92f3daa527adac752b8fc52d492176697a292`
- **自检复现命令**：
  ```powershell
  pwsh -NoProfile -File "G:/CODEX/New Manga/tools/governance/check.ps1" -TaskPath "G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE/doc/tasks/ARCH-DOC-REBASELINE.md"
  ```
- **审查步骤**：
  1. Reviewer（DeepSeek Harness）检查 worktree 中 7 份证据报告与 5 篇架构文档的对齐内容；
  2. 验证主仓无任何写入或修改；
  3. 核实未合入 main、未执行 push。

---

## 下一任务建议（必填）

- **Task ID / 标题**：`ARCH-DOC-REBASELINE 审查与下游 Gate 释放`
- **推荐 Agent / Reviewer**：Reviewer 为 **DeepSeek Harness**；Integrator 为 **Codex**
- **推荐原因与前置依赖**：
  - 本任务作为架构文档重基线 Gate，已产出全部所需证据与映射定义，按 AC7 需由非作者（DeepSeek Harness）进行独立审查；
  - 审查通过后，由 Codex 裁决向各下游消费者任务（P09 消费 AC1–3、P18 消费 AC4、P20 消费 AC5、P16/P17 消费 AC6）释放对应前置输入。
- **Recovery point**：
  - 仓库：`G:/CODEX/New Manga`
  - 分支：`codex/arch-doc-rebaseline` @ 本次 delivery commit
  - worktree：`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`
- **允许修改路径**：
  - Review 阶段由 DeepSeek Harness 写入 `doc/reviews/ARCH-DOC-REBASELINE-*.md`
- **禁止范围与新增授权条件**：
  - 禁止合并 main；禁止修改产品代码；禁止放宽任何 AC 质量阈值。
- **交付物**：
  - DeepSeek Harness 的独立 Review 报告及 Codex 的集成裁决。
- **可直接转发给 Agent 的指令**：
  ```text
  请 DeepSeek Harness 审查 ARCH-DOC-REBASELINE 任务交付成果：
  - 工作区：G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE
  - 分支：codex/arch-doc-rebaseline
  - 任务与证据：doc/tasks/ARCH-DOC-REBASELINE.md 与 verification/ARCH-DOC-REBASELINE/**
  - 重点核对：主仓未被覆盖、AC1~AC6 逐项结论客观真实（无虚假 PASS）、文档对齐严格基于 worktree HEAD 且不降阈值。
  ```

---

## 风险与遗留

1. **主仓 dirty 文档留存说明**：主仓 `doc/01~08, 13, AD-001` 存在的未提交历史修改未被覆盖，其 SHA-256 已永久锁定于 `verification/ARCH-DOC-REBASELINE/source-pins.json`。后续若主仓需统一清理或提交，需由 Codex 独立统筹。
2. **下阶段实现任务风险**：新架构下 React 与 Python Core 的 IPC 通信延迟与大图像二进制加载性能，需在 P09 实施阶段尽早建立端到端基准，防止长图渲染帧率劣化。
