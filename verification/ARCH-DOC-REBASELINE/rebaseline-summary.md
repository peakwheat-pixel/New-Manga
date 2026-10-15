# ARCH-DOC-REBASELINE 架构文档重基线总览与 Gate 裁决报告

**任务 ID**：ARCH-DOC-REBASELINE  
**任务名称**：新架构需求、验收及输出格式映射 Gate  
**Owner**：Antigravity  
**Reviewer**：DeepSeek Harness  
**Base Commit**：`4ef92f3daa527adac752b8fc52d492176697a292`  
**工作区坐标**：`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`  
**分支**：`codex/arch-doc-rebaseline`  
**生成时间**：2026-10-15  

---

## 1. 任务背景与核心红线

本任务是架构文档 Gate 的正式重基线：负责将既有产品需求与验收标准映射至唯一演进目标架构 [AD-001](doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md)（Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy），为后续任务 P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）提供前置 Gate 输入。

### 核心红线遵守情况
1. **不修改产品范围、不降低任何阈值**：所有功能需求、性能指标、安全规范与数据完整性要求全部保留且无放宽。
2. **禁止原位覆盖主仓未提交文档**：已建立 `source-pins.json` 锁定主仓未提交修改指纹，本 worktree 独立实施。
3. **严格限制修改文件范围**：仅修改 allowlist 允许的文件（`doc/02`, `05`, `07`, `08`, `13`, `doc/tasks/ARCH-DOC-REBASELINE.md`, handoff 与 `verification/ARCH-DOC-REBASELINE/**`）。`doc/01, 03, 04, 06, AD-001` 严禁落笔，产品代码、Schema、依赖零变动。
4. **禁止虚假声明 PASS**：历史 PySide6 PASS 绝不继承，未实测项如实标注为 PARTIAL 或 NOT_RUN。

---

## 2. AC1–AC6 逐项结论与证据索引

| 验收项 | 核心要求与覆盖范围 | 裁决结论 | 对应证据路径 | 未决项与后续责任 Gate |
|---|---|---|---|---|
| **AC1** | 01–08 逐份覆盖核验；新技术架构、权限边界与 UI 映射的正式来源确立 | **PARTIAL** | [ac1-coverage-and-sources.md](verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md) | Tauri IPC 代码级 Schema 编译与前端通信验证待 **P09（AC1–3）** |
| **AC2** | 领域模型、Pipeline、版本、受控来源、持久化、错误语义跨文档一致性对照 | **PARTIAL** | [ac2-cross-document-consistency.md](verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md) | 新架构端到端持久化与错误恢复自动化测试待 **P09（AC1–3）** |
| **AC3** | 四个同级一级页面、默认书架、基础 Reader、延期项一致性；四页设计独立释放声明 | **PARTIAL** | [ac3-four-pages-and-deferred.md](verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md) | 四页具体 React 视觉与交互设计由 ZCode 主责，通过独立设计 Task 推进，待 **P09（AC1–3）** |
| **AC4** | P18 的 JA/KO、无字页、质量 AC 对应新链；7 维全证据责任规范；历史结果不继承 | **NOT_RUN** | [ac4-p18-quality-and-responsibility.md](verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md) | 新架构模型实测基准待 **P18（AC4）** 在新流水线上运行并出具报告 |
| **AC5** | P20 NFR 在 Tauri/WebView2/Python sidecar/Windows 下对旧条目逐项保留且不降阈值；新证据 Gate | **NOT_RUN** | [ac5-p20-nfr-stack-rebaseline.md](verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md) | 新二进制构建的真实环境性能与进程树内存测量待 **P20（AC5）** 执行 |
| **AC6** | P08-FMT 5 大格式（PNG/ZIP/CBZ/PDF/文本）长期验收追踪表与安全异常矩阵 | **NOT_RUN** | [ac6-p08-fmt-traceability.md](verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md) | 格式导入管道待 **P16**，导出管道待 **P17**，前置 Gate 契约已冻结 |

---

## 3. 跨文档对齐与调整提案建议（针对未允许直接修改的文档）

依据规则，`doc/01`, `doc/03`, `doc/04`, `doc/06`, `doc/AD-001` 不在本次允许修改列表内，任何需要微调的语义只以提案形式在此登记，留存 Codex 后续裁决：
1. **关于 doc/01、04 中的术语标记建议**：
   - 建议在未来由 Codex 统一对 01、04 文档的顶栏增加与 02、05 相同的元数据说明：“产品行为与信息结构继续有效，UI 组件实现以 AD-001 目标架构为准”。
2. **关于 doc/06 中的 ViewModel 引用建议**：
   - 06 文档中个别地方提及“ViewModel 状态投影”，建议后续在 P09 实施时统一将其注解为“Tauri IPC 传输的 Application State DTO”。
3. **关于 AD-001 的历史清理建议**：
   - 主仓工作区中存在的关于 AD-001 历史描述的简化版，可在本轮 Rebaseline 集成后由 Codex 统一裁决是否合入。

---

## 4. 总结与交付状态

本任务已彻底澄清旧技术栈与 AD-001 目标架构的映射关系，构建了覆盖完整、权限清晰、语义严格一致的文档重基线框架，产出全部 6 项核验证据，为后续 P09、P18、P20、P16/P17 的工程落地提供了坚不可摧的架构凭据。
