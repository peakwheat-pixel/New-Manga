# 2026-10-13 文档治理 Rebaseline 记录

## 范围与结论

只治理文档权威关系、当前导航、重复状态段和已确认的架构措辞；不改产品代码、目标架构、P02 原始 evidence/source pin 或 Task 的冻结范围。

旧版本先复制到本目录的 source/，每个副本均与复制前源文件 SHA-256 一致。source/ 中是重排前原文快照；相对链接仍按原目录语境解释。它们只供审计/恢复，不参与当前决策。

| 重排前源文件 | bytes | SHA-256 |
|---|---:|---|
| AGENTS.md | 5,923 | 4364211DD1AF81BE61AC5CBFDE363AF073C6C51E5DBBC85BA667A0D78D1A3D1D |
| doc/00_INDEX.md | 5,686 | 22F27C939D9238114ECAD6146995D643217A029410AB95D136B5DEE30E76407E |
| doc/STATUS.md | 5,956 | 7320BD16E00A7C373B7226844AF34812BD1C5330FB33D87A15DBB1BAD870D62B |
| doc/REBASELINE_PLAN.md | 6,888 | DA9674D00DBF57EA5145EF75F00E8D74D618142661D16D61B9C7821FE3F1A970 |
| doc/tasks/README.md | 3,065 | 326C49BCE511D569BCDD027C5A898FDA6803D95D87505ED841CF6FF2B1E7CE65 |
| doc/WORKSPACE_GOVERNANCE.md | 8,304 | A4A4BF6643212C02D0206C5731F9C5E8890D5EB5D7D224170D6A3B062AE83D11 |
| doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md | 9,179 | 7A6CB8CB5D8156D626514CF3485649AD1DE4FDC39AFB9FCE527EFF924017E755 |
| doc/04_USER_FLOW.md | 36,337 | 41FE394123056811E996F222CF9DC4F7A68306087FC2EAC772582815873E34A9 |
| doc/03_DATA_MODEL.md | 57,734 | D1A4DD9DDC5F4970ED1306990ECF8454FAC972BAEF813C312BB2772ACB2E5650 |
| doc/05_UI_MAPPING.md | 45,158 | 7FE1192449B21A8A9FE34B4BDF73ACD91C06676BFAF8DCE6A47772FB15AC2D57 |

## 冲突裁决

- 最终目标固定为 Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy；AD-001 是唯一架构权威。
- Python + PySide6/QML + SQLite 仅为旧生产基线。迁移中间态只能由当前释放的 Task 定义，不是第二个目标，也不会恢复 QML 实现授权。
- AD-001 原注册快照中 T3.2.1/QML parity、旧 M2 release list、Qoder ownership 和 open-decision 文本已从当前决策文档拆出，完整原文留在 source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md。
- 04_USER_FLOW 中“05 定义 QML 控件映射”改为历史映射说明；05_UI_MAPPING 中 QML 组件节由“目标边界”改为 Legacy 示例。
- D03 与 D04 原将 Legacy D02 列为直接架构依据；现明确其仅是旧生产基线历史上下文，数据和用户流程意图仍按产品需求参考。
- TASK-002 保持 task-scoped：G06–G13 的语义仅在当前 Task 明确引用时适用，并从属于 AD-001；本次未改动该契约文件。
- STATUS 曾把当前 H1 adjudication 指向上游 A6 review-adjudication；现已修正为 H1 专属的 codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md。A6 裁决仍由 H1 Task 的上游证据区引用。
- 原 AD 注册中的 remote drift 备注是历史快照：当前 doc/09 要求每个 Task 实测 remote；本次只读 Git 查询观察到 origin=https://github.com/peakwheat-pixel/New-Manga.git。

## 导航瘦身与证据保护

- STATUS 只保留当前 Task、Gate、阻塞和权威证据指针；详细 pins 留在当前 Task、Review/adjudication、checkpoint 及原始 evidence。
- REBASELINE_PLAN 只保留当前 DAG、释放前置条件与阻塞链；历史版本继续见 2026-10-12 archive。
- 00_INDEX 成为 Document Truth Map，集中维护事实权威、文档分类和最小读取集。WORKSPACE_GOVERNANCE 不再重复维护架构分类表；Task 索引不复制 Status。
- P02 Task、Review、checkpoint、verification 和 evidence/source pins 均未移动、改名或删除。历史记录靠入口规则退出默认上下文，按当前 Task 引用按需读取。
- 对 doc/ 下文件做了 SHA-256 byte-identical 检查，没有发现重复文档组；删除 0。明确历史证据/当前引用继续留在原路径；未确认的历史文件不作搬迁。

## 归档文件

本目录的 source/ 包含 10 个重排前源文件快照。加本 README 共新增归档文件 11 个；原位置上的当前版本仍为主入口。

H1 Review evidence preservation check: DSH response 14078 / 6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19; Codex input verification 14002 / 7B823A05313DA2B053C76B81744667BF041B8FD9AF0933F1162DCDADFB372515; H1 adjudication 7665 / 9D4B95DA5263B0C52A3621748E875760CAAADF153ED5C39BDA5955520DF57232. All three match the active Task pins after this rebaseline.
