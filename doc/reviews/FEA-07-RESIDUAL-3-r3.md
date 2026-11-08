# FEA-07-RESIDUAL-3 Review r3（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | **`8e9420f41`**（r2 返修） |
| 结论 | **`approved`** —— P0=0 / P1=0 / **P2=0** / P3=4 |

## 实跑
build 0/0；全量 **1794/0/107**（App 831/0/11、Host 302/0/72）；gated AC4 **16/16**（两次）且真实 `%APPDATA%` **14477→14477（delta=0）**；pytest 第 1 次 3394/1（未登记 flake `test_referenced_flow`，单测/整文件重跑绿）→ 第 2 次 **3395/0/10**；pins **18/18**；check PASS(3w)；工作树 clean。

## 复核
- **P1-01 真收口**：`ResolveDiagnosticsRoot` 被材质行与 `AppendScalingDiagnostics` 共用；grep 全 `src/NewManga.App` 无第三条硬编码日志路径（`Program.WriteFatal`/`AppOptions` 走 `LogDirectory`）；M5 变异（回退硬编码）→ RED（真实日志 +2）→ sha256 `0c4b818f…` MATCH → 复绿。
- **P2-01 已收口**：App 可见探针（`startup-diagnostics: isolation log-dir=… appdata=… cwd=…`）+ cwd 断言 + 隔离文件 + 真实 delta 组合链成立；DEFECTS/README 已纠正「env 注入不是隔离保证，主闸是 `--log-dir` 契约」；M4 RED 归属表述诚实。
- **回归/范围**：45 文件 ⊆ allowed_paths（含授权 `MainWindow.axaml.cs` +38/−10）；禁止面零 diff；`FEA-07` AC1/AC3/AC4 `[x] <<MET>>`、AC5 唯一 NA 零字节、AC7 未动。

## P3（非阻塞）
P3-01 fixture 注释旧口径；P3-02 M4b-r2 默认套件 +2 未计入汇总；P3-03 M5 日志缺 BEFORE/AFTER；P3-04 缩放写入口「调用点」未被直接断言（headless 无法制造真实 DPI 变化）。
