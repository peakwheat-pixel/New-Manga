<!-- FEA-10 scope review r6 (Codex independent, approved) -->
# FEA-10 / FEA-10-PREREQ-1 建卡 scope review r6（Codex 独立）

- Reviewer：Codex 全新上下文（未参与建卡/实现/修订；只读）。
- reviewed_head：`1254d4e01608d3c9577872abb1dedea5661889aa`。
- 结论：**approved P0=0/P1=0/P2=2（非阻断）**；PREREQ-1 维持 approved；FEA-10 在 PREREQ-1 done 前不得 ready。
- DSH 处置：FEA-10 scope 冻结 + Appointment（`doc/reviews/FEA-10-appointment.md`）；PREREQ-1 实施中。

---

verdict：**approved；P0=0 / P1=0 / P2=2（非阻断）**。两卡可作为 scope freeze／DSH Appointment 依据，不等于实施授权。
reviewed_head：`1254d4e01608d3c9577872abb1dedea5661889aa`。
身份/来源：用户指定独立 scope reviewer r6；Codex 全新上下文 `/root`，`reviewer_kind=agent`；未参与建卡、实现或修订；无文件修改、commit、push。

- **FEA-10-PREREQ-1：维持 approved。**
- **FEA-10：approved。** PREREQ-1 done 前仍不得 ready／实施。

r5 findings 闭环：

- **P1-1：已闭环。** 七个测试文件恢复完整路径和列表前缀；frontmatter 静态核验为合法 YAML；生产/测试授权无裸文件名、目录级范围或多余 `__init__.py`／`conftest.py`。
- **P2-1：已闭环。** AC7 明确先 `--stop`、再 `--start`，复用同一 DataRoot/DB；pins 调用已补为完整 `pwsh -NoProfile -File tools/governance/verify_pins.ps1`。
- **P2-2：已闭环。** PREREQ 已移除 `WireJson.cs` 授权及用途；真实错误解析和业务错误类型位于 `Wire/CoreProtocol.cs`。
- Commands、既有测试及新增测试用途与写域对应；request builder 三路径正确，现有 `payload_hash` 未被误当成 endpoint/model/body 全摘要。
- AC／验证矩阵／ADJ 与 C-08、C-13 自洽；wire 2.12 与 Core minor 分离，硬前置明确；未发现冻结契约或 FEA-11/12/13/14 越界，`proposed` 不构成实施授权。
- `185415347..1254d4e01` 仅两卡、ADJ、r5 报告归档，共四文件；无生产代码或冻结契约变更。

剩余最小修复（均非阻断）：

- **P2-1：** [PREREQ:86](</G:/CODEX/New Manga/doc/tasks/FEA-10-PREREQ-1.md:86>) 过滤表达式的裸 `|` 会拆开 Markdown 表格；转义或将命令移出表格。
- **P2-2：** 两卡 Closeout 仍写“r4 待派发”，FEA-10 approval 亦停留 r4；DSH 冻结时同步当前轮次即可。

实际检查：`verify_pins.ps1` **EXIT=0，17/17 PASS**；契约及检查脚本相对被审 head 未变。
`check.ps1` **EXIT=1**：运行时当前工作区 PREREQ 已为 `in_progress`，与 READY DAG 不一致；这是被审 head 之后的状态，未计入上述 findings。
当前 `main=e45baa8b…`，common directory=`G:/CODEX/New Manga/.git`；观察到他人未提交 PREREQ 修改，未触碰。
**NOT_RUN：**固定 head 隔离治理复跑、通用 YAML 解析器、pytest、.NET build/test、真实 IPC/UI、故障注入、Core 重启；不判实现 AC 为 MET。

推荐下一步（可直接转发 DSH）：“请在 `G:/CODEX/New Manga` 核对当前 main 与 PREREQ 未提交认领状态，归档本 r6 结论并同步两项 P2；由已 Appointment 的 Codex 会话按 PREREQ 卡固定 base/写域实施，交付测试、verification、Handoff，再交全新上下文 Review。先消除当前 check 状态不一致并复跑 check/pins；FEA-10 等 PREREQ done 后释放，不 push。”