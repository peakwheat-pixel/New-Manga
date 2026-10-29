# V11R-C-3-I1 干净树 R6 重跑

- 生成时间：2026-10-30T04:35:40+08:00
- 分支：``v11r/c3-i1``；源码 HEAD：``641c0a075d5c09e1f7b1855dee5df572e9262c5e``
- **workingTreeDirty = false**（dependency-graph 与 contrast-matrix 均在干净树生成，见其 JSON 元数据）
- 证据文件清单（SHA-256 + 字节数）：``R6-clean-file-manifest.txt``（44 个文件）

## 1. 零引用门（干净树）

- ``verification/V11R-C-3/dependency-graph.json``：``repoHead=641c0a075``、
  ``workingTreeDirty=False``、142 引用 / 54 文件；
  分类仅 ``evidence-or-documentation=87`` + ``new-architecture=15`` + ``new-architecture-tests=21`` +
  ``platform-struct-unrelated=19``；fate 仅 ``EVIDENCE-PIN-PROTECTED=87`` + ``NOT-A-DEPENDENCY=55``。
  **legacy-theme-source / legacy-shell-production / legacy-tests 均为 0；DELETE/MIGRATE/REPLACE 均为 0。**
- 日志：``R6-clean-dependency-graph.log``、``dependency-graph-table.md``；执行态副本见 ``final/``。

## 2. 对比度矩阵（干净树）

- ``contrast-matrix.json``：``workingTreeDirty=False``、``failures=0``、``failing_pairs=0``。
- 日志：``R6-clean-contrast-matrix.log``、``contrast-matrix.md``；D-1 I3 副本在
  ``verification/V11R-D-1/I3/contrast-matrix.json``。

## 3. 构建与全量测试（干净树）

- ``dotnet build NewManga.sln -warnaserror``：0 warning / 0 error（``R6-clean-build.log``）。
- ``dotnet test NewManga.sln --no-build``：**0 失败**（``R6-clean-test.log``）：
  App 283 + 7 skip、ThemeEngine 235、DS 85、Host 49 + 28 skip、CoreClient 116 + 25 skip。

## 4. 双 shell 启动 / 优雅退出（不是 kill）

- 真实 sidecar bundle：``apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar``；
  独立 data-root、唯一 mutex；启动 8s 观察窗口，随后 ``WM_CLOSE``，等待进程退出。
- ``--shell=v2``：窗口标题 ``New Manga``，优雅关闭 **EXIT=0**。
- ``--shell=legacy``：窗口标题 ``New Manga``，优雅关闭 **EXIT=0**；host.log 记录
  single-instance → core_service ready → host_bridge ready → host-control session opened。
- 日志：``R6-clean-startup-smoke.log``、``R6-clean-v2-host.log``、``R6-clean-legacy-host.log``。
- 诚实说明：v2 本次未产生 host.log（ui-shell 的 P0“v2 启动 Host”仍待修复，见 Lead 排期）；
  v2 窗口创建与退出码 0 已记录，不把缺失的 Host 日志写成通过。
- 修复：legacy 在真实 sidecar 下此前关闭返回 -1（Host 停止时异常逃逸到未处理异常）；C-3-I1 将
  ``MainWindow.OnClosed`` 的 Host 停止改为 best-effort（记录 Trace，不改变正常退出码），本次两壳均 0。

## 5. 复现命令

``````powershell
git checkout 641c0a075d5c09e1f7b1855dee5df572e9262c5e
pwsh -NoProfile -File tools/v11r/build-dependency-graph.ps1
pwsh -NoProfile -File tools/v11r/contrast-matrix.ps1
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
``````
