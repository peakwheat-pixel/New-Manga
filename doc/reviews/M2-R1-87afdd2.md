---
task_id: M2-R1
reviewer: Codex
author: DeepSeek Harness
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
owner_start: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
reviewed_head: 87afdd2e87c46bc8f19d53e932fb641c2457e45b
post_delivery_head_checked: 1e534c6f670dfd3ecf5c05dc4edde32e09bef732
decision: changes_requested
findings_disposition: P2-001 open
---

# Review：M2-R1 — Qt Runtime Feasibility Spike

## 范围与依据

非作者 Review。固定审查 base=`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`、owner-start=`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`、reviewed_head=`87afdd2e87c46bc8f19d53e932fb641c2457e45b`。另核对 Handoff/evidence 后续文档 head `1e534c6f670dfd3ecf5c05dc4edde32e09bef732`。作者为 DeepSeek Harness，Reviewer 为 Codex。

审查了 M2-R1 Task、研究报告、Handoff、`verification/M2-R1/**` 的 01–08 日志/清单、3 个探针和原始 JSON/PNG；并对照 M2-D1 审计、M2-R1 授权范围及 AD-001。`Standards` 与 `Spec` 视角均已执行；按仓库 Review 口径，本报告分别记录 Architecture 与 Verification 结论。

## Standards

未发现超出授权写集合或违反已记录边界的实现变更。作者差异仅修改 M2-R1 Task、研究报告、Handoff 和 `verification/M2-R1/**`。没有 `src/**`、`tests/**`、依赖/打包/Schema、共享规划文件或 `verification/T3.2.1/**` 改动。

## Spec

AC1–AC5 的证据主体齐全。三种 QPA 平台均有实测；结论限于 Windows 11 build 26200 上的 `windows`、`offscreen`、`minimal` 插件，没有推广到其他 OS。`offscreen` 与 `minimal` 的 `PARTIAL`、QML/`QQuickWindow` 的 `UNVERIFIED`、生产入口与产品测试的 `NOT_RUN` 均有明确保留，没有将这些结果记成产品 PASS。Windows 测得真实字形使用可用回退字体；精确请求字体仍通过 `available=False` 暴露替换，报告没有隐藏该状态。

### Finding

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| P2-001 | P2 | `verification/M2-R1/07-evidence-manifest.md:26,87`; `doc/tasks/M2-R1.md:51,62`; `doc/handoffs/M2-R1-87afdd2.md:17,46,118` | 正式运行数在多处记为 18，但同一清单逐项列明主矩阵 9 次、字体补救 5 次、事件循环 6 次，总计 20 次。`raw/` 下共有 21 个 JSON：20 个正式运行和 1 个明确排除的 smoke。当前数字使 AC2/3 的复核统计与保存的原始证据不一致；各正式运行的退出结果本身未见失败。 | 只读枚举并解析 `verification/M2-R1/raw/**/probe.json`：总计 21；去除 `raw/smoke/` 后 20，`exit_code != 0` 或非空 `errors` 为 0。分组计数为 9+5+6。全目录 PNG 共 45 个，含 smoke 与补救图。 | 统一修正文档为 20 次正式进程、21 个 JSON（其中 1 个 smoke），并核对相关 PNG/输入图文件数描述；提交新的 delivery/Handoff head 后重新 Review。 | open |

## Architecture

**结论：通过审查范围。** 三个探针在设置 QPA 环境后才导入 PySide6；调用真实 `QtFontCatalog`、`QtTextLayoutEngine`、`QtImageCompositor` 与 ports DTO，不导入 `bootstrap.app`、不访问 SQLite。实验图像/JSON 写入调用者指定的 `--workdir`/`--json`；交付日志指向 `verification/M2-R1/raw/**`。字体补救只读取 `C:\Windows\Fonts\msyh.ttc`，没有安装或复制字体。未见触碰真实用户数据根的路径。

§5 处于 AC4 明确授权的 adapter 边界“建议”范围：报告标注为非约束性研究建议、不选择技术、不释放实现；未改 M2-D1 矩阵、架构决策或生产代码。文中“必须/硬约束”措辞作为提交 Codex 决定的建议出现，未被写入当前规划状态，因此本轮不判为越权。产品规则仍需后续由 Codex/用户按正式 Task 冻结。

## Verification

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定点与写集合 | `git diff --name-only 5d989ba..87afdd2`; `git diff --check 5d989ba..87afdd2`；检查允许/禁止路径 | 指定 DeepSeek worktree；delivery=`87afdd2` | **PASS**：79 paths；全部落在 Task 允许路径；越界/禁止路径 0；`git diff --check` exit 0 | `08-delivery-scope-and-diff-check.log`；独立重算同结果 |
| Handoff 后追加 | `git diff --name-only 87afdd2..1e534c6`; `git diff --check 5d989ba..1e534c6` | delivery 至 post-delivery head | **PASS**：新增 Handoff、08 日志，并回填 Task/研究报告 delivery 元数据；全属授权文档路径；check exit 0 | Git diff；worktree branch 当前在 `1e534c6` |
| 禁止路径零修改 | 对 owner-start..delivery 路径清单筛 `src/**`、`tests/**`、`requirements*`、`packaging/**`、Schema 与 `verification/T3.2.1/**` | owner-start..delivery | **PASS**：0 命中 | 独立路径筛查；08 日志 §3/§4/§7 |
| 原始运行结果 | 只读枚举 `raw/**/probe.json` 并解析 `exit_code`、`errors` | delivery 证据 | **PASS（运行结果）/FAIL（文档计数）**：20 个正式 JSON 均 exit 0 且 errors 为空；另 1 个 smoke。文档所写 18 次不成立，见 P2-001 | 21 个 JSON；主矩阵 9、补救 5、事件循环 6、smoke 1 |
| 原始 PNG | 查看 windows/offscreen/minimal 主矩阵和 offscreen appfont 样本；核对 PNG 与 JSON 摘要 | delivery 证据 | **PASS**：windows 样本显示真实 fallback 字形；offscreen/minimal 样本为方块；appfont 样本恢复字形，与报告陈述一致 | `raw/windows/run1/output_page.png`、`raw/offscreen/run1/output_page.png`、`raw/minimal/run1/output_page.png`、`raw/supp-offscreen-appfont/output_page_offscreen_appfont.png` |
| Product suite / QML / main entry | 审阅报告 §6 和 Handoff 未运行项 | delivery 证据 | **NOT_RUN / UNVERIFIED**，正确保留；因本 Task 未改生产代码，不据此声称产品 Gate 通过 | 报告 §4、§6；Handoff 验证表 |

## 结论与复审

**decision: `changes_requested`。** 除 P2-001 的运行次数/原始产物计数不一致外，所审平台结论范围清楚，未发现 `UNVERIFIED`、`PARTIAL` 或 `NOT_RUN` 被误写为 PASS；AC5 范围断言经独立 diff 复核成立；未发现探针触及用户数据根或 §5 越权。

该 Review 只适用于 reviewed_head=`87afdd2e87c46bc8f19d53e932fb641c2457e45b` 及所列的文档追加 head。P2-001 修复后需生成新的固定 delivery/Handoff head 并复审；目前不集成、不将 `doc/tasks/M2-R1.md` 标为 `done`，也不登记 M2D1-22 新状态。产品测试与 QML 仍保持 `NOT_RUN`/`UNVERIFIED`，不构成批准阻断，因为它们已如实列为本 Task 的限制；当前阻断项为证据数量修订。
