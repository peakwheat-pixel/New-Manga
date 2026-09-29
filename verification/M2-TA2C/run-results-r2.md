# M2-TA2C r1 返修复验

返修代码/元数据 HEAD=`66dc361dac18b02fe3e4b773e9d0091ce6e37f60`，Windows PowerShell，Python `C:/Python314/python.exe`。r1 Review=`changes_requested` 的 P2-1/P2-2 已闭合：KO 固定 10 个来源状态改 `READY` 并限定其含义；所有非空 `checksum_inventory` 以仓库根目录为路径基准，JA/KO Pepper&Carrot 均指向同一实际清单。定向测试新增断言固定该语义。

| 命令 | EXIT | 结果 / raw |
|---|---:|---|
| `python -m pytest tests/m2_test_assets -q` | 0 | 25 passed；[pytest-assets-r2.log](pytest-assets-r2.log) |
| `assets.py list --level smoke` | 0 | READY=20；inventory checked=92 missing=0 failures=0；[asset-cli-r2.log](asset-cli-r2.log) |
| `assets.py verify --language ja --level smoke` | 0 | READY=10；同上 |
| `assets.py verify --language ko --level smoke` | 0 | READY=10；同上 |
| `assets.py verify --language ko --level regression --case-id K11 --case-id K12 --case-id K13` | 0 | READY=3；同上 |
| `assets.py missing --level regression` | 0 | READY=23 / MISSING=8 / MISSING_GATED_ASSET=37；同上 |
| `assets.py download --language ko --level regression --case-id K11 --case-id K12 --case-id K13` | 0 | downloaded=0 existing=6 failures=0；同上 |
| `python -m pytest tests/m2_acceptance -q --tb=no` | 1 | `BASELINE_FAILURE`，与固定 claim 前完全同组 8 failed / 24 passed / 3 skipped；[acceptance-r2.log](acceptance-r2.log)、[baseline](acceptance-baseline.log) |

曾尝试将 `required_files()` 的日语/韩语 member 校验提前到 status 路径，导致模拟无效 profile 的已有 `PARTIAL` 语义变为 `ValueError`；首次复验 1 failed / 24 passed，见 [pytest-assets-r2-initial-fail.log](pytest-assets-r2-initial-fail.log)。已撤回该 P3 建议，保留 `load_manifest`、`download` 和 `validate_public_case` 的现有语言校验；上述固定 HEAD 的最终 25 项测试全过。r1 DSH 沙箱 `tmp_path` WinError 5 为 Reviewer 环境限制，不等同作者测试失败。

Review 会话在 worktree 生成空 `.dsh-review-tmp/`；删除命令被自动策略拒绝，目录被忽略且不影响 tracked diff 或资产。空 stderr 日志及 JSONL 原始记录作为 r1 证据保存。
