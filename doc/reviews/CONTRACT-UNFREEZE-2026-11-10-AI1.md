# C-07 契约 UNFREEZE 记录（2026-11-10，AI-1 落地）

- 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-AI1.md`
- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（C-07 API Inventory）
- 授权依据：`ADJ-2026-11-10-FEA14-S5-SCOPE` §2.1 单次 C-07 UNFREEZE 名单——AI 切片 P21–P25 实现落地后的统计与冻结记录更新。
- 变更范围（**条款语义不变**）：
  1. 代码统计节 `IHostController` 74 → **79**；合计 81 → **86**（新增 `ListPromptTemplatesAsync` / `SavePromptTemplateAsync` / `DeletePromptTemplateAsync` / `CopyBuiltinPromptTemplateAsync` / `GetPromptTemplateReferencesAsync`）。
  2. 正式成员表按 `generate_api_inventory.py` stdout 重建：79 方法 + 4 非方法成员，逐行一致（`ALL_MATCH: True`）。
  3. 「S5 计划追加」节 **25/25 全部落地**、无待实现行（P1–P25 全部并入正式成员表）。
  4. 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C07.md` §1 pin 链补 v1.7 原值 + v1.8；§1B/§2 条件 3（`1/79/6=86`）/§3/§5 同步。
- 前 pin（v1.7）：`89781583964eb81db0e12974fdd03adc44231461ac3b2fad65f0eacdb74261c6`
- 新 pin（v1.8）：`58dbae4c14d7ec4b946bbf27a237415b938a7160e9c8b311db6dd0377da9dfef`
- 复核：`generate_api_inventory.py --check` EXIT 0；`verify_pins` 18/18；v1.8 字节由 FEA-14-AI-1 r1 独立复核覆盖。
