# M2-S1 证据索引（Large-Media Resource Channel Feasibility Spike）

本目录是 DeepSeek Harness 作为 M2-S1 Owner 在独立 C: clone
（`C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`，branch
`agent/deepseek/M2-S1-resource-channel-spike`，固定 base
`85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`）中的全部研究证据。

## 边界声明

- 本 Task 只产出研究文档、隔离探针、原始证据与 Handoff；**没有**产品 IPC server/runtime、
  Tauri command、React consumer、GUI 实现。
- 未修改 `src/**`、`tests/**`、依赖、Schema、`doc/contracts/**`、AD-001 或任何 M2-C1 工件。
- 未访问真实用户漫画库、源文件、凭据或模型缓存。全部载荷是 `%TEMP%` 下**合成**生成的 PNG。
- 探针不导入 `src/**`，只用 CPython 标准库 + ctypes，可被非作者 Reviewer 直接重跑。

## Codex 释放证据的位置（重要）

Codex 的释放/派发证据位于共享仓库 `origin/master`（`610f99dc79923e0be48c5b5dd633ff4facfb40e4`）：

- `verification/M2-S1/release-85a2aa7.md`
- `verification/M2-S1/dispatch-85a2aa7.md`

按派发要求，Owner 分支停留在固定 base、**不 merge 治理提交**，因此这两个文件**不在本分支**，本 Task
也**没有**创建、修改或删除它们。需要查阅时用
`git show origin/master:verification/M2-S1/release-85a2aa7.md`。

## 文件索引

| 路径 | 内容 |
|---|---|
| [`00-environment-and-recon.md`](00-environment-and-recon.md) | 固定点、clone 形态、Contract blob、环境与判定（文字版） |
| [`01-source-and-consumer-reality.md`](01-source-and-consumer-reality.md) | AC1：AS-IS 图片/tile 生产者与消费者、四类资源生命周期、Core/host seam |
| [`02-evidence-manifest.md`](02-evidence-manifest.md) | 证据清单、脚本/结果 hash、复现步骤、`NOT_RUN`/`UNVERIFIED` 汇总 |
| [`03-checkpoint.md`](03-checkpoint.md) | 恢复检查点（另一 Agent 可据此继续） |
| [`probes/`](probes/) | 可重跑探针与 runner（`00_recon.ps1`、`m2s1_lab.py`、`make_fixtures.py`、`probe_a..e`、`run_all.ps1`） |
| [`raw/`](raw/) | 原始日志（含确切命令与 exit code）、收集到的结果 JSON、fixture 清单与 hash |
| [`04-verification-plan-results.md`](04-verification-plan-results.md) | Task「验证计划」四行的实际执行结果与命令/exit 摘要 |

## 复现

```powershell
# 只读固定点核验
pwsh -NoProfile -File verification/M2-S1/probes/00_recon.ps1

# 全套探针（合成 fixture 生成在 %TEMP%\m2s1-lab，仓库内只留 hash 与日志）
pwsh -NoProfile -File verification/M2-S1/probes/run_all.ps1 `
  | Tee-Object -FilePath verification/M2-S1/raw/00-run-all.log
```

要求：Windows 10/11 x64、Python 3.14（本机 `C:\Python314\python.exe`，3.14.6）、PowerShell 7。
探针会在 `%TEMP%\m2s1-lab` 下创建约 200 MB 合成 fixture；删除该目录即可清理。
