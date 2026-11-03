**FEA-09 UNFREEZE r2 独立契约复核报告**

**结论：`changes_requested`；P0=0 / P1=6 / P2=2。A、B 两包均暂不可据此进入获批语义修订提交或重冻。** 可继续准备修订稿；生产返修仍须等待重冻及 DSH 范围授权。

1. **身份、对象与基线**

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；未参与 FEA-09 实现、I001 裁决、r1 起草或 r2 修订；未派发子代理，不参与后续返修。
仓库：`G:\CODEX\New Manga`；分支 `main`；Git common directory：`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`68a46dfe501f0dbe02d4e223817f3ff17e3bb99c`，未变化。
对象：未跟踪的 `doc/reviews/FEA-09-UNFREEZE-r2-amendments.md`，不属于上述提交内容。
提案：13642 bytes；审查前后 SHA-256 相同：
`7366902bf93014ebe4453aff3c68218a124b6549615a844d6d742fe3845c0230`。
r1 review 实际 SHA-256：`9fd8efb6ae4ab783e5ab0263a9bfa9414cad1a8028b07922a67dcbeed601ca44`，与 r2 引用前缀相符。

审查前后 `git status --porcelain=v1` 相同：16 项既有 ` D`，3 项 `??`。
3 项 `??` 为 `doc/reviews/FEA-09-UNFREEZE-{r1-amendments,r1-review,r2-amendments}.md`。
16 项 ` D` 的共同前缀为 `verification/FEA-09/native-registry/`；各目录后接 `/isolated-data/host/source-access/`：

| 目录 | quarantine 文件名 | corrupt 文件名 |
|---|---|---|
| `37d836da52c94ad082d1bd01dcad9ea0` | `78129efd63cd4a4ab5ccd56fd9a7f0e2.dat` | `registry.v1.dat.corrupt-202611031328183382729` |
| `59949b7674c84c5297963275759606bf` | `fae26d327bb4463d940427d17881f9ae.dat` | `registry.v1.dat.corrupt-202611031328047249567` |
| `94737b1ab618406b9329c68637a2decc` | `2953b0220e7c424194e26d207017e793.dat` | `registry.v1.dat.corrupt-202611031353035436397` |
| `d5e7ddf952c14c3b8e01ac92af56e6d4` | `189d4ab58a1c4194a5d9862b6701e88a.dat` | `registry.v1.dat.corrupt-202611031354042159987` |

quarantine 文件位于 `quarantine/`；每组另有 `registry.v1.dat`、`registry.v1.lock`。未推断删除原因。
只读声明：未修改仓库、Git 配置或用户数据；未创建报告文件，未 commit/push；仅通过本输出交付。

2. **U-001…U-009 逐项处置**

这里的 CLOSED 仅表示提案条款已处置该 finding，不表示实现已通过。

| ID | 判定 | r2 依据与剩余最小修复 |
|---|---|---|
| U-001 | **CLOSED** | §0、A1:31–59 明确独立 OR；负例限定两 witness 均失败，旧失败说明分支化。 |
| U-002 | **OPEN** | A1:42–45 增加布尔字段，但缺 source_hash 等字段的合法缺值形状，且 ReaderProjection 冻结 DTO 不允许零尺寸／缺 original；见 R2-001/002。 |
| U-003 | **OPEN** | A2:74 已删除主要矛盾，但“旧 complete”仍未统一正尺寸定义，“无 artifact 页可见”未限定时间及页删除；见 R2-003。 |
| U-004 | **OPEN** | B1:97–103 已补签名绑定，但 secret 文件本身的 token/path、reparse、替换及安全删除边界未冻结；fresh grant 重绑定与选择也未定义；见 R2-004。 |
| U-005 | **OPEN** | B1:103–106 补计数键、冷却和 PDF 接缝；仍缺原子消费、并发准入、锁定及拒绝分支的清理规则；见 R2-005。 |
| U-006 | **OPEN** | B1/B3 的新 capability 和四象限方向正确；A3 同键内容替换尚无完整失效规则，M2-C1 修改范围仍遗漏 ReaderProjection；见 R2-002/006。 |
| U-007 | **CLOSED** | A2:71/76 要求同连接、固定 t、三路径全部验证、非空资源禁跳 verifier，并要求破坏查询／mapper 必失败；具体边界见下。 |
| U-008 | **CLOSED** | 已删除 1298 页误述，反例改为 1–8；M2-C1 使用 2.12 系列标记。分包版本衔接仍须登记。 |
| U-009 | **OPEN** | C:126–128 补三种指纹及旧 pin，但批准提案后才生成契约正文，缺修订提交后的精确字节复核步骤；见 R2-007。 |

3. **A 包判断**

`V_managed=V_artifact∨V_copy_original` 自洽，符合 I001 方案 B；不要求补 ORIGINAL 行，不直接违反 C-01b SC-07/15/39 或 ADJ-001。
矩阵 1–8 的 witness 组合基本正确；其中 1、2 的“R 可读”必须以文件存在、受管根校验及读取成功为前提，不能由 V 单独推出。
page 时间／尺寸只限制 copy；revision 时间限制 artifact；父级软删同时否定两个 witness。thumbnail-only 可以 V 真、R 假。
P1–P5 原字节保留可行，但最终文件尚不存在，不能宣称已经验证字节不变。
必须同步替换 C-05 §3.1 总定义、§3.2 表及旧反例说明，避免“追加”后仍保留 managed 总分支仅为 artifact 的现行陈述。
C-15 §4.1 三谓词仍可分离；`original_available` 应明确表示何种数据库投影能力，不能冒充磁盘实时可读性。
迁移断言 2 的并集可实现、可判定；断言 5 对 thumbnail-only 无 original 的旧库阻断升级，是既定资源门禁，不能靠隐藏页规避。
断言 3 仍有 R2-003 的矛盾，因此目前不能整体认定迁移断言无假通过／无错误拒绝。

同连接构造 repository **本身不违反** C-15 §1。
允许的是同一受限连接上的纯查询与纯投影；不能调用当前完整 `handle_get_reader_projection`。
后者在 `core_service.py:3605/3620` 调用 resolve／publish，涉及资源读取、缓存／catalog 副作用，超出迁移回调允许范围。
应明确“生产纯投影构建路径”与 wire handler 的边界，资源检查仅经 `IResourceVerifier`；固定 t 还应传入基线和所有读路径。

4. **B 包判断**

fresh signed grant 与 payload 严格匹配，能阻止未签名的任意路径注入；**尚不足以覆盖验证后路径替换及删除目标安全**，见 R2-004。
新 capability `source.resolve-secret/1` 可区分当前同样宣告 `source.read/1` 的旧 Core；缺失时在创建／发送秘密前拒绝，解决旧 Core 静默忽略扩展的正常调用路径。
四象限可接受，但能力探测异常也须 fail-closed；新 Host 不得尝试发送后再靠 REQUIRED 判断兼容性。
B1 已明确 PDF raster 接缝；实现还须贯穿 protocol／adapter，保留无密码调用，并明确 bytes→文本转换及 PDF 错密的 typed 映射。
密码计数采用页＋版本是明确选择，但不等同于 source 级三次限制；若需要 source 级限制，须另行裁定，不能混称。
保留 Core minor=3 **可以接受**，无需仅因可选字段强制 bump；前提是 M2-C1 明文登记 capability 为强制配对条件及旧端拒绝面。
minor bump 不能替代安全校验，也不能自动解决 A 包 ReaderProjection 的破坏面。

5. **Findings（位置以 r2 行号为准）**

| ID | 级别 | 位置 | 触发、影响与最小修复 |
|---|---|---|---|
| R2-001 | **P1** | A1:42–45 | thumbnail-only 页可同时缺 source_hash、size 等导入列；r2 只放宽 ref／尺寸。`Page` 仍要求非空 source_hash（entities.py:51），不得用 thumbnail hash 冒充源 hash。冻结全部缺值字段及默认值、mode 限定和只读类型；禁止该投影经 add/update 回写 provenance。 |
| R2-002 | **P1** | A2:71/78；A3；C:129 | 要求 reader projection 返回无 original／零尺寸行，与 M2-C1:915–928 的正尺寸、必填 original/resource_ref/sha256 冲突；当前 handler 还会 resolve/publish。明确纯投影与 wire 投影，冻结不可读行 DTO、兼容处置及错误呈现；将 M2-C1 Reader/相关消费方纳入 A 包，迁移回调不得调用发布型 handler。 |
| R2-003 | **P1** | A2:74；C-15 §1 断言 1/3 | 旧 `_COMPLETE_PAGE_WHERE` 只要求尺寸非 NULL，C-15 complete／v7 回填要求 >0；宽0行使集合相等不可满足。r2 又无条件称旧 complete 无 artifact 可见，遗漏未来时间／页软删。固定正尺寸基线及异常旧行 disposition，同步断言1/3，明示可见需完整 copy witness。保留零尺寸／未来／软删反例。 |
| R2-004 | **P1** | B1:97–103；C-16 §7.3/5 | signed path 相等不证明消费时仍为原 secret；现有 secrets.py:128/154 按路径读、零填充和删。冻结 token→私有目录文件名映射、TTL≤grant、无 reparse／替换的同一对象消费删除，未验证路径绝不清理。定义 fresh grant 到既有 binding 的重绑定及按 secret 精确选 grant，不能依赖随机 grant_id 排序或已过期 import grant。另明确 resolve 携带 path 对“绝对路径仅在签名 grant”规则的窄例外，或改为仅 token 查找。 |
| R2-005 | **P1** | B1:103–105 | 只锁计数允许多请求在第三次失败前同时开始解密；“一次性”未定义 token 原子 claim，重放可重复读。锁定期、授权失败、cache hit、取消与崩溃的清理／计数效果也未唯一确定。冻结准入＋消费＋计数的线性化、冷却起点、哪些错误计数、cache hit 是否重置；拒绝分支由 Host 清理自己创建的文件，Core 仅清理已验证对象，崩溃由启动孤儿清扫恢复。 |
| R2-006 | **P1** | A3:84–86 | 声称 first-publish-wins 不变，却允许摘要变化后同 `resource_id`、同 `"original"` revision 更换内容；未规定 Host 热缓存、已签发资源引用／lease 的失效和并发发布。冻结不可变内容方案，或完整规定内容代次／失效／重发语义；覆盖 original→copy 回退及并发旧 revision，不得仅比较 revision.file_hash 与 catalog。 |
| R2-007 | **P2** | C:126–128 | 当前先批准提案、后编辑契约、再重冻，未保证契约实际字节已复核。改为语义修订提交→固定各文件三种指纹→新上下文核对精确正文→冻结提交仅元数据→§1B 逐项差异；旧 pin/Review 保留。 |
| R2-008 | **P2** | A3/B2/C:129/E | 下游仅写“登记”尚非影响记录；遗漏 C-14、UI-1 的具体消费行为，A/B 共改 M2-C1 又无后包基线。补影响表：C-04b 内容摘要、C-08 快照/资源失败、C-09 迁移备份、C-14 缓存/lease、导出、UI-1 密码重试与不可读页；每项给不改依据或 amendment/Task。B 固定 A 后 M2-C1 指纹及唯一版本链。 |

6. **拆包、冻结与进入条件**

按 I001／I005 拆 A、B 合理，不必另建密码专用契约；建议 A 先完成，B 基于其最终 M2-C1 字节。
C-06 已有 secretRef、全字段签名、四维 scope、session／expiry／撤销语义；保持这些不变时，fresh grant 补充无需必然 UNFREEZE C-06。
若最终采用新增 grant 字段、跨页／跨版本继承或放宽授权，则必须显式纳入 C-06，不能由 C-16 单方面覆盖。
三种指纹、§1B、旧 pin 保留与 M2-C1 单独登记方向正确；`verify_pins.ps1` 只覆盖17对象，不能为 M2-C1 或语义兼容背书。
当前下游影响仅是待办，尚未完成登记；当前 P1 未闭合，不能进入获批重冻或释放 I001/I005 生产返修。

7. **实际只读核验与结果**

已读取指定 r2、r1 review／提案、契约、裁决、impl review、FROZEN／matrix／verify_pins，以及指定生产代码；补查 Page、source_read_refs、M2-C1 Reader DTO 和协作规则。

| 实际命令／核验 | 结果 |
|---|---|
| `git --no-optional-locks rev-parse HEAD`、branch/common-dir、审查前后 status | EXIT 0；上述基线、状态不变 |
| Node 只读文件 API＋SHA-256 | r2 13642 bytes，前后指纹一致 |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | EXIT 0；**PASS all 17** |
| `pwsh -NoProfile -File tools/governance/check.ps1` | EXIT 0；**PASS，3 warnings**（非终态 Task、STATUS/PLAN 体量） |
| `C:/Python314/python.exe -B -c <纯内存探针>` | EXIT 0；当前 Page 缺 hash 抛 ValueError；宽0旧谓词计1、C-15正尺寸谓词计0 |
| 常规 `exec_command` | Windows error 740；改用 Node 只读 API／直接子进程，无提权 |
| pytest／.NET tests／build／真实 IPC／DPAPI／迁移全链／并发及泄漏扫描 | **NOT_RUN**；本轮未创建测试产物或数据库文件 |

内存探针仅验证当前类型与谓词差异，不是 r2 实现验收。治理 PASS 仅证明当前检查范围与既有冻结指纹。

8. **推荐下一步与可转发指令**

推荐由 **DSH** 在 FEA-09 下处置本报告并准备 r3；本 Reviewer 不返修。建议不等于 Task 释放。

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、`main`，base/head=`68a46dfe501f0dbe02d4e223817f3ff17e3bb99c`；执行前刷新并保留既有变更。按 R2-001…008 修订 A/B 精确条款、完整投影 DTO、迁移基线、安全消费状态机、资源失效及下游影响表，交付 r3 与逐项 disposition。仅在登记写域内修改提案、必要契约及冻结治理文档；禁止生产代码、Schema/依赖、UI实现、用户数据、历史证据改写及 push。先固定语义修订提交与各文件三种指纹，再 Appointment 新上下文只读复核；approved 且 P0/P1=0 后方可仅元数据重冻。运行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，M2-C1 单独核验；未运行项保持 NOT_RUN。重冻及范围授权完成后再分配实现。