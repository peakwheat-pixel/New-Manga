# 文档与工作区治理

生效日期：2026-10-12。产品目标架构保持 `Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy`，依据 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 和 2026-09-28 用户裁决。本规则只约束文档、证据、临时目录和 Agent 上下文，不改变产品功能或架构。

## 当前有效文档最小集

Agent 默认优先读取：

1. `AGENTS.md`
2. `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 及当前 Task 明确引用的其他有效 AD/ADR
3. `doc/STATUS.md` 当前状态段
4. `doc/REBASELINE_PLAN.md` 当前 DAG 段
5. 当前 Task
6. 该 Task 最新有效 Review/adjudication
7. 当前 rolling checkpoint

`doc/00_INDEX.md` 只用于解析当前导航和恢复指针；`doc/09_COLLABORATION.md` 按需读相关章节。文件中标注为历史/已取代的段落不参与当前决策。不得默认通读历史目录、历史任务、全部 verification、旧 Review 或 checkpoint。 `REBASELINE_PLAN.md` 与 `STATUS.md` 仅保留当前 DAG/状态、必要近期摘要和历史归档锚点；完整旧快照统一放入 `archive/history/`，不作当前授权来源。

## 文档分类

| 分类 | 含义与处理 |
|---|---|
| `CURRENT` / `ACTIVE` | 当前决策、规划、运行状态或当前 Gate 明确依赖的资料。不得移动或改写其证据内容。 |
| `LEGACY` | 旧生产基线或迁移参考。可以说明历史实现；不得描述为当前产品目标或新 Task 的默认实现依据。 |
| `HISTORICAL` | 已完成 Task、Review、handoff、checkpoint 或验证结果；保留其当时语义，不参与当前授权/DAG。 |
| `SUPERSEDED` | 有明确后继或更新快照的资料。标记后只按需读取，不能因此假定原始证据可删。 |
| `ARCHIVE` | 已按引用映射迁入统一 archive 的历史材料；保留原路径映射和内容 hash。 |
| `REDUNDANT` | 经逐字节或逐项比较证明内容完整重复，且无唯一证据价值、无当前引用。 |
| `SAFE_TO_DELETE` | 已确认无引用、无审计/恢复价值、无用户数据、无 dirty/unique Git 内容的派生物。 |
| `UNKNOWN_DO_NOT_DELETE` | 来源、价值、授权、内容或引用不确定；原位保留并记录不确定点。 |

架构文档当前分类：`AD-001` 为目标架构权威；`doc/01_FUNCTIONAL_ARCHITECTURE.md` 与 `doc/04_USER_FLOW.md` 保留产品功能/流程意图，不定义技术栈，也不自动释放实现任务；`doc/02_TECHNICAL_ARCHITECTURE_.md` 是 PySide6/QML Legacy Production Baseline；`doc/05_UI_MAPPING.md` 是旧 QML UI 映射；`doc/06_TRANSLATION_PIPELINE.md` 保留业务流程与数据安全要求，其中 Qt 展示/接线是 Legacy Reference；`doc/07_NON_FUNCTIONAL_REQUIREMENTS.md` 与 `doc/08_ACCEPTANCE_CRITERIA.md` 是混合文档，产品级要求仍保留，技术专属实现与旧 Gate 为 Legacy，当前 Task/contract 负责映射和执行授权；`doc/13_ACCEPTANCE_TRACEABILITY.md` 保留旧编号、旧 reviewed head 与当时证据结果，不把历史结果继承为新架构验收；`doc/10_CURRENT_STATE_AND_GAPS.md` 是 2026-09 初始接管快照；`doc/11_ARCHITECTURE_MAPS.md` 是 2026-09-22 Legacy As-Is 快照；`doc/12_ROADMAP.md` 是导航与历史里程碑，当前排期只看 Plan/Status。`doc/09_COLLABORATION.md` 的当前 Review 标准排除 Legacy QML/PyInstaller 规则。Task、Review、checkpoint 和 verification 按 Task 自身状态与当前引用分类，不能按文件名批量归档。

## Workspace 路径

源码仍在 `G:\CODEX\New Manga`。所有**新建**派生产物使用相邻目录 `G:\CODEX\New Manga.workspace\`：

| 路径 | 内容 |
|---|---|
| `worktrees/<TASK-ID>/` | 新建 linked worktree；旧 worktree 不自动搬迁。 |
| `builds/<TASK-ID>/` | cargo、frontend、package 等可重建构建输出。 |
| `artifacts/<TASK-ID>/` | 交付包和生成产物；被验证引用时保留。 |
| `temp/<TASK-ID>/` | 短期可重建临时数据，Task 结束后按安全规则清理。 |
| `agent-output/<agent>/<TASK-ID>/` | CLI/session 原始输出及 Agent 交换材料。 |
| `task-envs/<TASK-ID>/` | Task 专属虚拟环境/隔离配置。 |
| `exchange/<TASK-ID>/` | 有明确来源和生命周期的跨 Agent 交换。 |
| `archive/<category>/<TASK-ID>/` | 不再活跃、但需要保留的仓外派生物。 |

禁止在 `G:\CODEX\` 根目录新建临时 `repair-*`、`build-*`、`qoder-tmp`、`P02-*`、`*-exchange`。版本化历史文档的统一归档目录为仓库根 `archive/`。迁移现存内容前必须保存映射与 hash，并核对所有 inbound references；当前 Gate 依赖文件不得移位。

## Verification 与清理门槛

- 保留最终 adjudication、最终有效 Review、当前 Gate 所依赖的原始 evidence/source pins，以及恢复当前 Task 必需的 rolling checkpoint。
- r1/r2/r3/r4、retry、attempt 等过程文件仅在最终文件逐项覆盖其唯一结论、所有引用已迁移、没有当前 Gate/source pin 依赖后，才可归档或删除。
- Task 的唯一 READY/DAG 权威是 `REBASELINE_PLAN.md`；唯一运行状态权威是 `STATUS.md`。DONE、SUPERSEDED、CANCELLED、HISTORICAL Task 不得作为 READY 节点。
- worktree 仅在 Task 已明确 done/closed、clean、无 untracked、HEAD 无独有提交且不属于任何当前 Task 后才可移除。Dirty、唯一文件/提交或归属未知的 worktree 保留。
- 不为瘦身运行 Git history rewrite 或未经证明的 GC；孤立对象、临时 refs、外部目录和数据库默认按 `UNKNOWN_DO_NOT_DELETE` 保留。

## 训练数据、模型权重与测试素材

大型训练数据、模型权重、测试漫画/图片和公开数据集统一存放在 `G:\CODEX\New Manga.workspace\`，不得继续散落到 Task worktree、仓库 ignored 目录或 `G:\CODEX\` 根目录临时文件夹。

| 内容 | 统一目录 |
|---|---|
| 训练集、公开数据集、标注与样本来源 | `datasets/objects/sha256/` |
| `.pt`、`.onnx`、`.pth`、`.ckpt`、`.safetensors` 等模型产物 | `models/objects/sha256/` |
| 测试漫画、验证图、golden fixture、人工检查素材 | `test-materials/objects/sha256/` |
| 已停用、来源未知或仅需审计保留的数据 | `archive/worktree-data/objects/sha256/` |
| 全局身份、来源映射与分类索引 | `data-registry/registry.json` |

对象按 SHA-256 内容寻址：`<category>/objects/sha256/<hash 前两位>/<完整 SHA-256>.<扩展名>`。整个 workspace 对相同内容只存一个物理对象；若对象同时用于多个类别，其他分类 manifest 引用其 `object_id` 与真实 canonical path，不另复制一份。文件名相同不能作为去重依据。

每个导入对象必须在 master registry 中有记录，至少包含：稳定 `object_id`、SHA-256、字节数、canonical path、所有源文件相对路径与原 worktree、Task/用途、获取时间、来源 URL 或提供者、版本/数据集标识、许可证及许可证证据、允许用途、署名要求、再分发限制、当前引用与去重别名。公开可访问不等于允许再分发；许可证或来源不清楚时标为 `unknown/private-only`，仅限本地留存和任务验证，不公开分发，也不得以“可重新下载”为由删除唯一源数据。

导入流程：先将文件置于 `temp/<TASK-ID>/` 或受治理的 workspace staging；生成来源/许可证记录与 SHA-256 manifest；比对已有 registry 查重；验证源文件与 canonical 对象的 SHA/size；随后写入对象库并更新 master/category manifest。Task、脚本或配置只引用 manifest `object_id`/registry 路径，不硬编码旧 worktree 的绝对路径。需要编辑、裁切、转码或重新标注时，先复制到 Task 临时目录，绝不原位修改内容寻址对象。

Task worktree 可以包含代码和轻量 manifest 引用，不得包含数据集、模型 checkpoint 或大体积测试漫画的私有副本。Task 关闭后，派生缓存按普通清理门槛处理；源数据只有在所有当前引用已更新、迁移文件数/字节数/哈希验证通过、许可证和恢复条件有记录、worktree 无未提交/独有 Git 内容后，才可随旧 worktree 一起移除。删除使用普通 `git worktree remove`，不得用 `--force` 掩盖数据或状态问题。
