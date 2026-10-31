# AC3（R-003）：测试日志格式规范化

日期：2026-11-01。Owner：DSH。

## 问题（来自 SAFETY-6 Review R-003）

`verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh-test-log.txt` 只有测试摘要，缺少：
完整命令、EXIT 码、运行时间戳；负向对照以散文描述，无法据此复跑。

## 本 Task 的格式（已执行）

`ac1-fix-tests.txt` 与 `ac1-negative-control.md` 现在固定包含：

| 字段 | 示例 |
|---|---|
| generated_at | ISO 8601，例如 `2026-11-01T01:47:12.1234567+08:00` |
| host / shell | `COMPUTERNAME` + pwsh 版本 |
| 完整命令 | `dotnet build NewManga.sln -v q --nologo`、`dotnet test … --filter …` |
| 原始输出 | 完整 stdout/stderr 追加，不裁剪 |
| EXIT | 每条命令后的 `EXIT=<code>` 行 |
| 负向对照 | 独立文件，含可复制执行的步骤与实测失败行 |

## 验收自检

- `ac1-fix-tests.txt`：含 `generated_at`、两条 `## command:` 段、两处 `EXIT=`（实为 0）。
- `ac1-negative-control.md`：含 4 步可复现命令与实测 `EXIT=1` / FAIL 行。
- 后续 SAFETY 系列证据统一采用该格式。
