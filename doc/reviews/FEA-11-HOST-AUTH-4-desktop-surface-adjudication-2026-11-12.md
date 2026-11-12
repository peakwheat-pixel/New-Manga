---
task_id: FEA-11-HOST-AUTH-4
adjudicator: ZCode CLI session sess_885811e6-a26e-48fd-bd1f-3dd7afb4e856 / turn turn_88dcb208-cc41-4366-a698-02f34b4e133c
adjudicator_kind: agent
reviewed_head: 30a131229aee23b2cb3a27ab853ec1f49b1b0a7b
decision: BLOCKED
cli_exit: 0
---

# FEA-11-HOST-AUTH-4：桌面执行面可用性裁决

**外层执行元数据**：ZCode CLI 0.17.1，Node v24.15.0；session sess_885811e6-a26e-48fd-bd1f-3dd7afb4e856，turn turn_88dcb208-cc41-4366-a698-02f34b4e133c，trace 3356ca7b-589e-4a45-b2fe-9abec24fdeef；命令使用 --mode yolo --surface desktop --json，CLI EXIT 0。派发时 branch main、HEAD 30a131229aee23b2cb3a27ab853ec1f49b1b0a7b、工作树 clean。
**裁决范围**：只确认当前 ZCode 会话是否具备普通交互桌面 PowerShell 执行面；只有存在该执行面才继续全量基线取证。本报告不代表 Task 已释放或验收。

## Verdict：BLOCKED

当前 ZCode 会话没有可用的普通交互桌面执行面。其 computer-use 客户端 bootstrap 成功，但 getState() 与 requestAccess(["observe","act"]) 均返回 Computer Use is unavailable for this node_repl session。该结果是会话后端缺席，不是权限请求被拒绝。

因此，ZCode 本次没有执行 8 个 .NET 项目或 pytest；这些项均为 NOT_RUN，EXIT=n/a。pytest attempt2 的既有状态保持 3519 passed、10 skipped、16 failed、EXIT 1，失败仍未归因。

## 独立复核到的本机探针

Codex 在 PowerShell 7.6.9 / dotnet 10.0.401 下，于同一 reviewed HEAD 执行 NewManga.Appearance.Tests 单项目探针。构建成功，但 TestHost 在加载测试前因 System.ComponentModel.Win32Exception (5) 于 ProcessManager.OpenProcess 中止，EXIT 1；测试计数 NOT_RUN。该探针不是 8 项目全量基线。

## Task 与边界

Task 仍为 proposed，必须保持 proposed，不得置为 ready，不得开始实现。未改源码、Task、Plan、Status、ACL 或安全设置；未运行全量 pytest；未将 NOT_RUN 记为 PASS。解除阻塞需要一个当前 Agent 可访问的普通交互桌面 PowerShell 执行面，随后按原计划实测基线。此为执行环境前置，不是等待人工审批。

## 原始证据

- ZCode 独立探测记录：仓外文件 G:\CODEX\New Manga.workspace\agent-output\codex\FEA-11-HOST-AUTH-4\zcode-desktop-surface-probe-20261112.log，SHA-256 8c4f608db861a7433770a666bf13f51edc1feb89dc7af4cf85e9ae15f990458d。
- ZCode CLI 原始响应：仓外文件 G:\CODEX\New Manga.workspace\agent-output\codex\FEA-11-HOST-AUTH-4\zcode-desktop-baseline-probe-20261112.log，SHA-256 84c6729cfca7a675f12cc21274b726f8c084aac80b5058963400d700d5a27d0e；包含 session、turn、trace、完整 response 与 CLI EXIT 0。
- Codex 单项目 TestHost 探针：仓外文件 G:\CODEX\New Manga.workspace\agent-output\codex\FEA-11-HOST-AUTH-4\dotnet-host-probe-20261112-current-head.log，SHA-256 fa5ffa41bff5a3595386563314d918005f1dac0d51102e764e4e68cd323833fe。
- 版本化汇总与生成时 HEAD / EXIT：verification/FEA-11-HOST-AUTH-4/logs/zcode-desktop-surface-probe-20261112.log。

## 下一步

保持 Task 为 proposed。待 ZCode Desktop 提供可用的 computer-use 后端，或当前 Agent 获得普通交互桌面 PowerShell 执行面后，再按前一 release-readiness 裁决逐项取证；在此之前不实施 HOST-AUTH-4。
