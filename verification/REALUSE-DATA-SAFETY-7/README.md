# verification/REALUSE-DATA-SAFETY-7

REALUSE-DATA-SAFETY-7：SAFETY-6 独立 Review（approved，P2×3）的收尾。

| 文件 | 内容 |
|---|---|
| `ac1-fix.md` | R-001 并发 NRE 的根因、修复与验证表 |
| `ac1-negative-control.md` | 负向对照：移除修复后并发用例失败（EXIT=1）的可复现步骤 |
| `ac1-fix-tests.txt` | 修复后构建 + 全量测试原始日志（generated_at / 命令 / EXIT） |
| `ac2-eol-pin.md` | R-002：`.gitattributes` eol=lf 规则与 11 条 pin 的 old→new 对照 |
| `ac3-log-format.md` | R-003：测试日志格式规范与自检 |

约束：本 Task 未改冻结契约、未动用户数据、未 push；SAFETY-6 证据仅重新检出为 LF 并更新 2 条 pin，内容不变。
