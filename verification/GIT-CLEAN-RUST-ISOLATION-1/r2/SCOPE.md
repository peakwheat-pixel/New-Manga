# r2 范围裁定（Codex）

依据 dsh-review-r1.md（3b035365682db0965bbde4b0a6113e3e000ae7e7，blocked）及用户“额度已恢复，继续任务，auto”。Owner ZCode、Reviewer DeepSeek Harness。

仅在 source-r2 / codex/git-clean-rust-isolation-r2 修订；累计基线仍 e34a90d001cce1fa966aec7d2b032bb5ad1cf148，起点3b03536。旧source、r1源码/运行器/日志/Review/冻结包只读保留，新证据只能写r2路径。当前没有r2 delivery head，不预签Appointment。

- R-001：目前证据不能裁定纯测试或生产缺陷。允许测试侧增加握手/确定性调度和观测，消除sleep猜测，保留原时间和回收断言；这是新判别变量。不得整体串行、放宽断言、修改生产taskkill250ms或fallback/kill/reap/join预算。若新证据显示生产时序问题，登记BLOCKED并停止该部分，交Codex另冻生产Task；不再跑旧3b同条件全套（已失败2次）。
- R-002：故障注入须记录错误类型、实际writer/reader阶段、耗时、真实管道阻塞及所有权转移；正常/取消仍真实Python Core。可用cfg(test)观察/协调真实worker，但禁止用假worker、仅测试延迟或替身填满32冒充生产饱和。若保持生产语义下无法达到32，解释机制并保留AC3 BLOCKED；不得为凑峰值改生产或放宽peak门槛。
- R-003：测试侧记录PID+创建时间/命令或自持进程句柄，取消与Drop后同身份消失；列明自有线程、pipe/handles、accepted/refused的最终所有者。不能把registry0等同OS回收，也不能杀未核实身份的进程。
- R-004：ac1的track与holder必须共享同一受测registry，在锁未释放时证明等待，释放后注册；可test-only显式传递registry，生产holder仍global。
- R-005：取消override锁超时静默回全局，owner场景fail-closed；测试私有状态可用thread-local或显式传入，不得线程局部化生产registry。
- R-006：以有所有权guard/Arc替代Box::leak；完成显式reap/join与清理。复用现有结构，避免新依赖。
- R-007：测试取消接口须返回/检查kill与wait结果；取消成功和Drop完成分别断言。

修改传播面限于library_bridge.rs的cfg(test)隔离/观察、main.rs测试模块连接、multichannel_stress_tests.rs与新测试运行器；不改Cargo/依赖/共享接口/Core/React。纯生产路径MAX32、registry锁/容量/背压、holder、Drop/shutdown及taskkill语义零变化。非cfg门面改动必须证明与原生产行为等价。

Owner只编辑文件和r2 RESULT/HANDOFF/checkpoint；当前CLI edit模式缺Bash permission client，禁止重复探测cargo/npm/git写等已拒操作，禁止切yolo。Codex正常工具代跑验证/提交。每一新代码版本先编译，固定head后默认并发两次连续通过才满足AC2，同条件失败最多2次。压力1/8/20+取消+真实管道故障，120s+清理30s；packaged未从新head新建冻结sidecar即NOT_RUN。任何新head必须新Appointment后独审。

不push、不done、不改源main/父候选/旧证据/系统ACL，不删清/GC/prune，不动他人文件。
