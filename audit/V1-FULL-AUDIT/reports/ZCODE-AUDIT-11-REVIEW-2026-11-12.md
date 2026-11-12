# AUDIT-11 安全及异常恢复阶段 — ZCode 独立 Review

- 日期：2026-11-12
- Reviewer：ZCode（独立新 session，plan-mode 只读）
- reviewed_head：`e10fd1ee7e326255ffebb4ca529ecee5dfa477d9`
- session：`sess_5f0ece9a-542e-46d0-93ae-76a596b6c39a`
- turn：`turn_b7103000-a9a4-48fc-b390-a7ac5767f004`
- trace：`948d6d18-393f-4e84-b49e-338bfddf0780`
- CLI：`zcode 0.17.1`，EXIT 0，stderr 0 bytes

## 结论

**ACCEPT。** Review 认定阶段报告、suite 映射、问题台账、证据 pin 和专项状态相互一致；AUDIT-11 原始指令的 16 个检查面均有对应矩阵行，产品 finding 的威胁前提和影响边界没有被扩张。该接受是对审计交付质量的审查，不改变产品侧 AUDIT-11 `FAIL`、Release Gate `BLOCKED` 或 Task `in_progress`。

ZCode 报告 0 个 P0/P1/P2 阻断项和 1 个 P3 观察。

## P3-1：扫描器源指纹在生成证据后发生差异

ZCode 比较 `logs/audit-11-static-inventory-20261112.log` 中的扫描器 SHA-256 `4BFDDE17…` 与审计提交中的扫描器源文件，发现哈希不同。Review 在只读 plan-mode 下不能使用 `git diff`/`git show` 确认变化成因，因此提出披露变化或重跑并更新 pin。

Review 后的本地字节复核已确认成因：在检查 `git diff --cached --check` 时，`security_static_inventory.py` 第 37 行被报告有尾随空格；为清除该 whitespace，提交前删除了一个 ASCII 空格。只在当前文件第 37 行末尾重加该空格，重建文件 SHA-256 即精确等于扫描日志中的 `4BFDDE17DC29EF7619D3A385F010E0877DC6527865C6FC8B5DFD34660F6BD456`；当前已 pin 的扫描器字节为 `8D71732C7DB12CD14711E7AE9E83CCF2F2D753DD3EAEE526B5E446B1463476D8`。长度分别为 6,193 与 6,192 bytes。重建命令、生成 HEAD 和 EXIT 见 `logs/audit-11-scanner-source-hash-drift-20261112.log`。

该单字节差异只改变源码空白，不改变 Python token 或扫描逻辑。静态扫描结果 JSON 哈希 `44630F7E7C4EB2185F04C3C84363A64E834F43A87BD41A9EC2757EA496A2D5E3` 与现存结果一致，统计字段也经 Review 对照；本次未重跑 scanner，未把该步骤记作新 PASS。P3 以此披露关闭。

## Review 核验范围

ZCode 对照了原始 AUDIT-11 要求、阶段报告、suite 映射、问题台账、Task 状态与 Canonical Evidence；读取了 probe 源码、静态 scanner 与 JSON、源码清单和相关 logs，并抽查了 `managed_storage.py`、`nmbak.py`、credentials/network、image/archive、SQL/restore plan、sandbox/process、Host logging 与 `SidecarProcess.cs` 等报告引用位置。Reviewer 核实：

- `SEG-B-PROBES-001` 的 junction 前提和 `publish` 写出边界与代码吻合；`SEG-B-PROBES-002` 的磁盘写失败与恢复限制有对应 probe；`NM-AUD-0001` 的 helper 结果没有冒充生产 sidecar 行为。
- 目标状态一致：AUDIT-00 limited PASS、AUDIT-01 FAIL、AUDIT-02 BLOCKED、AUDIT-11 FAIL、AUDIT-03–10/12–14 NOT_TESTED；Release Gate BLOCKED、Task in_progress。
- Task Canonical Evidence 的抽样 SHA-256 符合 raw Git blob（LF 归一化）口径，引用 commit 包含对应文件；门禁日志按其自身 generated HEAD/EXIT 判定。
- NuGet 检查明确限定为 `--no-restore` 和当时配置源；Python `pip-audit` 不可用及 NuGet 网络请求未独立追踪的限制已披露。

## 限制

本 Review 未运行测试、probe、构建、扫描或治理检查，未独立复现 probe；未访问网络/远端仓库、真实用户数据、数据库或图像内容。部分源码仅按报告引用抽查，未逐行检查整个仓库；未读 static inventory JSON 的全部候选行。具体未读列表和边界见原始 ZCode 回执 `evidence/zcode-audit11-review-20261112.json`。

## 原始回执

原始 CLI JSON、派发与 stderr/EXIT 摘要分别保存在：

- `evidence/zcode-audit11-review-20261112.json`
- `logs/zcode-audit11-review-dispatch-20261112.log`
