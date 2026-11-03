**结论：`changes_requested`；P0=0 / P1=1 / P2=0。**
R11-002 已闭合；R11-001 部分闭合，仍不足以形成可冻结且兼容 M2-C1 的 Reader 语义。

Reviewer：Codex，独立上下文 `/root`；未参与 FEA-09 实现、I001 裁决或 r1–r12 起草修订；未派子代理。
仅标准输出报告；未修改仓库、commit 或 push。

仓库：`G:\CODEX\New Manga`；branch=`main`；Git common directory=`G:/CODEX/New Manga/.git`。
`reviewed_head`／结束 HEAD：
`a7f6363003573dd42d65033b2a84dff5d6c3e2d9`
r12 为未跟踪工作树文件，3450 bytes，**不属于 reviewed_head 的提交字节**。
读取与结束复验 SHA-256 相同：
`b3fb1cb34043e635acf7d794c932ebb1e98335ee483e8b1fc593d338b56e25a9`

审查前后 status 完全相同：16 项既有 ` D`、20 项 `??`。
删除项均在 `verification/FEA-09/native-registry/`；未跟踪项为 impl-design、r3–r11 amendments/review、r12 amendments。
`git status --porcelain=v1 --untracked-files=all` 输出 SHA-256：
`dbe6e83d73c11de8af4fba5c6a1e7b44e59c7861b637178e42320c477b24c389`

已读取全部指定材料，包括本轮存在的 r9/r10 Review；沿用 r11 对 (a)/(b)/(d)、管理读路径及无 DTO 扩展方向的认可。

1. **R11-001：部分 CLOSED，兼容与恢复完整性仍 OPEN。**

- 可跳过的11类逐页失败与其余错误整请求失败、不返回部分结果，边界已明确；正式字节应使用完整 `SOURCE_*` code。
- 保存页可读：保留 page_id／offset；保存页不可读但属于 V：向后找可读页，无则回绕，offset=0，已明确。
- 无进度：从最小可读页、offset=0，已明确。
- V 非空但零可读、V 空：均整请求返回 `TARGET_NOT_FOUND`，不返回成功空集，已消除必填初始 page_id 无处落点的问题。
- `initial_position.page_id ∈ pages[]` 已成为明确不变量；但该条件**不足以证明旧客户端兼容**。

**R12-001 — P1：Reader 页集、请求分派及移出页锚点仍存在外部歧义／兼容破坏。**
位置：r12:19–24、29；M2-C1 §6.3:952–956。

- **页集兼容破坏**：r12:19 明确从保存页开始返回后缀。反例：A/B/C 均可读，保存页为 B，则旧客户端只收到 B/C，无法向前导航至 A。初始位置属于数组并不能恢复丢失的章节页。
- **beginning/resume 未分派**：保存页为 B 时，`start_position="beginning"` 依 M2-C1 应从首 Page、offset=0 开始；r12 未限定恢复规则只适用于 resume，仍可能返回 B／保存 offset。
- **已移出页恢复不唯一**：r12:22“用 sort_order 求 a”未定义排序键到 V 逻辑序的转换。若剩余页 sort_order 为10/30、逻辑序为0/1，移出页 sort_order=20，直接比较与按排序位置转换会分别回绕首项或选择末项，客户端初始页不同。

**最小修订**：统一 pages 为章节可读全集、按规范序返回，仅 initial_position 决定起点；明确 beginning/resume 分派并保留 saved_progress；给移出页一个确定的排序位置映射或明确回退规则。
无需冻结遍历算法、SQL 或 DTO 映射，也无需新增字段。

2. **R11-002：CLOSED。**

r12:36–39 已明确：
撤销／Revoke／EOF 后失效→`SOURCE_GRANT_REVOKED`（authorization,false）；
grant 过期→`SOURCE_GRANT_EXPIRED`（authorization,true）；
多义／claim 重放→`SOURCE_ACCESS_DENIED`（authorization,false）。
这与 C-16 §6 一致，并替换 r11“撤销→DENIED”的直接冲突；未发现此项需要新增的外部契约 P1。

3. **冻结判断与验证。**

当前仍有上述一个外部可观察 P1，r12 **不能 approved，也不能进入获批语义提交／重冻**。
补齐并经新上下文批准后，可按既定流程推进：语义提交→三指纹／old-new blob→已提交字节复核→仅元数据重冻→check＋17 pins；M2-C1 单独登记精确版本、指纹、no-diff 及行为兼容依据。
impl-design 的旧 DTO／请求字段仍须同步，契约优先；不另计本轮 P1。

pytest／.NET／build／真实 IPC／DPAPI／迁移／竞态／泄漏扫描／check／17 pins：**NOT_RUN**。

推荐下一步：由 **DSH** 在现有 FEA-09 下处置 R12-001，再 Appointment 新上下文只读复核。
可直接转发：
> DSH：请原字节归档本报告。在 `G:\CODEX\New Manga`、main，base/head=`a7f6363003573dd42d65033b2a84dff5d6c3e2d9` 刷新并保留既有变更；登记写域后，仅修订新提案、同步 impl-design及必要治理记录，补齐 Reader 全集、beginning/resume 和移出页恢复规则。禁止生产代码、Schema、依赖、UI、用户数据、历史证据改写及 push。交付逐项 disposition、修订稿和指纹；运行 `pwsh -NoProfile -File tools/governance/check.ps1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`，未运行项保持 NOT_RUN。新上下文 approved 且 P0/P1=0 后，再推进语义提交、字节复核及元数据重冻。