# Codex r2 Review 处置（2026-10-25）

独立Review：r2/dsh-review-r2.md；reviewed_head=1829a38a41587a0d680001a40d206886afb0911d，base=e34a90d001cce1fa966aec7d2b032bb5ad1cf148，decision=blocked。DSH续接同session独审，CLI exit0，实际产物有效。Codex接受阻断裁决，不批准集成、父升级或推送。Task保持in_review，无当前实施执行；旧r1、r2源代码/日志/包/Review字节全部保留。

## Findings 登记

| Finding | r2结论 | 当前处置/升级前条件 |
|---|---|---|
| R-001 | closed，仅本head测试证据 | 接受当前默认并发两次153/0/6/12；不外推所有生产负载可靠性 |
| R-002 | partial | 注入有效但未触32；接受/拒绝、backpressure、holder容量路径未验证，合并R2-F01/F02继续open |
| R-003 | 核心closed | OS身份/逐worker回收证据接受；ledger和child-lock tasklist残余转R2-F04 |
| R-004 | closed | 同registry实际等待→释放→注册证据接受 |
| R-005 | 核心closed | 超时fail-closed与生产等价性接受；分支直接测试/owner mismatch转R2-F05 |
| R-006 | partial | Box::leak去除、正常清理接受；异常remaining与holder Arc生命周期转R2-F03 |
| R-007 | closed | 20/20 kill/wait+独立Drop/OS退出证据接受 |
| R2-F01 P1 | open，直接阻断 | peak0/32，不降低门槛；先另冻test-only故障注入/容量验证设计，验证accepted/refused真实所有权；当前没有生产缺陷证据 |
| R2-F02 P2 | open | 真实write timeout错误码/消息、writer/reader unfinished须变硬断言；日志有值不等于程序强制 |
| R2-F03 P2 | open | guard异常/未完成worker收尾与holder Arc生命周期，需有界显式账本与可验证断言；不能把打印后detach当完成 |
| R2-F04 P2 | open | 实际threads_spawned/joined相等断言；child-lock中tasklist自身exit必须成功，孙进程检查不得假绿 |
| R2-F05 P2 | open | 直接验证owner槽读超时panic；owner mismatch应明确不可达或断言，不静默用global |

AC2可标MET只限1829默认source；AC1仍PARTIAL，AC3 BLOCKED；AC4新Appointment已执行且产物blocked，不能用手续完成替代技术Gate。fault回收检查在peak之前确实逐项通过；remaining=0是打印值，后续remaining断言因peak失败未执行，不能表述为故障场景整体通过。

## 下一范围决定

暂不新建生产修复Task：独审没有证据要求修改生产MAX32、锁/背压、holder、kill/reap/join或taskkill预算。不得为凑32改生产。

推荐下一切片由ZCode承担“test-only容量注入/验证设计 + R2-F02..05收紧方案”；先由Codex另建冻结Task，明确真实worker/管道、accepted/refused/holder所有权、120s+30s预算与不可达时的证据要求，再释放实施。设计必须区分生产真实I/O故障与人工worker延迟；不能预先保证注入能触32，也不修改本Task AC。若在不变生产语义下无法构造，交Codex/用户裁定AC，保留原未满足事实。当前该下一切片尚未释放，READY仍无，避免在不明确注入机制时继续堆压力代码。新交付必须新head、新Appointment独审。

可直接转发给ZCode（仅在Codex另冻Task并登记READY后执行）：从固定1829a38的新独立副本开始，先给不改生产语义的容量注入设计，逐一说明真实管道worker如何进入32 registry、accepted/refused句柄及holder归属如何证明，若不可达给可核验机制证据。列出R2-F02..05最小测试修订、panic/异常清理与fail-closed分支测试；不要用假worker或延迟凑32，不改旧证据/源main/ACL，不push/done。先交设计与判别方案给Codex，未冻结实现范围前不得改产品源码。Reviewer为独立DeepSeek Harness，不自审。

Core ENV-2仍proposed，V2–V5尚无明确取值；未释放运行。父Task仍in_review/r1blocked，1829未替换父e34。父若以后升级，仍需DIAG-50..52及父review-package-r2/PACKAGE_MANIFEST.json交叉链、新head自身packaged先冻结sidecar后12项，以及新的父Appointment；本次Rust Review不能代替。

## 保全与限制

不push、不done、不改main HEAD/生产源码/系统ACL，不清理。r1包55、r2包59、源码734、Task66个原pin经DSH独立匹配；后续新登记的Review/处置是补充链，不改旧manifest。ZCode CLI本轮最终HTTP429/exit1保持披露，不将部分文件交付写成CLI成功。
