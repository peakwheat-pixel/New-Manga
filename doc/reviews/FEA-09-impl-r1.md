# FEA-09 独立实现 Review r1

## 0. 元信息

| 项目 | 记录 |
|---|---|
| Reviewer | Codex，当前独立会话 `/root` |
| 模型 | GPT-6 系列 Codex；未取得可核验的精确模型 ID |
| 独立性 | 本会话未参与 FEA-09 实现、scope-r2 或契约复核；不参与后续返修 |
| 辅助审查来源 | 独立上下文子任务 `/root/standards`、`/root/spec`；均只读，未参与实现 |
| 时间 | 2026-11-03；结束核验时间 22:07，Asia/Shanghai |
| 仓库／分支 | `G:\CODEX\New Manga`／`main` |
| Git common directory | `G:\CODEX\New Manga\.git` |
| reviewed_head | `6a164253d1fa9ad801036d150c9bc981964689ca` |
| 指定 diff 基线 | `f9a2fa8e077f21c93131237171a32e85f6942200` |
| 审查后 HEAD | 与 reviewed_head 相同 |
| 审查前后 status | 完全相同：`main`，16 个既有 tracked 文件显示 `D`，详见下表 |

**基线说明**：`d3d7cd564`、`ceae03edb` 均已是 `f9a2fa8e0` 的祖先。因此，指定基线实际已经包含 Phase A/B，不能称为全部 FEA-09 实施前基线。本轮仍读取、抽查了 Phase A/B 代码、提交及测试，没有仅依赖指定 diff 排除它们。

审查前后 Git 显示的 16 个 `D` 均位于：

`verification/FEA-09/native-registry/<目录>/isolated-data/host/source-access/`

每个目录下均包含下列四项：

| 目录 | quarantine 文件 | corrupt 文件 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `quarantine/78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `registry.v1.dat.corrupt-202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `quarantine/fae26d327bb4463d940427d17881f9ae.dat` | `registry.v1.dat.corrupt-202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `quarantine/2953b0220e7c424194e26d207017e793.dat` | `registry.v1.dat.corrupt-202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `quarantine/189d4ab58a1c4194a5d9862b6701e88a.dat` | `registry.v1.dat.corrupt-202611031354042159987` |

另外两项为各目录中的 `registry.v1.dat`、`registry.v1.lock`。Git 同时输出四个 `host/` 目录无法打开的 warning。本轮不据此推断删除原因，也未恢复、清理这些文件。

执行通路：常规 shell 在创建进程时返回 Windows error 740；随后通过 Node `child_process.spawnSync`、文件只读 API 和内存 SHA-256 计算完成检查，未申请提权。

**未修改声明**：未修改仓库、冻结契约、Git 配置或用户数据；未创建报告、测试文件、数据库或证据文件；SQLite 探针全部使用 `:memory:`，Python 使用 `-B`；未执行 add/commit/push。报告仅通过本次输出交付。

## 1. Verdict

**`changes_requested` — P0=0／P1=8／P2=3。**

当前不能进入 DSH 最终集成通过阶段，Task 不能置 `done`。

已有真实 IPC 与生产 V2 command adapter 的单图成功证据，前置冻结链未回退。但本轮确认了可见性谓词错误、授权 scope 校验缺失、部分导入恢复失败、加密源链路不完整及生产缓存约束未接线等问题。

**AC-1…AC-10 本轮均不能升为 MET。** 原有 PARTIAL 标记应保留；环境受限的独立复跑另记 BLOCKED／NOT_RUN，不能转成产品 PASS。

## 2. AC 逐条判定表

下表中的既有测试数字属于作者／DSH 记录；本 Reviewer 的实际执行结果单列在第 5 节。

| AC | 判定 | 已有依据与实际缺口 |
|---|---|---|
| AC-1 格式矩阵 | **PARTIAL** | scanner 有 21 项测试；存在四份预生成 fixture 及 SHA 表，AES fixture 明确为 method 99 typed unsupported。尚无五类输入逐项成功／unsupported／损坏／空内容完整登记；加密 PDF 导入存在实际失败，见 R1-I004。不能用 scanner 成功替代 decoder／生产链路成功。 |
| AC-2 顺序 | **PARTIAL** | 自然序、重复成员及 PDF ordinal 代码和测试存在；完整的文件夹 `1/2/10/100`、嵌套、同键稳定 tie-break 判别矩阵未闭合。 |
| AC-3 occurrence／共享 | **PARTIAL** | 重复归档成员保留 occurrence；跨项目共享测试验证 source 行共享、binding 独立。阅读进度、人工修改和处理结果独立性仍缺实际回归。 |
| AC-4 密码 | **PARTIAL** | 十项密码测试包含 Windows DPAPI helper、ZipCrypto 错密重试和 secret 删除；测试主要使用 fake access。未覆盖真实 Host→Core 加密输入→resolve；加密 PDF 导入和加密源读取均有缺陷。现有审计文件明确不代表真实 IPC／Host 日志完整审计。 |
| AC-5 plan／receipt／取消 | **PARTIAL** | accepted／running、取消、重放、busy、跨重启 receipt 不存在及自然键测试存在。默认策略下部分容器重试丢失剩余页，已复现；项目／策略确认未冻结；后台异常丢失 typed 原因。 |
| AC-6 真实 IPC／V2／源守恒 | **PARTIAL** | `Fea09RealIpcTests` 实际构造 Python source 子进程及生产 CoreServiceClient、Registry、Coordinator；新增 dispatcher 也为真实生产 command adapter。现有 JSON 与 wire 的 17 frames 一致。仅覆盖单图成功路径；folder、密码、撤销、失败／取消等未形成完整 IPC 矩阵，源 mtime／旧资源守恒也未完整断言。新增 UI 仍归 UI-1。 |
| AC-7 迁移／双读／回退 | **PARTIAL** | v7 DDL 与 C-15 SQL 去除外围空白、归一行尾后逐字一致；迁移失败回滚、旧写者拒写，本轮内存复跑成功。生产 managed 可见性却没有使用冻结的 `V_artifact`；迁移验证 SQL 与真实 repository 查询分离，现有测试未发现该问题。磁盘满／启动切入口等故障验证仍缺。 |
| AC-8 交付证据 | **PARTIAL** | 本轮 check PASS、pins 17/17、四 PNG 不变。DSH 记录 build 0/0、.NET 1298/0/58、pytest 100；本轮未独立复现这些数字。EV 仍有大量 PENDING、重复 ID、过期 hash 和未登记文件；资源收口、最终集成未完成。 |
| AC-9 Registry／授权／lease | **PARTIAL** | Registry 持久化、generation、撤销代码及组件测试存在；strict lease 在同一句柄上验证身份、尺寸与 digest。生产 resolve 未校验完整四维 scope；folder 首次导入的授权回退不可用；原生 reparse／ACK／EOF 竞态矩阵未闭合。 |
| AC-10 cache／预算 | **PARTIAL** | 独立 RenditionCache 组件确有预算、LRU、活跃引用、并发排队和恢复逻辑，组件测试存在；生产 resolve 未使用该组件。生产路径还存在解码后检查预算、错误缓存前缀及只检查文件存在的问题。 |

## 3. 安全与边界核验

| 项目 | 核验结果 |
|---|---|
| 前置状态 | PREREQ-1 仍为 `done`，integration/delivery 指向 `24c10567926fb302d9bac6ba63ae92d673cf9e83`；该提交是 HEAD 祖先。r7 为 approved。 |
| 冻结字节 | `git diff 24c105679..HEAD -- doc/plan/FEA-CONTRACT-FROZEN-* doc/plan/FEA-C*` 为空。C-05 v1.1／C-06 v1.1／C-15 v1.0／C-16 v1.0 未回退；17/17 pin PASS。 |
| 写域 | 指定范围共 278 个变更路径；生产源码、测试、FEA-09 文档／证据位于 Task 写域。STATUS／PLAN／rolling checkpoint 属 DSH 治理更新，单独识别，未当成普通 Owner 写域。 |
| 依赖／打包 | 未发现 requirements、NuGet／csproj 或 packaging 改动。 |
| UI／共享组合根 | 未发现 Views／ViewModels、axaml、App 组合根或 sln 改动；未新增 C-07 接口面。 |
| 原始字节发布 | referenced 路径调用解码／重新编码 PNG；未发现把 raw user-source 直接发布的生产分支。但预算与缓存有效性仍不合格。 |
| 源文件／真实数据 | 已读代码未见新增原文件写删／回收站流程；测试使用合成输入。本轮没有操作真实用户数据、外部卷、生产 AppData 或回收站。 |
| push | 本会话未 push。提交内容及本地状态不能证明其他历史会话从未 push，因此不作该扩大声明。 |

冻结字节通过只证明未擅改契约，**不证明实现符合契约**。

## 4. 实现正确性抽查

### 4.1 Standards 轴

独立子任务 `/root/standards` 提出三项 P1，本报告分别登记为：

- R1-I002：生产 resolve 未验证四维 scope。
- R1-I006：folder 首次导入后的 grant 回退不可用。
- R1-I007：预算在昂贵解码之后检查。

未将纯风格 smell 作为阻塞 finding。

### 4.2 Spec 轴

独立子任务 `/root/spec` 确认部分重试、加密 PDF、加密 resolve、生产 cache、预算和计划确认六项问题；预算与 Standards 轴重复，只计一次。

主 Reviewer 另确认生产 `V_artifact` 偏离、后台 typed 错误丢失及 EV 收口问题。以下为实际反例。

### 4.3 纯内存反例及正向检查

所有探针使用真实 scanner／planner／runtime／repository，输入和 DB 均在内存；grant、密码或 decoder 接缝按场景注入。**它们不是原生文件／DPAPI／IPC PASS。**

| 探针 | 实际结果 |
|---|---|
| 3 页 ZIP，提交第 1 页后请求取消，再默认 `skip` 重试 | 首次 `cancelled`：imported=1、pending=2；重试 `completed`：imported=0、skipped_sources=1、pending=0；DB 仍只有 **1 页**。 |
| 加密 PDF，预览不可知页数，正确密码后暴露 2 页 | plan=`encrypted`；最终 `failed`，reason=`SOURCE_PLAN_STALE`；DB **0 页**。PDF inspector 为注入接缝。 |
| managed artifact-only 页与无 artifact 的完整导入列页 | 冻结 SQL `V_artifact` 返回 `artifact-only`；实际 `get_page(artifact-only)` 为 None，实际 list 返回 `no-artifact`，两者方向均错误。 |
| v7 尾部注入失败 SQL | 保持 schema **v6**，`sources` 表不存在；回滚成立。 |
| v7 库交给仅认识 v1–v6 的 runner | 抛出 **SchemaTooNewError**。 |
| page-unit 提交时注入错误项目 | pages／sources／bindings 均回滚为 **0**；但 receipt reason 为 **null**，typed 原因丢失。 |
| plan 后把 chapter 改属另一 book，同时把策略从 skip 改为 import_as_new | start 仍 accepted，最终 completed，binding 写入新 book；没有 SOURCE_PLAN_STALE。 |

`SOURCE_PROJECT_MISMATCH` 的**同事务关系守卫存在且回滚有效**；问题是后台工作层未把该异常转换为冻结的失败原因。

`V_ref` 的完整性／healthy binding／digest 关联存在，父级删除亦有查询条件；但 get/list 未落实注释声称的时间条件，managed 分支尤其没有 artifact/revision 判定。迁移 callback 对另一份 SQL 的守恒检查，不能替代真实读路径验收。

## 5. 独立复跑结果

| 实际命令／检查 | EXIT／结果 | 到达程度 |
|---|---|---|
| 常规 `exec_command` 读取技能文件 | 进程创建失败：Windows error 740 | 随后改用 Node，未提权 |
| `git rev-parse HEAD --show-toplevel --git-common-dir` | 0；HEAD／根目录／common dir 匹配 | 已运行 |
| `git status --porcelain=v1 --branch`，审查前后 | 0；输出完全相同 | 已运行 |
| `git diff --name-only f9a2fa8e0..HEAD` | 0；278 路径 | 已对照写域 |
| `git log --oneline f9a2fa8e0..HEAD`、指定 commits 的 show/stat | 0 | 已核对阶段内容 |
| `git merge-base --is-ancestor 24c105679 HEAD` | 0 | 前置未回退 |
| `git merge-base --is-ancestor d3d7cd564 f9a2fa8e0`；对 ceae03edb 同查 | 均 0 | 指定基线已含 A/B |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **0；PASS，3 warnings** | 当前 Task 指向 FEA-09 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **0；PASS all 17** | 已运行 |
| `C:/Python314/python.exe -B -m pytest tests/fea09 -q -p no:cacheprovider` | **1；No module named pytest** | suite 未启动 |
| Python `-B -c` 七项纯内存探针 | **0**；结果见第 4 节 | 不等同 pytest suite |
| `dotnet --version` | **0；10.0.401** | SDK 可启动 |
| `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | **NOT_RUN** | 当前环境只读；build 会写产物 |
| .NET 全量／Host.Tests／CoreClient.Tests | **NOT_RUN** | 未声称独立通过 |
| `NEWMANGA_FEA09_IPC=1 NEWMANGA_BUILD_PYTHON=… dotnet test … --filter Fea09RealIpcTests` | **NOT_RUN** | 会写隔离数据，且测试直接覆盖仓库 IPC 证据，不符合本轮只读约束 |
| 四 PNG 与 `b26840acd` blob 原字节 SHA 比较 | **4/4 相同** | Node 内存计算 |
| EV 逐行文件／SHA／commit 检查 | 已运行 | 结果见第 7 节 |

三项治理 warning 涉非终态 Task 数量及 STATUS／PLAN 体量预算。

四 PNG SHA-256：

| 文件 | SHA-256 |
|---|---|
| reader.png | `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2` |
| settings.png | `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162` |
| shelf.png | `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a` |
| workbench.png | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` |

DSH 既有记录为 build 0/0、pytest 100、.NET 1298 passed／0 failed／58 skipped；默认新增的真实 IPC 测试贡献一个 skip。其余 skip 的逐项原因没有在本报告中独立重跑确认，不能据此完成 AC-8。

## 6. Findings 表

路径均相对仓库根目录。

| ID | 级别 | 位置 | 问题与最小修复 |
|---|---|---|---|
| **R1-I001** | **P1** | `src/infrastructure/sqlite/library.py:355`、`:95`、`:426`；`tests/fea09/test_read_paths.py:158` | **生产 managed 可见性不符合冻结 V_artifact。** 查询仍要求导入列，mapper 再拒绝 NULL managed ref；valid artifact-only 旧页不可见，无 valid artifact 的完整导入列页却可见。现有“artifact-only”测试实际创建完整导入列、无 artifact，固化了错误判据。最小修复：让 get/list／projection 使用冻结模式分派及时间条件，支持 artifact-only 投影／资源解析；迁移验证调用真实生产读路径，补双向反例。依据 C-05 §3.1、C-15 §1／§4。 |
| **R1-I002** | **P1** | `src/application/importing/referenced/resolve.py:72`；`src/infrastructure/resource_channel/source_read_refs.py:301`、`:345`、`:374` | **grant 选择没有验证四维 scope 与绑定身份。** source 匹配只看 source_id，物理回退只看容器 digest／volume／file ID；生产路径没有调用 verify_scope。同 source_id、错误 version／entry／rendition，甚至指向另一物理文件的有效 grant 可被选中。最小修复：按 binding 的 accepted version、entry、所需 rendition 和物理身份严格匹配；首次导入也须完成受限授权映射，不能用身份回退代替 scope。补生产 resolve 负测。 |
| **R1-I003** | **P1** | `src/application/importing/referenced/planner.py:172`；`runtime.py:375` | **部分导入后的默认重试整源跳过剩余页。** 任一 binding 即令 already_referenced=true，默认 skip 随后直接整源返回。本轮 1/3 页取消后重试，库仍为 1 页而报告 completed。最小修复：区分全部／部分已绑定；部分场景逐 entry 跳过并补齐未提交页，保持冻结计数公式。补真实“部分已引用”测试；现有测试先完整导入 8/8，不能证明该场景。 |
| **R1-I004** | **P1** | `src/application/importing/referenced/scanner.py:393`；`runtime.py:458` | **加密 PDF 正确密码仍无法导入。** 预览 entries 为空，解密 rescan 有页后仍要求每页存在于旧 plan pages，第一页即 SOURCE_PLAN_STALE。最小修复：容器和授权确认成功后，为有限预览建立解密后的参与页及计数；增加真实加密 PDF 无密／错密／重试成功测试。 |
| **R1-I005** | **P1** | `src/application/importing/referenced/resolve.py:105`；`reader.py:46`、`:106` | **已导入加密源不能生产读取。** resolve 不获取／传递密码；ZipCrypto 使用 pwd=None，PDF raster.open 也不接收密码。最小修复：补符合短期 secret 契约的读取密码流程及 raster 接口适配，覆盖加密源 import→resolve，不能持久保存口令或复用已销毁 secret。 |
| **R1-I006** | **P1** | `src/infrastructure/resource_channel/source_read_refs.py:323`；`src/application/importing/referenced/runtime.py:432` | **folder 首次导入后的 grant 回退不可用。** Core 新分配 src-*，与预先铸造 grant 的 source_id 不同；identity 回退只接受非空 container_facts，folder 恰为空。现有真实 IPC 只测 image。最小修复：建立 folder 导入后受四维 scope 约束的映射／重授予流程，补 folder import→resolve；不得放宽成路径回退。 |
| **R1-I007** | **P1** | `src/application/importing/referenced/reader.py:106`、`:117`、`:130`；`runtime.py:611` | **解码预算在内存消耗之后检查。** PDF render、图片 load／转换／PNG 编码完成后才比较尺寸；导入 probe 也直接进入 decoder。小预算无法阻止大图先耗尽内存。最小修复：在解码／渲染分配前检查尺寸、scale 和预算，约束归档成员解压，并接入生产并发上限；负测应证明超限未调用昂贵解码。 |
| **R1-I008** | **P1** | `src/bootstrap/core_service.py:3410`、`:3419`、`:3518`；`src/infrastructure/sqlite/library.py:1616`；`tests/fea09/test_referenced_resolve.py:184` | **生产缓存绕过冻结强约束。** 每次先完整解码，再仅按 page_id／文件存在命中；未使用 RenditionCache 总预算、LRU、并发、活跃引用及崩溃校验。metadata 写入 pages/ 前缀，违反 source-renditions/ 要求；decoder／参数 key 变化仍可返回旧文件，损坏文件未重建。最小修复：将真实发布／命中流程接入受控缓存，以内容 key 和 digest／尺寸校验；修正错误前缀测试。 |
| **R1-I009** | **P2** | `src/application/importing/referenced/planner.py:45`；`runtime.py:198` | **确认未绑定原项目和 duplicate_policy。** PlanRecord 不保存原 book，start 不比较原策略；本轮修改 book＋策略后仍 accepted／completed。最小修复：计划保存并在确认时核对项目、策略及相关冻结事实，变化返回 SOURCE_PLAN_STALE。 |
| **R1-I010** | **P2** | `src/application/importing/referenced/runtime.py:350`；`:528`；`tests/fea09/test_referenced_flow.py:607` | **后台异常使 receipt 丢失原因和失败计数。** SourceProjectMismatch 等非 SourceImportError 落入外层 broad except，仅置 operation failed；本轮项目守卫回滚后 reason=null。最小修复：把已知存储错误转换为冻结 typed 原因，设置对应 item outcome／failed_sources，保留 pending 数量；测试断言 reason_code 与计数。 |
| **R1-I011** | **P2** | `verification/FEA-09/EV.md:3`、`:93`、`:96`、`:100` | **EV 不是可关闭的最终证据链。** 仍声称未提交旧 HEAD，90 行 PENDING，EV-090／091 重号，EV-087 hash 过期，当前 AC matrix 未被当前 pin 覆盖，另有大量未登记文件。最小修复：保留历史证据原字节，建立唯一 ID 的最终逐文件清单；明确 current／historical 字节口径，补 commit pin，核实 16 个既有 D，完成资源处置与 DSH 集成记录。 |

## 7. 证据链核验

### 7.1 EV 登记

实际读取到：

- **97 条数字 EV 行**，其中 **90 条仍为 PENDING**。
- **EV-090、EV-091 各使用两次**。
- 已登记数字 EV 路径本轮均可读取。
- FEA-09 下共有 **240 个 tracked 路径**；计入 EV 自引用后，仍有 **142 个路径未被清单列出**，主要为重复组件产物、Registry 文件，以及 `logs/dsh-integration.md`。

具体不一致：

| 项目 | 实际核验 |
|---|---|
| EV-087 `wire-redacted.ndjson` | 登记 834 bytes；当前为 **3336 bytes**，SHA 为 `cd1ea68a824784626bb32564e5b50e93281e8f28562a394fc0bddb0c240084ff`，不匹配登记值。 |
| EV-091 AC-MATRIX | pin 指向 `3d308f449…` 的旧 matrix；该 blob hash 匹配，但当前文件已更新为 **4302 bytes**。旧 pin 不能证明当前 matrix 内容。 |
| EV-090 resolve log | 当前工作树及所 pin blob 的 SHA 均匹配。 |
| EV-092 sharing log | 工作树 SHA 匹配；blob 与工作树存在换行口径差异。 |
| EV-093…095 IPC 文件 | 当前工作树 SHA 均匹配登记；对应 commit 含文件，工作树／blob 换行口径有差异，不能混称同一原始字节。 |

旧 pin 本身不因历史性而无效；问题在于当前清单没有清楚区分历史快照与最终被验收内容。

### 7.2 IPC 真实性与复现性

`Fea09RealIpcTests.cs` 没有使用 fake controller：

- 启动参数显式导入仓库 `src/bootstrap/core_service.py`。
- 使用真实 stdio、CoreServiceClient、SourceAccessRegistry、SourceReadCoordinator。
- V2 路径使用 `HostCommandDispatcher → CoreServiceClient`。
- JSON 中的 17 项命令序列与 wire 文件相符，包含两次 resolve。

因此，现有材料支持“**真实单图 IPC／生产 command adapter 曾运行**”，不能扩展成“五格式、密码、取消、撤销和失败矩阵均通过”。

测试依赖调用方提供真实 Python 解释器；代码没有固定解释器身份或运行代码 head 指纹。本轮没有证据表明使用了 fake，但也不能宣称该证据具备防伪执行证明。

此外，测试每次直接写入：

- `verification/FEA-09/ipc/fea09-real-ipc.json`
- `verification/FEA-09/ipc/fea09-real-ipc.wire.ndjson`

复跑会覆盖已 pin 文件，故本轮未执行。后续应让执行产物进入 workspace，再由 DSH 显式归档。

### 7.3 commit 内容与描述

指定八个实现 commit 均存在，其主要内容与 message 的阶段描述对应。

不过：

- `3f205655` 的“解码预算强制”目前是解码后拒绝，不足以证明内存预算受到保护。
- `081cb2c3` 的物理身份回退确已实现，但存在 scope 和 folder 缺口。
- `ab3f3131` 确实加入生产 dispatcher 测试，不能因仍缺 UI-1 而否认这一增量，也不能据此提升整个 AC-6 为 MET。

## 8. 结论与推荐下一步

**必须返修。当前不得将 FEA-09 标为 done，也不能据本报告进入最终集成通过。**

推荐下一步由 **DSH** 归档并裁决 findings，再交原实现会话返修；本 Reviewer 及两个审查子任务不参与修改。修复后安排新上下文复审，最终集成仍由 DSH 执行。

可直接转发：

> DSH：请原字节归档本报告为 `doc/reviews/FEA-09-impl-r1.md`，以 reviewed_head=`6a164253d1fa9ad801036d150c9bc981964689ca` 登记 changes_requested（P0=0/P1=8/P2=3）。先核实并保留审查前已有的16个 Registry D 状态，逐项处置 R1-I001…011；将返修交原实现 Agent，会话不得包含本 Reviewer 或 `/root/standards`、`/root/spec`。优先修复生产 V_artifact、四维授权、部分导入恢复、加密源和生产缓存约束；补针对反例的测试。保持冻结契约、依赖、UI、共享组合根及真实用户数据边界，不重开 FEA-08，不 push。测试产物置 workspace，最终证据由 DSH 单点归档，补齐 EV／资源收口。交付固定修复 head、逐项 disposition、实际 build／Python／.NET／真实 IPC／check／17-pin 结果后，再委派新上下文复审；全部 AC 继续按实际结果保留 PARTIAL，未通过最终集成前不得 done。