# C-07 契约 UNFREEZE 记录（2026-11-10，LIB-1 落地）

- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`
- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（C-07 API Inventory）
- 授权依据：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1 单次 C-07 UNFREEZE 名单——LIB 切片 P5–P8 实现落地后的统计与冻结记录更新。
- 变更范围（**条款字节不变**）：代码统计节 `IHostController` 65 → **69**；合计 72 → **76**（新增 `UpdateBookMetadataAsync` / `ReorderChaptersAsync` / `UpdateChapterMetadataAsync` / `CreateChapterWithMetadataAsync`）。
- 前 pin（v1.4）：`8d92a32feed771e416d1c1c003ec806e0c5c4712209fd2e097c0a723252bab5c`
- 新 pin（v1.5）：`9c1eb974342af889c8c3acb8b7f7d7893ba44f05ee4b32c871116e249b321d74`
- 复核：`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18。

## 附录 v1.6（2026-11-10，LIB-1 r1 处置：成员表同步）

- 触发：`doc/reviews/FEA-14-LIB-1-r1.md` R-05（C-07 正式成员表仍 54 行、S5 节口径未同步）与 R-07（冻结记录缺 v1.3–v1.5 行）。
- 变更范围（**条款字节不变**）：`doc/plan/FEA-C07_API_INVENTORY.md`
  1. 正式成员表按 `generate_api_inventory.py` stdout 重建：`IHostController` 69 方法 + 4 非方法成员、`IReaderProgressSink` 1、`IRunController` 6，逐行与 stdout 一致（脚本核对 `ALL_MATCH: True`）；
  2. P1–P15 从「S5 计划追加」节移入正式成员表；实签名以代码为准，与 v1.2 计划类型不同处：P12 `Task<string?>`、P14 `Task<BookReadingProgressInfo?>`、P15 `Task<int>`；
  3. 剩余计划节只列 P16–P25（10 条，不计入统计）。
- 统计：不变（`IHostController` 69 / 合计 76）；`--check` EXIT 0。
- 冻结记录：`doc/plan/FEA-CONTRACT-FROZEN-C07.md` §1 补 v1.3–v1.6 pin 链，§1B/§2/§3/§5 同步。
- 前 pin（v1.5）：`9c1eb974342af889c8c3acb8b7f7d7893ba44f05ee4b32c871116e249b321d74`
- 新 pin（v1.6）：`7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`
- 复核：`verify_pins` 18/18、`generate_api_inventory.py --check` EXIT 0；v1.6 字节由 LIB-1 r2 独立复核覆盖。
