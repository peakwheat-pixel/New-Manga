---
task_id: FEA-11-HOST-AUTH-1
reviewer: 独立上下文 fresh subagent（DSH 派发；parent session-20e77fbf-d068-4823-b34b-4a7a9efbd4b4；未参与实现）
reviewer_kind: subagent
author: DSH（Lead/Architect/Integrator；本卡实施）
base_commit: 7ab9eea87
reviewed_head: 24a0bbca3
decision: changes_requested
---

# Review：FEA-11-HOST-AUTH-1（r1）

> 本报告由 DSH 依据 r1 Reviewer 返回的完整报告正文落盘（2026-11-05）。Reviewer 只读 HEAD `24a0bbca3`，diff `7ab9eea87..24a0bbca3`；工作树审查前后 clean；C-17 零 diff；无新增依赖；未 push。

## 结论
**changes_requested**：P0=0、P1=2、P2=10。方向正确：Host 已真正自签六字段 HostAuthorization（operation_id 注入、Registry durable 先于 journal），无 P0 安全洞；但 **AC3 未 MET**（端到端/ACK 重发/崩溃点缺失、失败-重试语义不完整），且本批 6 个新文件 + TASK_LEDGER 超出卡内 allowed_paths。

## AC 判定
- **AC1 MET**（canonical 4 向量经 Python 独立复算一致；缺 <0x20/非 BMP/浮点拒绝向量）。
- **AC2 MET**（Minter 六字段/随机 id/摘要/注入；authorizations 的 identity_digest 仍来自调用方，由 Core 复核）。
- **AC3 PARTIAL**（顺序代码成立；无顺序断言/ACK 重发/崩溃点/HostRuntime e2e；失败后新 op id 重试语义未定义；JournalEntry 无 error_code/retryable）。
- **AC4 PARTIAL**（r3 接受 + 用户 limitation 存在；P0-1 闭合依赖 AC1–3）。

## Findings（摘要）
- **P1-1**：AC3 完成度（顺序断言/ACK 重发/崩溃点/e2e；失败-重试语义；failed 的 error_code/retryable；HostRuntime 接线未测）。
- **P1-2**：治理范围（6 新文件 + TASK_LEDGER 不在 allowed_paths；owner/base_commit/reviewer/approval 空；STATUS/LEDGER/卡不一致）。
- **P2-1**：key 排序 UTF-16 ordinal ≠ Unicode code point（非 BMP 不可达但规范偏差）。
- **P2-2**：CanonicalJson 缺 Caps/typed 错误（仅内部使用可接受）。
- **P2-3**：Minter 摘要断言自证循环（需外部固定向量/注入 id seam）。
- **P2-4**：Host 输入校验不足（plan_id/plan_digest 静默兜底、grant_ids 静默丢弃、generation 未包装、重复 registry 未去重）。
- **P2-5**：registry 授权范围用全部 roots（Contains 同义反复）；多 registry 非原子；Begin 在 Authorize 之后。
- **P2-6**：journal 形状非冻结 HostJournal DTO；无 error_code/retryable；receipt 未重算 canonical。
- **P2-7**：ACK 发原始 authorization 而非 fresh（pre-existing）；注释与实现顺序相反。
- **P2-8**：证据卫生（trx 未入库、首跑失败被覆盖、code head/evidence commit 未注明）。
- **P2-9**：IPC flaky 复现（全量 .NET 后首跑 1 failed/2 passed→复跑 3/3），且 IPC 为 Core 直连不能作 Host e2e 证据。
- **P2-10**：CORE_UNAVAILABLE 不在 §8 闭集（pre-existing）。

## 门禁复核（独立）
fea11 40 passed；pytest 全量 3051/10/0；.NET 全量 1370/0/78；check PASS；pins 18/18；C-17 零 diff；工作树 clean。

## 对 done 的意见
不同意 done。最低：P1-1（顺序/ACK 重发/崩溃点/e2e 或明确拆分并改 AC3 措辞）、P1-2（scope/元数据/STATUS 一致）、P2-7/P2-6 修复或编号 deferral；P2 其余可登记/defer。

## 自审声明
fresh subagent（parent session-20e77fbf），未参与实现；只读仓库，未修改 tracked 文件、未 commit/push；全量 .NET 后已 git checkout 恢复 FEA-09；工作树 clean。
