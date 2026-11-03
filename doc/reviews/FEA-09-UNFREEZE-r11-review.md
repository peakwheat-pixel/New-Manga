**结论：`changes_requested`；P0=0 / P1=2。**
阻断项仅涉及外部可观察的契约语义，不要求冻结内部算法或扩大 DTO。

Reviewer：Codex，独立上下文 `/root`；未参与指定实现、裁决或提案起草修订，未派子代理。
仅标准输出；未修改仓库、commit 或 push。

仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r11 为未跟踪工作树文件，8282 bytes，**不属于上述 commit 的提交字节**。
读取与结束复验 SHA-256 均为：
`de91043f76cdb98af1944a12a2df4b94bff6ea8571e0531d193abb905307eead`。
审查前后 `git status --porcelain=v1 --untracked-files=all` 完全相同：16 项既有 ` D`、16 项 `??`。
状态输出 SHA-256：`453dd26aa8497566005fd81e7de8ca223ed0cd3f6a4d9f987281b5d41ef843f6`。

证据限制：**r9/r10 Review 文件均 ENOENT，Git 全历史对应路径查询为空**。
已读 r8 Review、r9/r10 提案、impl-design、指定契约、冻结记录/矩阵及 I001；不能据提案转述证明缺失 Review 的 findings 已关闭。

1. **(a)–(d) 冻结充分性**

- **(a) 足够**：managed 独立 OR witness、artifact 不受 copy 列否决、V≠R、referenced 模式隔离明确。
- **(b) 足够**：正尺寸基线、分支守恒、固定 t／同事务连接、三路径核验、资源门禁及破坏测试具备判别力；既有人工数据／Lock／current/pinned 守恒继续有效。
- **(c) 管理读路径足够，Reader 响应边界尚不足**，见 R11-001。
- **(d) 安全不变量基本闭合，但撤销错误映射冲突**，见 R11-002；未发现另需扩域的安全阻断项。

2. **仅需补齐的 P1 最小项**

**R11-001 — P1：跳过不可读页后的 Reader 响应与恢复结果未闭合。**
位置：r11 第39行；M2-C1 §6.3。

反例：保存进度指向不可读 V 页，但章节仍有可读页；或章节 V 非空但全部不可读。
r11 要求跳过并返回可读部分，同时“不改变 initial_position”；既有 DTO 又要求非空形状 `{page_id, scroll_offset_y}`。
当前无法确定客户端收到整请求错误还是成功空集，以及初始位置是否指向被过滤页。
“既有错误面”仅限定词表，不能确定哪些失败允许部分成功、哪些仍整请求失败。

**最小修订**：明确可跳过失败与整请求失败的边界；规定无可读页时的既有 typed 结果；规定保存锚点被过滤时的恢复结果及 offset。
可采用既有错误码、既有 DTO 和既有恢复规则，无需新增字段，也无需冻结遍历算法。

**R11-002 — P1：撤销的可观察错误码与既有契约冲突。**
位置：r11 第59行；C-16 §2／§6／§7；C-06 §3.10。

r11 写“撤销/多义→`SOURCE_ACCESS_DENIED`”，既有 C-16 明确撤销→`SOURCE_GRANT_REVOKED`。
两者会使相同撤销状态产生不同客户端结果，不能交由实现检查顺序决定。

**最小修订**：撤销保留 `SOURCE_GRANT_REVOKED`；多义／重放仍可用 `SOURCE_ACCESS_DENIED`；category/retryable 沿既有表。
无需规定内部候选选择函数或代码执行顺序。

3. **无 wire／Reader DTO 扩展是否可接受**

**可以接受该方向**：V 全集经管理／诊断投影保留，Reader 仅输出可读页，不必为不可读页扩展 DTO。
这与 V/R 分离相容；前提是管理路径保留 typed 诊断，且补齐 R11-001。
字段形状不变并不自动证明行为兼容；部分成功、全不可读和恢复行为必须有明确契约判据。

4. **fresh-grant 与四象限**

Auth 与 Secret-G 分离可行：cache miss 时 0→REQUIRED、1→验证并一次性消费、多→DENIED；cache hit 仍需 Auth，但不消费秘密。
继承 C-06/C-16 的签名、session、generation、identity、预算、即时撤销／EOF 失效，并结合路径验证、同对象消费清理、Host 超时／取消及孤儿回收、零泄漏要求，安全闭环可实现。
并发串行化、claim、锁与句柄 API 留给实现设计及实现 Review。

| Host×Core | 契约预期 |
|---|---|
| 旧×旧 | 保持既有行为，不获得新增 resolve 密码能力 |
| 新×旧 | 能力缺失／探测异常→`CORE_CAPABILITY_MISSING`，不创建秘密文件 |
| 旧×新 | 不承诺新增密码链路；合法 Auth 下缓存可用，cache miss 无 Secret-G→REQUIRED，缺 Auth 仍拒绝 |
| 新×新 | fresh-grant 协议生效；四象限运行证据仍待实现验证 |

5. **冻结、登记与下一步**

A 单包可行：语义提交→逐文件三指纹／old-new blob→已提交字节复核→仅元数据重冻→check＋17 pins；C-16 同批或依赖明确地后续冻结均可。
M2-C1 无字节变更可以单独登记，无须为记录而修改正文；须记录精确版本／指纹、无 diff 证据及 Reader 行为兼容依据，不能仅写“无改动”即证明兼容。
P2：impl-design 仍含 `secret_token`、`unavailable_pages` 和旧缓存／错误顺序；应在实现前同步，契约优先，不据此追加本轮 P1。

pytest／.NET／build／真实 IPC／DPAPI／迁移／竞态／泄漏扫描／check／17 pins：**NOT_RUN**。

推荐下一步：由 **DSH** 处置两项 P1，再 Appointment 新上下文复核；本报告不释放生产返修。
可直接转发：
> DSH：请原字节归档本报告。在 `G:\CODEX\New Manga`、main，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9` 刷新并保留既有变更；于 FEA-09 登记写域，仅修订新提案、impl-design及必要治理记录，补齐 R11-001/002并补归档真实 r9/r10 Review。禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。交付逐项 disposition、修订稿与指纹；运行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，未运行项保持 NOT_RUN。新上下文 approved 且 P0/P1=0 后，再执行提交字节复核及元数据重冻。