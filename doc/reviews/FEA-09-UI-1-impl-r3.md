<!-- FEA-09-UI-1 implementation review r3 (Codex independent) -->
# FEA-09-UI-1 实现 Review r3（Codex 独立）

- Reviewer：Codex 全新上下文；未参与实现/返修；只读。
- reviewed_head：`091f702bfd331d02f4384af4278f9740d1731c47`。
- 结论：changes_requested，P0=0/P1=0/P2=3（N1/N4/N5）。
- DSH 处置：见 Task/Handoff r3 处置节。

---

verdict: **changes_requested**
P0=0 / P1=0 / P2=3
reviewed_head: `091f702bfd331d02f4384af4278f9740d1731c47`
身份/来源：Codex 全新上下文 `/root`，独立实现 Reviewer r3；未参与实现或返修。只读检查，未修改仓库、commit、push。
辅助审查：独立只读子任务 `/root/standards`、`/root/spec`。

N1–N5 核验：

- **N1：PARTIAL**。成功日志均有 `EXIT=0`；8 程序集日志汇总确为 **1317/0/74**；IPC TRX 确为 **16/0/0**。原 P1 的成功记录缺失已实质修复，但保全仍有 P2 缺口。
- **N2：PASS**。receipt Grid 为 `Auto,Auto`，CountsText 独立第二行；标题 Grid 误放行定义已移除。静态检查未发现布局回归。
- **N3：PASS**。扫描覆盖生产 `registry.v1.dat` 原始持久化字节；AC-MATRIX/gates 已明确 opaque/DPAPI 边界，不再宣称验证 List() 明文视图。
- **N4：PARTIAL**。归档 UI 行和真实 receipt 均含 `FILE_IDENTITY_CHANGED`，章节为 0 页；测试关联方式仍不能严格保证断言来自本次新增帧及 UI 行。
- **N5：PARTIAL**。proposed 已标历史，frontmatter 为 `in_review`；delivery_head、EV commit 和 Closeout Record 尚未同步到已提交状态。

剩余 findings（Standards 1 项；Spec/证据 2 项）：

- **P2 / N1：全量 TRX 被覆盖，原始日志缺执行命令。** [full-test.log:35](</G:/CODEX/New Manga/verification/FEA-09-UI-1/logs/dsh/full-test.log:35>) 起反复覆盖同一路径，最终 TRX 仅保留 App.Tests **670/0/7**；三份日志均无命令头。最小修复：按程序集保存唯一 TRX，记录实际命令、环境、EXIT，并更新 EV；现有日志可支持总数，不能把单份 TRX 当作全量明细。
- **P2 / N4：断言仍可绕过 UI 行且帧增量算法不严谨。** [测试:145](</G:/CODEX/New Manga/apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea09UiImportIpcProductionTests.cs:145>) 将多个日志拼接后按总长度截取，前部文件增长会让历史后缀进入 delta；`:155` 又允许仅 `Snapshot.LastError` 满足断言。最小修复：逐文件记录 offset，关联本次 operation/request；直接断言单条 receipt 行 OutcomeText 同码及 0 页。
- **P2 / N5：交付指针仍未固定。** [Task:18](</G:/CODEX/New Manga/doc/tasks/FEA-09-UI-1.md:18>) 仍写“提交后回填”，35 项 EV commit 为 pending，`:141–142` 仍称等待 r2、未提交。最小修复：DSH 后续文档提交固定 delivery_head、填写各证据实际所在 commit，更新当前复审状态。

R1–R7 spot-check：

- **R1**：token 创建即登记清理上下文，未 accepted 出口由 finally 清理；失败 IPC 负测保留。
- **R2**：receipt 暂时失败保留 operation、轮询与取消入口。
- **R3**：folder 转交 Host 枚举，App 未恢复递归或授权逻辑。
- **R4**：真实 HostController + VM + HostRuntime + Python stdio 闭环保留；未用 fake 冒充 AC-4。
- **R5**：多加密源 typed 拒绝保留。
- **R6**：逐项已提交/待处理计数已绑定显示。
- **R7**：skipped_pages 与 skipped_sources 分开显示。

冻结与验证：

- C-05/C-15/C-16/C-07、FEA-08/09 closeout、组合根、其它页面及旧 ImportPages 未改。
- `7f4f4d3cd..091f702b` 除 DSH 集成的 STATUS 外均在 allowed_paths；需将该例外如实列明。
- 实跑：C-07 `--check` **PASS**；`check.ps1` **PASS，3 warnings**；`verify_pins.ps1` **17/17 PASS**；Task EV 哈希 **35/35 匹配**。
- AC-1…AC-5：现有行为证据可判 **MET**；N1 证据保全、N4 防回归断言仍为 **PARTIAL**，不宜宣称 N1–N5 全闭环。
- NOT_RUN：build、全量 .NET、真实 IPC、整窗口视觉/E2E；前三项仅核验归档日志/TRX，未臆测复跑结果。
- r2 报告未归档；本次按指定 Handoff 处置节与 gates.json fallback 核验。

推荐下一步（可转发 DSH）：**请在 FEA-09-UI-1 既有范围内闭环上述 N1/N4/N5 三项 P2，保存完整命令及分程序集 TRX，固定交付与 EV commit，更新证据哈希；随后指定全新上下文 Codex 只读复审固定新 head。**