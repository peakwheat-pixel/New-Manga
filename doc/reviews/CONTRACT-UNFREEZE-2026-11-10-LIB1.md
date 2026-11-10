# C-07 契约 UNFREEZE 记录（2026-11-10，LIB-1 落地）

- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`
- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（C-07 API Inventory）
- 授权依据：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1 单次 C-07 UNFREEZE 名单——LIB 切片 P5–P8 实现落地后的统计与冻结记录更新。
- 变更范围（**条款字节不变**）：代码统计节 `IHostController` 65 → **69**；合计 72 → **76**（新增 `UpdateBookMetadataAsync` / `ReorderChaptersAsync` / `UpdateChapterMetadataAsync` / `CreateChapterWithMetadataAsync`）。
- 前 pin（v1.4）：`8d92a32feed771e416d1c1c003ec806e0c5c4712209fd2e097c0a723252bab5c`
- 新 pin（v1.5）：`9c1eb974342af889c8c3acb8b7f7d7893ba44f05ee4b32c871116e249b321d74`
- 复核：`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18。
