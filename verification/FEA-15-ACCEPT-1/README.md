# FEA-15-ACCEPT-1 验证记录（进行中）

- 验证产品基线：`d63d735a712dbe47100db2e72b4d59a73dfd1f62`；该提交相对原始接续 HEAD `164ebabcfa90b92fc46c07238280960fc01f7423` 仅变更本 Task 治理文档。
- 2026-11-10：隔离 linked worktree `G:/CODEX/New Manga.workspace/FEA-15-ACCEPT-1/clean-tree`；构建前无 `bin`/`obj`。`dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`：0 警告、0 错误、EXIT 0，见 `build.log`。
- 初次 pytest 因隔离 `APPDATA` 隐藏 Python 用户包而找不到 pytest，EXIT 1，见 `pytest-full.log`。保留用户包位置并隔离 AppData/TEMP 后的完整重跑：3515 passed / 16 failed / 12 skipped，EXIT 1，见 `pytest-full-retry.log`（含逐条 skip 原因）；不能记为全绿。失败包括 v7 fixture 的 `custom_rank` 缺列以及插件沙箱/导出钩子相关项目，根因和影响范围待裁决。
- 主树同隔离环境定向复跑插件沙箱文件和 3 个导出 hook 参数用例：4 passed / 15 failed，EXIT 1，见 `pytest-main-targeted.log`；不能将这些失败归为仅由 linked worktree 造成。内存 v7 阶段查询缺列的独立复现见 `v7-repro-2.log`，不等于证明正常迁移至 v14 后失败；首次复现日志的 worktree HEAD 查询受权限限制，已保留原输出与事后说明。
- 内存正向探针 `v7-v14-probe.log`：v7 查询重现缺列；迁移至 v14 后 `custom_rank` 存在，对不存在 chapter 的查询正常返回 `None`，EXIT 0。该探针不证明真实用户库迁移、现存业务数据完整性或回退通过。
- 主树 `pytest --collect-only -q` 收集 3542 项，EXIT 0（`pytest-collect.log`）；全量运行汇总 3543 个结果含收集阶段 skip，口径不同。PREREQ-2 历史报告记 3456 collected，但未提供逐项清单和解释器信息，差异原因尚未完整核实。
- 8 个 .NET 项目逐项执行，2 个项目失败，EXIT 1：App 884 passed / 4 failed / 11 skipped；Appearance 21/0/0；ApplicationCore 31/0/0；CoreClient 164/0/27；DesignSystem 117/0/0；Host 198/123/74；Presentation 72/0/0；ThemeEngine 253/0/0。命令、各项目 EXIT 与跳过原因见 `dotnet-full.log`。App 4 项堆栈终止于 `get_RepoRoot()` 的 NotNull 失败；linked worktree 的 `.git` 文件形态与失败的关联由源码和对照实验支持。Host 失败包括仓库定位和 ACL 拒绝，不能把所有失败归因于同一原因。
- 原测试 `tests/fea11/conftest.py` 硬编码共享 `G:/CODEX/New Manga.workspace/FEA-11/fixtures` 且不清理。`fixture-observation.log` 按本次测试时窗列出 62 个候选目录；仅时间相关，未证明独占归属，未清理。后续须先裁定隔离方案。
- 插件沙箱测试会调用 `icacls /grant`，尝试在 Python 解释器和其目录授予 AppContainer 访问权限，`close()` 不撤销授权。事后只读检查 `C:/Python314/python.exe` 与 `C:/Python314` 可见多个 AppContainer SID 的 ACL；运行前未采集 ACL 快照，不能判定本次新增项，也不能声称未修改系统 ACL。未删除或修改这些授权；须由 ZCode 裁决资源处置与后续安全测试方法。
- 旧安装包 `G:/CODEX/New Manga.workspace/FEA-15-A2-1/out/NewManga-0.1.1-setup.exe` 存在，SHA-256 `486a22758c03c8cd2383b6cb05f6e91524cf5545094ef1533d89f73814d3ba10`；其基线之后产品代码已有变化，不能证明当前 HEAD 的安装。当前 HEAD 安装、真实双入口 UI 和真实用户库升级/回退均尚未实测，不得记 PASS。
- 当前构建的 legacy/Fluent 两入口以隐藏窗口、各自隔离 data/theme/log/TEMP 和 mutex 启动，2 秒仍存活、退出码均 0，进程级结果 EXIT 0；日志未匹配 fatal/unhandled，真实 data/theme 目录的文件名/大小/mtime 元数据指纹前后一致（不等于内容逐字节证明）。详见 `ui-process-smoke.log`。因隐藏窗口，视觉可见性、用户导航和四页交互仍为 NOT_RUN；进程级结果不等于 UI 验收通过。
- 主树既有 App/Host Release 测试程序集哈希与隔离树新构建程序集不同；为保护未跟踪的既有构建产物，未覆盖它们，也未将旧程序集执行结果冒充当前版本对照。
- 仓外 `git archive` 对照：首次全仓解包因历史文件名不兼容 Windows 而 EXIT 1，保留不完整结果（`source-fixture.log`）；仅提取 `apps/desktop-avalonia` 并在夹具根建空 `.git` 目录后，4 项 App 仓库定位测试 4 passed、EXIT 0（`dotnet-repo-root-control.log`）。这支持原失败与 linked worktree 的 `.git` 形态相关；该对照是构造环境，不是完整主树测试。
- 同一对照夹具中两项 Host 样例：仓库定位样例 passed，ACL 样例仍 `UnauthorizedAccessException`，共 1 passed / 1 failed、EXIT 1（`dotnet-host-control.log`）；不能据此归因全部 123 项 Host 失败。
- 仓外固定版本插件源码和专用 Python venv 对照：解释器解析到任务目录，沙箱测试 6 passed / 10 failed、EXIT 1（`plugin-fixture.log`、`plugin-control.log`）；它仍依赖系统 Python 标准库和用户包，不能单独判定根因。AppContainer profile 属用户级系统资源，测试可创建或复用 profile，未做事前清单、未清理或断言无副作用。所有夹具、虚拟环境、档案和输出保留，未清理。
- 默认与指定 Task 的 `check.ps1` 均 PASS（3 warnings，EXIT 0）；`verify_pins.ps1` 18/18 PASS、EXIT 0。以上为认领后的执行结果；最终门禁仍需重跑并留日志。
- r1 P2-1：本卡原登记的 29 条 EV/SRC pin 使用本机工作区字节口径，其中 26 条与 Git blob 哈希不同，跨 checkout 不可复现；需后续 pin 口径治理卡处理，本卡不改仓库级行尾规则。
- 裁决日志实际顺序：`zcode-second-decision-raw.log` 为中期处置 II，`zcode-serial-decision-raw.log` 为撤回并行建议的串行化补充，`zcode-evidence-decision.log` 为最终证据分类与收口路径裁决。文件名保留原样。
- 证据文件实际平铺于本目录，日志命令和退出码与本 README 共同提供复现入口；这与原证据计划的 `logs/` 子目录结构不同。

## NOT_RUN / 待定

- 当前 HEAD 安装包安装、四页面真实交互、双 UI 可见窗口会话：NOT_RUN；旧安装包仅作历史参考。两入口隐藏进程级冒烟另见上文。
- 当前 v14 真实用户库升级及 `pre_restore` 回退：尚未执行。A4-1 合成 v8→v9 历史演练不能代替它。
- 独立 Review r1 已出，条件处置后的 r2、最终验收结论与最终门禁仍待完成。
