# C-07 契约 UNFREEZE 记录（2026-11-10，READ-1 落地）

- 载体：doc/reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md
- 契约：doc/plan/FEA-C07_API_INVENTORY.md（C-07 API Inventory）
- 授权依据：ADJ-2026-11-10-FEA14-S5-SCOPE §2.1 单次 C-07 UNFREEZE 名单——READ 切片 P9–P15 实现落地后的统计与冻结记录更新。
- 变更范围（**条款字节不变**）：
  1. 代码统计节：IHostController 方法数 54 → **61**；合计 61 → **68**（新增 7 条 READ 命令：GetReadingPreferencesAsync / SaveReadingPreferencesAsync / ListBookmarksAsync / CreateBookmarkAsync / DeleteBookmarkAsync / GetBookReadingProgressAsync / ResetReadingProgressAsync）。
  2. 其余条款、命令面、冻结语义一律不变；旧 pin 保留可追溯。
- 前 pin（v1.2）：5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6
- 新 pin（v1.3）：$h
- 复核：generate_api_inventory.py --check EXIT 0（渲染 61/68 与文档一致）；erify_pins 需在冻结记录 pin 更新后 18/18。
