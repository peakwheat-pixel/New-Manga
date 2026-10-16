# P12-C1 导入 wire 覆盖对照

状态：`WIRE_COVERED / CONTRACT_ONLY`。本表证明 rev 2.2 的导入 wire 能承载所列要求；不代表 Python Runtime、Tauri host issuer 或任何产品 Gate 已实现/通过。

**来源与边界：** [D08](../../doc/08_ACCEPTANCE_CRITERIA.md)；[P08 SCOPE_DRAFT 第 32 行与工作包 P12 第 78 行](../P08/SCOPE_DRAFT.md)；[P09 Task](../../doc/tasks/P09.md)、[P09 import contract](../../doc/contracts/P09_IMPORT_CONTRACT.md) 与 [P09 提交/回滚证据](../P09/commit-order-and-rollback.md)；契约 [§5.6](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md) / [§10.4](../../doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md)。

## D08 七条 AC

| D08 AC | 冻结 wire 承载点 | 覆盖结论与限制 |
|---|---|---|
| `AC-IMPORT-001` Managed Copy [P0] | §5.6 `ImportFileResult.filename/source_sha256`；`ImportPageResult.page_id/source_order/sort_order/sha256/width/height`；§10.4 只读引用 | **WIRE_COVERED**：字段可表达 basename、源 hash、页 hash、真实尺寸及 Managed Copy 成功页。Page 仅在 Managed Original 原子发布后提交。P09 已验证行为，当前 P09 AC3 的“项目永久删除后源 hash 对照”仍为 `BLOCKED`，不由本 Task 宣称完成。 |
| `AC-IMPORT-002` 用户源文件不修改 [P0] | §10.4 限定 Core 对已选来源只读、无写/移/删能力；§5.6 `source_sha256` 提供本次读取基线 | **WIRE_COVERED**：导入 wire 不携带路径，也不给写能力；后续对照可使用报告中的源 hash。导入/翻译/重修/重渲染/删除链的重新 hash 仍须由产品验收验证；P09 Task 记录项目级永久删除用例缺失，D08 门槛未降低。 |
| `AC-IMPORT-003` Copy 中断不产生坏 Page [P0] | §5.6 页级 `outcome/side_effects/page_id` 与文件级 `pending`；P09 的 publish-before-Page 顺序 | **WIRE_COVERED**：结果可区分已提交页、失败/待处理页；承诺 Page 不会引用缺失/半截 Managed Original。P09 允许 Page 事务失败后留下完整、不可见的 Managed Original 孤儿，因此不能把该异常报告成零副作用。 |
| `AC-IMPORT-004` Unicode 路径 [P1] | §5.6 basename 字段保留 Unicode；§10.4 保持路径仅在 Core/host 内部 | **WIRE_COVERED**：中文、日本語、한국어、Emoji、空格、括号文件名可保留；结果不暴露路径。实际导入成功仍由 Runtime/产品验证。 |
| `AC-IMPORT-005` 重复检测 [P1] | §5.6 `duplicate_policy`、页 `duplicate/outcome/sha256` | **WIRE_COVERED**：默认 `skip`，按 Chapter 活动 Page 和本批前序成功页的内容 SHA-256 判重；显式 `import_as_new` 新建 Page/Managed Original，不覆盖旧项；软删除 Page 与 source order 遵循 P09。 |
| `AC-EXT-IMPORT-003` 未加密 PDF 按页 [P2] | §5.6 每个 PDF 页的 `page_index/outcome/sha256/width/height/source_order/sort_order`；文件 `source_sha256` | **WIRE_COVERED**：支持按 PDF 原始页序记录每页 PNG Managed Original 的 hash/真实尺寸，同时区分原 PDF source hash；源 PDF 只读。 |
| `AC-EXT-IMPORT-004` 加密/损坏 PDF 零半成品拒绝 [P2] | §5.6 `ImportItemError.code/category`、`rejected` 与 `side_effects=none`；PDF 全页 preflight | **WIRE_COVERED**：加密、损坏、零页或任一页渲染失败可按文件拒绝并带稳定错误类别，首次 Copy 前无 Page、Managed Original、temp。Runtime 必须保持 P09 文件级预检；不以部分导入替代原 Gate。 |

## P08 / P12 工作包对照

| 来源行 | 冻结要求 | 本 Task 覆盖 | 范围裁定 |
|---|---|---|---|
| P08 `SCOPE_DRAFT.md:32` | 图片/文件夹/PDF/MOBI 导入；真实尺寸、受控来源、Managed Copy、损坏/加密/逃逸/重复/中断/Unicode、源 hash 零变化 | §5.6 + §10.4 覆盖图片、显式文件集合、已选文件夹直接子项、PDF、错误与报告字段 | 来源格式采用 P09 当前冻结边界：图片/文件夹 + PDF；MOBI、CBZ、网页、缩略图不进入本 Task。P09 记录的 2026-10-16 用户裁决排除 MOBI；不修改 SCOPE_DRAFT，也不降低 D08 AC。 |
| P08 `SCOPE_DRAFT.md:78` | P12 书架与导入 UI；依赖 P09/P08，UI 另行释放 | §5.6 提供 P12 后续消费者所需 Core wire；§12 限定 Python IPC Runtime | 本 Task 不授权或实现 UI、Tauri/Rust/React、空库端到端链或其他 P12 产品行为。 |

## 依据与未完成 Gate

- P18 `verification/P18/terminal-matrix.csv` 对 JA/KO 的 `ImportPages` 均记录 `UNKNOWN_COMMAND`；`verification/P18/raw/ja-r3/sidecar-stdout.jsonl` 原始响应同样为 `UNKNOWN_COMMAND`。该事实说明 runtime 缺口，不代表 rev 2.2 已实现。
- P09 的现有实现与测试支撑契约语义；P09 `AC3` 仍因缺项目级永久删除而 `BLOCKED`。本矩阵只证明 wire 可承载验收输入/输出及安全限制，不把 `BLOCKED` 改为 `PASS`。
- Python Runtime、host grant issuer、兼容版本实际运行、拒绝零写与产品 UI 均 `NOT_RUN`，由后续独立 Task 按冻结 allowlist 验证。
