# C-07 契约 UNFREEZE 记录（2026-11-10，FONT-1 落地）

- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md`
- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（C-07 API Inventory）
- 授权依据：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1 单次 C-07 UNFREEZE 名单——FONT 切片 P1–P4 实现落地后的统计与冻结记录更新。
- 变更范围（**条款字节不变**）：代码统计节 `IHostController` 61 → **65**；合计 68 → **72**（新增 `ListFontAssetsAsync` / `ImportFontAssetAsync` / `DeleteFontAssetAsync` / `RefreshFontAssetsAsync`）。
- 前 pin（v1.3）：`59ab90f7d717fdd44816d22284d00e2a53ab48581d644c97e9dccd3ccc6a1b5a`
- 新 pin（v1.4）：`8d92a32feed771e416d1c1c003ec806e0c5c4712209fd2e097c0a723252bab5c`
- 复核：`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18。
