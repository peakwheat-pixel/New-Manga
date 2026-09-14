# TASK-003 验收方法与素材规范

状态：**Frozen for verification planning**（TASK-003 交付，待 Codex 独立 Review）。本文件定义验收**方法、环境、证据口径、性能测量协议、模型阈值状态与组级标识**，不代表任何产品行为已经通过。

依据：[D08 验收标准](../08_ACCEPTANCE_CRITERIA.md)（产品验收目标与优先级的唯一权威）、[D07 §97～101](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[D13 追踪](../13_ACCEPTANCE_TRACEABILITY.md)、[TASK-002 最小契约](../contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md)、[TASK-002 复审 F-08](../reviews/TASK-002-885c9a9.md)、[协作协议 §4/§6](../09_COLLABORATION.md)。

## 1. 权威边界

| 文件 | 唯一权威内容 | 不负责 |
|---|---|---|
| [D08](../08_ACCEPTANCE_CRITERIA.md) | 产品验收目标、185 个编号 AC 的编号/标题/优先级、Release Gate、结果枚举、证据类型清单 | 具体测试方法、环境档位、采样次数 |
| 本文件 | 验收方法、环境档位、证据口径、性能测量协议、模型阈值状态、组级 `ACG-*` 标识与执行方式 | **不新增、删除或改写任何产品要求与优先级** |
| [D13](../13_ACCEPTANCE_TRACEABILITY.md) | AC → 主责任 Task 的追踪路由与当前结果 | 不定义验收方法（只回链本文件） |
| [Fixture Manifest](../fixtures/MANIFEST.md) | 素材 ID、场景、来源/许可、生成方式、预期属性、Hash、状态 | 不定义产品行为或阈值 |

发生冲突时：产品语义、范围与优先级以 D08 与用户决定为准；执行方法与环境口径以本文件为准。任何产品范围变化必须先修订 D08 并保留用户决定，不能以本文件或测试实现替代设计决策。

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
- 文档证据只能证明文档层结论。**不得用文档、Mock 或作者自查证明产品行为**（D08 §4、D13 说明）。
- 同一 AC 存在多条证据时，只要有一条 FAIL 即该项为 FAIL。

## 3. 标识体系

| 类型 | 形式 | 权威来源 | 规则 |
|---|---|---|---|
| 编号 AC | `AC-<主题>-<3位序号>`（如 `AC-PERF-001`） | D08 | 185 条，编号/标题/优先级不得改动；本文件不复制其正文 |
| 组级要求 | `ACG-<主题>`（如 `ACG-SMOKE`） | 本文件 §8 | 仅用于 D08 中**没有编号子项**的 10 个主题，标识一经发布不得重命名 |
| 测试用例 | `T-<AC ID 或 ACG ID>-<2位序号>` | 各实现/验证 Task | 一个 AC 可有多个用例；用例 ID 全局唯一 |
| 运行记录 | `RUN-<Task ID>-<2位序号>` | 各实现/验证 Task | 一次实际执行的完整记录，绑定 commit 与环境 |

`ACG-*` 与 D08 主题一一对应，不发明新的产品 ID 或优先级（D13 原则）。D08 后续若为这些主题增加编号子项，`ACG-*` 保留为组级回链，不删除历史记录。

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
| 普通操作（冷启动、页面切换、面板响应、搜索、DB 查询、TM 查询、PageList 加载） | 3 次 | 20 次 | P95（并记录 P50 与最大值） | ENV-B |
| AI 步骤（OCR、Translation、Inpaint、Render、Vision OCR） | 1 次 | 5 次 | P95（并记录 P50 与最大值） | ENV-D |

规则：

- 每个测量项必须绑定数据集 ID（[D07 §99](../07_NON_FUNCTIONAL_REQUIREMENTS.md) 的 Dataset A～E 或 [Fixture Manifest](../fixtures/MANIFEST.md) 中的等价素材）。
- AI 步骤必须按 `Provider / Model / Device` 分别记录，禁止合并为一个总平均值（D07 §100）。
- 环境字段缺失、预热次数不足或测量次数不足的记录，结果为 `NOT_RUN`，不得降级为"参考值"充当 PASS。
- 阈值来源：D08 §43（AC-PERF-001～006）与 D07 目标数值。这些数值是**目标基线、未经真实 Benchmark 验证**；本文件不修改、不放宽、不新增阈值。
- 未达到阈值时按 D08 AC-PERF-001 的现行规则记 `FAIL` 并阻塞 Release；正式豁免需用户决定并同步 D07/D08（TASK-001 已确认当前无生效豁免）。
- 普通 CI 不强制完整 GPU Benchmark（D07 §101）；Release Candidate 必须在 ENV-B/ENV-D 执行完整 Benchmark 并生成 `benchmark-report.md`（D08 §71）。

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

## 8. 组级要求（`ACG-*`）

D08 中以下 10 个主题没有编号子项，使用稳定组标识；执行方式由本文件定义，产品要求仍以 D08 对应章节为准。

| ACG ID | D08 章节 | 组级要求要点 | 执行方式 | 环境 | 证据 | 当前结果 |
|---|---|---|---|---|---|---|
| `ACG-DPI` | §51 | 100～200% 显示缩放与多屏可达性 | 手工视觉：DPI 组合矩阵 + 双屏/副屏消失/主屏切换 | ENV-C | 截图集 + 检查清单 | NOT_RUN |
| `ACG-SMOKE` | §53 | 干净 Windows 发布包完整主流程 | 手工端到端：安装 → 导入 → 翻译 → 阅读 → 导出 → 退出 | ENV-C | 操作记录 + 截图 + 包 Hash | NOT_RUN |
| `ACG-OFFLINE` | §56 | 离线本地能力可用、远程不可用状态 | 网络隔离 + 本地 Provider 路径；远程失败必须显式提示 | ENV-A（断网） | 日志 + 截图 | NOT_RUN |
| `ACG-PRIVACY` | §57 | 远程 Provider 数据类型提示 | 文案与触发点检查 + 首次使用提示 | ENV-A | 截图 + 文案清单 | NOT_RUN |
| `ACG-SET` | §59 | 设置继承与值来源 | 单元（继承优先级）+ UI（来源显示） | ENV-A | 测试输出 + 截图 | NOT_RUN |
| `ACG-PROV` | §60 | OCR/Translation/Inpaint/Render 来源链 | 集成：Region/Artifact 的 provenance 字段与 UI 展示一致 | ENV-A | 数据转储 + 截图 | NOT_RUN |
| `ACG-ERROR` | §62 | 错误分类 | 单元：错误码与分类映射表全覆盖，无未分类错误 | ENV-A | 测试输出 + 映射表 | NOT_RUN |
| `ACG-ERRUI` | §63 | 错误在页面/进度/详情可定位 | UI 自动化 + 手工：三类入口均能到达同一错误对象 | ENV-A | 截图 + 测试输出 | NOT_RUN |
| `ACG-AUTO` | §64 | Autosave 条件性要求或明确保存 | 集成 + UI：自动保存触发点与显式保存路径 | ENV-A | 测试输出 | NOT_RUN |
| `ACG-SYNC` | §67 | 06/07 对 03 的同步核验与 Schema 冻结 Gate | 文档/契约检查：契约 §2～§10 与 §11 向量存在且被独立 Review | 静态 | 契约 + [TASK-002 复审](../reviews/TASK-002-885c9a9.md) | PASS（契约层）；实现层 NOT_RUN |

`ACG-SYNC` 的 PASS 仅限契约层（`b1b3f5d..885c9a9` 已独立批准并集成），**不代表**任何 Schema 或产品行为已验证。

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
| §43 AC-PERF | 6 | Benchmark（§6：3 预热/20 次；AI 1/5） | ENV-B/D | benchmark-report.md |
| §44 AC-CAP | 4 | 容量压力（Dataset B/C/E） | ENV-B | benchmark 报告 + 资源曲线 |
| §45 AC-MEM | 3 | 内存长跑测量 | ENV-B | 内存曲线 + 报告 |
| §46 AC-GPU | 3 | 设备故障注入 + 回退可追踪 | ENV-D | 测试输出 + 日志 |
| §47 AC-CACHE | 3 | 集成（不清业务真值、Pinned 保护、活动 Run 保护） | ENV-A | 测试输出 |
| §48 AC-DISK | 1 | 低磁盘故障注入 | ENV-A | 测试输出 + 日志 |
| §49 AC-LOG | 3 | 集成 + 轮转/诊断包检查 | ENV-A | 测试输出 + 样例包 |
| §50 AC-NFR-UI | 2 | 并发/响应性测试（AI 不阻塞 UI） | ENV-A | 测试输出 + 帧时序 |
| §51 AC-DPI | 0（组级 `ACG-DPI`） | 手工视觉 | ENV-C | 截图集 |
| §52 AC-PKG | 3 | ENV-C 打包与启动（Qt DLL、干净系统） | ENV-C | 安装包 Hash + 截图 |
| §53 AC-SMOKE | 0（组级 `ACG-SMOKE`） | 手工端到端 smoke | ENV-C | 操作记录 + 截图 |
| §54 AC-OPTIONAL | 2 | 环境矩阵（缺重型模型仍可启动） | ENV-C | 测试输出 |
| §55 AC-MODEL | 2 | 集成（下载进度、不完整不 Ready） | ENV-A | 测试输出 |
| §56 AC-OFFLINE | 0（组级 `ACG-OFFLINE`） | 网络隔离验证 | ENV-A | 日志 + 截图 |
| §57 AC-PRIVACY | 0（组级 `ACG-PRIVACY`） | 文案与触发点检查 | ENV-A | 截图 + 清单 |
| §58 AC-CONFLICT | 2 | 并发故障注入（Optimistic Write Guard、同能力写冲突） | ENV-A | 测试输出 + 状态转储 |
| §59 AC-SET | 0（组级 `ACG-SET`） | 单元 + UI | ENV-A | 测试输出 + 截图 |
| §60 AC-PROV | 0（组级 `ACG-PROV`） | 集成 + 数据检查 | ENV-A | 数据转储 + 截图 |
| §61 AC-CLEAN | 3 | 集成（Current/源文件不清理、Debug Artifact） | ENV-A | 测试输出 |
| §62 AC-ERROR | 0（组级 `ACG-ERROR`） | 单元 + 映射表检查 | ENV-A | 测试输出 |
| §63 AC-ERRUI | 0（组级 `ACG-ERRUI`） | UI 自动化 + 手工 | ENV-A | 截图 + 测试输出 |
| §64 AC-AUTO | 0（组级 `ACG-AUTO`） | 集成 + UI | ENV-A | 测试输出 |
| §65 AC-CLOSE | 2 | 集成（运行中关闭、Dirty 与 Running 分离） | ENV-A | 测试输出 |
| §66 AC-DOC | 3 | 文档检查 | 静态 | 检查脚本 + commit |
| §67 AC-SYNC | 0（组级 `ACG-SYNC`） | 契约/文档检查 | 静态 | 契约 + 复审报告 |

**合计：185 个编号 AC + 10 个组级标识，覆盖 D08 全部 61 个主题。**

## 10. 未编号扩展项与 01～07 补充内容

[D13 的"01～07 中需补充验收的内容"](../13_ACCEPTANCE_TRACEABILITY.md) 列出的 7 类条目（PDF/MOBI/网页导入、Plugin/Hooks、字体、Sakura 监控、检测与配色正确性、G06～G13 精确 AC、NFR 口径）。本文件对它们的处理约定：

- 这些条目**尚未成为编号 AC**，不得在验收中以"未列出"为由跳过；主责任 Task 先补设计或 AC，再由本文件登记执行方式。
- 新增 AC 必须写入 D08（保持编号/优先级体系），并在 D13 建立路由、在本文件登记执行方式；三者顺序不得颠倒。
- 检测 / 配色 / SourceStyle 的正确性验证沿用 §7 的质量方法，阈值同样为 `UNAPPROVED_THRESHOLD`。

## 11. 当前状态与未完成项

| 项 | 状态 | 说明 |
|---|---|---|
| 验收方法、环境档位、证据口径、性能协议、组级标识 | 已定义 | 本文件 |
| 素材取得 | **missing / planned** | 见 [Fixture Manifest](../fixtures/MANIFEST.md)；未取得任何素材，未提交未授权图片 |
| 性能实测 | NOT_RUN | 无应用实现、无 ENV-B/ENV-D 基准数据 |
| 模型质量实测 | BLOCKED | 无素材、无实现、阈值 `UNAPPROVED_THRESHOLD` 未获批 |
| 185 个编号 AC 的产品验证 | NOT_RUN | 无应用源码与可测试产物（D13 一致） |
| D08 / D13 产品定义 | 未改动 | 本文件不新增产品要求；D13 只增加回链 |

## 12. 变更控制

- 修改本文件的**方法层**（环境、次数、证据格式）需要新的已授权 Task 与固定 commit Review。
- 修改**阈值或范围**属于产品决定：必须先由用户批准，再同步 D08/D07 与本文件，并保留批准记录。
- 本文件与 D08 出现冲突时，不得自行裁决：以 D08 为准执行，并把冲突记录到 Gap Register 交由 Codex 处理。
- 素材许可变化必须同步 [Fixture Manifest](../fixtures/MANIFEST.md)，不得先提交素材再补授权。
