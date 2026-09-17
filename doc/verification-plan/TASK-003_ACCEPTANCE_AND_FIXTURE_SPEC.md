# TASK-003 验收方法与素材规范

状态：**Frozen for verification planning**（TASK-003 已完成独立 Review，并由 merge commit `db269e9` 集成）。本文件定义验收**方法、环境、证据口径、性能测量协议、模型阈值状态与组级标识**，不代表任何产品行为已经通过。

依据：[D08 验收标准](../08_ACCEPTANCE_CRITERIA.md)、[D07 §97～101](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[D13 追踪](../13_ACCEPTANCE_TRACEABILITY.md)、[TASK-002 最小契约](../contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)、[TASK-002 复审 F-08](../reviews/TASK-002-885c9a9.md)、[协作协议 §4/§6](../09_COLLABORATION.md)。

## 1. 权威边界

| 文件 | 唯一权威内容 | 不负责 |
|---|---|---|
| [D08](../08_ACCEPTANCE_CRITERIA.md) | 验收目标、185 个编号 AC 的编号/标题/优先级、Release Gate、结果枚举、证据类型清单 | 具体测试方法、环境档位、采样次数 |
| [D07](../07_NON_FUNCTIONAL_REQUIREMENTS.md) | 质量目标与目标数值（含性能阈值基线） | 验收方法与证据格式 |
| 本文件 | 验收方法、环境档位、证据口径、性能测量协议、模型阈值状态、`ACG-*` 稳定标识与执行方式 | **不新增、删除或改写任何产品要求与优先级**；**不维护任何 AC 的当前结果** |
| [D13](../13_ACCEPTANCE_TRACEABILITY.md) | AC → 主责任 Task 的追踪路由**与当前结果** | 不定义验收方法（只回链本文件） |
| [Fixture Manifest](../fixtures/MANIFEST.md) | 素材 ID、场景、来源/许可、生成方式、预期属性、Hash、状态 | 不定义产品行为或阈值 |

**结果真值的唯一位置**：某个 AC / ACG 当前是什么结果，只由 [D13](../13_ACCEPTANCE_TRACEABILITY.md) 的结果列或**绑定固定 commit 的** Handoff / Review 报告维护。本文件不得出现任何"当前结果"列、结果摘要或状态统计。

发生冲突时：验收目标与优先级以 D08 为准；质量数值以 D07/D08 为准；**产品范围与用户流程按 [索引的 Source of Truth 表](../00_INDEX.md) 归 D01/D04/D05**，产品范围变化由用户决定。执行方法与环境口径以本文件为准。任何产品范围变化必须先修订权威文档并保留用户决定，不能以本文件或测试实现替代设计决策。

## 2. 结果枚举与使用规则

每项验证结果只能取 D08 §3 的枚举之一：

```text
PASS
FAIL
BLOCKED
NOT_RUN
N/A
```

使用规则：

- **PASS** 只用于**已实际执行**且满足验收预期的检查，必须绑定 commit、环境、命令或操作步骤与证据路径。
- **FAIL** 用于实际执行后不满足预期；不得用"下次修"代替记录。
- **BLOCKED** 用于依赖缺失、外部条件不可得（如无可用 GPU、素材未取得、契约未冻结）导致**无法执行**；必须写明恢复条件。
- **NOT_RUN** 用于尚未执行且没有已知阻塞的检查。未执行一律写 `NOT_RUN`，禁止写 PASS。
- **N/A** 只用于经用户或 Codex 明确判定不适用的条目，必须写明判定依据；不得用 N/A 静默缩减范围。
- **复合值或自定义状态（如"PASS（契约层）"）不是合法结果**：一项只能取上述五值之一，其他信息写入证据列。
- 文档证据只能证明文档层结论。**不得用文档、Mock 或作者自查证明产品行为**（D08 §4、D13 说明）。
- 同一 AC 存在多条证据时，只要有一条 FAIL 即该项为 FAIL。

## 3. 标识体系

| 类型 | 形式 | 权威来源 | 规则 |
|---|---|---|---|
| 编号 AC | `AC-<主题>-<3位序号>`（如 `AC-PERF-001`） | D08 | 185 条，编号/标题/优先级不得改动；本文件不复制其正文 |
| 零编号主题组 | `ACG-<主题>`（如 `ACG-SMOKE`） | 本文件 §8.1 | D08 中**没有编号子项**的 10 个主题 |
| 未编号规范组 | `ACG-<名称>`（如 `ACG-BENCH`） | 本文件 §8.2 | D08 §68～§73、§76 的全局规范 |
| 扩展项 | `ACG-EXT-<名称>`（如 `ACG-EXT-FONT`） | 本文件 §8.4 | D13 登记、尚未成为编号 AC 的扩展要求 |
| 测试用例 | `T-<AC ID 或 ACG ID>-<2位序号>` | 各实现/验证 Task | 一个 AC 可有多个用例；用例 ID 全局唯一 |
| 运行记录 | `RUN-<Task ID>-<2位序号>` | 各实现/验证 Task | 一次实际执行的完整记录，绑定 commit 与环境 |

`ACG-*` 与 D08/D13 的条目一一对应，不发明新的产品 ID 或优先级（D13 原则）。标识一经发布不得重命名；D08 后续若为这些条目增加编号子项，`ACG-*` 保留为组级回链，不删除历史记录。

## 4. 环境档位

| 档位 | 用途 | 最低记录字段 |
|---|---|---|
| ENV-A 开发机 | 单元、Repository、集成、UI 自动化 | D08 §6 全字段（App/Commit/Schema/Windows/Python/PySide6/CPU/RAM/GPU/VRAM/Driver/CUDA/DPI/显示器数/主屏分辨率） |
| ENV-B 基准机 | 性能与容量（§6） | ENV-A 全字段 + 电源计划、后台负载说明、磁盘类型、固定数据集 ID |
| ENV-C 干净 Windows | 打包、Smoke、DPI/双屏视觉 | 干净系统版本与补丁级别、是否安装 Python、DPI 组合、显示器拓扑 |
| ENV-D GPU 机 | AI 步骤性能与设备回退 | ENV-B 全字段 + GPU 型号/VRAM/驱动/CUDA 运行时 |

- 每个档位的能力与限制必须写入运行记录；未达到档位要求的测量不得作为 Release 证据。
- Provider 相关验证额外记录 D08 §6 的 Provider Profile / Model / Local 或 Remote / Network Profile。
- **Secret、Token、完整请求体不得写入验收报告或日志证据**（D08 §6、契约 §10）。

## 5. 证据口径

| AC 类别 | 最低证据 | 存放位置（相对仓库根） |
|---|---|---|
| 单元 / Repository / Domain | 测试输出（含用例 ID、通过数、退出码） | `verification/<Task>/logs/` |
| Pipeline / 并发 / 恢复 | 测试输出 + 关键状态转储（Run/Task/Step/Stage） | 同上 |
| UI / ViewModel | 自动化输出 + 关键界面截图 | `verification/<Task>/screenshots/` |
| 数据保护（Revision/Lock/源文件） | 前后 Hash、DB 快照、失败注入记录 | `verification/<Task>/logs/` + `artifacts/` |
| 性能 / 容量 / 内存 | Benchmark 报告（§6 格式）+ 原始样本 | `verification/<Task>/benchmark-report.md` |
| 打包 / Smoke | ENV-C 操作记录 + 安装包 Hash + 截图 | `verification/<Task>/10-packaging/` |
| 设计与文档 Gate | 检查脚本输出 + 固定 commit | `verification/<Task>/` |

每条运行记录至少包含 D08 §4 的字段（Test ID / Priority / Environment / Preconditions / Steps / Expected / Actual / Result / Evidence / Notes）。结果目录沿用 D08 §74 的分类，但目录名与 Task 对应即可，不因本文件改变 D08 的推荐结构。

## 6. 性能测量协议

**固定参数（本文件冻结，未经用户批准不得放宽）：普通操作固定 3 次预热后测量 20 次；AI 步骤固定 1 次预热后测量 5 次；两者都报 P95。**

| 类别 | 预热 | 测量次数 | 统计量 | 环境 |
|---|---|---|---|---|
| 普通操作（页面切换、面板响应、搜索、DB 查询、TM 查询、PageList 加载） | 3 次 | 20 次 | P95（并记录 P50 与最大值） | ENV-B |
| AI 步骤（OCR、Translation、Inpaint、Render、Vision OCR） | 1 次 | 5 次 | P95（并记录 P50 与最大值） | ENV-D |
| 冷启动 | **不适用通用预热**（见 §6.5） | 20 次 | P95（并记录 P50 与最大值） | ENV-B |

### 6.1 计时边界

| 测量项 | 起始事件 | 结束事件 |
|---|---|---|
| 冷启动 | 进程创建（或可执行文件启动调用） | 主窗口可交互：默认书架渲染完成并接受输入 |
| 一级页面切换 | 用户触发切换动作 | 目标页面首帧可见且可交互 |
| 固定面板响应 | 触发面板操作 | 面板状态更新可见 |
| Book 搜索 | 查询提交 | 结果列表渲染完成 |
| Translation Memory Exact / Fuzzy | 查询提交 | 匹配结果返回且可用于 UI |
| PageList 加载 | 打开章节 | 列表可滚动且缩略图占位完成 |
| DB 查询 | 语句提交 | 结果集就绪 |
| AI 步骤 | Step 开始记录 | Step 产出提交或失败返回 |
| 内存 / 峰值 | 进程启动 | 场景结束（峰值取采样最大值） |

### 6.2 时钟与估计量

- 计时必须使用**单调时钟**（`Stopwatch` / `time.perf_counter`），不得使用受系统时间调整影响的 wall clock。
- P95 估计量固定为 **nearest-rank**：将 N 个有效样本升序排列，取第 `ceil(0.95 × N)` 个（N=20 → 第 19 个；N=5 → 第 5 个）。
- P50 同样使用 nearest-rank（N=20 → 第 10 个；N=5 → 第 3 个）。
- 同时报告最大值与样本数。不同估计量（如线性插值、均值±标准差）产生的结果不得与 Gate 结论混用。

### 6.3 样本异常规则

- 全部样本必须原样记录，不得删除或重排；任何排除都要在报告中逐条列出原因。
- 仅当出现可归因的环境异常（后台任务抢占、电源状态切换、外部进程、驱动重置）时，可将该样本标为 `excluded` 并**补跑同等数量**的新样本。
- 排除后有效样本数不足（普通操作 < 20、AI 步骤 < 5）时，该项结果为 `NOT_RUN`。
- 不得用"重跑覆盖旧样本"的方式美化结果；旧样本与新样本都保留在证据中。

### 6.4 数据集与阈值

- 每个测量项必须绑定数据集 ID（[D07 §99](../07_NON_FUNCTIONAL_REQUIREMENTS.md) 的 Dataset A～E 或 [Fixture Manifest](../fixtures/MANIFEST.md) 中的等价素材）；容量项的数据集路由见 §9 的 AC-CAP 行。
- AI 步骤必须按 `Provider / Model / Device` 分别记录，禁止合并为一个总平均值（D07 §100）。
- 环境字段缺失、预热不足或测量次数不足的记录，结果为 `NOT_RUN`，不得降级为"参考值"充当 PASS。
- 阈值来源：D08 §43（AC-PERF-001～006）与 D07 目标数值。这些数值是**目标基线、未经真实 Benchmark 验证**；本文件不修改、不放宽、不新增阈值。
- 未达到阈值时按 D08 AC-PERF-001 的现行规则记 `FAIL` 并阻塞 Release；正式豁免需用户决定并同步 D07/D08（TASK-001 已确认当前无生效豁免）。
- 普通 CI 不强制完整 GPU Benchmark（D07 §101）；Release Candidate 必须在 ENV-B/ENV-D 执行完整 Benchmark 并生成 `benchmark-report.md`（D08 §71）。

### 6.5 冷启动专用规则

冷启动**不得**套用 §6 的通用预热，否则会把暖启动当成冷启动测量：

- 每个样本必须从满足冷定义的状态开始：无残留应用进程、无上一次运行留下的内存/缓存预热、记录 OS 文件缓存状态。
- 样本之间必须重新回到该状态；无法可靠重置缓存（例如无法清空 OS 文件缓存）时，必须在报告中记录该限制，并把结果标 `BLOCKED`，不得用暖启动值充当冷启动。
- 冷启动的计时边界与样本数按 §6.1/§6 执行（20 次，无预热）。

## 7. 模型质量评估方法与阈值状态

本仓库当前**没有任何来源支持的模型质量数值阈值**（D01 §5 的能力矩阵来自未提供的旧材料，D07/D08 未给出 OCR 准确率、翻译质量或 Inpaint 质量的数值目标）。因此：

| 评估对象 | 指标（方法层，不含数值） | 数据要求 | 阈值状态 |
|---|---|---|---|
| 文字检测 | Region 召回/精确、漏检与误检计数、几何 IoU 分布 | 人工标注的 Fixture 子集，标注版本固定 | `UNAPPROVED_THRESHOLD` |
| OCR | 字符准确率、编辑距离、按语言（日/韩/中）分层 | 同上，含竖排与彩色 Webtoon | `UNAPPROVED_THRESHOLD` |
| 翻译 | 人工可用性分级（可用/需小改/不可用）与术语一致率 | 双人独立评分，记录分歧处理 | `UNAPPROVED_THRESHOLD` |
| Inpaint / Clean | 人工视觉分级与残留文字计数 | 固定 Mask 输入与前后对照图 | `UNAPPROVED_THRESHOLD` |

规则：

- `UNAPPROVED_THRESHOLD` 表示**方法已定义、数值待用户批准**；在获得用户批准并同步 D08 之前，任何模型质量项不得判 `PASS`，结果为 `NOT_RUN` 或 `BLOCKED`（素材未取得时）。
- 禁止虚构数值、禁止用 Mock Provider 的输出充当质量证据、禁止把"跑通流程"当作质量通过（D08 §71 与 D13 说明）。
- 阈值获批后，必须在本文件与 D08 对应条目同步登记，并保留批准记录。

## 8. 组级标识与执行方式

### 8.1 D08 零编号主题（10 项）

D08 中以下主题没有编号子项，使用稳定组标识；产品要求仍以 D08 对应章节为准。本表**不记录当前结果**（结果见 [D13](../13_ACCEPTANCE_TRACEABILITY.md)）。

| ACG ID | D08 章节 | 组级要求要点 | 执行方式 | 环境 | 证据 |
|---|---|---|---|---|---|
| `ACG-DPI` | §51 | 100～200% 显示缩放与多屏可达性 | 手工视觉：DPI 组合矩阵 + 双屏/副屏消失/主屏切换 | ENV-C | 截图集 + 检查清单 |
| `ACG-SMOKE` | §53 | 干净 Windows 发布包完整主流程 | 逐步骤手工端到端（见 §8.5） | ENV-C | 操作记录 + 截图 + 包 Hash |
| `ACG-OFFLINE` | §56 | 离线本地能力可用、远程不可用状态 | 网络隔离 + 本地 Provider 路径；远程失败必须显式提示 | ENV-A（断网） | 日志 + 截图 |
| `ACG-PRIVACY` | §57 | Provider 设置页说明上传给远程 Provider 的数据类型 | 检查设置页披露内容与可读性 | ENV-A | 截图 + 文案清单 |
| `ACG-SET` | §59 | 设置继承与值来源 | 单元（继承优先级）+ UI（来源显示） | ENV-A | 测试输出 + 截图 |
| `ACG-PROV` | §60 | OCR/Translation/Inpaint/Render 来源链 | 集成：Region/Artifact 的 provenance 字段与 UI 展示一致 | ENV-A | 数据转储 + 截图 |
| `ACG-ERROR` | §62 | 错误分类 | 单元：错误码与分类映射表全覆盖，无未分类错误 | ENV-A | 测试输出 + 映射表 |
| `ACG-ERRUI` | §63 | 错误在页面/进度/详情可定位 | UI 自动化 + 手工：三类入口均能到达同一错误对象 | ENV-A | 截图 + 测试输出 |
| `ACG-AUTO` | §64 | Autosave 条件性要求或明确保存 | 集成 + UI：自动保存触发点与显式保存路径 | ENV-A | 测试输出 |
| `ACG-SYNC` | §67 | 06/07 对 03 的同步核验与 Schema 冻结 Gate | 文档/契约检查：契约 §2～§10 与 §11 向量存在；**Gate 只有在正式实现满足契约并通过 §11 向量后才可通过** | 静态 | 契约 + 独立 Review 报告 + 实现证据 |

`ACG-SYNC` 的证据只说明契约已冻结；**契约获批不等于 Schema 或产品 Gate 通过**。

### 8.2 D08 未编号全局规范（§68～§73、§76）

| ACG ID | D08 章节 | 要求要点 | 执行方式 | 环境 | 证据 |
|---|---|---|---|---|---|
| `ACG-AUTOTEST` | §68 | 按 D08 §68 的自动化测试最低覆盖清单（Domain rules、Repository CRUD、Soft Delete、Lock、Revision、Constraint 优先级、TM 写入规则、Pipeline 计划、Step skip/stale、Pause/Continue/Stop、Crash Recovery、Retry、Artifact 原子提交、Provider 解析、Proxy 策略、Context 写回范围、Webtoon 坐标映射、Task 进度聚合） | 建立覆盖矩阵，逐类给出用例或明确缺失 | ENV-A | 覆盖矩阵 + 测试输出 |
| `ACG-UITEST` | §69 | 按 D08 §69 的 UI/ViewModel 最低覆盖清单（默认导航书架、4 一级页面、Book→Chapter→Workbench、Book→Chapter→Reader、PageList 多选、Region Inspector 绑定、TaskProgress 状态、暂停/停止/继续 enable state、失败页筛选、Dirty Close、Settings inheritance display） | 同上 | ENV-A | 覆盖矩阵 + 测试输出 |
| `ACG-VISUAL` | §70 | 手工视觉验收（100～200% DPI、双屏、长文本、中/日/韩、超长文件名、空状态、Loading、Error、Disabled、Hovered、Selected、Focused） | 手工检查清单逐项 | ENV-C | 截图集 + 清单 |
| `ACG-BENCH` | §71 | 每个 Release Candidate 生成 `benchmark-report.md`（Cold Start、Page Switch、Book Search、Large PageList、Webtoon Memory、TaskProgress Update、DB Query、Peak RAM、Peak VRAM） | 按 §6 协议执行并产出报告；无数据不得写"性能已优化/达标" | ENV-B/D | benchmark-report.md |
| `ACG-DATASAFE` | §72 | 按 D08 §72 的数据安全 Gate 逐项执行（源文件 Hash 不变、人工译文不被覆盖、current Revision 不被破坏、Pinned 不被清理、Stop 不回滚、Crash 不误判、Migration 可恢复、Secret 不入库不入日志） | 逐项执行；任一 FAIL 即 BLOCK RELEASE | ENV-A | 测试输出 + Hash + 扫描 |
| `ACG-RELEASECHECK` | §73 | 按 D08 §73 的最终 Release Checklist 逐项核对 | 发布前逐项核对并链接证据 | ENV-C | 清单 + 证据链接 |
| `ACG-READY` | §76 | READY 判定条件（P0 全 PASS、P1 全 PASS、无数据安全/人工覆盖/源文件破坏/数据库损坏 Blocker、干净 Windows Smoke PASS） | 汇总判定；不满足即 NOT READY | 静态 | verification-summary + 判定 |

**明确排除（非验收项）**：

| D08 章节 | 排除理由 |
|---|---|
| §74 建议验收结果目录 | 目录结构建议，不构成通过条件；证据存放由 §5 与各 Task 约定覆盖 |
| §75 verification-summary.md 推荐格式 | 格式建议；其内容要求已由 `ACG-READY` 与 `ACG-RELEASECHECK` 覆盖 |

### 8.3 执行路由与优先级

- `ACG-DATASAFE`、`ACG-SMOKE`、`ACG-READY` 属 Release 阻塞项：任一 FAIL 时按 D08 §72/§76 阻塞发布。
- `ACG-AUTOTEST`/`ACG-UITEST`/`ACG-VISUAL`/`ACG-BENCH`/`ACG-RELEASECHECK` 的缺失按 `NOT_RUN` 记录，并计入 Release Checklist。
- 以上标识不改变 D08 的优先级体系；它们没有独立 P0/P1 级别，阻塞性由 D08 对应章节决定。

### 8.4 扩展项（D13 登记的 7 类）

这些条目**尚未成为编号 AC**，不得因"未列出"而跳过；主责任 Task 先补设计或 AC，再由本文件登记执行方式。

| ACG ID | 来源 | 内容 | 处理路径 |
|---|---|---|---|
| `ACG-EXT-IMPORT` | D01 §2；D04 §8；D05 §52 | PDF / MOBI 导入（网页导入已按 U-1 取消） | TASK-024 §1.2 定义 PDF/MOBI 边界；网页 AC-EXT-IMPORT-001/002 已退役；TASK-023 仍冻结 |
| `ACG-EXT-PLUGIN` | D01 §2；D02 §12；D07 §72 | Plugin / Hooks、AI 生成插件 Agent | TASK-024 确认条件与 AC，TASK-025 实现 |
| `ACG-EXT-FONT` | D01 §2；D05 §48 | 字体上传与资源处理 | TASK-024 确认 AC，TASK-022 实现 |
| `ACG-EXT-SAKURA` | D01 §2；D02 §11 | Sakura 服务监控、模型/设备就绪状态 | TASK-024 明确范围，TASK-019 落实 |
| `ACG-EXT-DETECT` | D06 §6/§8 | 检测、配色与 SourceStyle 正确性 | 用 §7 质量方法；TASK-016/019/014 验证 |
| `ACG-EXT-CONTRACT` | D03/D06；G06～G13 | 状态、复合写回、Pin/TM/Review、SFX 的精确 AC | TASK-002 已冻结契约；精确 AC 待 TASK-003/024 补齐后登记 |
| `ACG-EXT-NFR` | D07 目标数值；D08 发布要求 | SHOULD/P1/豁免口径与基准环境 | TASK-001/003 核对，TASK-026 实测 |

### 8.5 ACG-SMOKE 完整步骤

按 D08 §53 逐步执行（不得缩写掉持久化检查），全部 PASS 才可发布：

```text
启动
→ 默认书架
→ 创建 Book
→ 创建 Chapter
→ 导入 Page
→ 进入工作台
→ 执行至少一个 Mock / Local Pipeline
→ 保存
→ 阅读
→ 导出
→ 关闭
→ 再启动
→ 数据仍存在
```

## 9. 主题级执行方式（覆盖全部 185 个编号 AC）

编号、标题与优先级以 [D08](../08_ACCEPTANCE_CRITERIA.md) 为唯一权威；下表只登记执行方式，同主题内的编号 AC 共用该方法，除 §6/§7 另有协议者。

| D08 主题 | 编号数 | 测试类型 | 环境 | 主要证据 |
|---|---|---|---|---|
| §7 AC-NAV | 3 | UI 自动化 + 集成 | ENV-A | 测试输出 + 截图 |
| §8 AC-WIN | 6 | UI 自动化 + 手工（双屏/DPI） | ENV-A/C | 测试输出 + 截图 |
| §9 AC-LIB | 4 | Repository + 集成 | ENV-A | 测试输出 |
| §10 AC-CH | 4 | Repository + 集成 | ENV-A | 测试输出 |
| §11 AC-IMPORT | 5 | 集成 + 文件系统（Managed Copy、源文件 Hash） | ENV-A | 测试输出 + Hash 记录 |
| §12 AC-PAGE | 3 | 集成 + UI | ENV-A | 测试输出 |
| §13 AC-WEBTOON | 5 | 集成 + 坐标映射单元 + 内存（§6） | ENV-A | 测试输出 + Benchmark |
| §14 AC-REGION | 4 | 单元 + Repository | ENV-A | 测试输出 |
| §15 AC-OCR | 4 | 集成（fake transport）+ 质量（§7） | ENV-A / 质量另定 | 测试输出 + 质量报告 |
| §16 AC-SFX | 3 | 单元 + Pipeline | ENV-A | 测试输出 |
| §17 AC-CONSTRAINT | 4 | 单元 + Repository | ENV-A | 测试输出 |
| §18 AC-TM | 4 | 单元 + Repository | ENV-A | 测试输出 |
| §19 AC-TRANS | 4 | 集成 + Context 写回范围检查 | ENV-A | 测试输出 |
| §20 AC-LOCK | 5 | 单元 + Pipeline（写入前复查） | ENV-A | 测试输出 |
| §21 AC-REV | 4 | 单元 + Repository（current/Pin） | ENV-A | 测试输出 |
| §22 AC-STYLE | 5 | 单元 + 渲染集成 | ENV-A | 测试输出 + 截图 |
| §23 AC-INPAINT | 4 | Pipeline 集成（Prov/Clean 版本） | ENV-A | 测试输出 |
| §24 AC-RENDER | 2 | Pipeline 集成（不触发 OCR/Inpaint） | ENV-A | 测试输出 |
| §25 AC-RFULL | 5 | Pipeline 集成（单 Region 全链 + Lock 覆盖） | ENV-A | 测试输出 |
| §26 AC-CMD | 4 | 命令计划单元测试 | ENV-A | 测试输出 |
| §27 AC-PIPE | 4 | 单元 + 集成（Step 可追踪、Skip/Stale） | ENV-A | 测试输出 |
| §28 AC-PAUSE | 3 | Pipeline 并发（安全边界） | ENV-A | 测试输出 |
| §29 AC-STOP | 3 | Pipeline 并发（不回滚、不是 Delete） | ENV-A | 测试输出 |
| §30 AC-CRASH | 3 | 故障注入 + 恢复集成 | ENV-A | 测试输出 + 状态转储 |
| §31 AC-RETRY | 2 | Pipeline 集成（保留上游、派生 Run） | ENV-A | 测试输出 |
| §32 AC-PROGRESS | 7 | ViewModel 自动化 + 聚合单元 | ENV-A | 测试输出 + 截图 |
| §33 AC-PROVIDER | 4 | 集成（fake transport、快照与恢复） | ENV-A | 测试输出 |
| §34 AC-FALLBACK | 2 | 集成（显式策略） | ENV-A | 测试输出 |
| §35 AC-NET | 4 | 集成（代理桩、不静默 Direct） | ENV-A | 测试输出 + 日志 |
| §36 AC-SEC | 5 | 安全：DB/日志 Secret 扫描 + TLS 配置 | ENV-A | 扫描输出 + 测试输出 |
| §37 AC-ART | 3 | 故障注入 + Hash 校验 + 原子提交 | ENV-A | 测试输出 + Hash |
| §38 AC-DB | 5 | Repository + Migration（前备份、失败恢复、旧 App 打开） | ENV-A | 测试输出 |
| §39 AC-BACKUP | 4 | 集成 + 文件系统（Restore 不改源文件） | ENV-A | 测试输出 + Hash |
| §40 AC-TRASH | 4 | 集成（软删除、永久删除确认、源文件安全） | ENV-A | 测试输出 |
| §41 AC-EXPORT | 3 | 集成 + 导出产物校验 | ENV-A | 测试输出 + 产物 Hash |
| §42 AC-READ | 5 | UI + 集成（进度独立、RTL/LTR、Webtoon） | ENV-A | 测试输出 + 截图 |
| §43 AC-PERF | 6 | Benchmark（§6：3 预热/20 次；AI 1/5；冷启动见 §6.5） | ENV-B/D | benchmark-report.md |
| §44 AC-CAP | 4 | 容量压力：`AC-CAP-001→DS-E`、`AC-CAP-002→DS-B2`、`AC-CAP-003→DS-C`、`AC-CAP-004→DS-D` | ENV-B | benchmark 报告 + 资源曲线 |
| §45 AC-MEM | 3 | 内存长跑测量 | ENV-B | 内存曲线 + 报告 |
| §46 AC-GPU | 3 | 设备故障注入 + 回退可追踪 | ENV-D | 测试输出 + 日志 |
| §47 AC-CACHE | 3 | 集成（不清业务真值、Pinned 保护、活动 Run 保护） | ENV-A | 测试输出 |
| §48 AC-DISK | 1 | 低磁盘故障注入 | ENV-A | 测试输出 + 日志 |
| §49 AC-LOG | 3 | 集成 + 轮转/诊断包检查 | ENV-A | 测试输出 + 样例包 |
| §50 AC-NFR-UI | 2 | 并发/响应性测试（AI 不阻塞 UI） | ENV-A | 测试输出 + 帧时序 |
| §51 AC-DPI | 0（组级 `ACG-DPI`） | 手工视觉 | ENV-C | 截图集 |
| §52 AC-PKG | 3 | ENV-C 打包与启动（Qt DLL、干净系统） | ENV-C | 安装包 Hash + 截图 |
| §53 AC-SMOKE | 0（组级 `ACG-SMOKE`） | 手工端到端（§8.5 全步骤） | ENV-C | 操作记录 + 截图 |
| §54 AC-OPTIONAL | 2 | 环境矩阵（缺重型模型仍可启动） | ENV-C | 测试输出 |
| §55 AC-MODEL | 2 | 集成（下载进度、不完整不 Ready） | ENV-A | 测试输出 |
| §56 AC-OFFLINE | 0（组级 `ACG-OFFLINE`） | 网络隔离验证 | ENV-A | 日志 + 截图 |
| §57 AC-PRIVACY | 0（组级 `ACG-PRIVACY`） | 设置页披露检查 | ENV-A | 截图 + 清单 |
| §58 AC-CONFLICT | 2 | 并发故障注入（Optimistic Write Guard、同能力写冲突） | ENV-A | 测试输出 + 状态转储 |
| §59 AC-SET | 0（组级 `ACG-SET`） | 单元 + UI | ENV-A | 测试输出 + 截图 |
| §60 AC-PROV | 0（组级 `ACG-PROV`） | 集成 + 数据检查 | ENV-A | 数据转储 + 截图 |
| §61 AC-CLEAN | 3 | 集成（Current/源文件不清理、Debug Artifact） | ENV-A | 测试输出 |
| §62 AC-ERROR | 0（组级 `ACG-ERROR`） | 单元 + 映射表检查 | ENV-A | 测试输出 |
| §63 AC-ERRUI | 0（组级 `ACG-ERRUI`） | UI 自动化 + 手工 | ENV-A | 截图 + 测试输出 |
| §64 AC-AUTO | 0（组级 `ACG-AUTO`） | 集成 + UI | ENV-A | 测试输出 |
| §65 AC-CLOSE | 2 | 集成（运行中关闭、Dirty 与 Running 分离） | ENV-A | 测试输出 |
| §66 AC-DOC | 3 | 文档检查 | 静态 | 检查脚本 + commit |
| §67 AC-SYNC | 0（组级 `ACG-SYNC`） | 契约/文档检查 + 实现 Gate | 静态 | 契约 + 复审报告 + 实现证据 |
| §68～§73、§76 | 0（组级见 §8.2） | 全局规范，见 §8.2 | 视条目 | 见 §8.2 |
| §74、§75 | 0（明确排除，见 §8.2） | 非验收项 | — | — |

**合计：185 个编号 AC + 24 个组级标识（10 零编号主题 + 7 全局规范 + 7 扩展项），覆盖 D08 全部 61 个主题与 D13 的扩展登记。**

## 10. 变更控制

- 修改本文件的**方法层**（环境、次数、证据格式）需要新的获授权 Task 与固定 commit Review。
- 修改**阈值或范围**属于产品决定：必须先由用户批准，再同步 D08/D07 与本文件，并保留批准记录。
- 本文件与 D08 出现冲突时，不得自行裁决：以 D08 为准执行，并把冲突记录到 Gap Register 交由 Codex 处理。
- 素材许可变化必须同步 [Fixture Manifest](../fixtures/MANIFEST.md)，不得先提交素材再补授权。
- 新增 `ACG-*` 标识必须先确认其在 D08 或 D13 有对应条目，再登记；不得为规避验收而拆分或合并标识。
