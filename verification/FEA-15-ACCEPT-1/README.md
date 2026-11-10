# FEA-15-ACCEPT-1 验证记录（进行中）

- 验证产品基线：`d63d735a712dbe47100db2e72b4d59a73dfd1f62`；该提交相对原始接续 HEAD `164ebabcfa90b92fc46c07238280960fc01f7423` 仅变更本 Task 治理文档。
- 2026-11-10：隔离 linked worktree `G:/CODEX/New Manga.workspace/FEA-15-ACCEPT-1/clean-tree`；构建前无 `bin`/`obj`。`dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`：0 警告、0 错误、EXIT 0，见 `build.log`。
- 初次 pytest 因隔离 `APPDATA` 隐藏 Python 用户包而找不到 pytest，EXIT 1，见 `pytest-full.log`。保留用户包位置并隔离 AppData/TEMP 后的完整重跑：3515 passed / 16 failed / 12 skipped，EXIT 1，见 `pytest-full-retry.log`（含逐条 skip 原因）；不能记为全绿。失败包括 v7 fixture 的 `custom_rank` 缺列以及插件沙箱/导出钩子相关项目，根因和影响范围待裁决。
- 主树同隔离环境定向复跑插件沙箱文件和 3 个导出 hook 参数用例：4 passed / 15 failed，EXIT 1，见 `pytest-main-targeted.log`；不能将这些失败归为仅由 linked worktree 造成。内存 v7 阶段查询缺列的独立复现见 `v7-repro-2.log`，不等于证明正常迁移至 v14 后失败；首次复现日志的 worktree HEAD 查询受权限限制，已保留原输出与事后说明。
- 内存正向探针 `v7-v14-probe.log`：v7 查询重现缺列；迁移至 v14 后 `custom_rank` 存在，对不存在 chapter 的查询正常返回 `None`，EXIT 0。该探针不证明真实用户库迁移、现存业务数据完整性或回退通过。
- 主树 `pytest --collect-only -q` 收集 3542 项，EXIT 0（`pytest-collect.log`）；全量运行汇总 3543 个结果含收集阶段 skip，口径不同。PREREQ-2 历史报告记 3456 collected，但未提供逐项清单和解释器信息，差异原因尚未完整核实。
- 8 个 .NET 项目逐项执行，2 个项目失败，EXIT 1：App 884 passed / 4 failed / 11 skipped；Appearance 21/0/0；ApplicationCore 31/0/0；CoreClient 164/0/27；DesignSystem 117/0/0；Host 198/123/74；Presentation 72/0/0；ThemeEngine 253/0/0。命令、各项目 EXIT 与跳过原因见 `dotnet-full.log`。App 4 项失败堆栈指向 `Directory.Exists(.git)`，linked worktree 的 `.git` 为文件；Host 失败包括仓库定位和 ACL 拒绝，不能把所有失败归因于同一原因。
- 原测试 `tests/fea11/conftest.py` 硬编码共享 `G:/CODEX/New Manga.workspace/FEA-11/fixtures` 且不清理。`fixture-observation.log` 按本次测试时窗列出 62 个候选目录；仅时间相关，未证明独占归属，未清理。后续须先裁定隔离方案。
- 插件沙箱测试会调用 `icacls /grant`，尝试在 Python 解释器和其目录授予 AppContainer 访问权限，`close()` 不撤销授权。事后只读检查 `C:/Python314/python.exe` 与 `C:/Python314` 可见多个 AppContainer SID 的 ACL；运行前未采集 ACL 快照，不能判定本次新增项，也不能声称未修改系统 ACL。未删除或修改这些授权；须由 ZCode 裁决资源处置与后续安全测试方法。
- 旧安装包 `G:/CODEX/New Manga.workspace/FEA-15-A2-1/out/NewManga-0.1.1-setup.exe` 存在，SHA-256 `486a22758c03c8cd2383b6cb05f6e91524cf5545094ef1533d89f73814d3ba10`；其基线之后产品代码已有变化，不能证明当前 HEAD 的安装。当前 HEAD 安装、真实双入口 UI 和真实用户库升级/回退均尚未实测，不得记 PASS。
- 主树既有 App/Host Release 测试程序集哈希与隔离树新构建程序集不同；为保护未跟踪的既有构建产物，未覆盖它们，也未将旧程序集执行结果冒充当前版本对照。
- 默认与指定 Task 的 `check.ps1` 均 PASS（3 warnings，EXIT 0）；`verify_pins.ps1` 18/18 PASS、EXIT 0。以上为认领后的执行结果；最终门禁仍需重跑并留日志。

## NOT_RUN / 待定

- 当前 HEAD 安装包安装、四页面真实会话、双 UI 真实会话：尚未执行；隔离及旧安装包适用性待裁决。
- 当前 v14 真实用户库升级及 `pre_restore` 回退：尚未执行。A4-1 合成 v8→v9 历史演练不能代替它。
- 最终独立 Review、阶段验收结论、最终门禁与 canonical evidence：尚未执行。
