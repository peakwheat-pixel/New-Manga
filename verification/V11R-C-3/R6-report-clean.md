# V11R-C-3-I1 干净树 R6 重跑（终版）

- 分支：``v11r/c3-i1``（已 merge main ``a0fa98b``，含 INT-2 v2 Host 修复、A-8 CLI、L4 证据）
- **源码 HEAD**：``e41017aa99fba1e161569ae7d73ec7da9c518ddd``（本证据 commit 的父提交）
- **workingTreeDirty = false**：dependency-graph 与 contrast-matrix 均在干净树生成（JSON 元数据自证）
- 证据文件清单：``R6-clean-file-manifest.txt``（SHA-256 + 字节数，含本报告）

## 1. 零引用门（干净树）

- ``dependency-graph.json``：``repoHead=e41017aa``、``dirty=false``，**145 引用 / 56 文件**；
  ``evidence-or-documentation=89``、``new-architecture=15``、``new-architecture-tests=21``、
  ``platform-struct-unrelated=20``；fate 仅 ``EVIDENCE-PIN-PROTECTED=89`` + ``NOT-A-DEPENDENCY=56``。
  **legacy-theme-source / legacy-shell-production / legacy-tests 均为 0；DELETE / MIGRATE / REPLACE 均为 0。**
- ``R6-clean-dependency-graph.log``、``dependency-graph-table.md``；``final/dependency-graph.executed.json``
  与 ``final/dependency-graph.clean.json`` 均为 dirty=false 的同一终态副本。

## 2. 对比度矩阵（干净树）

- ``contrast-matrix.json``：``dirty=false``、``failures=0``、``failing_pairs=0``。
- ``R6-clean-contrast-matrix.log``、``contrast-matrix.md``；干净副本 ``final/contrast-matrix.clean.json``。

## 3. post-I1 构建与全量测试（当前 main 基线）

- ``dotnet build NewManga.sln -warnaserror``：**0 warning / 0 error**（``R6-clean-build.log``，``R6-build.log`` 同步）。
- ``dotnet test NewManga.sln --no-build``：**0 失败**（``R6-clean-test.log``，``R6-test.log`` 同步）：
  - App **309** 通过 / 7 跳过
  - ThemeEngine **235** 通过
  - DesignSystem **85** 通过
  - Host **49** 通过 / 28 跳过
  - CoreClient **116** 通过 / 25 跳过
- 说明：字节实测值以本机日志为准；Reviewer 提到的 119+22/308+7 是 main 上另一时刻的采样，
  本分支 merge main 后实测为 116+25/309+7，0 fail 不变。

## 4. 双 shell 启动 / 优雅退出（实测退出码 0/0）

- 真实 sidecar：``apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar``；
  独立 data-root、唯一 mutex；**``--exit-after 2500``**（pin 的解析键为 ``exit-after``，不是
  ``exit-after-ms``；后者不存在于 AppOptions，使用它会被忽略并导致不退出。未改产品逻辑）。
- ``--shell=v2``：EXIT=**0**；``R6-v2-host.log`` / ``R6-clean-v2-host.log`` 记录
  core_service ready → host_bridge ready → host-control session opened（INT-2 修复后 v2 Host 已启动）。
- ``--shell=legacy``：EXIT=**0**；``R6-legacy-host.log`` / ``R6-clean-legacy-host.log`` 同样记录完整 Host 会话。
- 汇总：``R6-clean-startup-smoke.log``，并已把干净结果同步到规范的 ``R6-startup-smoke.log``；
  ``R6-host-startup.log`` 已改为 v2 的 host.log（原文件内容是 legacy，按复审意见修正）。
- 两壳均无 ``FORCED_KILL``、无 ``terminated_by_harness`` 字样，退出码来自自然关窗。

## 5. 复现

``````powershell
git checkout e41017aa99fba1e161569ae7d73ec7da9c518ddd
pwsh -NoProfile -File tools/v11r/build-dependency-graph.ps1
pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
``````
