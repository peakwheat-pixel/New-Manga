---
task_id: M2-DERIVED-GC-2-DESIGN
author: Codex
recipient: DeepSeek Harness / Codex Integrator
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
delivery_head: 8dd88c56becbb5a5c1942aeb7664c24ce86b9944
status: awaiting_independent_review
---

# Handoff：preview 安全回收设计

## 交付结果

release=69d7cc08，设计初稿=a35915c2，文档验证器修正与失败日志保留=8dd88c56。分支 codex/m2-derived-gc-2-design，worktree G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN；common directory 指向主仓库 .git。

设计：`doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md`；源证据：`verification/M2-DERIVED-GC-2-DESIGN/reality-source.log`。最小方案是仅回收有准确来源/明确退役/非current非pinned的副本，必须先有跨进程静默窗口保护。长会话、pinned和未知历史副本仍保留。专用catalog辅助表与trusted mark方法仅是后继 Task 的拟议变更；当前生产代码/Schema/wire/依赖零改动。

| AC | 本次判定与限制 | 证据 |
|---|---|---|
| AC1 | 设计调用链核对完成：双 sidecar、随机key、来源缺位、grant局部性、Rust轮换、Managed current/pinned、读取句柄 | 设计 §1、source log |
| AC2 | 13条可删/必留/未知矩阵已给出；不是运行安全证明 | 设计 §4 |
| AC3 | 静默租约、明示退役、current/pin、逃逸/句柄、崩溃顺序设计完成；native租约与混合旧runtime启用 Gate仍 planned/NOT_RUN | 设计 §2–3 |
| AC4 | 后继 allowed_paths/G1–G7与指令准备完成；实际后继base/worktree必须在设计集成后落Task，不伪造已创建路径 | 设计 §5–6、本节后续指令 |
| AC5 | 设计范围核验通过；真实DSH独立批准/集成尚待执行，当前不得done | design-check.log；后续Review |

## 验证证据

PowerShell / C:/Python314/python.exe：`python verification/M2-DERIVED-GC-2-DESIGN/check_design.py`；依赖两merge祖先通过、产品树delta为空、矩阵/Gate/路径/行界检查 PASS。最新执行绑8dd88c56的日志在后续metadata提交追加。两个早期检查失败属于验证器（Gate名称与含中文分隔符路径解析）并保留日志，未改产品实现；不是产品失败也不抹掉失败记录。

`git diff --check` EXIT=0；产品回归/native锁双进程/实际回收 **NOT_RUN**（本设计不执行collector），不套用旧1886/55/140的数字。

## 下一任务建议（待设计批准/集成后填写实际恢复点）

Task=M2-DERIVED-GC-2；Owner建议ZCode，非作者Reviewer=DeepSeek Harness，Integrator=Codex。依赖本设计done、GC-1/RC4done。需要显式冻结专用catalog辅助Schema与trusted mark生命周期seam；主产品Schema/公共wire/React/依赖禁止修改。

Recovery point：当前设计分支/head=8dd88c56、base=ab4b7c11、设计worktree如上；后继实现branch/worktree **待Codex创建**，后继base须采用本设计实际integration commit，不把8dd88c56当尚未发生的主线集成。

交付固定代码commit、判别测试、verification原始日志（shell/解释器/HEAD/EXIT/skip）、Handoff；G1–G7含真实双进程静默保护、current/pinned/未知保留、路径/句柄与crash恢复。设计批准不豁免G7旧runtime迁移证据；无法证明则不启用live-preview sweep并记录BLOCKED。

可转发的后继准备指令（本阶段不能代替正式释放）：

```text
ZCode：仅在Codex正式释放M2-DERIVED-GC-2后执行。读取其Task、doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md及其非作者Review；采用Task实际repo/worktree/branch/base/head，不使用设计草案的未来路径。
按设计§5点名文件实现明确来源/retired+受控启动静默窗口；复用artifact repo与publisher/catalog，保护current/pinned/源文件/人工/Lock/Managed Copy；不做TTL猜删、在线回收、未知历史来源回填。专用catalog辅助表/trusted mark仅按正式Task冻结范围，禁止主产品Schema/React/依赖/公共wire变更。
按§6 G1-G7交付真实native双进程/恢复/边界证据与定向pytest/cargo，所有日志带命令、解释器、固定HEAD、EXIT；旧runtime未退出或入口租约覆盖不能证明就fail-soft不删并记BLOCKED，不降低Gate。固定commit+Handoff交DSH非作者Review，再由Codex集成与集成后验证；本指令未授权直接开工。
```

## 风险与遗留

本设计需要后继验证的命名空间租约；当前源码没有这个保护。混合旧runtime无法仅凭锁文件/进程名判断安全。回收只在重启静默窗口，长会话容量不承诺；pinned/未知来源持续保留。未实际修改或清理任何用户数据/历史worktree。
