# probe/ 使用说明（由 DSH 创建，DSH 未执行）

DSH 本会话无 shell 能力（沙箱 `SetNamedSecurityInfoW failed (Win32 5)`），
两个 probe 文件因此**处于 NOT_RUN 状态**，交 Codex 实跑后再独立审查。

## 文件
- `run_dll_diag_probe.ps1`：编排探针。步骤 1 hash 门 → 2 bundle 闭包枚举 → 3 安装树枚举（填 C12 UNKNOWN）
  → 4 可选 lab 复制（`-CopyBundle`）→ 5 purged-PATH 复现运行 → 6 PE 导入表探针 → 7 产物清单。
- `pe_import_probe.py`：纯标准库 PE 导入表/延迟导入表解析（只按字节读文件，从不加载或执行被检对象）。

## 执行（建议）
```powershell
Set-Location 'G:/CODEX/New Manga.worktrees/PACKAGED-AC1-DLL-DIAG-dsh'
pwsh -NoProfile -File verification/M2-PACKAGED-AC1-DLL-DIAG/probe/run_dll_diag_probe.ps1 `
  -InstallDir '<待填：本次 clean-start lab 的 install 目录>' -CopyBundle
```
Python 解释器默认 `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（既有环境，不新增依赖）。

## 安全边界
- 只写 `verification/M2-PACKAGED-AC1-DLL-DIAG/{lab,raw}/`；**不写** `RUNNER-SNAPSHOT-DEBT-codex`。
- 只改**子进程**环境变量以复现 purged PATH；不改系统 PATH、不改共享 env、不安装 Qt。
- 不触碰 `src/apps/tests/packaging`，不部署/推送/合并。
- 无 secret 输出；清单只含路径、字节数与 SHA256。

## 结果解释边界
- 步骤 2/3/6 是**静态**证据：文件存在或导入表可解析 ≠ 能加载。
- 只有步骤 5 的真实进程运行才是加载验证；步骤 5 复现成功仍不等于"根因 DLL 已确定"，
  必须结合步骤 6 的 `missing_union` 与原始 traceback 才能缩小到具体模块。
- 若步骤 5 出现 `NO_REPRO`，必须记录环境差量，**不得**宣称原 Gate 修复。
