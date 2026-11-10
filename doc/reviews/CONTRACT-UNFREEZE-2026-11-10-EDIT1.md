# C-07 契约 UNFREEZE 记录（2026-11-10，EDIT-1 落地）

- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-EDIT1.md`
- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（C-07 API Inventory）
- 授权依据：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1 单次 C-07 UNFREEZE 名单——EDIT 切片 P16–P20 实现落地后的统计与冻结记录更新。
- 变更范围（**条款语义不变**）：
  1. 代码统计节 `IHostController` 69 → **74**；合计 76 → **81**（新增 `ListIssueMarkersAsync` / `CreateIssueMarkerAsync` / `ResolveIssueMarkerAsync` / `ReopenIssueMarkerAsync` / `DeleteIssueMarkerAsync`）。
  2. 正式成员表按 `generate_api_inventory.py` stdout 重建：74 方法 + 4 非方法成员，逐行一致（`ALL_MATCH: True`）。
  3. 「S5 计划追加」节只保留尚未实现的 AI-1 P21–P25（已落地 20/25）。
  4. 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C07.md` §1 pin 链补 v1.6 原值 + v1.7；§1B/§2 条件 3（`1/74/6=81`）/§3/§5 同步。
- 前 pin（v1.6）：`7c033bf76af1726b71e1ce92a5b3c221d880cf7a36bfc44ef3d4467582d5457d`
- 新 pin（v1.7）：`89781583964eb81db0e12974fdd03adc44231461ac3b2fad65f0eacdb74261c6`（r1 独立复核发现 S5 节残留 P16–P18 三行 → 删除后重算；初值 `bb775912…` 仅历史，不作校验基准）
- 复核：`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18；v1.7 字节由 FEA-14-EDIT-1 r2 独立复核覆盖。
