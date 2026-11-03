**结论：`changes_requested`；P0=0 / P1=1 / P2=0。r14 尚不可 approved／重冻。**

Reviewer：Codex，独立上下文 `/root`；未参与 FEA-09 实现、I001 裁决或 r1–r14 起草修订。
本次只读、仅标准输出；未修改仓库、commit 或 push。

仓库：`G:\CODEX\New Manga`；分支 `main`；Git common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r14 为未跟踪文件，2372 bytes，不属于上述提交字节。
审查前后 r14 SHA-256 相同：
`afb924d2f2ef416c332181078225554d15cb2fb06a9e973861231ee50cc0c54d`
审查前后 `git status --porcelain=v1` 完全相同：16 项既有 ` D`、24 项 `??`。
状态输出 SHA-256：`c57d6d9ee6007f13838fa5acc50ce6dc911bc2ac34a52f550383303350d9c014`。

已核对指定必读材料；r12 Review 本轮存在。沿用 r13 已确认的其余外部语义，不以内部算法／DTO 映射提出 P1。

1. **R13-001：部分闭合，仍有一项外部兼容性 P1。**

像素单位、分页0、保存页可读时原值恢复、替代页0及取消归一化，均与 M2-C1 方向一致。
但 [r14:11](</G:/CODEX/New Manga/doc/reviews/FEA-09-UNFREEZE-r14-amendments.md:11>) 新增“**非负整数；既有语义**”，并非既有契约要求。

**R14-001 — P1：整数限制缩窄合法 offset，且与原值恢复冲突。**
[M2-C1 §6.3:935](</G:/CODEX/New Manga/doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:935>)、948将 offset 定义为 `number`；955–956要求源图像素坐标及有限、非负、页高范围校验，未要求整数。
反例：高度10000的可读 Webtoon 页合法保存 `scroll_offset_y=5000.5`；r14:13要求恢复5000.5，r14:11却禁止该值。拒绝、取整或原值恢复会产生不同客户端结果。
最小修订：将“非负整数”改为“非负有限数值，合法范围沿用 M2-C1 §6.3”；明确不取整、不归一化，合法保存值原值恢复。

2. **R13-002：CLOSED，外部结果唯一。**

r14:22–27以完整 `(sort_order,page_id)` 比较确定0-based插入位置。
示例 `(10,a)/(10,c)`、保存页 `(10,b)` 唯一得到 `a=1`，选择可读页c。
无DB页行取 `a=0`；无 `logical_order>=a` 的可读页时回绕至最小可读页；零可读沿用 `TARGET_NOT_FOUND`。未发现残余外部歧义。

3. **冻结判断。**

仅剩 R14-001；当前不能进入获批语义提交／重冻。
修正并经新上下文 approved、P0/P1=0后，可依既定流程推进：
语义提交 → 三指纹／old-new blob → 已提交字节复核 → 仅元数据重冻 → check＋17 pins。
M2-C1须登记精确版本、指纹、no-diff及行为兼容依据；本报告不批准尚未形成的提交字节或生产返修。

pytest／.NET／build／真实IPC／DPAPI／迁移／竞态／泄漏扫描／check／17 pins：**NOT_RUN**。

推荐下一步：由 **DSH** 处置唯一最小修订并委派新上下文复核。
可直接转发：
> DSH：请原字节归档本报告；在 FEA-09、main，以 reviewed_head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9` 为来源，刷新并保留既有变更，登记写域后仅修订新提案中的 offset 整数限制，交付 disposition、修订稿及SHA-256。禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及push。新上下文 approved且P0/P1=0后，再推进语义提交、提交字节复核及仅元数据重冻；check／17 pins未运行时保持NOT_RUN。