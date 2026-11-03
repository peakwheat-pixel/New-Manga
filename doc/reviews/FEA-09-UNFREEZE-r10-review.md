**结论：`changes_requested`；P0=0 / P1=2 / P2=0。r10 尚未闭合两项契约语义，不能 approved 或进入获批语义提交/重冻。**

Reviewer：Codex，独立上下文 `/root`；未参与 FEA-09 实现、I001 裁决、r1–r9 起草或 r10 修订；未派子代理。
仅标准输出；未修改仓库、commit 或 push。

仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`。
r10：未跟踪工作树文件，5126 bytes，**不属于 reviewed_head 提交字节**。
审查读取与结束复验 SHA-256：
`dd8ba188ecdf3ef3fdab1cdf801a6e9494a77859407ad51c1e1634af3134739e`

审查前后 status 相同：16 项既有 ` D`、15 项 `??`。
删除项均为 `verification/FEA-09/native-registry/` 四组 registry/lock/corrupt/quarantine 文件；
未跟踪项为 impl-design、r3–r8 amendments/review、r9/r10 amendments。
status 输出 SHA-256：`26cc1e68a2ff2f7b09e978f1c7ea4c03e0e53fef13cca9b3cf700439b91063f7`。

**证据限制**：指定的 `FEA-09-UNFREEZE-r9-review.md` 不存在（`ENOENT`），Git 全历史该路径查询为空。
因此无法证明与 r9 原始 findings 逐字闭合；以下按用户指定的 R9-001/002 及现有条款核验。
已读取其余指定提案、Reviews、impl-design、契约、FROZEN/矩阵和 I001 裁决。

1. **R9-001：部分闭合，仍 OPEN — P1。**
位置：r10:12–25；M2-C1 §6.3:941–956。

对象形状已恢复；正常可读锚点保留 offset、不可读锚点向后找/回绕、全不可读返回 V 内初始页、无进度从首可读页开始，均已有规则。
V 非空且无整请求错误可成功；V 空返回 `TARGET_NOT_FOUND`；其余 REQUEST 错误保留原 envelope，边界基本明确。
但仍有三处外部可观察结果不能唯一兼容：

- `start_position="beginning"` 未被排除在恢复规则之外；存在保存进度时，r10:13 与 M2-C1“首 Page、offset=0、保留 saved_progress”发生冲突。
- r10:17“用 sort_order 求锚点序 a”未定义排序键到 0-based 序的转换及同 sort_order 的 page_id 边界；移出章节后当前 sort_order 也不必是原章节位置。
- r10:14 明确把 `pages` 截成锚点后的后缀；这会删除仍可读的前方页，旧客户端无法向前导航。其他恢复分支的 pages 范围也未统一；“初始 page_id 存在”不足以证明兼容。

**契约层最小修复**：明确 beginning/resume 分派；给移出页一个确定的锚点转换规则（含并列键、无行）；统一 pages 为章节可读全集、仅 initial_position 决定起点，或显式修订分页/导航兼容边界。Webtoon 仅有效 resume 保留 offset，其余归零；saved_progress 保持原语义。

2. **R9-002：部分闭合，仍 OPEN — P1。**
位置：r10:32–56；C-16 §2/§6。

单候选情况下，签名→grant 过期→撤销→授权的顺序已写明；
仅撤销候选不降级 DENIED、grant expiry 与 secret_ref expiry 分层、cache 在冷却之前，方向正确。
列出的 category/retryable 与 C-16 §6 一致，但多候选仍无唯一结果：

- “被选中参与判定”没有可观察选择/归约规则。两个同 scope 候选分别已过期、已撤销且均无有效授权时，可分别得到 EXPIRED 或 REVOKED。
- 有效 Auth 候选与 token 匹配但已过期/撤销的 Secret 候选并存时，第3–5步可能先失败，第56行却允许其他 Auth 候选通过；cache 命中是否受该 Secret 阻断也不明确。
- 第9步“至少两个 Secret 候选”与“secret_ref 已过期”可同时成立，仍可能 DENIED 或 REQUIRED；双层过期唯一性只覆盖了单候选情形。

**契约层最小修复**：定义 Auth 存在性与失败候选的结果归约、Secret 何时参与前置校验及其与缓存的关系；明确多匹配与过期重叠时的唯一结果。无需冻结内部选择函数，但必须让上述相同候选集合只有一个合规结果，并明确继承或修订 C-16 §2 的适用范围。

3. **冻结与实现判据。**
V/witness/R、迁移守恒、投影最低集及资源边界未发现本轮新增必须扩域的 P1。
impl-design 仍含旧 DTO/授权/cache 顺序，应按最终语义同步；设计不得替契约选择上述答案。
A→B、语义提交→三指纹/old-new blob→已提交字节复核→仅元数据重冻的流程可执行；当前语义前置未满足。M2-C1 仍须单独登记，17 pins 不覆盖该 amendment。

验证：`check.ps1` EXIT 0、PASS（3 warnings）；`verify_pins.ps1` EXIT 0、17/17 PASS。
pytest／.NET／build／真实 IPC／DPAPI／迁移实测／竞态／泄漏扫描：**NOT_RUN**。

推荐下一步由 **DSH** 处置两项最小契约 P1；可直接转发：
> DSH：请原字节归档本报告及缺失的真实 r9 review。恢复点为上述仓库/main/reviewed_head；保留既有变更，仅修订提案、同步 impl-design及必要治理记录，明确 Reader 分派/锚点/全集和多候选错误归约；不修改生产代码、Schema、依赖、UI、用户数据或历史证据，不 push。交付逐项 disposition、修订稿与指纹，Appointment 新上下文只读复核；approved且P0/P1=0后再按A→B推进提交字节复核与元数据重冻。