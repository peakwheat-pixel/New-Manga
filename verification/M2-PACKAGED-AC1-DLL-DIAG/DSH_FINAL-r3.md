**r2 报告整合完成（DSH 无 shell，实跑由 Codex 完成）。**

**本轮改动文件**
- `verification/M2-PACKAGED-AC1-DLL-DIAG/REPORT.md`（r2 版）
- `verification/M2-PACKAGED-AC1-DLL-DIAG/dll-closure-matrix.json`（r2）
- `doc/tasks/M2-PACKAGED-AC1-DLL-DIAG.md`（AC1–AC4 勾选＋证据、status→**in_review**、追加 r2 运行记录）
- `doc/handoffs/M2-PACKAGED-AC1-DLL-DIAG-20261008-dsh.md`（r2，引用固定证据 head）
- 未改：所有 `raw/**` 原文、`local-evidence.md`、Codex 支持 probe、产品/packaging、其它历史证据；无新增依赖、无修复。

**矩阵更新**
- C11 UNKNOWN → **PROVEN**：包内 `_internal/icuuc.dll` 遮蔽 System32 同名 ICU，导出仅 `_78`（`ucnv_open_78` 等 6 个），而 `Qt6Core.dll` 导入 20 个无后缀 `ucnv_*`/`UCNV_*`；Qt6Core 原生加载 WinError 127 → QtGui ImportError。
- C13（搜索路径）→ PROVEN 相关；C14（符号级错配）→ PROVEN 根因；C1–C7 REJECTED；C8/C9/C10 维持"未观察到/影响 UNKNOWN、不参与根因"；C12 部分解决（lab 与 installed 的 Qt6Gui/Qt6Core/icuuc **hash 一致**，但 installed 树未做改名对照）。
- 勘误：ERR-1 `symbol-probe.json` "缺 64 符号"= pefile 默认 8192 导出上限伪差（已排除）；ERR-2 初次 wrapper 路径预检/缺 PATHEXT 失败保留；ERR-3 r1 的"126 高置信"作废。

**执行者与环境**：执行者=Codex（本机隔离执行，只写自有 lab/raw）；子进程 purged `PATH=C:\WINDOWS/System32;C:\WINDOWS`、显式 `PATHEXT`、stdin EOF、data root 指向 lab。**实测 bridge：原 case EXIT1/0.8s（QtGui 错误复现）、改名 icuuc 对照 EXIT0/0.42s；外层 wrapper EXIT0 ≠ bridge PASS。** DSH 侧复跑/ git 校验仍 **NOT_RUN**（Win32 5）。

**UNKNOWN 限制**：原 Gate 运行的 Win32 错误码（原日志无 GetLastError，不得回填 127）；installed 树无改名对照、未在真 purged-PATH 安装态复跑；其它仍需 ICU78 的依赖未核实（**禁止全局删 ICU78**）；完整 26 项 Gate 未跑。范围限定**本固定产物＋本机**，不称 Gate PASS、不解除 runner debt。

**下一 Task 建议**：`M2-PACKAGED-AC1-ICU-ISOLATION-FIX`（未创建/未释放）；Owner 建议 Antigravity/ZCode，非作者 Reviewer=DSH；先冻结 `packaging/m2ac5/**`＋自有 verification，保护其它 ICU78 依赖与原 purged PATH；fresh Sidecar+NSIS→固定 installer SHA→完整 26 项→非作者 Review→Codex 集成；改依赖/共享契约先交用户。Task 已置 in_review，**AC5 待 Codex Review/集成，DSH 不自审不 done**；delivery_head 未猜，报告 commit 由 Codex 提交后补记。