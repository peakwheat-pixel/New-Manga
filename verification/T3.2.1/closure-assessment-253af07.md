# T3.2.1 全量 Release Gate 收口安排

Codex audit: 2026-09-23，PowerShell，`master` 固定检查点
`253af0720ba932b1af3fe2fe156262616dfedeca`。本文件是收口路线与缺项审计，
不构成验收 PASS、实现授权或集成许可。

## 固定对象与现有证据

- 产品实施基线 `c2fcb1ce575099f6e74f69c711f423040a545951`；交付分支
  `agent/antigravity/T3.2.1-repair-7`，tip
  `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04`。REPAIR-8 文档 Delivery
  `3cdfdee126e8aab6b7930e49460a753abc69dad0` 获 DeepSeek Harness
  `2585efd69009cd7620c6b020e67df90c7d49b0f1` 独立批准；该批准不覆盖产品 Gate。
- `verification/T3.2.1/build.log`、manifest、packaging/focused tests、local smoke、
  path safety 和 benchmark 属于开发机证据，主要绑定旧产品 head `7d687f5`。
  从 `7d687f5` 到当前 tip，`src/**`、`packaging/**`、依赖无差异，
  但 `tests/packaging/test_frozen_runtime_contract.py` 已改变；正式 Gate 应在
  最终固定 head 重新建立适用的测试和包证据。
- `clean-windows-smoke.log` 明写 `Simulated Clean Directory` 和 stripped PATH；
  `clean-windows-safety.log` 通过的是服务层探针；`benchmark-report.md` 测量
  `--smoke-test` / Qt offscreen，并非“点击程序至书架可交互”的 GUI 冷启动。
- 本机为 Windows 11 Pro x64 build 26200，有既存两个临时构建产物及 Python 3.12
  打包环境。`Get-VM` 当前账户返回权限不足；尚未验证有可用的独立 Windows 11
  测试机或 VM。现有开发机及剥离 PATH 模拟不能充当 AC3 干净机。
- 用户没有第二台电脑。原候选是在这台主机上使用**独立 Windows 11 Hyper-V VM**；
  宿主有约 32 GB RAM、充足磁盘、虚拟化已启用且 Hyper-V 服务正在运行。
  当前非提升账户不能运行 `Get-VM` 或查询可选功能；Windows Sandbox 可执行文件
  不存在。下一步由用户在提升的 PowerShell 运行只读 `Get-VM | Select Name,State`，
  确认是否已有 VM；若没有，再按 Microsoft 官方 Hyper-V 流程准备 Windows 11 ISO
  并创建独立 VM。VM 的存在、配置和 AC3 结果目前均未验证。
- 用户在提升的 PowerShell 两次运行 `Get-VM | Select-Object Name, State` 均无输出：
  当前 Hyper-V 没有已注册 VM。更少步骤的候选是 Windows Sandbox（同机的独立、
  每次启动全新且关闭即删除的 Windows 桌面）；宿主支持该功能，但当前未发现
  `WindowsSandbox.exe`，功能是否启用待用户在“启用或关闭 Windows 功能”确认。
  若启用，须先记录 Sandbox 内 OS、无开发依赖、完整包 hash 和 GUI 能力，再决定
  其证据能否满足 AC3/AC6/AC7；历史 runbook 中“物理机”字样不能据此写成实测。
  如 Sandbox 不可用或 GUI/进程/文件证据不足，退回 Hyper-V 完整 VM 路线。
- 用户启用 Windows Sandbox 时，Windows 功能报「并非所有的功能成功更改」。
  宿主 `C:/Windows/Logs/CBS/CBS.log` 在 2026-09-23 21:27:57 记录
  `STATUS_SXS_COMPONENT_STORE_CORRUPT` / `0x80073712`：解压 IIS 可选组件的
  `Microsoft.Web.Management.Aspnet.resources.dll` 失败，功能事务随后把
  `Containers-DisposableClientVM` 回滚为 Off。此为宿主组件存储修复前置，
  不归因于 New Manga，也不把 Sandbox 或 AC3 记为可用/PASS。用户随后在管理员终端
  运行 `DISM.exe /Online /Cleanup-Image /RestoreHealth`（成功）和 `sfc /scannow`
  （发现损坏并成功修复），并重启。2026-09-23 22:28:36 再次通过 Windows 功能界面
  启用 Sandbox 仍失败；新 CBS 记录同一 `0x80073712` 组件存储错误。用户随后在管理员
  PowerShell 单独运行 `Enable-WindowsOptionalFeature -Online -FeatureName
  Containers-DisposableClientVM -All`，仍收到「组件存储已损坏」。Sandbox 路线暂停；
  复查 2026-09-23 22:32:02–03 的 CBS，确认 `deltastore.cpp(3124)` 在
  `CRawStoreLayout::RecursivelyRegenerateComponentPayload` 报
  `STATUS_SXS_COMPONENT_STORE_CORRUPT`，随后解压 OC content 失败。宿主为 Windows 11
  Pro 25H2 x64 build 26200.9457。下一步先尝试 Settings > System > Recovery >
  Fix problems using Windows Update > Reinstall now 修复当前版本；该项不可用或修复后
  仍失败时，改用匹配版本/语言的官方安装媒体或转回独立 Hyper-V VM 路线。Sandbox
  与 VM 均未成功运行，AC3 仍为 `NOT_RUN`。

## 未闭环项与完成证据

| Gate | 当前口径 | 下一份必须取得的证据 |
|---|---|---|
| AC1/AC2、AC4 | 开发机构建、资源与清单已有证据；正式固定 head 待复验。两次 manifest 比较 exit 1，5437 项中 2 项 hash 不同，不得写成全包字节相同 | 固定 head 的完整 Build 1/Build 2 原始日志、依赖快照、两个 SHA-256 manifest、差异解释、资源检查与 exe hash。对“可复现”是否满足 Task AC2 作明确 Gate 判断 |
| AC3 / AC-PKG-002/003 | `NOT_RUN`；发布阻断 | 独立 Windows 11 x64 GUI 机器，无 Python、venv、源码、开发机 PATH；普通用户从复制并验 hash 的 onedir 包启动，展示真实主窗口与 Qt/QML 页面；记录 OS/依赖清单、命令或操作、截图/录像、原始 stdout/stderr、exit code 与失败诊断 |
| AC5 / AC-OPTIONAL-001/002 | `NOT_RUN` | 固定包/隔离环境无 PyTorch、大型修复模型、OCR runtime；Core/UI 启动，缺依赖 Provider 显示 Not Ready/Missing Dependency 且不崩；记录环境清单和可复核输出 |
| AC6 / AC-SMOKE | `PARTIAL / NOT_RUN` | 在同一干净机用 `NewManga.exe` 逐步完成书架→Book→Chapter→导入→工作台→至少一个 Mock/Local Pipeline→保存→阅读→导出→退出→重启恢复；步骤截图、产物及 SQLite 前后证据。服务层 `run_clean_flow_probe.py` 不能代替 GUI 发布包走查 |
| AC7 | `PARTIAL / NOT_RUN` | 同一发布包走查的源文件 hash/mtime 前后值、Managed Copy、Lock、current/pinned Revision、人工确认内容、SQLite 行与 Secret 日志检查；失败时保留隔离 fixture 与错误输出，不碰真实用户数据 |
| AC8 | 开发机 path-safety 已有证据；干净机适用性待核 | Unicode 数据根、默认 `%LOCALAPPDATA%`、显式 `--data-root`、只读程序目录、普通用户权限、退出后 tasklist 原始输出与 SQLite 独占锁探针 |
| AC9 / AC-PERF-001 | 5 次 `--smoke-test` P95=1.09s，不能证明书架可交互 P95≤3s | 固定推荐硬件与 Windows 11 环境下至少 5 次真正 GUI 冷启动，记录点击/进程启动到书架可交互边界、每次原始值、P50/P95 算法和结果；Windows 10 best effort 单列 NOT_RUN 或实测，不作推断 |
| R-014 | `open` | Build 2 独立原始构建日志；进程残留检查保存真实 `tasklist` 输出及命令/exit code。旧摘要“0”不可替代可复核输出 |
| R-015 | `open`（P2） | 将 `verify_path_safety.py:24` 的 `dict[str, any]` 改成正确类型，并运行该脚本/适用检查；归入下一授权实现切片 |
| R-016 | `open`（P2） | 在同一处列出 275 与 160 各自的测试选择命令、收集总数、passed/skipped/failed、环境与差值原因；修正文档口径，不伪造重跑结果 |
| F-003 | `open / deferred P2` | 下次授权触碰 REPAIR-6 文档时顺带改正四处“固定源”称谓；不单独释放 REPAIR-9 |
| AC10 | REPAIR-8 文档 Review approved；产品全量 Review/集成未完成 | 对最终产品 head 与全部干净机证据进行 DeepSeek Harness 非作者 Review；P0/P1 全通过后 Codex 集成复验与 integration evidence |

## 执行顺序、Owner 与 Gate

1. **Codex 固定测试对象和环境。** 确认独立 Windows 11 x64 实机或 VM 的操作人、
   GUI/普通用户权限、文件传入及证据取回方式；确认无 Python、源码、venv、开发机
   PATH。若环境不可得，AC3/AC6/AC7 保持 `NOT_RUN`，T3.2.1 保持 release-blocked。
   不用本机 stripped-PATH 模拟替代。
2. **Codex 登记下一实施切片后由 Antigravity 执行。** 从当前交付 tip 与现有
   `packaging/build.ps1`、`clean-windows-runbook.md` 复核输入，冻结新的构建/测试
   head；补 R-014 的第二次原始 build 与 tasklist 输出、R-015 类型修复、R-016
   测试数字对账；在固定 head 重跑必要的 `tests/packaging`、focused tests、
   `compileall`、资源/manifest/hash 检查。具体 allowed paths、branch、base 由
   Codex 在释放 Task 时登记；当前安排本身不授权改动交付分支。
3. **独立 Windows 验收。** 测试操作人使用固定产物与隔离 fixture，按上述
   AC3→AC5→AC6/AC7→AC8/AC9 顺序执行并存入 `verification/T3.2.1/**`。
   每项记录 shell/OS/hardware、被测 commit、artifact hash、操作或命令、原始
   输出、exit code、截图/录像/数据库证据及 PASS/FAIL/BLOCKED/NOT_RUN。
   如需新构建或代码修复，重新冻结 head 并重跑受影响项目。
4. **独立 Review 和 Codex Gate。** DeepSeek Harness 对最终固定 head、Handoff、
   证据和开放 findings 做非作者复审。只有 P0/P1、干净 Windows、安全和性能 Gate
   全部满足，且 Review approved，Codex 才可考虑合并，随后在 master 重跑受影响
   检查、写 integration evidence 和更新 STATUS。当前不得合并
   `agent/antigravity/T3.2.1-repair-7` 或宣称 READY。

`verification/T3.2.1/release-gate-c2fcb1c.md` 的 PASS TO START 只授权实施；
本清单不更改 D08 的阈值或发布优先级，不提供豁免。
