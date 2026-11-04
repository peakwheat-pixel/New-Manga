<!-- FEA-09-UI-1 implementation review r4 (Codex independent, approved) -->
# FEA-09-UI-1 实现 Review r4（Codex 独立）

- Reviewer：Codex 全新上下文；未参与实现/返修；只读。
- reviewed_head：`d39951296b217cd849629ffb1e5e4c678ec0c812`。
- 结论：**approved，P0=0/P1=0/P2=2（非阻断残留 N1 时间元数据/N5 状态文字）**。

---

verdict: **approved**
P0=0 / P1=0 / P2=2（非阻断残留）

reviewed_head: `d39951296b217cd849629ffb1e5e4c678ec0c812`
身份/来源：Codex 全新上下文 `/root`，独立实现 Reviewer r4；未参与实现/返修。本轮只读，未修改、commit、push。

| 项目 | verdict | 核验结论 |
|---|---|---|
| N1 | PARTIAL，可接受 | 8 份独立全量 TRX 合计 **1317/0/74**；IPC **16/0/0**；各项目 EXIT=0。命令及时间元数据仍有 P2，见下。 |
| N4 | PASS | 逐文件字节 offset 提取追加帧；直接断言 receipt 行 `FILE_IDENTITY_CHANGED`、章节 0 页；已移除 `Snapshot.LastError` 兜底。 |
| N5 | PARTIAL，可接受 | delivery_head 与 **42 项 EV commit** 均固定到 `b14e04da`，文件存在、blob 与 HEAD 一致、SHA-256 **42/42**；Task 为 `in_review`、待 r4。仍有旧状态文字。 |

残留 findings / 最小修复：

- **P2／N1：日志头尚不能还原完整实际命令。** [full-test.log:1](</G:/CODEX/New Manga/verification/FEA-09-UI-1/logs/dsh/full-test.log:1>) 使用 `<each test project>`，未逐项记录完整命令、唯一 TRX 参数及 shell；full/IPC 的 DATE 为 10:36/10:40，而 TRX 实际运行约为 10:11–10:15。最小修复：补实际调用记录，明确运行时间与整理时间。**不阻断**：独立 run ID、完整逐例 TRX、结果日志及 EXIT 相互支持成功结果；不能宣称命令元数据已闭环。
- **P2／N5：当前状态文字未完全同步。** [Task:149](</G:/CODEX/New Manga/doc/tasks/FEA-09-UI-1.md:149>) 仍称“未提交”；Handoff 首部仍待 r3、STATUS 仍待 r2。最小修复：由 DSH 同步当前交付状态，保留历史记录。**不阻断**：固定交付/证据指针真实有效，未误标 `done`。

新增核验发现为上述 N1 时间元数据不一致，合并计入 N1；未发现新增产品缺陷。

- R1–R7 spot-check：token 异常清理、暂时失败保持轮询/取消、folder 交 Host、真实生产链路、多加密源拒绝、逐项计数与跳过页/源分别显示均保留。
- C-05/C-15/C-16/C-07、FEA-08/09 closeout、组合根、其他页面、旧 ImportPages 及 FEA-09 证据未改。
- `7f4f4d3cd..d3995129` 对照 allowed_paths：唯一外部项为 `doc/STATUS.md`，属 DSH 集成例外；PLAN、TASK_LEDGER 在该区间无改动。
- 实跑：inventory `--check` **PASS**；`check.ps1` **PASS（3 warnings）**；pins **17/17 PASS**；EV **42/42 PASS**；结束工作树干净。
- **NOT_RUN**：build、全量 .NET、真实 IPC、整窗口视觉/E2E；成功测试数来自归档日志/TRX核验。

| AC | 判定 |
|---|---|
| AC-1 | MET |
| AC-2 | MET（Registry 审计限原始 opaque/DPAPI 字节） |
| AC-3 | MET |
| AC-4 | MET（控件/VM＋真实 IPC，非整窗口 E2E） |
| AC-5 | MET |

推荐下一步（可转发 DSH）：**归档本 r4 approved，记录接受 N1/N5 两项非阻断 P2并同步状态文字；按既有授权完成集成验证与 Closeout。此 Review 不直接将 Task 标为 done。**