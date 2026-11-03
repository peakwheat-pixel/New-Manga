**结论：`changes_requested`；P0=0 / P1=2 / P2=0。**
接受“冻结契约语义、委托实现设计”的架构方向；r5 仍有两处语义缺口，A/B 包目前均不可作为获批方案进入语义修订提交或重冻。

**1. 身份与审查基线**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；本会话未参与 FEA-09 实现、I001 裁决、r1–r4 起草或 r5 修订，未派发子代理。
仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
审查前后 `reviewed_head` 相同：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r5、r4 提案、r3/r4 review 与 impl-design 均为未跟踪工作树文件，**不属于 reviewed_head 的提交字节**。

| 文件 | SHA-256 |
|---|---|
| r5-amendments（9876 bytes） | `b6714dff1eb67faccf217c81112d79300cec39f9645e8c51495dff8860ecb1b2` |
| r4-amendments（8650 bytes） | `8609c67fb0d055264b1a9d25bdebb5595cb28561d9a4d49089736916384a1283` |
| r4-review | `ae3a775bb481bc8b4f593fcbd0583a4361b6f77321a2f0c21753d2762fd6cc0c` |
| r3-review | `75d89a735396543f653127423739259f2db9f3ddfde9eaf2cee40a9a9ca96259` |
| impl-design | `b245010670377f2c783ca14dba4eabf6f87fe57196e77054ce607d38b41e542b` |

审查前后 r5、r4-review、impl-design 指纹一致；结束时核验其余上述指纹。
审查前后 `git status --porcelain=v1` 完全相同：16 项既有 ` D`、6 项 `??`。
`??`：上述五类文件，加 `doc/reviews/FEA-09-UNFREEZE-r3-amendments.md`。
16 项删除共同前缀为 `verification/FEA-09/native-registry/`；每组后接 `/isolated-data/host/source-access/`：

| 目录 | quarantine 文件 | corrupt 后缀 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `fae26d327bb4463d940427d17881f9ae.dat` | `202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `2953b0220e7c424194e26d207017e793.dat` | `202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `189d4ab58a1c4194a5d9862b6701e88a.dat` | `202611031354042159987` |

每组含 `registry.v1.dat`、`registry.v1.lock`、`quarantine/<文件>`、`registry.v1.dat.corrupt-<后缀>`。
只读声明：未修改仓库、配置、用户数据，未生成报告文件、commit 或 push；仅通过本输出交付。

**2. R4-001…R4-007 契约层闭合判定**

| Finding | 判定 | 依据 |
|---|---|---|
| R4-001 | **CLOSED** | 按数据可构造性区分 Page/降级投影，V 全集可观察、最低字段集、禁止回写/伪 provenance、未知 ID None 已冻结；端口、调用方分派与 DTO 映射可委托实现 Review。 |
| R4-002 | **OPEN** | logical_order、全不可读响应、保留不可读逻辑锚点及排除发布/内部错误已有进展；`RTyped` 未定义，无法唯一判定哪些失败进入 unavailable。见 R5-001。 |
| R4-003 | **CLOSED** | 恰一个 fresh G、四维匹配、多匹配拒绝、撤销/EOF fail-closed、binding/status/version 变化拒绝已明确；无需依赖旧 import grant 存活。缓存分支不得绕过这些授权要求。 |
| R4-004 | **CLOSED** | 在明确排除 Host 身份已被攻破的威胁模型下，规范 token/path、祖先无 reparse、普通文件、独占同句柄消费与禁止清理未验证对象形成可审查不变量；创建身份映射和打开标志可委托。 |
| R4-005 | **OPEN** | “错误优先级表冻结”没有对应冻结表；impl-design 仍含冲突结果，缓存/冷却在唯一顺序中的位置未定。见 R5-002。 |
| R4-006 | **CLOSED** | 明确 C-04b 字节、现有字段及 digest 覆盖不变；unavailable 仅为 UI-1 展示需求，不再暗加 closed-shape 字段。 |
| R4-007 | **CLOSED** | r3 review 现已存在，完整哈希与 r5 引用前缀、报告 reviewed_head 相符；已读取原文，可核对发现链。Git 提交归档仍待 DSH。 |

CLOSED 仅指提案的契约处置，不表示实现或产品验收通过。

**3. 架构裁决与 A/B 包**

**架构裁决可接受，但当前委托尚未完整。**
函数签名、类型组织、mapper/调用方分派、锁与句柄 API、finally 代码结构可以不进入冻结字节。
错误结果、授权先后、计数与缓存行为属于外部可观察语义或安全不变量，必须有冻结判据；实现 Review 不能代替缺失的契约裁决。

**A 包：核心方案自洽且原则上可实现，整体仍 OPEN。**
C-05 独立 OR、witness 不互相否定、V/R 分离符合 I001 方案 B。
C-15 正尺寸基线、断言1/3的异常行处置、断言2同连接/固定 t/三路径核验、断言5非空禁跳 verifier，以及最低投影字段集均可落地。
合格 artifact 使 incomplete 页可见的规则，最终正文须同步消除 C-15 §4.3 的无条件“incomplete 不可见”措辞。
M2-C1 managed 同键摘要冲突拒绝、缺文件自愈仍比较既有摘要，保留不可变资源语义；不得扩大为限制 C-14 的 referenced rendition 重建。
Reader unavailable 的错误分类尚未闭合，因此 A 包暂不可整体批准。

**B 包：授权与能力设计成立，整体仍 OPEN。**
fresh signed G、resolve 仅 token 无 path、创建秘密前能力门禁，以及继承 r3 的旧/新 Host×Core 四象限方向可接受。
保持 Core `2.3` 不必然违规；必须在最终 M2-C1 amendment 中记录强制能力配对和准确拒绝面。
沿用现有 grant 字段、签名、四维 scope、预算、identity、generation 与即时撤销语义时，**无需额外 C-06 UNFREEZE**。
若实现选择绕过当前授权返回缓存，或新增签名字段/扩大 scope，则不在此判断范围内，须重新登记契约范围。

**4. 最小必须再改项**

**R5-001 — P1：Reader unavailable 的错误分类没有冻结判据。**
位置：`r5-amendments.md:12`、`:48`；`impl-design:28`。
`RTyped` 不是已有闭集或已定义谓词；impl-design 又概括为“resolve typed 失败的 V 页进 unavailable”。
授权撤销、identity 变化、预算超限、`INPUT_REVISION_CHANGED` 等均是 typed，不能从现文本唯一判断应返回整请求错误还是逐页 reason_code。
**最小修复**：冻结可进入 unavailable 的明确错误集合或无歧义分类规则，列出其余错误向上传播；同时明确 `pages[].order` 与 `logical_order` 共用 V 全集序、旧客户端忽略 unavailable 的限制及允许配对范围。无需冻结 UI 占位实现。

**R5-002 — P1：秘密通道的唯一错误结果与缓存/冷却边界仍未冻结。**
位置：`r5-amendments.md:15`、`:57`；`impl-design:39–45`。
r5 宣称冻结错误表，但正文没有表；未冻结设计将零匹配映射 DENIED，同时将缺失/过期 token 映射 REQUIRED，路径不匹配也同时落入 DENIED/REQUIRED。
设计中的“先查缓存，命中直接返回”与契约 capability→binding→G 顺序缺少明确衔接；缓存命中是否改变失败计数、冷却结束转移及并发准入的计数边界也不能仅由“3次/300s”推出。
**最小修复**：将一张无重叠的条件→code/category/retryable表纳入冻结条款，明确继承或替换 C-16 既有错误优先级。
补充少量语义：缓存返回仍须当前授权；缓存与冷却谁优先；计数 key/重置与并发边界；消费时校验 G 和 secret_ref 两层 expiry；claim 后终止不复用 token，清理失败由 Host 安全重试/孤儿回收。
锁类型、选择函数位置和 finally 写法继续委托实现设计。

**5. 冻结流程与实际验证**

A→B 顺序正确：A 语义提交→三指纹/old-new blob清单→新上下文复核已提交字节→仅元数据重冻；B 基于 A 最终 M2-C1 字节重复执行。
保留旧 pin/历史载体及 §1B 差异；M2-C1 单独登记，17 pins 不覆盖它。
当前应先完成上述两项语义修订并获新上下文 approved、P0/P1=0，再进入该流程；本报告不释放 I001/I005 实现。

| 核验 | 结果 |
|---|---|
| Git HEAD/branch/common-dir/status、文件读取与 SHA-256 | 已执行；前后状态一致 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；PASS，3 warnings，部分中文输出乱码 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；PASS all 17 |
| pytest/.NET/build/真实 IPC/DPAPI/迁移/竞态/泄漏扫描 | **NOT_RUN** |

已覆盖指定提案与 Reviews、impl-design、冻结契约/记录/矩阵、I001 裁决，并抽查所列生产接缝；本轮不签发实现验收。

**推荐下一步：由 DSH 在 FEA-09 下处置本报告，准备最小语义修订，再 Appointment 新上下文契约复核。可直接转发：**

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、`main`，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`；先刷新并保留既有变更。仅在登记写域内修订提案/impl-design及必要治理记录，按 R5-001/002补齐 Reader 错误分类和秘密通道唯一错误表、缓存/冷却语义；不扩为实现细节清单，不改生产代码、Schema、依赖、UI、用户数据或历史证据，不 push。交付逐项 disposition、修订稿和完整指纹，运行上述 check/pins；未运行项保留 NOT_RUN。新上下文复核 approved 且 P0/P1=0后，再按 A→B执行语义提交、已提交字节复核及元数据重冻；重冻和范围授权完成后再释放实现。