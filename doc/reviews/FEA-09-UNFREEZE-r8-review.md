**结论：`changes_requested`；P0=0 / P1=2。**  
认可契约收敛方向；仍有两项外部可观察语义未闭合，无需为此冻结内部算法。

Reviewer：Codex，独立上下文 `/root`，`reviewer_kind=agent`；未参与指定实现、裁决或提案起草修订，未派子代理。仅标准输出交付；未修改文件、commit 或 push。

仓库：`G:\CODEX\New Manga`；branch=`main`；common directory=`G:/CODEX/New Manga/.git`。  
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。  
r8 为未跟踪工作树文件，7043 bytes，**不属于 reviewed_head 的提交字节**。  
读取及结束复验 SHA-256 相同：`5779ce52b87b60fb85794643bc48fc3104b3667a9c0d18d25672f6eaa815f687`。

审查前后 `git status --porcelain=v1` 完全相同：16 项既有 ` D`、11 项 `??`。  
删除项均属 `verification/FEA-09/native-registry/` 四组既有 registry/lock/corrupt/quarantine 文件。  
未跟踪项为 impl-design、r3–r6 amendments/review、r7/r8 amendments。  
状态输出 SHA-256：`0e203d153e973dc4c82e81f00642fbd5ed6eca89e99670fa20c660893c238af2`。

**证据限制：`doc/reviews/FEA-09-UNFREEZE-r7-review.md` 不存在，读取为 ENOENT，Git 全历史路径查询为空。**  
因此不能证明与 r7 原始三项 findings 逐字闭合；以下按用户指定的 R6-001/002/003 对应面核验。已核对其余指定提案、Reviews、impl-design、契约、冻结记录/矩阵与 I001 裁决。

1. **三项对应面的判定**

| 对应面 | 判定 | 依据 |
|---|---|---|
| R6-001：Reader 分类与恢复 | **OPEN** | r8:37 引用 r6，而 r6 的 REQUEST 集合兜底不完整；r7 的完整补集规则未被明确继承。resume 边界仍未确定。 |
| R6-002：错误结果与 expiry | **OPEN** | r8:52 已恢复 C-16 §6 category/retryable；但 r8:53 继承 r6“双层任一过期→REQUIRED”，与既有 grant 过期→`SOURCE_GRANT_EXPIRED` 冲突。 |
| R6-003：缓存授权与秘密选择 | **CLOSED（契约语义）** | r8:47–50 已分离当前授权与 secret 消费：缓存仍需有效授权，但不需要 token/claim；秘密消费须唯一匹配，重放/多义拒绝。选择函数可委托。 |

CLOSED 仅指提案语义，不代表实现验收通过。

2. **必须进入冻结字节的最小项**

**R8-001 — P1：Reader 的响应边界与恢复结果仍不确定。**  
位置：r8:37；继承的 r6 §1；M2-C1 §6.3。

- 固定 PAGE_UNAVAILABLE 集合或等价明确分类，并规定**全部其余错误保持原 envelope 整请求失败、不返回部分成功**。可直接采用经裁定的 r7 分类，无需冻结遍历顺序。
- 明确 resume 锚点自身可读时是否包含该页；锚点后没有可读页但前方有时，返回何种确定结果。
- 明确 `unavailable_pages` 保留 `{page_id,reason_code,logical_order}`；r8 的二字段写法须与所引 r6 消歧。

这些决定客户端收到成功还是失败、如何恢复阅读及如何显示原因，属于 wire/产品语义；实现测试不能自行选择契约答案。

**R8-002 — P1：双层过期及秘密失败的可观察错误规则未消歧。**  
位置：r8:52–53；r6 §2.2；C-16 §2/§3/§6。

- 明确 grant 自身过期与 secret_ref 过期各自的 code，删除“任一过期→REQUIRED”与既有映射的冲突。
- 明确 resolve 继承或修订 C-16 的错误选择规则；新增秘密条件有重叠时，给出互斥分类或允许结果边界即可。
- 无需规定检查函数顺序；但“同输入唯一、测试锁定”不足以裁决两个实现分别稳定返回 REQUIRED 与 EXPIRED 是否都合规。

3. **不变量及安全性**

V/witness 独立 OR、V/R 分离、referenced 模式隔离已覆盖 I001 必要语义。  
迁移正尺寸基线、分支守恒、同连接/固定 t/三路径、非空 verifier 与破坏测试具备判别力；原有人工数据、Lock、current/pinned 守恒须继续保留。  
投影最低字段、NULL、禁止非 original hash 冒充和禁止回写，足以约束数据边界；端口及 mapper 可委托。  
resolve 的当前授权、唯一秘密匹配、一次性消费、路径验证、同句柄清理、缓存授权及泄漏审计，在继承 C-06/C-16 撤销、预算及 r5 威胁模型的前提下，**未发现新增必须扩域的安全空洞**。  
资源不可变须保留“缺文件自愈仍比较既有摘要”，且只约束 managed original；不得限制 C-14 合法 rendition 重建。  
能力门禁、四象限与 token-only 请求方向可执行；无需仅因可选字段强制提升协议 minor。

4. **委托、冲突规则与冻结流程**

“实现设计委托＋独立实现 Review＋测试矩阵”可执行；锁、选择算法、句柄 API、DTO 映射及内部遍历次序均可委托。  
impl-design §3 已规定**契约优先**；但当前 §2.2 仍含旧 G/token 前置及缓存直接返回，必须同步，不能作为已完成委托。仅设计冲突应修设计；只有改变冻结语义才需 UNFREEZE。  
测试矩阵覆盖面足够，实施时须逐条绑定不变量、预期结果与负例；上述两项语义补齐后，独立 Review 才有完整判据。

A/B 拆分、A→B、语义提交→已提交字节复核→仅元数据冻结均可执行。  
M2-C1 单独登记足够：须含精确版本字节、三指纹、old/new blob、diff、兼容/错误面及批准身份；17 pins 不覆盖它。  
r8 §4 的裁决须显式处置 findings；“待裁决”不能同时记作 approved/P0/P1=0，§3 前置仍须满足。

5. **验证与推荐下一步**

`check.ps1`：EXIT 0，PASS，3 warnings；`verify_pins.ps1`：EXIT 0，17/17 PASS。  
pytest／.NET／build／真实 IPC／DPAPI／迁移实测／竞态／泄漏扫描：**NOT_RUN**。机械 PASS 不覆盖 r8 语义或未来实现。

推荐下一步：由 **DSH** 在 FEA-09 下补齐上述两项最小语义并同步设计，再 Appointment 新上下文复核；本 Reviewer 不参与返修。可直接转发：

> DSH：请原字节归档本报告。恢复点 `G:\CODEX\New Manga`、main，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`；先刷新并保留既有变更。仅在登记写域内修订新提案、impl-design及必要治理记录，补齐 R8-001/002，补归档真实 r7 review；禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。交付逐项 disposition、修订稿与指纹；运行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，未运行项保持 NOT_RUN。新上下文 approved且P0/P1=0后，按A→B执行提交字节复核与元数据重冻；建议不等于实现释放。