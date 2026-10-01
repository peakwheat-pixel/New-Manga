# M2-SFX-TRANSLATE-ENTRY 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-SFX-TRANSLATE-ENTRY`；链：批次 release `8996ca55`（fork；Task 授权基线 8e0de8d0，r1 R8 注记）→ `a377a25a`(implement) → `453f6d73`(handoff/Task 回填) → 集成修正（本 commit，r1 条件由集成方闭合）
- Review：DSH r1 **`approved_with_conditions`**（0×P0/P1；R1 语义登记 P2 + R2 行数 P3 + 6×P3/P4；`doc/reviews/M2-SFX-TRANSLATE-ENTRY-a377a25a-dsh-r1.md`，sha256 `594318c0…f38`）。代码面静态核对无正确性缺陷（默认 SKIP 零变化/fail-fast 值域/非 SFX 泄漏防护成立）

## r1 条件闭合（集成修正 commit）

| # | 处置 |
|---|---|
| R1（P2） | 作用域登记（要求部分）：handoff §方案落点+Task AC2 行明写「策略仅对此后新建 region 生效，既有 region 不回溯；恢复=重新检出或全新 data root」；`Region.apply_sfx_policy` 无消费者+pinning test 登记为后续候选（建议部分） |
| R2（P3） | +49 净行更正为 **+80**（hunk 净增 0+1+6+49+13+11，文件 1123→1203 行） |
| R3-R5（P3/P4） | 登记接受：坏 settings_json 沿用 TASK-050 容忍语义（fail-fast 限解码成功后非法值）；恢复路径=修正/删除 pipeline_defaults.settings_json 的 sfx.policy（启动阻断自愈限制已登记，未来设置键契约/UI 写入面前置校验=候选）；`_load_pipeline_defaults` vs `_load_pipeline_settings` 双读取器一致性=hygiene 候选 |
| R6-R8（P4） | 登记后续（正则转义/None 分支用例=候选）；红态归档=本 commit 补 `pre-fix-tests-against-base-src.txt`（checkout base src 方法：collection error，与 Owner 声称一致；绿态 sfx-tests-green.log 21 passed）；base 注记=R8 |

## 运行时复跑（集成方）

- 绿态：21/21 passed（`tests/core/test_sfx_policy_settings.py`+`test_sfx_policy_end_to_end.py`）
- 红态：base src 下 collection error（exit=2）——归档含溯源行
- post-merge 三套件：见 main close commit（预期 530+1sk=509+21）

## 后续候选（登记，另行释放）

1. React 设置页接入 `sfx.policy` 键（UI 面归 Qoder）
2. region 级策略更新入口 + pinning test（r1 R1 建议部分）
3. executor backfill 单 region 调度片（Owner 相邻发现）
