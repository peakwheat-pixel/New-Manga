# 20 个具名未提交文件逐份语义评估

- Owner：Codex
- 对照基线：当前分支 main，HEAD=8f73a4202275c49e6eb22634c2f8f6590c9bd697
- 评估范围：content-diff-assessment.md 中列明的 20 个路径。
- 方法：读取工作区磁盘字节；仅将 CRLF 中的 CR 折算掉，再与 git cat-file -s HEAD:<path> 及 git diff --ignore-cr-at-eol 的语义差异核对。依据同时参照当前 STATUS、REBASELINE_PLAN、现行治理文档及文件自身时间/用途。下表行号使用工作区或 HEAD 对应版本的行号。
- 范围外文件未纳入本表；本报告未读取或改动 apps/desktop/src-tauri/**、apps/desktop/frontend/**、verification/P20-AC4-FPS-1/**。

## 逐份判定

| 文件 | 工作区版 vs HEAD 版 | 判定 | 依据（差异要点与位置） | 建议处置 |
|---|---|---|---|---|
| .qoder-credits/report.json | 工作区 6,599 LF 折算字节；HEAD 61,876 字节。工作区 generatedAt=2026-10-08，HEAD=2026-09-26，但采集量及内容结构大幅不同。 | USER_DATA | 工作区 :3,35,77,89-90,94,258 记录 1 trip、32,079 tokens、0 tool calls/reads，并将 artifact 指向本地通路探测 canvas；HEAD :3,35,77,89-90,94,111,2392,2400 记录 133 trips、21,727,640 tokens、157 tool calls、36 reads 及另一 session/artifact。时间较晚不足以证明工作区版可替代较完整历史统计，属于 Qoder 侧使用数据。 | ASK_USER |
| AGENTS.md | 工作区新增当前阅读范围、治理检查与 workspace/archive 治理规则；HEAD 仍使用旧的默认通读口径。 | WS_IS_CURRENT | 工作区 :3-9 限定当前有效上下文及按需读取历史证据，:44-48 规定 workspace、inventory、archive 及归档引用保护；这些与本会话生效指令一致。HEAD :5-10,38-39 缺少上述现行条款。 | KEEP_AND_COMMIT |
| doc/00_INDEX.md | 工作区是简洁的权威地图；HEAD 含旧 P02/P04/P08 状态快照和大量已过期的当前态叙述。 | WS_IS_CURRENT | 工作区 :3-31 明确列出 AD-001、Plan、Status、Task、Inventory 等来源及冲突规则；:50-62 将旧 QML/M2/Qoder 文本归为历史并限制默认扫描。HEAD :3-15 仍把旧 P02 作为当前执行点。 | KEEP_AND_COMMIT |
| doc/01_FUNCTIONAL_ARCHITECTURE.md | 工作区只增加范围边界说明；主体功能架构未变。 | WS_IS_CURRENT | 工作区 :3 明确本文件描述功能/页面目标，不指定技术栈，历史 QML 映射不构成目标架构；HEAD :3 仍直接进入 To-Be 定义而无此边界。与当前唯一桌面目标 AD-001 一致。 | KEEP_AND_COMMIT |
| doc/03_DATA_MODEL.md | 工作区增加概念数据模型边界，并收窄旧 D02/TASK-002 引用的适用条件。 | WS_IS_CURRENT | 工作区 :3,7-15 明确本文不是当前 SQLite schema/实现状态，D02 仅作旧基线背景，TASK-002 契约仅在当前 Task 明确引用时适用；HEAD :3,7-15 未限定，容易把旧架构语境当现行实现依据。 | KEEP_AND_COMMIT |
| doc/04_USER_FLOW.md | 工作区将旧 QML UI 映射明确标为历史映射；保留用户流程意图。 | WS_IS_CURRENT | 工作区 :3,9-23 说明流程不定义技术栈、不自动授权实现，QML/Qt 不属于目标架构，React/Tauri 映射由当前 Task/contract 冻结；HEAD :3,9-23 仍将 UI Mapping 和组件映射表述为后续技术定义。 | KEEP_AND_COMMIT |
| doc/06_TRANSLATION_PIPELINE.md | 工作区增加业务语义与旧 UI 接线的边界说明；流程主体保留。 | WS_IS_CURRENT | 工作区 :3 保留 Pipeline 阶段、恢复和数据安全要求，同时将 QML/UI Thread、Qt 接线定为 Legacy，并说明 Python Core 经 Tauri IPC 服务 React；HEAD :3 把旧 UI 映射并列为目标实现上下文。 | KEEP_AND_COMMIT |
| doc/09_COLLABORATION.md | 工作区以 lifecycle v2 替换 v1 状态说明，并新增 evidence、review 和 resource closeout 规则。 | WS_IS_CURRENT | 工作区 :66-78 定义 READY/ACTIVE/REVIEW/DONE 与唯一状态权威，:80-94 定义 Canonical Evidence、Review 生命周期、Resource Manifest、closeout 和只读 governance check；:183-197 更新当前标准来源及守卫描述。HEAD :65-77,165-196 无这些 v2 约束或仍引用 Legacy 技术条款。 | KEEP_AND_COMMIT |
| doc/11_ARCHITECTURE_MAPS.md | 工作区新增历史/Legacy 分类声明；图表内容未变。 | WS_IS_CURRENT | 工作区 :3 将 2026-09-22 的 Python/PySide6/QML 图表明确标为历史快照，并把当前目标与实现事实指向 AD-001/STATUS/Plan/Task；HEAD :3 直接引出图表，未提示读者它们不是当前架构。 | KEEP_AND_COMMIT |
| doc/12_ROADMAP.md | 工作区将文件收敛为导航并链接当前事实源；HEAD 保留旧 P02 当前状态和旧里程碑正文。 | WS_IS_CURRENT | 工作区 :3-14 明确本文件不定义目标架构、READY DAG、Task 状态或实现授权，并链接当前 AD-001、Plan、Status 及已归档路线；HEAD :3-5 仍称 P02 正在执行、写有旧 Owner 与未运行验收。归档目标 archive/history/2026-10-12/12_ROADMAP.md 存在。 | KEEP_AND_COMMIT |
| doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md | 工作区记录用户已批准的唯一当前目标；HEAD 混有旧 M2 首波释放、QML 保留/Parity 及过时开放裁决。 | WS_IS_CURRENT | 工作区 :2-17,21-31 固定 Windows + React/TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy，明确不自动授权实现，并标出 Legacy 边界；旧完整文本由 :31 链接至已存在的 archive 快照。HEAD :1-48 将 M2 首波授权和旧 QML迁移文本写入当前决策正文。 | KEEP_AND_COMMIT |
| doc/WORKTREE_SAFETY_INVENTORY.md | 工作区记录 2026-10-13 Stage 5/6 迁移和收口结果；HEAD 是 2026-09-20 的旧 94-worktree 清单。 | WS_IS_CURRENT | 工作区 :10-29 记录 Stage 5 迁移、复核及收据，:31-50 记录 Stage 6 删除前核验与执行结果；HEAD :3-15 自称 2026-09-20 快照、94 worktrees 且未删除/修剪。旧清单已由工作区 :10 链接至 archive。 | KEEP_AND_COMMIT |
| doc/templates/HANDOFF.md | 工作区增加 Codex closeout 与 Handoff 权限边界；HEAD 无此要求。 | WS_IS_CURRENT | 工作区 :46 要求 DONE 前按 Task 的 Canonical Evidence/Resource Manifest 收口，并说明 Handoff 不授权集成、删除或关闭；与协作协议 §4 一致。HEAD :44-46 无该生命周期约束。 | KEEP_AND_COMMIT |
| doc/templates/REVIEW.md | 工作区增加固定 reviewed head 与历史化规则；HEAD 仅有通用 Review 内容。 | WS_IS_CURRENT | 工作区 :21 将 Review 绑定 YAML 的 base_commit/reviewed_head，并规定新 head 或新 Review 后旧报告不再是当前批准；与生命周期 v2 的精确 head 绑定一致。HEAD :19-21 缺少该规则。 | KEEP_AND_COMMIT |
| doc/templates/TASK.md | 工作区将 v1 模板升级为 lifecycle v2，并新增证据、资源和关闭记录结构。 | WS_IS_CURRENT | 工作区 :5,14-18 增加 governance_version: 2、delivery/evidence/closeout 字段，:59-82 增加 Canonical Evidence、Resource Manifest、Closeout Record；HEAD :3-17,51-53 仍为 v1 且没有这些表。新 Task 已按此格式使用。 | KEEP_AND_COMMIT |
| doc/tasks/P02.md | 工作区尾部仍称 Build 是唯一 READY、尚待 preflight；HEAD 已记录 Build 集成和后续产品 Task 派发。 | HEAD_IS_CURRENT | 工作区 :1012-1013 的“Build 未启动”与同一 Task 前部 :5,34-35 的 closed_with_limitations、新时点成果已主线集成不一致。HEAD :1013-1014 记录 Build/Cargo 已集成且 BC-AC5=PARTIAL、后续 Task 已派发；当前 STATUS:21 也保留 BC-AC5 PARTIAL。 | RESTORE_HEAD |
| doc/tasks/P02-NEW-TIME-X6.md | 工作区记录 X6 已完成 post-run Review/adjudication、证据与资源 closeout；HEAD 仍停在 in_review/AC7 pending。 | WS_IS_CURRENT | 工作区 frontmatter :6,26-27 为 approved 且 evidence/resource complete，:57,83,111,116,124-125,184-187 记录 AC7、DSH APPROVED、Codex convergence 与 closeout。HEAD :6,26-27,55-57,83,112-121 仍称 Review/governance pending。父 Task 当前主线集成记录见 doc/tasks/P02.md:34-35。 | KEEP_AND_COMMIT |
| doc/tasks/P02-NEW-TIME-X6-BUILD-CARGO.md | 工作区把 Task 回退到待启动/未执行；HEAD 记录已审查、已集成，BC-AC5 保留 PARTIAL。 | HEAD_IS_CURRENT | 工作区 :6,9,16,21,26-27,45-52,71-75 为 ready、Owner=ZCode、无 integration commit、AC 均未运行。HEAD :6,9,16,19,21-22,51-53,72-79 为 approved、Owner=Antigravity、integration_commit=20d554e...、INTEGRATED、DSH/Codex APPROVED，且明确 BC-AC5=PARTIAL；当前 STATUS:21 保留该 residual。直接复核的 blob 为工作区=e0b7d869a72084fa770994380c65f1bf92fdd637、当前 HEAD=28dd6e16610ef7c01b20309c400b7ed0ee1fad26、cb452b7db:path=4bcd05bcbe2ad4f83fee028e1a8910c2a7ec4874，三者并不相同；因此不采纳该精确 blob 关系，判定依据是上列状态与 AC 差异。 | RESTORE_HEAD |
| verification/P19/codex-review-r2.md | 工作区补充复核范围和 R2-004 对状态指针不一致的发现；reviewed head 不变。 | WS_IS_CURRENT | 工作区 :14,27,36,44 明确 R2 完整差异包含 STATUS/Plan 指针更新，并将该不一致纳入 R2-004 与核验范围；HEAD :14,27,35,43 漏掉该范围/finding。工作区仍绑定相同 reviewed_head=cf4161ac...，新增内容补足该固定 head 的审查记录。 | KEEP_AND_COMMIT |
| verification/PROJECT-ROADMAP-20261008/ROADMAP.md | 工作区将较晚的 P02 Stage A r4 状态写入 2026-10-08 命名的历史目录；HEAD 保留该快照的较早状态。 | HEAD_IS_CURRENT | 工作区 :1,3,5 仍标注 2026-10-08，却写入 Stage A r4、后续 Review 尚未开始等较晚工作点；HEAD :1,3,5 保留该日期快照的旧 P02 状态。当前 P02 已关闭并主线化，工作区内容也不再代表当前状态；为保持证据路径的时间含义应保留 HEAD。 | RESTORE_HEAD |

## 分组汇总

### 按判定

- WS_IS_CURRENT：16
- HEAD_IS_CURRENT：3
- MIXED：0
- USER_DATA：1
- UNKNOWN：0

### 按建议处置

- KEEP_AND_COMMIT：16
- RESTORE_HEAD：3
- MERGE_MANUALLY：0
- ASK_USER：1
- NO_ACTION：0

## 方向计数复核

按本报告 20 个路径的磁盘字节重新核算，工作区每个 CRLF 只剔除其中的 CR 字节后与 HEAD blob 比较：12 个路径工作区内容字节较多，8 个较少。content-diff-assessment.md 摘要写的 11/9 与其自身 20 行 REALDIFF 数值及当前磁盘复算不一致；本报告以上述可复算的 12/8 为准。长度只用于核对方向，不作为语义判定依据。

## 需要用户单独裁决

- .qoder-credits/report.json：该文件是用户侧 Qoder 使用报告。工作区生成时间较晚，但覆盖量大幅减少；仅凭当前证据不能判定应保留哪一份。建议用户决定保留工作区报告、保留 HEAD 历史报告，或先另存两份后再处理。裁决前不要改动该文件。

## 处置状态

**本轮未执行任何处置动作。** 除本报告外，20 个评估文件均未修改、恢复、暂存或提交；没有读取受保护路径中的文件内容，也没有写入这些路径。