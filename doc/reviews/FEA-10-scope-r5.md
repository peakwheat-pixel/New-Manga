<!-- FEA-10 scope review r5 (Codex independent) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r5（Codex 独立）

- Reviewer：Codex 全新上下文；未参与建卡/实现；只读。
- reviewed_head：`1854153473c63d556fb47fcebde7966594439168`。
- 结果：PREREQ-1 **approved**（残留 P2 非阻断）；FEA-10 changes_requested P0=0/P1=1/P2=2。
- DSH 处置：`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md` §Scope Review r5。

---

verdict：**changes_requested**；**P0=0 / P1=1 / P2=2**。
两卡整体尚不能作为 scope freeze 依据。

- **FEA-10-PREREQ-1：approved**，仅残留非阻断 P2。
- **FEA-10：changes_requested**，须修复 P1 后进入 scope freeze。

| r4 finding | r5 闭环判定 |
|---|---|
| P1-1 写域一致性 | **部分闭环**：PREREQ 新测试已授权；Host 误列已删除；Commands 与测试矩阵已具体化。但 FEA-10 七个测试授权被破坏，见下。 |
| P2-1 可复跑验证 | **部分闭环**：PREREQ 已补 build、真实过滤类名、完整 pins 命令、日志/EXIT；FEA-10 已明确隔离根和同库重开，但仍有不可直接执行的命令写法。 |
| P2-2 用途映射 | **部分闭环**：request builder 三路径及业务错误类型已正确，传输枚举用途已移除；`WireJson` 用途仍不准确。 |

剩余 findings 与最小修复：

- **P1-1｜FEA-10 frontmatter/写域损坏。** [FEA-10:62](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:62>) 起七行变成裸文件名，缺少列表前缀与完整路径，破坏 YAML 且未授权矩阵要求的测试文件。恢复五个 `NewManga.ApplicationCore.Tests/` 和两个 `NewManga.App.Tests/` 完整路径；同时为已授权的两个 `__init__.py`、`tests/pipeline/conftest.py` 补用途/AC，或移出写域。
- **P2-1｜FEA-10 验证命令残留。** [FEA-10:149](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:149>) 的 `--stop|--start` 既破坏 Markdown 表格，也不是可直接执行的重启命令；拆成两次调用并复用同一 DataRoot/DB。[151 行](</G:/CODEX/New Manga/doc/tasks/FEA-10.md:151>) 的 `verify_pins.ps1` 仍须补完整调用。
- **P2-2｜PREREQ 用途描述偏差。** [PREREQ:60](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:60>) 将 `WireJson.cs` 描述为错误 payload 解析；真实代码仅提供 JSON 写入辅助，错误解析位于 `CoreProtocol.cs`。修正用途或移除该行及对应授权。

自洽/越界：AC、ADJ 拆分、wire 2.12/Core minor 边界及 PREREQ 硬前置成立；未发现新增冻结契约或 FEA-11/12/13/14 越界。`proposed` 不构成实施授权。
diff：`9bc2093d1..185415347` 仅两卡、ADJ、r4 报告归档，共 4 文件；无生产代码/冻结契约变更。

实际检查：`main`、工作区干净；common directory=`G:/CODEX/New Manga/.git`。
`check.ps1`：**EXIT=0，PASS（3 warnings）**；`verify_pins.ps1`：**EXIT=0，17/17 PASS**。
**NOT_RUN**：pytest、.NET build/test、真实 IPC/UI、故障注入、Core 重启行为；不判实现 AC 为 MET。

reviewed_head：`1854153473c63d556fb47fcebde7966594439168`
身份/来源：Codex 全新上下文 `/root`；用户指定独立 scope reviewer r5；`reviewer_kind=agent`。未参与建卡/实现/修订；无文件修改、commit、push。

推荐下一步（DSH，可直接转发）：“仅修订两卡及 ADJ，闭环上述三项，保持 proposed、不改生产代码/冻结字节、不 push；复跑 check/pins，提交固定 head 后交全新上下文复审。通过后先 Appointment PREREQ-1，FEA-10 等其 done。”