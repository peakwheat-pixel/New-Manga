# FEA-09 Scope Review r2

## 0. 元信息

| 项目 | 实际记录 |
|---|---|
| Reviewer | Codex，用户直接指派的独立审查会话 `/root` |
| reviewer_kind | `agent` |
| 模型 | GPT-6 系列 Codex；当前环境未提供可核实的精确模型 ID |
| 独立性 | 未参与 FEA-09 范围起草、scope-r1 处置、契约起草或 r1–r7 契约复核；本会话不参与 FEA-09 实现或返修 |
| 时间 | 2026-11-03 17:46:36–17:51:07，Asia/Shanghai |
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` |
| Git common directory | `.git`，即 `G:\CODEX\New Manga\.git` |
| reviewed_head | `19e6210047e664d1206347bd5259a6f075a9c028` |
| 被审 Task | `doc/tasks/FEA-09.md`，`proposed` |
| Task `git hash-object` | `aed4e21cd1f6d66981ef1109ce40c303cc7bee1b` |
| Task 工作树 SHA-256 | `965e52dae02973a19784639c22c361714f97cc8d210ad423b9cc616ba04e2738` |
| 审查前后 status | `git --no-optional-locks status --porcelain=v1` 均为空 |
| 结束复核 | HEAD、Task 两种指纹不变；`git diff --name-only` 为空 |

实际执行包括：

```text
git --no-optional-locks status --porcelain=v1
git branch --show-current
git rev-parse HEAD --git-common-dir
git hash-object doc/tasks/FEA-09.md
git merge-base --is-ancestor 24c10567926fb302d9bac6ba63ae92d673cf9e83 HEAD
git diff 220979ba81f37e857f241049535caef7246c97b1 HEAD -- <四份冻结契约>
git cat-file blob <commit>:<证据或PNG路径>
git diff --name-only
rg --files <指定代码目录>
rg -n <定向符号与调用点> <指定路径>
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-09.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```

常规 `exec_command` 两次在进程创建阶段返回 Windows error 740；随后通过 Node 文件读取 API 和 `child_process.execFile` 完成只读检查，未提权。SHA-256 在内存中计算。

**未修改声明：未修改仓库、冻结字节、Git 配置或用户数据；未执行 add/commit/push；未创建报告、测试库或证据文件。报告仅通过本次输出交付。**

## 1. Verdict

**`approved`**

本轮 **P0=0 / P1=0 / P2=2**。

前置存储与协议契约已经冻结并集成，当前写域能够承载 FEA-09 的 Core/Host 实现；UI、删除、备份、依赖和共享组合根边界明确。剩余两项属于验收文字与验证计划精度，由 DSH 在置 `ready` 前收尾，不需要重新裁决契约语义。

本批准仅为 **scope 批准**，不表示 FEA-09 已实现、AC 已通过或当前已获实施授权。

## 2. scope-r1 findings 闭环表

以下状态指范围问题闭环，不代表运行时能力 PASS。`Task` 均指当前 `doc/tasks/FEA-09.md`。

| ID | 状态 | 实际依据 |
|---|---|---|
| R1-001 | **FIXED** | Task `:12–14/:114/:124/:148` 登记硬前置及精确 DDL 边界；PREREQ-1 `:6/:17` 为 done/已集成；C-15 `:33–48` 冻结 v7、失败停留与预留表。 |
| R1-002 | **FIXED** | Task `:106/:116` 固定 Host 私有存储；C-15 `:280–302` 冻结位置、格式、DPAPI、逐根身份、锁、恢复与备份交接。 |
| R1-003 | **FIXED** | Task `:109/:115` 明确新增 `referenced/`，保留已有 images/documents；真实 managed 创建点仍在两包 service 中。 |
| R1-004 | **FIXED** | Task `:28–56` 已覆盖 Page、decoder、迁移、repository、Core 组装/dispatch、Host/CoreClient 和 Python/.NET 测试；协议载体由已冻结 C-16 承担。 |
| R1-005 | **FIXED** | Task `:72/:107/:125/:137` 保留真实 IPC、现有 V2 production adapter，并明确新增 UI 操作由 UI-1 承担；不宣称完整 UI 验收。 |
| R1-006 | **FIXED** | Task AC-9 `:140`；C-06 `:42/:69–70`、C-15 `:306–313`、C-16 `:65–69/:153` 给出撤销、失联与提交边界。 |
| R1-007 | **FIXED** | Task AC-7 `:138` 明列五读路径和 reader projection；C-15 `:35–44/:237–275` 给出双集合守恒、资源校验及 managed 写入维护。AC 简写精度见 R2S-001。 |
| R1-008 | **FIXED** | Task AC-10 `:141`；C-14 `:157–189`、C-15 `:172–201/:267` 覆盖预算、淘汰、活跃引用、崩溃校验与通道隔离。 |
| R1-009 | **FIXED** | C-16 已冻结，`:73–118` 定义密码引用、异步导入、plan/receipt/取消/重试；`:145–154` 定义日志前置脱敏及失联拒绝。 |
| R1-010 | **FIXED** | Task `:105/:119/:132/:135` 明确 AES typed unsupported、不新增依赖；C-16 `:78` 使用 `SOURCE_FORMAT_UNSUPPORTED`。 |
| R1-011 | **FIXED** | C-16 `:92–110` 冻结一页事务、状态全集、同名六计数字段、聚合公式及六类示例；Task AC-5 承担实施。 |
| R1-012 | **PARTIAL** | Task `:132–141/:157–187` 已补 v3 标记、planned 表、逐文件 EV 政策和 Manifest；Python/IPC/故障验证的精确 planned 命令仍留待实施时登记，见 R2S-002。 |
| R1-013 | **FIXED** | PLAN `:36–39` 当前 DAG 已改为 PREREQ-1 done→FEA-09 proposed，旧 residual 不再被列作当前进行中任务；STATUS `:7–10` 一致。 |

未发现 `NOT_FIXED` 项。

## 3. 范围／写域核验

### 3.1 逐目录核验

| 写域 | 核验结论 |
|---|---|
| `src/infrastructure/sqlite/{schema,migrator,library}.py` | 覆盖精确 v7 DDL、验证回调、投影、mapper、读写谓词与事务提交。当前 schema 仍只有 v1–v6，不能把契约冻结当成迁移已实现。 |
| `src/domain/pages/entities.py` | 必需且已授权。当前 `:28/:43–44` 强制 managed ref，referenced 模式必须受控扩展。 |
| `src/application/importing/referenced/**` | 可承载 plan、异步 operation、receipt、取消、密码引用、逐页提交及自然键重试。 |
| `images/**`、`documents/**`、`src/infrastructure/importing.py` | 覆盖旧 managed 写入完整性维护和支持子格式的密码解码。旧 `PdfiumDocumentRaster.open` 当前没有密码参数，不能宣称解密已具备。 |
| `application/resource_channel/**`、`infrastructure/resource_channel/**` | 覆盖新授权读取、strict lease、预算与 rendition/cache；不能据此引入导入业务编排或 FEA-11 状态机。 |
| `src/bootstrap/{core_assembly,core_service}.py` | 覆盖装配、能力声明、host-control allowlist、后台工作、EOF 废止、五读入口及 reader projection。当前 stdio 同步 dispatch，须按 C-16 实现立即接受后轮询。 |
| `NewManga.Host/**` | 覆盖 Registry、DPAPI/ACL 接缝、锁、grant、撤销 ACK、Host handler 和能力 Gate。目录授权不包含新增依赖授权。 |
| `NewManga.CoreClient/{Issuer,Commands,Wire}/**`、`CoreServiceClient.cs`、`Transport/WireLog.cs` | 覆盖新增命令及序列化、签名、安全日志和客户端调用。`WireFrame` 本身定义于已授权的 `WireLog.cs`。 |
| Python 指定 tests、`tests/fea09/**`、Avalonia tests | 可承载新增矩阵与兼容回归；宽 tests 写域不授权无关测试重写。 |
| Task/Handoff/Review/`verification/FEA-09/**` | 已显式覆盖交付证据。STATUS/PLAN/ledger/Appointment 等由 DSH 执行治理更新。 |

没有发现必须修改却明确被排除的生产路径。

`Transport/SidecarProcess.cs` 当前负责构造原始 frame，但不在写域。可在现有已授权的 frame/log 定义与客户端边界实现契约要求；若实现方案确需修改该文件，必须先由 DSH 精确登记扩域，不能把它视为已获授权。

越界限制成立：

- App Views/ViewModels、生产 App adapter 修改归 UI-1；FEA-09 仅增加已有路径的真实消费测试。
- C-07 保持冻结；FEA-09 不新增 `IHostController`。UI-1 如新增端口，另走 UNFREEZE。
- 不创建 `source_sync_plans/source_operations`，不实现 FEA-11/12/13 产品流程。
- 无原文件写删、回收站、备份产品实现、新依赖或 push 授权。
- 共享组合根仍由 DSH 单点提交。

### 3.2 逐 AC 可执行性

| AC | 判定与实施证据要求 |
|---|---|
| AC-1 | 可判定。五类 fixture 登记 decoder/SHA/结果/副作用；AES 必须精确断言 `SOURCE_FORMAT_UNSUPPORTED`，不得计入解密成功。 |
| AC-2 | 可判定。断言有序 entry/page ID、ordinal 与唯一稳定排序键，包含同键 tie-break。 |
| AC-3 | 可判定。重复 occurrence 不按 digest 折叠；跨 book 共享 entry，但 PageId、进度、人工修改、处理结果独立。`import_as_new` 不绕过项目内 entry 唯一性。 |
| AC-4 | 可判定。按 C-16 区分 REQUIRED/INVALID/UNSUPPORTED；Plan 不消费密码，Start 后使用新一次性引用；扫描 Frames、NDJSON、日志及证据中的字面量与可逆编码。 |
| AC-5 | 可判定。必须使用 C-16 accepted→running→终态、逐页事务、重放/冲突/项目锁及计数公式；不能只证明客户端等待被取消。 |
| AC-6 | 可判定。真实隔离 sidecar、实际序列化和 production adapter；源 hash/mtime 守恒，既有 managed/derived 保留；新增 UI 操作不在本 Task 宣告完成。 |
| AC-7 | 可判定，但需按 R2S-001 展开模式边界。分别验证完整集合与 managed V 集合守恒；覆盖资源不可验证、v7 回滚、旧写者拒写、双读与功能开关。`SOURCE_PROJECT_MISMATCH` 已有明确同事务回滚责任。 |
| AC-8 | 可判定。.NET `1292 passed / 0 failed / 57 skipped`，总数 1349，是基准；新增及变化单列，Python 分列，skip 逐条，EV 逐文件，不 push。 |
| AC-9 | 可判定。覆盖 Registry 持久化失败、撤销 ACK 失败、generation、根替换、scope 错配、过期、EOF；提交前强校验。原生 DPAPI 无证据时保持 LIMITED。 |
| AC-10 | 可判定。覆盖 key、单次预算、总上限、并发排队、LRU/同时间大文件、活跃引用保护、损坏重建及通道隔离；按 C-14 同时保护 preflight 已列产物。 |

当前真实代码及旧测试只能提供兼容基线。例如旧 `ImportPages` 测试使用进程内 StringIO，现有 `ImportExportUiTests.cs:18–24` 使用 fake controller；两者均不能替代 AC-6 的真实 IPC/UI 消费证据。

## 4. 依赖与前置核验

### 4.1 PREREQ-1 与冻结链

已实际读取 scope-r1、PREREQ-1、契约复核 r1–r7 原文、四份当前契约及冻结记录、C-01b/C-07/C-14、UNFREEZE、UI-1、STATUS/PLAN、Gate 裁定、AD-002/003 和当前 checkpoint 相关段落。

确认：

- PREREQ-1 为 `done`，integration/delivery 为 `24c10567926fb302d9bac6ba63ae92d673cf9e83`，该提交是当前 HEAD 的祖先。
- r7 原文为 **approved，P0/P1/P2=0**。
- r7 被审 head 至当前四份契约的 diff **均只改状态行**，未发现冻结时夹带条款修改。
- scope-r1 原文为 32,902 bytes，其 SHA-256 与 Task 登记一致。
- 契约 r1–r6 原文指纹与 r7 列出的历史指纹一致；r7 当前 SHA-256 为 `56176012a2a34b4d6245b2468d162aa9381c9913a41a5a8d068c863d324ce57d`。

当前 pin：

| 契约 | 工作树 SHA-256 |
|---|---|
| C-05 v1.1 | `a234346fb0eec2304c598024740bd0c26eea18117dde6dae5b49410192d58e82` |
| C-06 v1.1 | `8faa8cd139f2e9c599dcd34063a5ac1a85941ecac287fcd693eb43d2109b2003` |
| C-15 v1.0 | `6da686178f4d2e739906938e2bbcfbb57c9d59f3836e17c80c8764b477cd91bc` |
| C-16 v1.0 | `6e7f8d3d7a81c3588a8db1878579e4b1f4fd5330e4bbbab54e5ff5165afa1b0f` |

PREREQ-1 六项 EV 文件均存在于所 pin 的 integration commit；工作树 SHA-256 全部匹配登记值。它们的 LF blob SHA-256 不同，属于必须区分的字节口径，不能混称两者相同。

### 4.2 本轮机械检查

| 检查 | 本轮实际结果 |
|---|---|
| `check.ps1 -TaskPath doc/tasks/FEA-09.md` | EXIT 0，PASS，3 warnings |
| `verify_pins.ps1` | EXIT 0，**PASS all 17** |
| 四 PNG 与 `b26840acd` blob 比较 | 四文件原字节均相同 |
| build、.NET/Python 产品测试、真实 IPC/UI | **NOT_RUN** |

3 warnings 涉非终态 Task 台账及 STATUS/PLAN 体量预算，不代表 scope 不合格。

### 4.3 协同与释放

- FEA-08、FEA-01-FREEZE-1 均登记 done；本轮没有重开或复验 FEA-08。
- UI-1 仍 proposed，依赖 FEA-09；“并行准备”仅指只读准备，不是并行实施授权。
- UI-1 完成前，不得宣称提案 `:1040` 的完整 Source 导入 UI 验收通过。
- `G-DELETE-IMPL` 不阻塞当前只读源／导入／缓存范围。
- 当前 owner/reviewer 未指派、base 仍为 scope-r1 head，这是 **ready 前治理动作尚未执行**，不是依赖未冻结。
- DSH 完成第 7 节后，可以置 `ready`。

## 5. 新 Findings 表

| ID | 级别 | 位置 | 问题、影响与最小处理 |
|---|---|---|---|
| **R2S-001** | **P2** | Task `:108/:136/:138`；C-05 `:61–94`；C-15 `:39–44`；C-16 `:89–97` | **AC 简写未显式限定冻结后的谓词和恢复边界。** “各半写负例不可见”不可推广到旧 managed artifact-only 页；“referenced complete 可见”仍需父级/时间/healthy binding；可见不等于当前可读。重启恢复也不意味着 receipt 跨重启持久化。建议在 AC-5/7 或判别表明确：referenced incomplete 不可见；managed artifact-only incomplete 仍按旧 V；授权撤销可保持 V 但 R typed 失败；重启查询旧 operation 返回 `SOURCE_OPERATION_NOT_FOUND`，自然键重试保留已提交页。契约答案已冻结，无需改契约。 |
| **R2S-002** | **P2** | Task `:157–168`；scope-r1 `:431` | **验证计划仍缺可复制的 Python/IPC/故障 planned 命令及冻结条款到证据的细分映射。** 现表仅写 suite/步骤，容易漏掉 accepted 重放、冲突、项目忙锁、六类计数、旧 managed 写入维护及迁移双集合。置 ready 前登记命令、解释器/task-env、隔离根、预期码/状态和拟议证据文件；尚不存在的测试继续明确 planned/NOT_RUN，不伪装成可执行或 PASS。 |

两项均不要求扩大生产写域或修改冻结语义。

## 6. 未覆盖／无法核验项

- 未运行 FEA-09 产品实现、build、.NET/Python 回归、真实 IPC/UI、性能或缓存压力测试。
- 未验证生产迁移 callback、违规操作拦截、真实资源失败回滚、撤销竞态、ACK 超时及后台停止。
- 未执行原生 DPAPI、ACL、跨 session 锁、断电恢复、ZipCrypto/PDFium 密码产品路径。
- PREREQ-1 的 pin 负测日志实际覆盖缺记录与错 pin；本轮未重跑其负测，也不声称日志覆盖了全部失败分支。
- PREREQ-1 DDL 日志末尾仍写 `C15 v2 DDL VALIDATION`；本轮不将该标签解释成完整 v5 运行验收。最终条款依据为 r7 原文、冻结差异及当前 pin。
- Task 的 temp `DELETE_SAFE` 仍需 closeout 时逐项核实，不能作为预先删除授权。
- 未扫描历史资料、未触碰真实用户数据、外部卷、AppData 生产根或回收站。

## 7. 结论与 DSH 最后动作

**范围可以批准；当前尚不能仅凭本报告自动进入实施。DSH 完成以下动作后，可执行 `proposed → ready`：**

1. 原字节归档本报告至 `doc/reviews/FEA-09-scope-r2.md`，登记报告指纹、reviewed_head、Task 指纹及两项 P2 disposition。
2. 按冻结契约补齐 R2S-001/002；将 Task 标题、依据中“DDL 未冻结／待前置冻结”改为历史来源说明，当前事实指向 C-15/C-16。
3. 冻结实际 owner、实施 Reviewer 及其来源；建议实现者为**另一未参与 scope review 的 Codex 会话**，本会话不参与实现。
4. 更新 `base_commit`，保留 scope-r1 历史锚点；固定 branch/worktree、allowed_paths、验证环境与证据口径。
5. 同步 STATUS、PLAN、rolling checkpoint、ledger 和 Appointment；UI-1 保持独立 scope/端口冻结责任。
6. 重跑 check/vpins，要求 PASS／17/17；AC 继续保持未实施状态，产品验证计划继续 NOT_RUN。
7. 由 DSH 置 ready，Owner 明确认领后才进入 in_progress；禁止 push。

推荐下一步由 **DSH** 执行范围释放收尾。可直接转发：

> DSH：请在 `G:\CODEX\New Manga`、`main`，以 scope-r2 reviewed_head=`19e6210047e664d1206347bd5259a6f075a9c028` 为审查恢复点，先核实 HEAD/status。原字节归档本报告，处置 R2S-001/002，仅更新 FEA-09 Task、验证计划、Appointment 及必要 STATUS/PLAN/checkpoint/ledger；冻结契约与历史证据不改。登记实际 owner、上下文独立的实现 Reviewer、实施 base 和隔离环境，交付报告指纹、disposition、固定释放记录及 check/vpins 实际结果。确认前置仍 done、17/17 后才置 ready；实现交给另一 Codex 会话，本 reviewer 不参与。UI-1 另行冻结，不宣称完整 UI 验收；禁止用户数据操作、新依赖、重开 FEA-08 或 push。