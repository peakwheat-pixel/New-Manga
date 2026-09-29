# Integration record：M2-TA2C-TOOLING-GAPS

- 集成方：Codex（代行，ZCode 编排会话，用户全权授权 2026-09-28/30）；集成日期 2026-09-30
- base=`f3d684eb`（release）→ claim `19f8200e` → 实现+交付 `a164e414` → 回填 `1fd2787d`
- Review：DSH 非作者静态 **r1 `approved` 一次通过**（0×P0/P1/P2；7×P3 全非阻塞；报告 [1fd2787d-dsh-r1](../../../doc/reviews/M2-TA2C-TOOLING-GAPS-1fd2787d-dsh-r1.md)，按被审 head 归档）
- 交付内容：load_manifest source_url 主机白名单（实测冻结 {www.peppercarrot.com, huggingface.co}）+ verify 运行时消费 benchmark_sources[*].checksum_inventory（存在性 + local_asset_inventory.json 逐文件哈希复核，BENCHMARK_INVENTORY checked=4 failures=0）+ 判别性参数化断言（含 ko_sfx_dialogue_cleaned_webtoon=ko-webtoon-audit.json 存在性；坏路径 failures 演示）+ cases.json naming_note + 目录命名现状快照断言（不重命名）
- 集成验证：worktree 复跑 pytest tests/m2_test_assets 34 passed EXIT=0；merge=`04165c76fab939e4a106f4a87f5045d674e8dac3`（无冲突）；post-merge main head 复跑 **34 passed EXIT=0**
- 遗留移交（planning 候选，均非阻塞）：①P3-1 inventory 非字符串值 fail-open；②P3-2 符号链接 resolve 包含性；③P3-3 inventory 身份绑定断言；④P3-4 JA 快照全枚举（J38-J47）；⑤P3-6 仓库级校验不受 --language/--case-id 限制的 README 显式化；⑥P3-7 畸形端口异常文案统一；⑦clippy 6 基线 error（Goal 候选池）

- 本文件（integration.md）与 final-scope-audit.log 由集成收口 commit 入库；区间审计实测 f3d684eb..1fd2787d 仅 14 允许路径、DIFFCHECK_EXIT=0。
