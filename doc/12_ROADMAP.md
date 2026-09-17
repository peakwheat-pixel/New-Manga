# 下一阶段可执行 Roadmap

更新日期：2026-09-17。TASK-001～TASK-014、TASK-028 设计、TASK-029 统一 SQLite 持久化实现、TASK-030 入口装配与 TASK-031 生产 ImageDecoder/Managed Copy 适配器已完成并集成；TASK-013 生产 Pipeline seam 已以 `integration_commit=49c72fdf` 集成，R-1 已以 `integration_commit=734d5b3` 完成生产 Workbench 装配并验证；TASK-016 已以 `integration_commit=9bf85f5` 完成独立实验集成，TASK-015/024/017 已收口 done（窗口内 Review 为 approved_subagent，三份外部 post-hoc Review 均 approved，findings 已由 `c7a02bd` 收口）；TASK-018/019 为 blocked；TASK-020～TASK-023、TASK-025～TASK-027 继续冻结。此路线依据 D01～D08 和 [Gap Register](10_CURRENT_STATE_AND_GAPS.md)，没有排入无来源的新产品能力，也不承诺未经验证的日期/工期。

## 1. 阶段与退出条件

| 阶段 | Task | 可审查结果 | 退出 Gate |
|---|---|---|---|
| 接管（本次） | 本文档组 | 现状、协作规范、11类目标视图、Gap、验收路由与27个Task | 用户审核接管结果，明确后续允许范围 |
| S0 契约与实施准备 | TASK-001/002/003/004/024 | 文档去歧义、最小契约、AC/素材规范、运行环境实验、扩展范围决定 | 初始Git基线可复现；阻断型契约关闭；用户批准冻结和拟实施范围 |
| S1 内容与工程基础 | TASK-005/006/007/008/009/012/029 | Core启动、受控导入、统一持久化、人工编辑保护、配置、四页导航及书架 | 无重型AI也能启动；Book/Chapter/Page/Region持久化；源文件Hash不变 |
| S2 可验证完整切片 | TASK-010/011/014/013/015 | 知识与Context、Mock任务编排、渲染、工作台进度、阅读和导出 | 导入→Mock管线→编辑→保存→阅读→五格式导出→重启；失败/暂停/停止/恢复验证 |
| R 模型研究支线 | TASK-016/017/018 | OCR/检测、Translation、Inpainting独立实验报告 | 模型/数据/设备可复现，结果有实际证据与明确限制；选型经Codex审核 |
| S3 真实能力集成 | TASK-019 | 已批准Provider、Mask/修复、模型就绪/下载/资源控制 | 真实样例完成管线且人工/范围/Revision保护通过；缺环境能力不标PASS |
| S4 场景与可靠性补全 | TASK-020/021/022/023/025 | Webtoon、恢复/清理、完整窗口/设置、多格式导入和获批扩展 | 对应全部AC有可复现实证；扩展范围没有悄悄遗漏 |
| S5 独立验证与RC | TASK-026/027 | 固定commit独立Review、真实代码架构图、Benchmark、Windows发布包 | D08完整Gate；未通过输出NOT READY，禁止把内部切片叫正式完成 |

S0内部 TASK-002 依赖001，003/004依赖002，024依赖003；先完成能闭合的契约，待用户选择的范围明确保留阻塞。阶段表是里程碑，不覆盖单个 Task 中更细的 depends_on。

~~~mermaid
flowchart LR
    TAKE["接管审核"] --> S0["S0 文档与契约"]
    S0 --> S1["S1 工程/内容基础"]
    S1 --> S2["S2 Mock完整切片"]
    S0 --> R["R OCR / Translation / Inpainting实验"]
    S2 --> S3["S3 真实Provider集成"]
    R --> S3
    S3 --> S4["S4 Webtoon/可靠性/完整UI/扩展"]
    S4 --> V["S5 独立验证"]
    V --> RC["RC打包/干净Windows验收"]
~~~

此图是依赖概览，不是所有工作必须阶段串行。例如 TASK-021 依赖006/011/015，可早于020；TASK-023在007/009/012/024后即可进行。精确依赖见 [Task索引](tasks/README.md)。

## 2. 第一批释放状态与后续建议

TASK-001～TASK-012 已集成完成：TASK-003 冻结验收/证据与 Fixture 规范并关闭 F-08；TASK-004 完成 Windows/PySide6/打包隔离实验；TASK-005 按方案 A 建立最小工程入口与架构守卫；TASK-006 完成持久化与 Artifact 安全提交基础；TASK-007 完成书架领域与本地图片导入，并关闭 F-01～F-03，按规则 deferred F-04；TASK-008 完成 Region 编辑、Revision 与人工保护，R-201/R-202 按 Review 记录 deferred；TASK-009 完成 Provider 配置、网络策略与凭据边界（实现 `dea1dee`，收口 `6c732be`）；TASK-010 完成翻译约束、TM 与 Context（实现 `1ea9c80`，收口 `a225790`，F-01/F-02 已关闭）；TASK-011 完成命令计划、任务调度与可恢复进度（实现 `6a2016b`，Review `36f874a`，integration `369e95f`，R-001～R-003 已登记收口）；TASK-012 完成四页导航与书架 UI（实现 `b324d4b`，收口 `78987c8`，R-001/R-002 已关闭）。TASK-014 完成配色与文字排版渲染（实现 `a61216a`，收口 `a943297`）；TASK-028 已完成统一 SQLite 设计冻结；TASK-029 已按该设计完成实现、独立 Review 与 Codex 集成（实现 `2ea5445`，收口 `0b0b855`）；TASK-031 生产 ImageDecoder/Managed Copy 适配器已按固定 Review 完成集成（实现 `c67a105`，R-001～R-003 收口 `d4fe993`，integration `e9d5185`）；TASK-030 入口装配最小切片已完成集成（实现 `c3f1893`，R-001～R-003 与登记事项收口 `a29f02e`，integration `fef9dd3`）；TASK-013 工作台与任务进度已完成集成（实现 `da1daf1`，Review `9fbfa48`，integration `f0814a8`），R-001～R-003 已收口；随后以 `base_commit=126bab5`、`reviewed_head=e5b58e7`、Review `8f7c454` 按 `integration_commit=49c72fdf` 集成生产 Pipeline seam；R-1 以 `base_commit=7c889cf`、`reviewed_head=7f3be54`、Review `r1-review-7f3be54.md` 按 `integration_commit=734d5b3` 完成生产 Workbench 装配，R-001/R-002 已修复，R-03 已关闭；其他业务功能继续冻结。

这里的顺序是建议，不以用户批准接管推定其批准全部开发。TASK-009、TASK-010、TASK-011、TASK-012、TASK-013、TASK-014、TASK-030 与 TASK-031 已完成集成；R-1 已完成；TASK-016 已完成集成，TASK-015/024/017 已收口 done；TASK-018/019 blocked；TASK-020～TASK-023、TASK-025～TASK-027 仍冻结；默认同一 ZCode 实例不得并行实现两个 Task，本次 TASK-012 例外使用独立 worktree/branch，其他任务仍遵循默认规则。用户若明确批准一组任务，Codex据此持续完成该组，无需重复请求同一授权。

## 3. 三 Agent 调度方式

| Agent | 优先工作流 | 可与其他Agent并行的条件 |
|---|---|---|
| Codex | 契约→工程/存储→Pipeline→可靠性→集成/RC | 稳定契约和基线先交付；独占共享Schema/依赖/装配写权限 |
| ZCode | 独立Feature：书架/编辑/配置/知识/渲染/UI/阅读/Provider/Webtoon等 | 依赖已done且路径不重叠；同一ZCode实例仍按任务顺序执行 |
| DeepSeek Harness | 规格/环境实验→OCR/Translation/Inpaint实验→各切片Review→最终验证 | 使用独立worktree和实验数据根；不能把三个实验同时视为三个额外Agent |

DeepSeek Harness 与 ZCode 已分别完成 TASK-003、TASK-004；当前连接事实与 Review 状态见 STATUS 和对应 Task，不在本路线图维护第二份进度。

典型协作窗口：Codex集成存储/契约后，ZCode做独立Feature，DeepSeek做已有明确数据/环境的实验。Code Review 插入各 Task 的 in_review 阶段，不拖到 TASK-026 才首次审查。

## 4. 依赖与修改范围规则

- 所有 Task 文件包含硬依赖、Acceptance Criteria、允许路径、测试要求与阻塞；TASK-001～TASK-014、TASK-028、TASK-029、TASK-030、TASK-031、TASK-016 已 done，TASK-015/024/017 为 done，TASK-018/019 为 blocked，TASK-020～TASK-023、TASK-025～TASK-027 为 proposed/frozen。
- 当前已集成 TASK-005～TASK-014、TASK-029、TASK-030、TASK-031 的对应源码与测试；未集成路径仍来自 D02/D05 建议结构，后续实施前仍须核对并更新 Task，不能以“路径只是建议”为由越界修改。
- 全局接口、Schema迁移、依赖清单和bootstrap修改需Codex明确分配；不能通过给各Agent整个src目录写权限实现所谓独立开发。
- 测试/实验首先使用临时独立数据目录；真实用户文件只读导入。Git共享不意味着各进程共享写入测试DB。
- 集成后再释放依赖任务，避免下游建立在未合并的私有分支/聊天约定上。

## 5. 范围与发布界线

S1/S2是阶段性切片，未完成的P0/P1继续登记NOT_RUN/BLOCKED，不能当正式版本发布。Mock只能验证数据流和恢复，不能替代实际OCR/Translation/Inpaint质量。性能数值继续作为目标，直到固定硬件/数据集实测。

PDF/MOBI、字体上传、Sakura监控、Plugin/Hooks与Plugin Agent仍有待决契约；网页导入已由用户于 2026-09-17 按 U-1 取消，相关 AC-EXT-IMPORT-001/002 退役。U-2～U-6 仍待裁决；TASK-023/025/019/022 继续冻结或 blocked，决定本身不释放任务。

不排入用户注册、产品团队协作/权限、Volume、角色工坊、Manga Insight/RAG或永久Webtoon Tile实体，因为D03 §47及D04 §54明确排除。三Agent协作仅属于开发流程。

## 6. 阶段交付标准

每个完成任务提供固定交付commit、AC对照、实际测试、Handoff与非作者Review。Codex集成后记录integration_commit与复验结果。最终发布仍按D08 §71～76，不用“27个任务都打勾”代替产品证据。

所有产物均留在同一Git仓库的文档与证据目录中；不依赖任一Agent聊天重建项目状态。
