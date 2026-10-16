# P18 真实运行记录

## 运行命令与环境

PowerShell 7.6.6；Python 3.12.3 为 P13 资源清单中已保留的 `T1.1.1-impl-py312` 环境。用 `-B` 禁止写 bytecode；不安装依赖。脚本只调用本机 JSONL Core sidecar，删除传给子进程环境的 key/secret/token 变量；未调用远程 API。每次 `NEWMANGA_DATA_ROOT` 都是本 Task 自己的 `verification/P18/raw/<lang>-r3/data`。

```powershell
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -B 'experiments/P18/run_core_slice_probe.py' --lang ja --image 'G:/CODEX/New Manga.workspace/test-materials/objects/sha256/9b/9bbd38763fde3a45e0dc3af61647ee8097f1345653dce99c32759a58c6c499e1.png' --output 'verification/P18/raw/ja-r3'
```

命令 exit=0（runner 完成归档）；Core sidecar exit=0。request-level 结果：`core.ping=ready`；`ImportPages=UNKNOWN_COMMAND`；`core.detect=INVALID_REQUEST`，输入 `2946×4167=12,275,982 px` 超过 `11,184,810 px` 限制；`core.shutdown=stopped`。完整原始 stdout/stderr bytes、UTF-8 可读副本、退出码、摘要分别在 `verification/P18/raw/ja-r3/`。模型与 OCR 未被调用。

```powershell
& 'G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe' -B 'experiments/P18/run_core_slice_probe.py' --lang ko --image 'G:/CODEX/New Manga.workspace/test-materials/objects/sha256/c4/c451815727ec24b64bfd7656fd7fe574879de4d9dc1d79013456f89cee22b7a2.png' --output 'verification/P18/raw/ko-r3'
```

命令 exit=0（runner 完成归档）；Core sidecar exit=0。request-level 结果：`core.ping=ready`；`ImportPages=UNKNOWN_COMMAND`；`core.detect=PROVIDER_NOT_CONFIGURED`，隔离 data root 缺少 pinned `ogkalu/comic-text-and-bubble-detector@16e8a622` 三文件；stderr 明示禁止运行时下载；`core.shutdown=stopped`。完整原始 stdout/stderr bytes、UTF-8 可读副本、退出码、摘要分别在 `verification/P18/raw/ko-r3/`。

## 逐步结果与 terminal

两次 sidecar 进程退出码都是 `0`，但只说明进程正常收到了 `shutdown`。`ImportPages` 不在 production Core IPC allowlist；导入没有成功，因而没有页 ID、`run_id` 或 Run/Task/Step terminal。没有发出伪造目标的 `StartRun`。JA 随后在 request guard 被像素上限拒绝；KO 随后在真实 detector provider readiness 检查中以 `PROVIDER_NOT_CONFIGURED` 拒绝。两种语言的 OCR、翻译、修复、渲染和 pipeline terminal 都 `NOT_RUN`，见 `terminal-matrix.csv`。没有以 sidecar exit=0 推导产品 PASS。

## 保留的仪器化尝试

首次 r1（`raw/ja/`、`raw/ko/`）用于核验 JSONL 请求形状与运行隔离；r2（`raw/ja-r2/`、`raw/ko-r2/`）改为原始 bytes 捕获；r3 是记录完整 Python/package/model/device 元数据的 canonical 运行。r1/r2/r3 request-level 结果一致，早期目录保留，不覆盖或删除；终态矩阵与结论只引用 r3。

Core 只对本次新建的隔离根运行启动恢复/GC；stderr 记录 `orphan_files_removed=0 dead_rows_removed=0`。没有访问或写入用户漫画库、主仓数据或其他 worktree。
