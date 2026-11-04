---
task_id: FEA-10-PREREQ-1
author: Codex（本实现会话）
recipient: DeepSeek Harness
base_commit: 1254d4e01608d3c9577872abb1dedea5661889aa
delivery_head: null
status: in_review
---

# Handoff：FEA-10-PREREQ-1

实现已留在 main 未提交工作树，实际开始/当前 HEAD `e45baa8b5946a1d581f30b025db045c77e99a6df`；没有 commit/push。base 之后两笔 ready/Appointment 文档提交保留。用户禁止本 Owner 提交，故 delivery_head 不冒填 HEAD；交付绑定 `verification/FEA-10-PREREQ-1/delivery-manifest.json` 的工作树字节 SHA-256，需 DSH 固定 commit 后任命新上下文 Review。此文件为实现交接，不是 Review 结论。

## 交付结果

- M2-C1 rev 2.12 additive 登记：§3.2 wire 2.12 与运行版本分离、§5.5 请求/PreparedRun/结果/3 码、§8 Proposed（未观察）3 行和两个局部例外；保留既有 Run 文本。
- `HostCommandRegistry.cs`：不可变 ordinal `AllowedRunErrorCodes`，保留既有命令路由/minor；未新增新命令 runtime。
- `HostCommandDispatcher.cs`：既有六 Run 出口捕获 typed 业务错误并投影；未注册码 unknown/安全消息/false，保留原 code/requestId；三新码按冻结值规范化；旧注册码映射保留。
- `WireTests.cs` 与新 `Fea10PrereqProjectionTests.cs`：原始 envelope/ASCII 保真、注册前后对照、安全消息、未知码、旧码与旧六命令 minor 回归。
- Task：认领/AC 标记/待裁决/EV/资源清单；证据目录含命令日志、逐项 AC、范围检查与交付 manifest。

没有修改 CoreProtocol 解析、CoreServiceClient、HostRuntime、Core dispatch、数据库/Schema、冻结契约或共享组合根；没有 PrepareRun/AcceptRun 的运行实现。

## 验证证据

逐项结果与原样命令见 [AC-MATRIX](../../verification/FEA-10-PREREQ-1/AC-MATRIX.md)；环境见 [ENVIRONMENT](../../verification/FEA-10-PREREQ-1/ENVIRONMENT.md)。

- CoreClient 定向 13/13、Host 定向 23/23；pins 17/17。
- 原定 restore build FAIL（path1 null）；补充 `--no-restore -p:UsedAvaloniaProducts=` 完整编译 PASS，0 warnings/0 errors。
- 全量命令不加 filter：1333 passed / 11 failed / 74 skipped，EXIT=1；权限/DPAPI/受限目录直接观察详见日志，未在 base 对照，不能签发无回归。
- 治理 FAIL：Plan READY 节点与 Task in_progress/in_review 不同步；Plan/STATUS 写域外，未擅改。最终重跑见 logs/governance-final.log。
- `git checkout` 恢复 FEA09 因 index.lock 权限失败；只读 Git 获取 HEAD checkout-filtered 字节恢复成功，FEA09 diff 为空。未触碰索引、未修改权限。

## 接收方式与风险

仓库 `G:/CODEX/New Manga`，main 主工作树；不建立 worktree。先验证 manifest SHA-256 和范围，再由 DSH 处置治理指针/运行环境并固定交付 commit。AC1–3 MET；AC4 PARTIAL（原定 build、全量及治理未绿；真实 sidecar 回归 skipped）；AC5 PARTIAL（独立 Review 未进行、集成未进行）。证据未提交，不能伪称 canonical evidence 已含于某 commit。

候选 wire 形状和 Host 策略需要新上下文语义审查；纯投影测试不证明真实新命令运行或恢复成功。不扩大 allowed_paths 修复其他测试/目录权限。源数据未访问或清理；没有新依赖/许可证变化。临时目录不确定项保留，资源处置由 DSH。

## 下一任务建议

Task：本卡实现 Review + DSH 门禁处置；FEA-10 仍 proposed，不释放运行实现。

Agent：DSH 先处置指针/环境并固定 commit，再任命全新上下文 Codex 或 ZCode 只读 Review；本实现会话不得自审。

Recovery point：上述仓库/main/指定 base/实际 HEAD + delivery-manifest。新 worktree 如需创建，待 DSH 创建。

Scope：Review 只读固定被审 head，报告仅 `doc/reviews/FEA-10-PREREQ-1-*.md`；DSH 的 Plan/STATUS 更新与集成属其既有治理责任。本卡 Owner 不获得写域扩展；冻结契约、FEA08/09 closeout、共享组合根与 Run runtime 禁止范围持续有效。

Deliverables：DSH 处置记录/固定 commit、全新上下文实现 Review；重跑原定 build、两项定向测试、全量 solution test、check/pins、scope diff；AC4/5 未通过前不得 done，不得把 skipped/NOT_RUN 写 PASS。

可直接转发：

> DSH：请接收 G:/CODEX/New Manga，main，Task FEA-10-PREREQ-1；base=1254d4e01608d3c9577872abb1dedea5661889aa，当前 HEAD=e45baa8b5946a1d581f30b025db045c77e99a6df。实现未 commit/push，以 verification/FEA-10-PREREQ-1/delivery-manifest.json 校验字节。请先处置 Task「待裁决」中的 Plan READY/STATUS 指针及原定 build/全量权限与 fixture 限制，固定交付 commit，再任命全新上下文 Codex/ZCode 对该 head 只读实现 Review，报告限 doc/reviews/FEA-10-PREREQ-1-*.md。Review 对照冻结 C-08 §3、Task allowed_paths、AC-MATRIX 和日志，验证两定向测试、原定 build、全量 solution test、check.ps1、verify_pins.ps1 与范围 diff；不得修改冻结字节、FEA08/09 closeout、共享组合根或实现 Run runtime，不 push。AC4/5 完成且 DSH 集成前本卡保持 in_review，FEA-10 不释放。

收尾新增限制：开始工作树 clean，最终发现两份非本会话创建的未跟踪 `doc/reviews/FEA-10-appointment.md` / `doc/reviews/FEA-10-scope-r6.md`，完整工作树范围检查 EXIT=1，来源待 DSH 核对。保留原样，manifest 排除它们；代码冻结后未扩大写域。
