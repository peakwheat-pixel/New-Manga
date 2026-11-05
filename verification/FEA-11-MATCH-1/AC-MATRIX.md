# FEA-11-MATCH-1 AC-MATRIX

| AC | 要求摘要 | 判定 | 证据（测试/日志） |
|---|---|---|---|
| AC-M1 | 变更容器路径提取并持久化 `pixel-digest/1` profile（EXIF 转置、W/H 转置后、orientation=1、canonical params、Pillow pin），可解码 entry 才产 profile，失败按 C10 降级且 scan 成功 | MET | `tests/fea11/test_source_match.py` 7 个 scan/unit 用例；`logs/pytest-match.log`；`logs/pytest-fea11.log` |
| AC-M2 | 7 维可比性（algorithm/decoder/decoder_version/canonical params/width/height/orientation）；`unique_pixel` 仅 1:1；`changed` 仅在双侧完整可比且像素不同 | MET | 6 个 matcher 用例 + relation/两代用例 |
| AC-M3 | 重复 pixel occurrence（含 1:2/2:1/交叠）整组 `duplicate_group`+needs_confirmation，禁 ordinal/locator 自动锚定；唯一字节分支不得绕过重复组（R1-02 判别性用例） | MET | `::test_byte_identity_does_not_bypass_a_duplicate_pixel_group` 等 3 个 matcher 用例 + scan→plan 链 |
| AC-M4 | 旧证据缺失/不可比 → `missing_old`/`incomparable`（含真实 v7 W/H-only 与 **R1-01 改名不可比 counterpart**）；counterpart-less 重复成员 → `missing`/`added`；totals 如实变化；ambiguous 双侧非空 | MET | 4 个 matcher 用例 + 真实 v7 fixture；W1 用例 |
| AC-M5 | `migrations[:7]`+真实导入 fixture；独立 match 测试（纯 matcher + scan 集成 + **sqlite_master 全表** scan 只读 + 两代 resync + apply 保留 canonical params + scan 丢失 typed `SOURCE_PLAN_STALE` 零提交）；W1/W1b 窄批 | MET | `tests/fea11/test_source_match.py`（20 passed）；`logs/pytest-fea11.log`（108 passed） |
| AC-M6 | pins 18/18、check.ps1 PASS、全量 pytest ≥3183/10、契约/schema/apps 零 diff、无新依赖（真实依赖文件 `requirements.txt`，仓库无 `pyproject.toml`） | MET | `logs/verify-pins.log`、`logs/gates.log`、`logs/pytest-full.log`（3203/10）、`logs/static-diff.log` |
