**裁决：选择 B，先完成 C-05/C-15 UNFREEZE，再实施明确的 Managed Copy original 等价分支。R1-I001 当前仍成立，不得提前标为 FIXED。**

只读声明：本会话未参与 FEA-09 实现或原 Review；仅核查文件与 Git 状态，未修改文件、未 commit/push、未运行测试。核查 HEAD 为 `7ab46b56edb218c9adf30fb00a09fdd9c6e7f4e5`，分支 `main`，Git common directory 为 `.git`。工作树存在其他会话变更及证据目录访问异常，本裁决不证明工作树清洁。

**1. 主方案与依据**

- **契约**：C-05 v1.1 §3.1 明确保持 `V_artifact` 语义；现有导入列判断不能解释为已获授权的等价实现。B 必须被记录为显式语义修订，不能追认现实现已经合规。
- **产品**：正常导入只持有 Page Managed Copy 引用，渲染服务也明确支持这种 original 表示。直接切为 artifact-only 会隐藏正常导入页；保留此表示更符合既有产品行为。
- **迁移**：C-15 §1 第2、3项明确要求 artifact 可见集合守恒，并要求旧 complete、无 artifact 的页仍不可见。**A 补 ORIGINAL 行同样会违反这些条款，也需要 UNFREEZE。**
- **风险**：B 无需批量制造 artifact/revision 身份、设置 current 指针或追溯赋予 revision 时间；减少对人工修改、Lock、current/pinned Revision 及恢复语义的影响。
- **测试**：既有测试通过不能消除契约冲突。记录中的 1298 是 .NET 测试数量；本问题必须补 Python 持久化、迁移及生产读路径测试。
- **不选 C**：先按未冻结的新定义实施，会继续造成契约与实现脱节。可以准备修订稿与测试设计，生产返修应等待重冻及 DSH 范围授权。

建议新定义为：

```text
V_managed(p,t) = V_artifact(p,t) OR V_copy_original(p,t)

V_copy_original(p,t) =
  页、章节、书均未软删
  AND source_mode='managed'
  AND integrity_status='complete'
  AND source_hash、managed_original_ref 非空
  AND width>0 AND height>0
  AND pages.created_at<=t
```

这里的等价分支覆盖既有 Managed Copy 表示及继续使用该表示的 managed 导入，不限于迁移前行；不改变新导入默认 referenced 的决定。
`V_artifact` 自身保持原条件，不受 pages 完整性列约束；其时间条件仍使用 revision 时间。
“artifact 优先”是资源选择规则，不是可见性短路：不合格 artifact 不构成 witness，但不能否定另一个独立、合格的 copy-original witness。
磁盘存在性、受管根授权与实际可读性仍属于 `R`，不得混入 `V`，也不得用任意路径回退。

**2. 最小安全改动清单**

- **契约文档**：修订 C-05 §3.1/§3.2、失败语义；C-15 §1/§4 同步新谓词、迁移集合与资源校验范围。完成 UNFREEZE、上下文独立复核、重冻及新 pin；历史冻结记录、Review 与旧 pin 保留。
- **`library.py`**：get/list 使用统一模式分派；补 managed artifact 分支、copy-original 分支及各自时间条件；避免多 artifact 导致重复页。
- **投影与资源解析**：修复 mapper 丢弃 artifact-only 页的问题；有合格 original revision 时可据其投影字段，不回写或伪造导入 provenance。仅有 clean/thumbnail 等 artifact 时不得冒充 original；缺少请求资源须 typed 失败，不能因此静默删除可见页。涉及 Page/共享投影类型时由 DSH 明确扩域。
- **迁移实现**：调整 `migrator.py` 基线与验证。预期集合取“旧 artifact 可见集合 ∪ 合格 copy-original 集合”，分别核验 artifact 分支守恒、总集合与生产 get/list/projection 一致。
- **迁移验证约束**：同一 `t`、父级条件与顺序；事务内仅用原验证连接，不能另开连接；资源检查覆盖新增 copy-original 可见页，失败仍回滚并拒绝切换入口。
- **数据与导入**：不补 ORIGINAL 行、不移动或复制资源；保持 managed 导入在副本已存在后，同事务写完整 Page 状态。无需新增表或修改 v1–v6；冻结 v7 SQL 若需调整，必须另列 UNFREEZE 范围。
- **测试与交付文档**：更新 `tests/fea09`、library/import/storage/resource resolve 相关测试，以及 Task、AC、Handoff 和判别力证据。现有误名的 artifact-only 测试须拆分，不能仅改名称或预期。

**3. R1-I001 处置**

保留原报告与 P1 结论；登记为“契约修订前置 + 实现返修”，不整体降为契约澄清项。
重冻后，原报告“完整导入列但无 artifact 必须不可见”的修复预期由新契约取代；artifact-only 丢页、时间条件缺失、mapper 与生产迁移验证缺口继续有效。

标为 **FIXED** 至少需要：

- 新契约已重冻、pin 通过，DSH 已登记返修范围与逐项 disposition。
- 真正 artifact-only 页：缺导入列、有效 current revision，get/list/projection 可见；有 original 时资源可解析。
- 真正 columns-only 页：无任何 artifact，合格 copy-original 可见且可读；半写、零/负尺寸、未来时间、父级删除均有反例。
- artifact 分支覆盖 NULL/dangling current、非 valid、未来 revision、非 VISIBLE_TYPES；referenced 页不得经 managed 分支穿透。
- 迁移样本包含上述两类页及混合集合，断言走真实生产读路径；故意破坏查询或 mapper 时验证必须失败，不能依赖两份 SQL 同为空集。
- 缺资源、授权失败、顺序、人工数据、Lock、current/pinned Revision 守恒及迁移回滚证据齐全。
- 固定修复 head 的相关 Python 回归、.NET/build、真实 IPC、治理检查与17项 pin 校验，以及新上下文复审和 DSH 集成验证通过；未运行项如实标记。

**4. 其他人工/用户裁决点：无。**

DSH 的范围冻结、UNFREEZE 登记、Review Appointment 与集成验证属于既有流程；本裁决不代替这些步骤，也不授权扩大资源处置范围。

**5. 推荐下一步及可转发指令**

下一步由 **DSH** 归档本裁决并准备契约修订；启动实现的条件是重冻及范围授权完成。恢复点为 `G:\CODEX\New Manga`、`main`，核查 base/head 均为上述 `7ab46b56…`；执行前须刷新并保留其他会话变更。

> DSH：请将本输出原字节归档到 `doc/reviews/FEA-09-I001-adjudication.md`。在 `G:\CODEX\New Manga` 的 FEA-09 下登记 B 方案，刷新当前 head；以核查点 `7ab46b56edb218c9adf30fb00a09fdd9c6e7f4e5` 为来源，准备 C-05/C-15 UNFREEZE、Task 处置及冻结记录。当前仅处理裁决归档与契约范围，不修改生产代码、Schema、依赖、UI、用户数据或既有证据。交付修订稿、条款差异与反例矩阵，委派新上下文复核；重冻后再分配 Codex 返修。运行 `pwsh -NoProfile -File tools/governance/check.ps1` 与 `pwsh -NoProfile -File tools/governance/verify_pins.ps1`，如实登记失败/未运行项；检查通过不替代契约复核与集成 Gate。不 push。