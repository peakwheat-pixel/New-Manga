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

各文件的当前/Legacy/历史分类、权威来源和 Agent 默认读取集统一见 [Document Truth Map](00_INDEX.md)。本规则定义归档与保留门槛，不重复维护第二份架构索引。Task、Review、checkpoint 和 verification 按当前引用及自身证据状态判断，不能按文件名批量归档。

文档替代时，先改写 `00_INDEX.md` 的权威指针/分类，再迁移或归档旧正文并登记原路径与 hash；唯一事实只保留在其权威源，副本只写指针。新旧文档冲突以 Truth Map 指定的事实来源裁决。检查器只对当前最小读取集执行引用、预算和架构哨兵检查，不扫描全库语义；新增/改动的当前文档必须同步更新 Truth Map，周期健康检查报告无法机器裁决的漂移。

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

## 治理主线分支（2026-10-20 登记）

**当前治理主线分支**：`antigravity/P09-AC3-DELETE-HARDEN-1`

**判据**：仓库现有数百条分支，`main` 与 `master` 都**不是**主线
（2026-10-20 实测：`main` 落后主线 **367** 个提交，`master` 落后 **2271** 个）。

**确认方法**（可复算）：

```
git log --oneline -20 -- doc/REBASELINE_PLAN.md
```

**该文件的最近 20 个提交全部落在 `antigravity/P09-AC3-DELETE-HARDEN-1` 上。**

**为什么需要这一节**：主线分支名没有任何命名约定能推断出来
（`AGENTS.md` 规定 Agent 使用自己的任务分支，而这条分支的名字是一个 Task 名，
实际上却承载了全项目的治理历史）。**没有登记时，每个新会话都必须靠翻提交历史反推。**

**维护规则**：
1. **治理提交（`doc/**`、`verification/**` 的核查与登记）落在主线。**
2. **Task 实施提交落在该 Task 自己的分支**（`agent/<name>/<TASK-ID>`）。
3. **主线切换时（重命名、建立真正的 `main`、或迁到新分支），必须同步更新本节。**

**未做**：重命名该分支或建立真正的 `main` 属于结构性变更，
需要单独裁定，不在本次登记的范围内。

## Verification 与清理门槛

- 保留最终 adjudication、最终有效 Review、当前 Gate 所依赖的原始 evidence/source pins，以及恢复当前 Task 必需的 rolling checkpoint。
- r1/r2/r3/r4、retry、attempt 等过程文件仅在最终文件逐项覆盖其唯一结论、所有引用已迁移、没有当前 Gate/source pin 依赖后，才可归档或删除。
- Task 的唯一 READY/DAG 权威是 `REBASELINE_PLAN.md`；唯一运行状态权威是 `STATUS.md`。DONE、SUPERSEDED、CANCELLED、HISTORICAL Task 不得作为 READY 节点。
- worktree 仅在 Task 已 Review approved、Codex 已记录 integration_commit 与集成后验证（或已为其他终态）、不再属于当前 Task，且刷新 Inventory 后 clean、无 untracked、HEAD 无独有提交、无当前引用时才可移除。Dirty、唯一文件/提交或归属未知的 worktree 保留。
- 不为瘦身运行 Git history rewrite 或未经证明的 GC；孤立对象、临时 refs、外部目录和数据库默认按 `UNKNOWN_DO_NOT_DELETE` 保留。
- Task 的完整 READY→DONE 状态、canonical evidence、Review/checkpoint 降级和资源 closeout 只由[协作协议 §4](09_COLLABORATION.md#4-task-文件约定)定义；本文件仅定义派生物位置与保留门槛。新 Task 结束时按 Resource Manifest 逐项核销，不按目录名推断安全。
- `STATUS.md` 上限 3,200 bytes / 45 行，`REBASELINE_PLAN.md` 上限 2,500 bytes / 35 行；达到上限前先把过期流水账移入 `archive/history/` 并保留简短锚点。机器预算由 `tools/governance/check.ps1` 检查。
- 每个 Task 的默认文档上下文目标 ≤12,000 tokens：只读 AGENTS、AD-001、STATUS 当前段、Plan 当前 DAG、当前 Task、最新 Review/adjudication、rolling checkpoint；额外历史只按当前 AC/pin 取用，并在 Task 记录原因。token 数以模型分词器估算为准，检查器不扫描历史目录估算 token。
- verification 只保存最终 adjudication、最终有效 Review、Gate 所需原始 pins 和当前 rolling checkpoint。尝试/重试输出默认写 workspace；每个 AC/Gate 在 Task 表中只指向当前 canonical item。旧版 P02 等共享证据路径按原 pin 保持，不为套用新布局而移动。

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
