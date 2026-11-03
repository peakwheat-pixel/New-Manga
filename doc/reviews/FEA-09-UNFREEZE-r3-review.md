**FEA-09 UNFREEZE r3 独立契约复核报告**

**结论：`changes_requested`；P0=0 / P1=5 / P2=1。A、B 包均未逐项闭合 r2 findings，当前均不可进入获批语义修订提交或重冻；可继续准备修订提案。**

1. **身份、对象与只读基线**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；未参与 FEA-09 实现、I001 裁决、r1/r2 起草或 r3 修订；未派发子代理，不参与返修。  
仓库：`G:\CODEX\New Manga`；分支 `main`；Git common directory：`G:/CODEX/New Manga/.git`。  
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。  
对象：未跟踪的 `doc/reviews/FEA-09-UNFREEZE-r3-amendments.md`，**不属于 reviewed_head 的提交字节**。  
r3：14761 bytes；审查前后 SHA-256 均为：  
`46f060928871f211dbd0a35fa03db4cb12cefa3a1a95c6b84f741b363a6aeb17`。

审查前后 `git status --porcelain=v1` 完全相同：r3 为 `??`，16 项既有 ` D`。删除项共同前缀为 `verification/FEA-09/native-registry/`，各目录后接 `/isolated-data/host/source-access/`：

| 目录 | quarantine 文件 | corrupt 文件 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `registry.v1.dat.corrupt-202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `fae26d327bb4463d940427d17881f9ae.dat` | `registry.v1.dat.corrupt-202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `2953b0220e7c424194e26d207017e793.dat` | `registry.v1.dat.corrupt-202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `189d4ab58a1c4194a5d9862b6701e88a.dat` | `registry.v1.dat.corrupt-202611031354042159987` |

每组另含 `registry.v1.dat`、`registry.v1.lock`；quarantine 文件位于 `quarantine/`。未推断删除原因。  
未修改仓库、Git 配置或用户数据，未创建报告文件，未 commit/push；报告仅经标准输出交付。

2. **R2-001…R2-008 逐项结论**

CLOSED 仅表示提案层面闭合，不表示实现验收通过。

| Finding | 判定 | 依据与最小修复 |
|---|---|---|
| R2-001 | **OPEN** | NULL hash/size、正尺寸或 NULL、禁止回写，使 thumbnail-only **具备可表达形状**；不再用 thumbnail/clean hash 冒充源 hash。但 managed 专用 PageView 被无条件用于 get/list，缺 referenced witness，并改变现有 Page 调用契约；见 R3-001。 |
| R2-002 | **OPEN** | M2-C1 Reader amendment 已纳入，迁移回调禁 wire handler／resolve／publish 已明确；但纯映射无法凭 PageView 生成首次发布资源引用，全部不可读、排序和恢复锚点也未冻结；见 R3-002。 |
| R2-003 | **CLOSED** | 正尺寸基线与断言1/3一致；零/负/NULL尺寸保持 incomplete；无 artifact 的软删／未来 complete 页仍不可见。注意当前 C-15 §2 SQL **已经要求正尺寸**，主要待改的是旧基线和断言，不能把既有 SQL 描述成新增修复。 |
| R2-004 | **OPEN** | payload 仅 token、path 来自签名 grant、拒绝未验证路径清理、同句柄消费方向正确；fresh grant 接续、四维绑定与秘密文件 identity 的可信来源仍缺；见 R3-003/004。 |
| R2-005 | **OPEN** | 原子 claim、逐 key 串行准入、第三次失败起冷却、不消费 cache hit 已补；cache hit 是否重置、取消／超时及冷却结束转移仍未唯一确定；见 R3-005。 |
| R2-006 | **CLOSED** | managed 同键内容不变、摘要冲突 typed 拒绝、original→copy 同受约束、单飞发布，已取代同键替换。必须将缺文件自愈解释为**仍先比较既有摘要**；不得因文件缺失改写摘要。 |
| R2-007 | **CLOSED** | 语义提交→逐文件三指纹→新上下文复核已提交字节→仅元数据冻结，流程可执行；§0 已要求 §1B 仅元数据差异。最终状态行改动后仍须计算最终 pin，保留语义提交指纹与旧 pin。 |
| R2-008 | **OPEN** | 消费方名称已齐，A→B 的 M2-C1 唯一版本链与 B 基线指纹顺序明确；但表内删除、快照、导出结论尚不能作为“无改动”依据；见 R3-006。 |

3. **剩余及新增 findings**

以下位置均为 r3 行号。

| ID | 级别 | 位置 | 触发、影响与最小修复 |
|---|---|---|---|
| R3-001 | **P1** | A2:51–67；A1:44 | managed 专用 `visibility_witness` 无 referenced 值，却无条件令 get/list 返回 PageView；还移除现有调用方使用的 `source_filename`、`width/height`、锁态及实体修改能力。生产 `library.py:426–479` 当前读出 Page、写回 Page。**最小修复**：明确 managed 投影适配范围、referenced 原路径和实体写路径；给字段来源／优先级／NULL规则及消费者迁移表。禁止将 original revision 投影 hash 作为导入 provenance 回写。同步修正 C-15 §4.3“incomplete 不可见”，限定 copy 分支，避免再次否定 artifact witness。 |
| R3-002 | **P1** | A2:67；A3:91 | 新库首次打开普通可读页时，纯 PageView 没有已发布 `resource_ref`；wire 又禁止 resolve/publish，无法满足 M2-C1:920 的必填 original 引用。translated 引用同样缺生产者。`unavailable_pages` 仅 ID/reason，未定义占位顺序、全不可读响应和 `initial_position`。**最小修复**：冻结投影／资源准备的分阶段流程，迁移只调用纯阶段；明确引用尚未发布与资源真正不可读的区别，并定义 canonical order、空集及恢复规则。 |
| R3-003 | **P1** | B1:104–109 | 第2步仍要求 **import-bound grant live**；fresh grant 注册不会调用 `bind_imported_entry`。原 grant 超过300秒或重启后，即使新 G 合法仍无法读取。第3步仅列容器 facts/kind/locator，未明确 G 的 source/version/entry/rendition 与请求绑定相等；同容器其他页的 token 可通过该文字条件。**最小修复**：定义 fresh G 对持久 binding 的严格再授权／绑定流程，取消对旧短期 grant 存活的依赖；按 token 精确选 G，验证完整四维及物理身份，禁止跨页／源／版本重用。 |
| R3-004 | **P1** | B1:105–112、115 | “文件 identity 与 token 映射一致”未定义映射何时建立、由谁认证及如何到达 Core；现有签名 secret_ref 只有 token/path/expiry。消费时才观察 identity 不能证明文件未被替换。秘密自身 expiry≤grant 也未写成消费校验。**最小修复**：冻结可信的创建时对象绑定及安全打开方案，校验 secret 和 grant 两层 expiry；零填充／删除必须作用于同一已验证对象。Host 拒绝、超时及启动孤儿清扫也须拒绝 reparse／替换，不能退回按路径擦除；若新增签名字段，显式扩大 C-06 修订范围。 |
| R3-005 | **P2** | B1:113–114；E:158 | “成功重置”未说明 cache hit；冷却结束是否清零、取消／超时发生在 claim 前后如何计数／清理／释放准入也无确定转移。继承 C-16 的启动清扫可覆盖孤儿清理方向，但测试清单不能替代状态规则。**最小修复**：补状态转移／责任表，明确 cache hit、冷却结束、取消、超时、EOF、崩溃，以及 claim 后终止时 token 永不复用。 |
| R3-006 | **P1** | D:147–152 | “删除目标仍用 V”错误：软删页按 P1 已不满足 V，但仍是彻底删除及保护披露对象；只对可读页计算内容摘要可能漏报待删文件／字节。C-08 没有授权此处凭空新增 `resource_ref=null+reason_code` 快照形状；导出“typed skip/错误”也未唯一选定，且遗漏稳定性 S。**最小修复**：删除目标／保护／文件清单独立于 V/R完整枚举；内容摘要按真实清单计算，无法枚举则 fail-closed。快照给出具体 DTO及失败处置依据，必要时 amendment；导出保留 S并冻结不可读目标的确定行为。 |

4. **兼容、资源与分包判断**

M2-C1 **必须正式修订**，r3 已承认此范围。可选 `unavailable_pages` 字段本身不必强制 minor bump；但“旧客户端忽略”不能证明页过滤、资源准备和初始位置语义兼容。须先解决 R3-002，再按 §3.2登记兼容矩阵及必要能力／版本配对。仅提高 minor 不能补齐这些语义。

B 的可选 token＋新 capability 可保留 Core `2.3`，前提是创建秘密前 fail-closed，且只对需要此能力的操作应用门禁。生产 `HostCommandDispatcher.cs:419–421` 当前只转发 page_id，后续实现必须贯穿 token 与脱敏。

采用不可变 managed 资源后，**无需仅为此增加内容代次**：旧引用继续指向旧不可变字节，新的冲突 resolve 返回 `INPUT_REVISION_CHANGED`。文件缺失重建仍须保留既有摘要约束；此规则应明确限定 managed original，不能阻止 C-14 允许的 referenced rendition 参数／decoder 变化与损坏缓存重建。

**A 包：不可进入获批语义修订提交或重冻**，先闭合 R3-001/002/006。  
**B 包：不可进入获批语义修订提交或重冻**，先闭合 R3-003/004并处置 R3-005，再基于 A 定稿的 M2-C1 字节推进。生产 I001/I005 返修仍等待重冻及 DSH 范围授权。

5. **实际只读核验**

已交叉读取指定提案／Reviews／裁决、契约及生产文件，并核对当前 Task、Status、Plan、rolling checkpoint。未读取无关历史证据目录。

| 实际命令／核验 | 结果 |
|---|---|
| `git -c safe.directory=G:/CODEX/New Manga -C "G:/CODEX/New Manga" rev-parse HEAD`；branch、toplevel、absolute common-dir | EXIT 0；与上述基线一致；仅命令级配置 |
| 同前缀 `git status --porcelain=v1`，审查前后 | EXIT 0；字节完全相同 |
| Node `fs.readFile`／行号切片；`crypto.createHash('sha256')` | r3 前后14761 bytes及哈希相同；r2 review 哈希前缀 `b0c5ec75`与r3引用相符 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；**PASS，3 warnings** |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；**PASS all 17** |
| 常规 `exec_command` | Windows error 740；改用 Node 只读 API／直接子进程，无提权 |
| pytest／.NET tests／build／真实 IPC／DPAPI／迁移实测／并发／泄漏扫描 | **NOT_RUN**；未创建测试数据库或产物 |

治理 PASS 与17项 pin只验证当前治理及既有冻结对象，不覆盖未提交 r3 的语义，也不为 M2-C1 amendment 背书。

6. **推荐下一步与可转发指令**

推荐由 **DSH** 在 FEA-09 下归档、处置本报告并准备 r4；本 Reviewer 不参与返修。建议不等于 Task 释放。

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、`main`，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`；先刷新状态并保留既有16项删除与r3。按 R3-001…006交付 r4、逐项 disposition、完整投影／授权／秘密生命周期规则及下游影响依据；仅修改登记范围内的新提案与必要治理文档，禁止生产代码、Schema/依赖、UI、用户数据、历史证据改写及 push。委派新上下文只读复核；approved且P0/P1=0后，按A→B执行语义提交、三指纹、已提交字节复核、仅元数据冻结及§1B差异登记。运行上述check/pins命令，M2-C1单独登记指纹；未运行项保持NOT_RUN。重冻并明确授权后再释放实现。