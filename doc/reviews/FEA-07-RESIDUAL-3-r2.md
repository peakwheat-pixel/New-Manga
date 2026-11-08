# FEA-07-RESIDUAL-3 Review r2（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `219405b30`（r1 返修） |
| 结论 | **changes_requested**（P0=0 / **P1=1** / P2=1 / P3=4） |

## 复核
r1 主路径已真修并独立复现：`--log-dir` 拥有材质日志；gated AC4 **14/14** 真实 AppData **delta=0**；脚本 4/4 delta=0；M4 变异 RED→sha256 MATCH→复绿；P2-03（recover 前改真实 DB `current_revision_id`/`inpaint_locked`）真修；P3-01/03/05 成立。

## P1/P2
- **P1-01**：`MainWindow.axaml.cs:156-158` 的 `RenderScaling` 分支仍硬编码真实 `%APPDATA%`，绕过 `--log-dir`，与「owns EVERY log file」矛盾（AC4 矩阵未触发，delta=0 仍真实）。
- **P2-01**：env 注入不改变 App 的 `GetFolderPath`（实测写 cwd 相对路径），「纵深防御」表述过强；M4 RED 实际由隔离目录断言承担；DEFECTS 口径需纠正。

## P3
README 基线 14275 vs 证据 14340；`mutation-4b` 日志缺 BEFORE/AFTER；backfill 尾部不可复现；D-R4b-7「16 文件」清单缺。
