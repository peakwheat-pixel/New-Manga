---
task_id: FEA-09
reviewer: Codex
reviewer_kind: agent
reviewer_source: 用户直接指派的独立 Codex 审查会话 /root
reviewer_configuration: gpt-6.1-sol / reasoning medium（按任务指定配置登记）
author: DSH（范围草案）
base_commit: null
reviewed_head: 6e274dd94c5b64d8fbc3f9d578363d3c502a2b68
reviewed_task_git_hash_object: 55abafbe61b91d3c649cefbb8c39a7026455f893
reviewed_task_worktree_sha256: b23a80d619f98c585107f4b811cb8a35fff6c65e0a3dac31df8e24d02ec3fa42
decision: changes_requested
---

# FEA-09 Scope Review r1

## 0. 元信息与审查边界

- 审查时间：2026-11-03 15:41–15:46，Asia/Shanghai。
- 仓库：`G:\CODEX\New Manga`。
- 分支：`main`。
- Git common directory：`G:\CODEX\New Manga\.git`。
- 被审对象：工作树中的 `doc/tasks/FEA-09.md`，不是假定的未来实现 diff。
- `git hash-object doc/tasks/FEA-09.md`：`55abafbe61b91d3c649cefbb8c39a7026455f893`。
- 工作树原始字节 SHA-256：`b23a80d619f98c585107f4b811cb8a35fff6c65e0a3dac31df8e24d02ec3fa42`。
- 审查前后 HEAD 相同，`git status --short` 均为空；被审文件 hash 相同。
- **未修改任何文件；未执行 add、commit、push；未触碰真实用户数据；未启动产品或运行 FEA-08 原型。**
- 本会话未参与该范围草案撰写，且不得参与 FEA-09 后续实现或返修。

审查覆盖 Architecture 与 Verification。采用规范及需求符合性视角，但按仓库 `doc/templates/REVIEW.md:15`，不要求并行双轴子代理。

## 1. Verdict

**`changes_requested`。**

发现 **P0 × 0、P1 × 9、P2 × 4**。

当前草案不能直接冻结为生产实现范围，主要原因是：

1. Source 生产实现的 DDL 前置未处理，且与 `out_of_scope` 直接冲突。
2. Registry 存储归属已有冻结答案，草案仍将违反 C-06 的选项作为待选方案。
3. 合法 referenced 页需要改动的 domain model、decoder、CoreClient、Python 测试和协议文档未得到完整写域。
4. Core→Host 进程内断言不能满足提案明确要求的 Core→Host→UI 结果。
5. 授权生命周期、缓存预算、完整性迁移和密码传输缺少可判定验收约束。

`G-CONTRACT` CLOSED、FEA-08 done 和机械检查 PASS 均不能替代这些前置。

## 2. 五项裁决

### 2.1 AES ZIP 依赖

**结论**

本次建议采用 **预生成 AES ZIP fixture + SHA-256，生产返回明确的 typed unsupported**。**本 Task 不新增 pyzipper 到生产或测试依赖闭包。**

支持的加密子格式仍须验证实际密码重试，例如 ZipCrypto ZIP/CBZ 和现有 PDFium 可解密的 PDF。AES ZIP 不得计入解密成功覆盖。

这是建议提交 DSH 的范围处置；AES 能力取舍须明确登记为产品限制，不能由实现者暗中决定。

**依据**

- `requirements.txt:12`、`:13` 已有 Pillow、`pypdfium2==5.13.0`；`requirements-dev.txt:1` 引入主 requirements，全文未列 pyzipper。
- `doc/research/FEA-08-source-capability.md:113`、`:127`：AES fixture 已预生成，标准库读取 AES 不可用，未引入 pyzipper。
- 同文件 `:158`、`:168`：生产 AES 支持仍属待裁决能力。
- `doc/tasks/FEA-09.md:21` 的 allowed_paths 未包含任何 requirements 或 packaging 文件。
- 提案 `:469` 要求按实际 decoder 给出支持矩阵，不能把“有 fixture”写成“支持解密”。

**对 Task 的修改建议**

- AC-4 明确区分“支持的加密格式密码重试”与“AES ZIP typed unsupported”。
- AES fixture 登记来源、生成方式、SHA-256；不得依赖开发机偶然安装的 pyzipper。
- 不修改 `requirements.txt`、`requirements-dev.txt`、`packaging/**`。
- 若产品要求本轮支持 AES 解密，先另行冻结依赖变更范围：精确版本、传递依赖、许可材料、生产 requirements、打包 requirements/spec、许可清单及干净打包 smoke。仅修改测试 requirements 不足以交付生产 AES 能力。

**风险**

预生成 AES fixture 只能证明识别、拒绝和无副作用，不能证明 AES 解密。测试环境安装 pyzipper 后成功，也不能证明发布包成功。本轮未独立审计 pyzipper wheel 及其传递依赖许可。

### 2.2 `SourceAccessRegistry` 持久化载体与 Schema

**结论**

**Registry 必须使用 Host 私有存储，不写 Core DB。** 这已经由冻结 C-06 确定，不是仍可自由二选一的设计问题。

同时，**FEA-09 仍被未冻结的 Core Source DDL 阻塞**。把 Registry 放到 Host 并不能解除 Core source schema/read/cache 的前置。

推荐 DSH 先拆出存储契约前置，完成独立复核后再释放 FEA-09。

**依据**

- `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:27`、`:28`：Host 归属、Host 私有存储、**不写 Core DB**；备份包内加密。
- `doc/plan/FEA-CONTRACT-FROZEN-C06.md:14`、`:15` 固定上述契约字节；`:17` 规定修订须 UNFREEZE。
- `doc/plan/GATE-CONTRACT-CLOSURE-2026-11-01.md:48` 至 `:55`：DDL 未冻，是任何 Source 生产实现的前置，须在释放实现 Task 前完成并复核。
- `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:117`：七类 Source 表的结构及迁移版本未定。
- `src/infrastructure/sqlite/schema.py:597` 至 `:604`：当前默认迁移为 v1–v6。
- `src/infrastructure/sqlite/migrator.py:69`、`:141`：现有版本迁移和事务机制。

**对 Task 的修改建议**

建议冻结以下具体方案，作为待 DSH 接受的实现约束：

- Host Registry：`<HostOptions.DataRoot>/host/source-access/registry.v1.dat`；测试必须注入隔离 DataRoot。
- 文件内容：带格式版本的 UTF-8 JSON，再使用 Windows DPAPI CurrentUser 保护；通过现有系统 API 绑定实现，不默认引入 NuGet 依赖。
- 不持久化短期 grant、session signing key、lease 或密码。
- 授权 generation、撤销状态和根身份必须持久化；重启重验根身份并建立新 session，旧 grant 不恢复。
- 同一数据根使用专用跨进程锁；现有全局单实例机制继续保留。锁冲突拒绝第二写者。
- 同目录临时文件、flush、原子替换；损坏、解密失败或不确定恢复时 fail-closed，不恢复陈旧授权。
- 撤销立即使当前 grant 失效；持久化失败时拒绝继续签发，不以旧磁盘状态重新授权。
- 备份导出接口及其加密要求形成明确交接，完整备份/恢复实现归 FEA-13；跨机恢复不得自动继承可用授权。

Core Source 数据建议沿用业务 `library.db` 的迁移链。**v7 是当前可预留的下一个版本，不是本报告替 DSH 冻结的版本。** 前置契约须确定全部相关表、约束、索引、外键、完整性字段、迁移版本及兼容策略，并明确哪些表本轮创建、哪些仅为 FEA-11/12 保留。

**风险**

仅有 Host 原子文件不能形成 Host 授权与 Core binding 的跨存储事务。必须冻结失败恢复次序；不得出现“Core 已发布 complete binding，Host 授权却尚未可靠持久化”的假成功。

### 2.3 UI 可观察路径

**结论**

选择 **真实 Host IPC + 现有 V2 消费路径的隔离证据**。**仅 Core→Host 进程内断言不够。**

现有 UI 可以验证部分既有结果，但无法据此承诺五类输入、密码重试和导入取消的完整 UI 验收。建议由 DSH 另行冻结最小 UI/adapter 接线切片，Owner 为 ZCode；FEA-09 对相应完整 UI AC 的收口依赖该切片。

**依据**

- 提案 `:1040` 明确要求每项断言 Core→Host→UI 结果。
- `doc/tasks/FEA-09.md:35`、`:65` 将结果缩为 Core→Host。
- `HostIssuer.cs:53` 至 `:55` 的旧扩展名集合无 ZIP/CBZ。
- `HostGrantCoordinator.cs:135` 至 `:165` 调用旧 `ImportPages`，再压缩为 summary。
- `ImportDockViewModel.cs:225`、`:314`、`:361`：逐行调用旧 controller、展示结果摘要。
- `ImportDockView.axaml:35` 至 `:47` 有开始、重试、跳过；没有密码输入或运行中取消入口。
- `ImportExportUiTests.cs:18` 至 `:24` 明确使用 fake controller，不能作为真实 IPC 证据。

**对 Task 的修改建议**

证据分层登记：

1. Python service/repository 故障测试。
2. 真正启动隔离 sidecar，经 Host/CoreClient 实际序列化传输。
3. 现有 V2 ViewModel/控件通过生产 adapter 消费该结果，断言状态、原因及计数。
4. 未有入口的密码、plan 确认、取消功能由单独冻结切片接线后复核。

不得修改 UI 代码即可增加已有路径的测试；但“UI 无写域”也不能用来豁免不可达的必需行为。DSH 若保留全部 UI 写域在范围外，必须明确建立接线依赖，不能把 AC-6 改成进程内后宣称满足原提案。

**风险**

Core 成功、fake UI 成功和真实用户路径成功是三种不同证据。旧 summary 还可能丢失逐项原因、receipt 和当前项目进度。

### 2.4 `IFileOperation` per-item sink / 真实取消

**结论**

**本 Task 不验证或实现 Windows 回收站的 per-item sink、`IFileCancel` 或真实系统取消。** 继承 FEA-08 的 LIMITED/UNAVAILABLE，归 FEA-12/D 流程处理。

本 Task 必须验证的是**导入取消**：Host/Application 抽象 seam、注入取消、提交边界及恢复结果；不能把取消 IPC 等待当作取消 Core 操作。

**依据**

- `doc/tasks/FEA-08.md:216` 明确保留这些限制。
- `doc/research/FEA-08-source-capability.md:176`、`:178`：真实取消未实测，per-item sink 未实跑。
- 提案 `:512` 至 `:514` 属原文件独立删除流程。
- `doc/tasks/FEA-09.md:37`、`:38` 已排除真实删除和 FEA-12。
- `src/bootstrap/core_service.py:3566` 至 `:3597` 有导入取消检查及句柄释放，但其运行事实本轮未测试。

**对 Task 的修改建议**

AC-5 增加：

- 取消前、解码中、提交前、提交后、丢 ACK 和重启恢复的可注入边界。
- 以冻结的提交单元判断：已提交保留，未提交不可见，receipt 可重复查询。
- Host 发起取消与 Core 实际接受取消分别有记录。
- mock/注入证据标明层级；不得升级为 Windows 原生取消 PASS。
- 不新增回收站生产代码或 destructive OS 测试。

**风险**

`CancellationToken` 可能只停止等待，Core 仍继续执行。必须证明业务取消结果，而不是只检查调用抛出取消异常。

### 2.5 `src/application/importing/` 落点

**结论**

“当前无 `.py` 源文件”**不属实**。

选择新增 **`src/application/importing/referenced/`** 子包，承载引用导入编排；**不并入 `resource_channel`**。

**依据**

实际已有七个 `.py` 文件：

- `documents/__init__.py`
- `documents/ports.py`
- `documents/service.py`
- `images/__init__.py`
- `images/ports.py`
- `images/service.py`
- `images/sorting.py`

其中：

- `images/service.py:39` 已有 `ImportImagesUseCase`，执行 Managed Copy。
- `documents/service.py:47` 已有 `ImportDocumentsUseCase`。
- `images/sorting.py:19` 已有自然排序。
- 提案 `:930` 明列 importing 写域。
- 提案 `:932` 将未来变化、重定位、同步落在 `src/application/sources/`。

**对 Task 的修改建议**

- 删除 Task `:48`、`:75` 的错误前提。
- 新子包负责 plan、确认、提交、receipt、取消、密码短期引用和导入去重策略。
- `resource_channel` 负责受限读取、授权、lease、rendition/cache，不承担导入业务编排。
- FEA-11 的 `sources/` 保留给 scan/diff/relink/resync；本 Task 不提前建设该状态机。
- 保留旧 managed 导入代码及兼容测试，不通过重写旧服务隐式改变旧 grant/命令语义。

**风险**

旧图片导入按 digest 去重，见 `images/service.py:80`、`:113`；直接复用该策略会丢失合法重复 occurrence。复用 decoder、排序函数不等于复用去重及提交语义。

## 3. Findings

所有 findings 均为 **open**；本报告没有执行修复。

| ID | severity | 位置 | 问题 | 依据 | 建议 |
|---|---|---|---|---|---|
| R1-001 | P1 | `FEA-09.md:36,48,52` | 范围包含生产 Source schema，却排除生产 DDL，并遗漏实现前置。 | Gate closure `:48–55`；AD-003 `:117–128`；当前 schema 仅 v1–v6。 | 先完成并复核存储契约；登记真实前置 Task ID，再开放精确 DDL 写域。 |
| R1-002 | P1 | `FEA-09.md:53,72` | 把 Registry 写 Core SQLite 当作待选方案，违反已冻结归属。 | C-06 `:27–28`；C06 冻结记录 `:14–17`。 | 固定 Host 私有存储；冻结格式、位置、加密、代次、锁和恢复协议。 |
| R1-003 | P2 | `FEA-09.md:48,75` | “importing 无 `.py`”是错误代码前提。 | 现有七个 `.py`；images service `:39`、documents service `:47`、sorting `:19`。 | 按真实已有包冻结新 referenced 子包及复用边界。 |
| R1-004 | P1 | `FEA-09.md:21–33` | 写域不足以完成 referenced 页及新授权协议。缺 domain Page、decoder、CoreClient、Python tests、协议载体。 | `domain/pages/entities.py:28,43` 强制 managed ref；`infrastructure/importing.py:315–338` 无密码入参；HostIssuer `:53–55`；C06 冻结记录 `:44`。 | 增加精确路径；共享模型及协议变更单列授权；禁止借宽目录写域修改无关功能。 |
| R1-005 | P1 | `FEA-09.md:35,65,73` | 将三层 UI 结果缩为进程内结果；现有页面不覆盖全部新操作。 | 提案 `:1040`；ImportDock View/VM；HostGrantCoordinator `:164`；UI tests 使用 fake。 | 保留真实 IPC/UI 验收；冻结最小接线切片及依赖，不能静默降低 AC。 |
| R1-006 | P1 | `FEA-09.md:53,65–67` | “旧 grant 不复用”仅为散文，没有授权失效、重启、根替换和 strict lease 的可执行负测。 | 提案 `:895`；C-06 `:39–65`；FEA-08 `:78`；现有 registry `:153,250–255`。 | 增加授权生命周期 AC；过期/撤销/代次错/Host 失联拒绝新读及提交；严格使用同一验证流。 |
| R1-007 | P1 | `FEA-09.md:55,66` | 五读路径未列名；缺旧谓词快照、半写回填、缺文件暂停切换、staging/journal 失败恢复。 | 提案 `:893,1026–1028`；library `:79,299–374`；Page `:43`。 | 明列五路径及 reader projection；冻结迁移守恒与失败矩阵，不能仅让 NULL managed ref 通过。 |
| R1-008 | P1 | `FEA-09.md:52,60–67` | cache 只有 key 描述，无上限、淘汰、活跃引用保护、崩溃校验等验收。 | AD-003 `:57–58`；C-14 SC-S14…S17 `:157–189`。 | 增加 cache AC：预算、LRU、并发、重建、非缓存保护和源/derived 通道隔离。 |
| R1-009 | P1 | `FEA-09.md:54,63,73` | plan/receipt 及安全密码传输没有冻结载体；旧命令不能直接承载。 | Core service `:3539–3543` 只接受旧字段；C06 冻结记录 `:36,44` 要求旧语义不变及 wire 修订；`WireLog.cs:82–105` 保存原文及 UTF-8 hex。 | 先冻结新增命令、版本、能力拒绝、receipt/重试边界及密码短期引用；验证普通 wire/evidence 日志无密码及可逆编码。 |
| R1-010 | P1 | `FEA-09.md:63,71` | 未区分 AES fixture 覆盖和生产解密能力；“仅测试依赖”无法支撑泛化密码重试承诺。 | requirements 两闭包无 pyzipper；FEA-08 capability `:113,127,168`。 | 按 §2.1 登记 AES unsupported；若要求解密，先完成生产依赖、许可和打包决策。 |
| R1-011 | P2 | `FEA-09.md:54,64` | “项目”的提交粒度未定义；容器、页、书籍和批次的取消计数可能不一致。 | 旧 PDF service `:162–206` 按页提交；旧 UI 按文件/文件夹行汇总。 | 在 plan/receipt 契约中定义计数与提交单元，分别覆盖文件夹及多页容器。 |
| R1-012 | P2 | `FEA-09.md:60–81` | v3 AC 缺状态标记；无逐项 planned 验证表、Canonical Evidence、Resource Manifest；“全量测试不减少”口径不完整。 | 协作协议 `:85,93,103,116–138`；Task 模板 `:44–75`。 | 补齐 v3 标记及证据表；区分 .NET 基准与 Python 测试，新增 skip 逐条解释。 |
| R1-013 | P2 | `REBASELINE_PLAN.md:37,39`；Task `:11` | Plan 当前叙述仍指向已终态 residual 的 in_progress；FEA-09 未在节点表完整列出依赖和存储前置。 | Plan `:22` 与 `:39` 自相矛盾；STATUS `:7–10` 指向 FEA-09 proposed。 | 由 DSH 同步当前 DAG；不改历史冻结证据，不由 reviewer 推断 ready。 |

### 范围完整性核对

| 提案要求 | 草案现状 | 审查结论 |
|---|---|---|
| 五类输入成功/不支持/损坏 | AC-1 已列 | 保留；需按实际 decoder 子格式和错误类别展开。 |
| 自然排序、PDF 页码 | AC-2 已列 | 既有排序可参考；新增目录层级、同键 tie-break 和 ordinal 断言。 |
| 重复名及重复同图 occurrence | AC-3 已列 | 不能继承旧 digest 去重；须验证条目与 binding 数量。 |
| 密码重试、日志/快照无密码 | AC-4 已列 | 缺安全传输和 wire hex 审计，AES 能力未定。 |
| 跳过、取消、进度、汇总 | AC-4/5 已列 | 缺提交粒度、运行中可达性、恢复及计数守恒。 |
| Core→Host→UI | 缩为 Core→Host | 不满足原提案。 |
| 源字节不变、不永久复制 | scope/AC-6 部分覆盖 | 应同时检查源 hash/mtime、managed/旧 derived 不变及新增产物分类。 |
| 共享源项目结果独立 | AC-6 已明确 | **不是遗漏**；需展开阅读进度、人工修改、处理结果的交叉断言。 |
| 五读路径/半写负例 | AC-7 概括提及 | 缺路径清单和迁移守恒。 |
| managed 双读、新 schema 禁旧写 | AC-7 已明确 | **不是遗漏**；需实际旧端拒写和关闭开关后的双读测试。 |
| 临时 grant 不变长期通行证 | scope 已写 | 缺 AC 和生命周期故障证据。 |
| 回退开关 | scope 已写 | 未形成明确开关动作和既有 referenced 页继续读取的 AC。 |

`G-DELETE-IMPL` 对本 Task **不构成依赖**，前提是保持只读源、导入和缓存范围，不加入回收站/原件删除。提案 §15.4 中删除、备份的全部行为不能机械并入 FEA-09；应保留类型隔离和后续交接约束。

## 4. 已核验、未覆盖及无法核验项

### 实际执行的只读检查

环境为当前 Windows 工作树；使用只读文件读取及 Git 命令。常规 exec 启动器因 Windows error 740 无法启动后，改用 Node REPL 读取文件及调用只读子进程，未提权、未修改权限。

| 检查 | 实际结果 | 证据口径 |
|---|---|---|
| HEAD、branch、common directory、status | HEAD 固定；main；common directory 为仓库 `.git`；前后 clean | 本报告元信息及工具标准输出。 |
| 被审 Task hash | Git hash-object 与工作树 SHA-256 已取得，结束时复核一致 | 本报告元信息。 |
| `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-09.md` | EXIT 0；`Governance check: PASS (3 warnings)` | 本次实际执行；warnings 涉非终态台账及 STATUS/PLAN 预算，不代表 scope 合格。 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；`PIN AUDIT: PASS (all 15)` | 本次实际执行；只证明冻结 pin。 |
| 旧 FEA-06 四 PNG | 逐文件与 `b26840acd` 对应 blob 字节相等 | 直接读取工作树及 Git blob 比较。 |
| build、.NET/Python tests、打包、UI 运行 | **NOT_RUN** | 只读 scope review 未运行会产生构建/测试文件的流程。 |
| FEA-08 R1–R8、真实卷或回收站实验 | **NOT_RUN** | 消费已归档结论，不重开、不复跑。 |

四 PNG 工作树 SHA-256：

| 文件 | SHA-256 |
|---|---|
| `reader.png` | `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2` |
| `settings.png` | `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162` |
| `shelf.png` | `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a` |
| `workbench.png` | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` |

### 明确未证明的内容

- `1292 passed / 0 failed / 57 skipped` 来自 `verification/FEA-08/logs/integration-verification.log:13`，是既有 **.NET solution** 基准，总数 1349；不是本轮复跑，也不是 Python 全量基准。
- 未重新核验 FEA-08 全部 EV 文件、原型脚本、R1–R8 或原始 OS 实验。
- 未验证真实 USB、SMB、云卷、Windows 原生取消或 per-item sink。
- 未验证任何 FEA-09 生产行为；目前没有可宣称的实现 PASS。
- 未测试性能、内存峰值、缓存上限、崩溃恢复、Registry 多实例一致性。
- 未验证新依赖许可及干净发布闭包，因为建议本 Task 不新增依赖。
- 未把源绑定的导入完整性与 C-05 artifact/revision 可见性视作同一谓词。两者衔接须由存储前置明确；不能凭本报告重新解释冻结 C-05。
- 本报告仅在标准输出交付，没有新建仓库日志或证据文件。DSH 归档后应对报告及其审查 hash 登记 canonical 引用。

## 5. 可直接落盘的 scope 冻结建议

以下是建议正文，须由 DSH 处置 findings、补齐实际前置 Task ID 并复审；**不构成当前实现授权**。

### 5.1 范围条款

1. 消费 FEA-08 已冻结的 strict-only、卷能力限制和 occurrence 结论；不得重开其原型或升级未经实测的能力。
2. 在已冻结的 Core Source 存储契约上实现引用登记、entry/version/binding、受限读取及有上限的 rendition/cache；不创建永久全尺寸输入副本。
3. 在 `application/importing/referenced/` 实现五类输入的预览 plan、确认、提交、receipt、失败重试/跳过、取消和进度。
4. Host 私有持久化 Registry 与短期 `source-read` grant 分离；旧一次性 `ImportPages` grant 及旧命令语义保持兼容。
5. 完成 referenced 页与旧 managed 页的双读及完整性迁移；合法 NULL managed ref 不伪装成 managed，也不绕过 binding 校验。
6. 为真实 Host IPC 和 V2 可达行为提供隔离证据；新增 UI 操作由 DSH 单独冻结最小接线切片。
7. 本轮 AES ZIP 仅验证 typed unsupported；支持的加密子格式验证密码重试。该能力限制须经 DSH 登记产品处置。
8. 实现关闭引用导入开关；关闭后禁止新引用导入，保留既有 managed/referenced 双读和已提交数据。

### 5.2 `allowed_paths`

建议保留现有路径，并按以下清单收窄或补齐：

```yaml
allowed_paths:
  - doc/tasks/FEA-09.md
  - doc/handoffs/FEA-09-*.md
  - doc/reviews/FEA-09-*.md
  - verification/FEA-09/**

  - src/application/importing/referenced/**
  - src/application/importing/images/**
  - src/application/importing/documents/**
  - src/application/resource_channel/**
  - src/infrastructure/resource_channel/**
  - src/infrastructure/importing.py
  - src/domain/pages/entities.py
  - src/bootstrap/core_assembly.py
  - src/bootstrap/core_service.py
  - src/infrastructure/sqlite/schema.py
  - src/infrastructure/sqlite/migrator.py
  - src/infrastructure/sqlite/library.py

  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Wire/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/WireLog.cs

  - tests/import_formats/**
  - tests/library/test_import_images.py
  - tests/library/test_import_sources.py
  - tests/library/test_sqlite_library.py
  - tests/core/test_p09_fu2_import_pages.py
  - tests/core/test_page_resource_resolve.py
  - tests/m2_resource_channel/**
  - tests/storage/test_schema_migration.py
  - tests/storage/test_upgrade_schema_data.py
  - tests/fea09/**
  - apps/desktop-avalonia/tests/**
```

附加冻结规则：

- `referenced/`、`tests/fea09/` 为拟议新增路径。
- domain Page、Schema、旧导入服务只允许本 Task 所需兼容改造；不能据此修改无关领域规则。
- 必须补列**实际选定的增量协议文档精确路径**。C06 冻结记录 `:44` 要求实现前处理 wire 字节；当前不能用 `doc/contracts/**` 通配授权代替该动作。
- `Host/**` 已包含 `NewManga.Host.csproj`，但不自动授权新增包依赖。CoreClient csproj 若需改动，须单列原因及路径。
- Host Registry 运行时文件不是仓库源码写域；测试运行时根固定在 `G:\CODEX\New Manga.workspace\` 下 Task 隔离目录。
- `requirements*.txt`、`packaging/**` 不纳入本轮。
- App Views/ViewModels、生产 App adapter、共享组合根不纳入此实现写域；由单独接线切片冻结。DSH 必须给重叠 seam 指定单一写者和集成顺序。

### 5.3 `out_of_scope`

```yaml
out_of_scope:
  - 真实用户数据、真实外部卷及 AppData 生产根测试
  - 原文件写入、删除、回收站操作及永久删除
  - IFileOperation per-item sink、IFileCancel、真实系统取消
  - FEA-08 原型返修或能力矩阵重新评级
  - FEA-11 scan/diff/relink/resync 状态机
  - FEA-12 删除、回收站、GC 与 G-DELETE-IMPL
  - FEA-13 完整备份、恢复、迁移产品流程
  - 未经 UNFREEZE 的冻结契约字节修改
  - requirements、packaging 和新增 NuGet/Python 依赖
  - UI 视觉重设计及未另行冻结的 UI 接线
  - push
```

应删除当前笼统“生产 Schema DDL out_of_scope”；改为“**只允许实施前置存储契约已冻结的精确 DDL**”。若继续排除全部生产 DDL，FEA-09 必须降为非生产准备任务，不能保留当前生产交付标题与 AC。

### 5.4 AC 定稿建议

保留 AC-1…AC-8，新增 AC-9/10，避免授权与缓存要求埋在散文中。以下全部为 **planned / NOT_RUN**。

| AC | 建议定稿 |
|---|---|
| AC-1 格式矩阵 | 单图、文件夹、ZIP、CBZ、PDF 各有成功、typed unsupported、损坏/空内容 fixture；登记 decoder、fixture SHA、错误类别、支持限制和无副作用断言。AES ZIP 明确 unsupported，不计解密成功。 |
| AC-2 顺序 | PDF 按数值页码；文件夹按授权范围内相对路径及文件名自然数字排序；覆盖 1/2/10/100、嵌套目录、同排序键及稳定 tie-break。 |
| AC-3 occurrence | 重复名、重复同图保留独立 entry/occurrence/binding；按 occurrence 保序；默认已引用源跳过与显式继续引用区分。两个项目共享源时，阅读进度、人工修改、处理结果分别独立。 |
| AC-4 密码与错误 | 支持的加密子格式覆盖无密、错密、重试成功、跳过；密码只经短期安全引用，不进入普通 task、snapshot、Registry、receipt、异常、wire/evidence 日志及其可逆编码；AES ZIP typed unsupported。 |
| AC-5 取消与进度 | 冻结文件/容器/页/项目计数和提交单元；取消后已提交保留、未提交不可见；覆盖提交前后、丢 ACK、异常及重启；Host 可观察当前项目进度及成功/失败/跳过/待处理汇总，重试不重复提交。 |
| AC-6 隔离链路与源守恒 | 各必需行为具有隔离 Core→Host→UI 结果证据；真实 IPC 使用生产 adapter。源 hash/mtime 不变；既有 managed/derived 不删除；无新增永久全尺寸输入副本。UI 接线缺失项不得以进程内测试代替。 |
| AC-7 完整性、升级与回退 | 明列 `existing_source_hashes`、`max_source_order`、`get_page`、`list_pages`、`handle_resolve_page_resource`，另测 reader projection。referenced complete 可见可解析；各半写/断 binding 负例不可见且可恢复；旧 managed 页 ID/顺序/计数/资源/人工数据/Lock 守恒。缺文件、磁盘满、中断不切入口；旧端拒写新 Schema。关闭引用导入后新导入被拒，既有双读保持。 |
| AC-8 证据与交付 | build 0 warning/0 error；.NET 基准 1292/0/57 总数1349，新增测试与变化单列，skip 逐项解释；另跑 Python 相关回归。check/vpins、四 PNG、范围 diff、独立 Review、DSH 集成验证；EV 逐文件登记，不 push。 |
| AC-9 授权与 lease | Registry 重启持久化、generation、撤销、根替换、跨根/reparse、错误 scope/version/entry/rendition、过期、Host 失联均有正负测；失败拒绝新读及提交；旧一次性 grant 不升级。读取采用 strict lease、同一验证流；commit 前有效授权及强校验。 |
| AC-10 cache 与预算 | key 包含 SourceVersion/entry/decoder/version/参数；content identity 与 rendition observation 分离。每请求预算、总字节上限、并发解码上限强制生效；LRU/同时间大文件优先、活跃引用保护、损坏缓存重建、崩溃恢复有负测。缓存不含唯一人工/结果/恢复数据，不写源目录；源读取与 derived 通道隔离。 |

补充要求：

- plan 冻结目标、类型、顺序、源版本及必要授权代；确认前源变化必须拒绝或更新预览。
- ZIP/CBZ 覆盖路径穿越、绝对路径、重复成员、编码、解压炸弹和预算超限；不把成员名直接用作可写路径。
- 文件夹扫描忽略隐藏/系统文件，递归不越授权根、不跟随越根 reparse。
- GIF 首帧、PDF 页码及渲染参数显式断言。
- v3 AC 行末使用合法标记。当前草案可用 `<<BLOCKED: 范围及前置存储契约未冻结>>`；实现后按真实结果更新，不提前标 MET。
- 测试命令、环境、结果和证据另成表；尚未实现的测试命令标 planned。

### 5.5 前置 Gate、契约与依赖动作

按以下顺序处理：

1. **Source 存储契约前置**：DSH 建立并登记实际 Task，冻结 DDL、迁移版本、完整性/可见性衔接、Host/Core 跨存储发布恢复次序；独立复核。
2. **协议补充**：冻结新增 source-read wire、`scope.entry` 与 EntryId 对齐、plan/receipt/取消/密码安全引用及兼容拒绝。保留旧 `ImportPages` 语义，不暗改冻结字节。
3. **UI 接线切片**：ZCode 承担最小接线；先冻结接口，明确实现/集成顺序及 FEA-09 的 UI 收口依赖。
4. **AES 能力处置**：登记本轮 unsupported，或另开生产依赖/许可/打包决策；不得以测试依赖偷换。
5. 补齐 FEA-09 allowed_paths、v3 AC、验证计划、Canonical Evidence、Resource Manifest、base/owner/reviewer。
6. 同步 Plan 当前 DAG 和 STATUS，由 DSH 再决定 ready。

现有 `depends_on: [FEA-08, FEA-01-FREEZE-1]` 的两个完成前置可以保留，但**不足以释放当前生产范围**。新增前置须使用真实存在且已登记的 Task ID，本报告不臆造已释放节点。

建议实现验证命令包括：

```powershell
dotnet build apps\desktop-avalonia\NewManga.sln --nologo
dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo
pwsh -NoProfile -File tools\governance\check.ps1 -TaskPath doc/tasks/FEA-09.md
pwsh -NoProfile -File tools\governance\verify_pins.ps1
```

Python targeted suite、真实 IPC、新故障测试和 headless UI 测试须由冻结 Task 列出精确 planned 命令。运行时使用外置 task-env、temp、证据输出目录；日志包含 command、shell/venv、cwd、head、EXIT 和逐条 skip。

EV 使用 `verification/FEA-09/**`，每个判别力文件独立登记；仓库文件 pin 含该文件的 commit 及明确字节口径，仓外输入 pin SHA-256。不得复用 FEA-08 的 EV 总数、pin 自例外或 LF 配置作为本 Task 自动授权。

### 5.6 Owner / Reviewer 建议

- 存储契约、共享 seam、协议裁决与集成：**DSH**。
- FEA-09 Core/Host 实现：由 DSH 指派**另一个未参与本次审查的 Codex 会话/实例**；本 reviewer 不参与实现或返修。
- 最小 UI 接线：**ZCode**，独立冻结 Task。
- 实现 Review：由 DSH Appointment 指定未参与实现/返修的独立上下文；可再次由本 reviewer 只读审查。

## 6. 结论与推荐下一步

**当前不可 `proposed → ready/in_progress`。** 保持 `proposed`，由 DSH 先处置 P1、冻结并复核存储/协议前置、确定 UI 接线和 AES 能力边界，再提交新字节的 scope 复审。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga`、`main`、本次审查 head `6e274dd94c5b64d8fbc3f9d578363d3c502a2b68` 基础上，先确认当前 HEAD/dirty 状态，处置 FEA-09 scope-r1 的 R1-001…R1-013。此轮仅进行文档裁决和前置 Task 冻结：补齐 Source DDL/迁移与发布恢复契约、保留 C-06 Host 私有 Registry 归属、冻结新增协议及密码安全路径、登记 AES unsupported 或提交产品依赖决策、为 ZCode 建立最小 UI 接线切片，并修订 FEA-09 写域、AC、验证和证据表。禁止实施生产代码、改写冻结历史字节、触碰用户数据或 push。前置 Task ID/路径须实际登记，恢复点及工作树由 DSH 固定，不臆造。交付 findings disposition、修订 Task、契约及依赖记录，运行只读 check/vpins，并交独立上下文复审；通过前保持 FEA-09 proposed。