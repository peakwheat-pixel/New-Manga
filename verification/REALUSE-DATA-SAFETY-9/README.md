# verification/REALUSE-DATA-SAFETY-9

REALUSE-DATA-SAFETY-9：SAFETY-8 独立 Review（approved，P2×3；R-001 已闭环）的收尾。

| 文件 | 内容 |
|---|---|
| `ac1-discriminating.md` | R-002：AC3 用例补判别性断言（close 窗口内 `PageIndex` 保持 3）与 pre-F-005 负向对照 |
| `ac1-fix-tests.txt` | 构建 + filtered + 全量原始日志（cwd / 命令 / EXIT） |
| `ac2-wording.md` | R-003：`ac2-eol-pin.md` 措辞修正为只记录已发生的审查结论 |

约束：本 Task 只改测试与证据文档，不改生产代码、冻结契约、用户数据；未 push。
