# AC1（F-001/F-002/F-003）：证据文档修正

日期：2026-11-01。Owner：DSH。基线：`main@bb7cbda1d`。

## F-001 pin 计数与表格

`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` 已重写：

- 明确 SAFETY-6 实际有 **12 条** Canonical Evidence（4 代码 + 8 证据）；
- 实际值变化 **5 条**（`E-AC1-READER-VM`、`E-AC1-LIBRARY-VM`、`E-AC1-TEST-FAKE`、`E-AC1-LOG`、`E-AC2-DATA`），未变 7 条；
- 对照表补齐 4 条代码 pin（此前完全未列）；
- 说明 pin 统一改为 commit blob（LF）基准，以及 `check.ps1:691-714` 的「工作树 → 回退 blob」核对机制。

同步修正 `doc/tasks/REALUSE-DATA-SAFETY-7.md` 的 AC2 描述与测试表计数（12 条 / 5 条更新）。

## F-002 负向对照配方

`verification/REALUSE-DATA-SAFETY-7/ac1-negative-control.md` 已改为 **post-delivery 配方**：

```powershell
cmd /c "git -C `"$wt`" show 29d06c462:$src > `"$result`""
dotnet build NewManga.sln -v q --nologo
dotnet test ... --filter "FullyQualifiedName~ClosingWhileSaveInFlight"
git checkout HEAD -- $src
```

并附 2026-11-01 实测输出：build EXIT=0；filtered **1 failed / 0 passed，EXIT=1**；恢复后 `git status` 干净。

## F-003 日志 cwd 与 filtered 段

`verification/REALUSE-DATA-SAFETY-8/ac1-fix-tests.txt` 的每段 `## command:` 都记录 `cwd=<绝对路径>`，
并且 **filtered 运行单独成段**（含输出与 `EXIT=`）：

- build：EXIT=0
- `--filter FullyQualifiedName~LibraryProgressRefreshTests`：**7/7 通过**，EXIT=0
- 全量：**396 通过 / 0 失败 / 7 跳过（403）**，EXIT=0

## 验收

- 计数与表格一致（12 / 5 / 7）；负向配方可在交付 head 上逐字复现；日志含 cwd、filtered 段与 EXIT。
