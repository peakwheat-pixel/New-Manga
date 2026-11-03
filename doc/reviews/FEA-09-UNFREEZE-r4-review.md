**结论：`changes_requested`；P0=0 / P1=4 / P2=3。A/B 包目前均不可作为获批方案进入语义修订提交或重冻。**

**1. 身份、对象与只读基线**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；本会话未参与 FEA-09 实现、I001 裁决或 r1–r4 起草/修订，未派发子代理。
仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
审查前后 HEAD 相同：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r4 为未跟踪工作树文件，8650 bytes，**不属于 reviewed_head 的提交内容**。
审查前后 r4 SHA-256 相同：`8609c67fb0d055264b1a9d25bdebb5595cb28561d9a4d49089736916384a1283`。
未修改仓库、配置或用户数据，未生成报告文件，未 commit/push；报告仅通过本输出交付。

**证据限制：指定的 `doc/reviews/FEA-09-UNFREEZE-r3-review.md` 不存在。**
工作树读取返回 ENOENT；`git ls-files` 与 `git log --all -- <path>` 均为空。
因此，以下 CLOSED/OPEN 按用户列出的六项问题和 r4 disposition 核验，**不能证明与原 r3 findings 全文逐字闭合**，也未验证其所引 `46f06092…` 指纹。

审查前后 `git status --porcelain=v1` 相同：16 项既有 ` D`、2 项 `??`。
`??` 为 `doc/reviews/FEA-09-UNFREEZE-{r3,r4}-amendments.md`。
16 项删除共同前缀：`verification/FEA-09/native-registry/`；下表每组均后接 `/isolated-data/host/source-access/`，各有 `registry.v1.dat`、`registry.v1.lock` 及所列两文件：

| 目录 | `quarantine/` 文件 | corrupt 文件 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `registry.v1.dat.corrupt-202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `fae26d327bb4463d940427d17881f9ae.dat` | `registry.v1.dat.corrupt-202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `2953b0220e7c424194e26d207017e793.dat` | `registry.v1.dat.corrupt-202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `189d4ab58a1c4194a5d9862b6701e88a.dat` | `registry.v1.dat.corrupt-202611031354042159987` |

**2. R3-001…R3-006 逐项结论**

| 原 ID | 判定 | 已修正部分、剩余问题与最小修复 |
|---|---|---|
| R3-001 | **OPEN** | referenced 仍返回 Page、降级行禁止回写、V 行不得过滤，方向正确；但混合返回改变现有 `PageRepository` 契约，调用方与序列化适配未冻结，且 Page 类型选择混入“可读”条件。按 R4-001 补齐。 |
| R3-002 | **OPEN** | 纯投影恒 null、wire 首次 resolve/publish、迁移禁 resolve/publish 已明确；正尺寸完整 DTO 得以保留。但 unavailable 页的合并顺序、全不可读章节、恢复位置及错误分类尚不能唯一实现。按 R4-002 补齐。 |
| R3-003 | **OPEN** | 取消 import-bound grant live 前置正确；fresh G 可以独立授权，原则上不违反 C-06。仍需冻结精确选择、撤销与 binding 变化的行为，并明确替换现有 `find_bound_for_source` 路径。按 R4-003 补齐。 |
| R3-004 | **OPEN** | token 文件名约束、同句柄消费删除能关闭部分路径与 stat→open 竞态；消费前 stat 不是 Host 创建身份，不能证明 stat 之前未替换；清扫路径也未继承完整安全规则。按 R4-004 补齐。 |
| R3-005 | **OPEN** | 单飞、三次失败、冷却起点/重置、cache hit 不计数不消费均有进展；错误映射与终止分支仍冲突，claim 后取消存在未定义窗口，启动清扫 Owner 未明确。按 R4-005 补齐。 |
| R3-006 | **OPEN** | 删除目标不再使用 V，软删/回收站对象仍纳入，修正正确；但摘要“标注 unavailable”超出现有 closed shape，不能同时声称无字节变化。其余表足以表达影响方向，尚需明确登记落点和未实现状态。按 R4-006 补齐。 |

**3. Findings（位置均为当前文件行号）**

**R4-001 — P1：混合返回尚未形成完整调用契约。**
位置：r4:23–31；r3 A2 §4.4；`src/application/library/ports.py` 的 `PageRepository`。
生产接口仍为 `get_page → Page | None`、`list_pages → list[Page]`；PageView 使用 `width_px/height_px`，没有 Page 的全部导航、锁态与编辑字段。
现有 `core_service.py:2289–2295/2552/3368–3370` 直接访问 `.width/.height/.source_filename`；只禁止强转不能防止读取失败或写流程误用。
此外，完整列页缺磁盘文件时仍可构造 Page；“Page 仅承载可读页”与纯 DB 投影、V/R 分离不一致。
最小修复：按字段可构造性决定 Page/PageView；保留未知 ID 的 None 语义；冻结独立访问器名称、公共字段、调用方分派与 typed 拒绝表，以及明确的 DTO 映射，禁止直接序列化混合 domain 对象。

**R4-002 — P1：Reader unavailable 扩展缺少可执行的顺序与进度语义。**
位置：r4:37–45/88；M2-C1 §6.3:915–956；`CoreServiceClient.cs:1227–1317`。
`unavailable_pages:[{page_id,reason_code}]` 即使内部排序，也没有 canonical order，无法与 `pages[]` 唯一合并；无法确定不可读页位于首、中、尾。
全不可读章节的返回、`initial_position` 指向 unavailable 页时的行为、可读页 `order` 是否保留空位也未冻结。
现有 CoreClient 只解析 `pages[]`，新字段不会自动进入 UI-1；“旧端忽略”只证明可解析，不能证明 V 页得到呈现。
最小修复：增加统一顺序信息或完整逻辑页顺序；冻结空/全不可读与 resume 规则、CoreClient 承接和旧端限制；列明哪些 typed R 失败进入 unavailable，发布故障等错误不得被一概吞掉。

**R4-003 — P2：fresh grant 方向成立，但授权切换边界仍需精确化。**
位置：r4:56–65/100；`source_read_refs.py:305–369/444–478`；`referenced/resolve.py:73–90`。
现有 `find_bound_for_source` 只查 import 建立的 `_bindings`；新注册的 fresh G 不会自然成为候选。
r4 未明确按 token 唯一选 G、四维 scope 的逐字段匹配及 binding 变化后的重新验证点；测试文字仍保留“撤销后仍可 resolve？”。
最小修复：明确 fresh-token 选择入口替换旧前置，匹配 source/version/entry/rendition 与当前授权关系；准入后、读取前重验。
仅旧 import grant 撤销且 G 仍有效可以继续；registry 撤销、G 撤销、EOF 必须沿用 C-06 fail-closed；binding/status/version 变化须拒绝或重新授权，冻结准确错误映射。
保持这些约束无需必然改 C-06；不得把“旧 grant 无需 live”解释为绕过当前 generation 或撤销集合。

**R4-004 — P1：文件创建身份与所有清理入口尚未闭环。**
位置：r4:64–65/75–77；r3 B1 消费段；`secrets.py:85–102/128–154`。
stat 后与句柄 identity 相等只证明两次观察一致；文件若在首次 stat 前已替换，复验仍会成功，无法兑现“拒绝替换”。
路径字符串位于私有目录也不能单独排除祖先 reparse、hardlink 或清扫时的对象替换；启动清扫目前只限定目录、名称和年龄。
最小修复：采用 Host 创建对象的可信 identity 映射，或保持创建句柄/等效不可替换所有权直到消费；明确完整祖先链、普通文件及链接边界。
消费与 Host 超时清理、启动清扫均须验证同一受管对象；删除使用已验证句柄，失败不得回退按未验证路径零填充/删除。
若 identity 通过新 wire 字段传递，应显式登记对应契约范围；不得暗加签名字段。

**R4-005 — P1：错误面与 claim 生命周期存在相互矛盾的结果。**
位置：r4:15/71–78；仍有效的 r3 B1 错误映射及冷却段。
r3 将路径非法映射 REQUIRED，r4 将 claim 失败中的路径非法/不匹配映射 DENIED；相同输入的优先级不唯一。
claim 与文件读取删除是分离步骤，claim 后立即取消并不意味着“Core 已读取并删除”；Host 超时删除还可能撞上 Core 独占句柄。
冷却直接拒绝与 cache hit 可返回的先后未规定；secret_ref 自身 expiry 的检查点也未明确。
最小修复：给出唯一决策顺序及 code/category/retryable 表；明确计数针对源解密失败，DPAPI/格式失败是否计数及成功重置时点。
claim 后进入不可跳过的 finally 清理，覆盖读取/解密/发布异常；Host 清理失败须有重试或孤儿回收。
指定启动清扫由 Host 负责，冻结 `<token>.bin` 匹配、TTL/年龄依据及安全对象校验；Core 不得另起无协调清扫。

**R4-006 — P2：C-04b “无字节改动”与 unavailable 标注不一致。**
位置：r4:51/84–89；C-04b:42–46。
现有 `DeletePreviewItem.contentSummary` 是 closed shape，仅有 chapters/pages/artifacts/deletedFiles/deletedBytes，没有 unavailable 字段；这些字段还参与 digest。
最小修复：明确 unavailable 只是已登记消费方的展示需求、不新增当前 wire 字段；若确需传输，登记 C-04b/M2-C1 amendment。
不得因只统计可读内容而缩减实际删除文件清单、保护披露或 digest 覆盖。
C-08/C-09/C-14/导出/UI-1 的影响方向基本齐全；载体须给出“不改依据或 amendment/Task”落点，特别避免把导出 typed skip 写成已经实现或已获冻结。

**R4-007 — P2：r3 Review 来源缺失，无法完成逐项闭合证明。**
位置：r4:4–5。
最小修复：DSH 原字节归档实际 r3 review，核验完整 SHA-256、reviewed_head 与 findings；再建立原文到 r4 条款的逐项映射。
不得根据 r4 disposition 反向重建原报告。

**4. 最小必须再改项与冻结判断**

A 包：补齐 Page/PageView 调用与 DTO 边界、Reader 顺序/进度/失败规则、C-04b 展示与协议边界。
B 包：补齐 fresh G 选择及撤销/绑定变化规则、可信创建身份与安全清理、唯一错误和终止状态机。
共同前置：补归档 r3 review；修订增量必须明确覆盖全部旧冲突条款。
r3 的正尺寸迁移基线、不可变资源内容、语义提交后精确字节复核，以及 r4 的 old/new blob 清单和 A→B 顺序可保留。
完成修订并获新上下文 approved、P0/P1=0 后，方可按既定流程提交契约语义、复核已提交字节，再仅元数据重冻；本报告不释放生产返修。

**5. 实际只读核验**

已读取 r1/r2 review 与提案、r3/r4 提案、所列冻结契约/记录/矩阵、I001 裁决，以及指定生产文件和 CoreClient Reader/Resolve 调用面；r3 review 缺失。

| 实际命令/核验 | 结果 |
|---|---|
| `git --no-optional-locks rev-parse HEAD`、branch、common-dir、审查前后 status | EXIT 0；上述基线和状态不变 |
| Node `fs.readFile/stat`、`crypto.createHash('sha256')` | r4 8650 bytes；前后指纹一致；r3 review ENOENT |
| `git ls-files -- <r3-review>`；`git log --all --format=… -- <r3-review>` | EXIT 0；均无记录 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；PASS all 17 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；PASS，3 warnings；部分中文输出乱码 |
| 常规 `exec_command` | Windows error 740；改用 Node 文件 API/直接子进程完成只读核验 |
| pytest/.NET/build/真实 IPC/DPAPI/迁移全链/并发竞态/泄漏扫描 | **NOT_RUN**；未创建测试数据库或产物 |

**推荐下一步：DSH 在 FEA-09 下准备 r5 并补齐审查来源，随后 Appointment 新上下文契约复核。可直接转发：**

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、`main`，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`；先刷新并保留既有变更。按 R4-001…007 交付 r5、原 r3 review 完整指纹及逐项 disposition，仅在登记范围内修改提案/载体；不改生产代码、Schema、依赖、UI、用户数据、历史证据，不 push。运行 check/pins，未运行项保持 NOT_RUN。新上下文复核 approved 且 P0/P1=0 后再进入 A→B 语义提交、已提交字节复核与元数据重冻；不提前释放 I001/I005。