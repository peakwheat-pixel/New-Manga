# Codex r2 验证与裁定（2026-10-25）

当前交付 head：1829a38a41587a0d680001a40d206886afb0911d；parent=3b035365682db0965bbde4b0a6113e3e000ae7e7；累计base=e34a90d001cce1fa966aec7d2b032bb5ad1cf148。独立source-r2、无remote；非main集成/父升级。Owner ZCode，Codex做接收修正与实际验证；Reviewer另行独立DSH。

## 归属与接收

ZCode同一session续接的CLI最终exit1/HTTP429，stdout无有效JSON；不是完整CLI成功。退出前已落盘两个源码、RESULT/HANDOFF/checkpoint及两个未运行ps1；原始交付复制到workspace/zcode-delivery-r2及OWNER_SNAPSHOT.json，不改写Owner记录。原r1 55文件与Review字节保留。

Codex接收修正：ac1持锁读快照自锁改读已有guard，并用cfg(test)真实锁超时计数证明holder先等待后注册；holder继承槽失败fail-closed；Child句柄直接复制为自有身份（避免OpenProcess按PID竞态），读取OS创建时间，等待确切进程对象；克隆现有finished/joined和pipe/thread handle原子槽，Drop后逐channel断言；两个构造函数补齐观察字段，账本核验数量分别=count/20。观察Arc不持有额外管道引用，不改变生产生命周期。Owner已自行修复取消线程向父线程返回identity、sampler捕获与tasklist错误状态；原版本SHA见Owner快照，最终SHA见包/日志。

## executed

环境/精确命令/源码与runner SHA/真实EXIT见workspace codex-validation-r2各JSON及日志RUN_HEADER。Python=C:/Python314/python.exe；Core来自本source-r2/src；所有数据及APPDATA/LOCALAPPDATA/TEMP/TMP放本Task r2环境；依赖cargo缓存共享父Task目录，crate从当前副本编译；unset RUST_TEST_THREADS/M2RC1_PACKAGED。实际运行器codex_verify_r2.py；Owner ps1未运行，不混同执行版本。

| 场景 | 结果 |
|---|---|
| frontend offline ci/build | direct npm ci和build exit0；第一次显式cmd包装因空格引用exit1，保留，不隐去；仅构建前置，运行时Rust尚dirty |
| cargo test --locked --offline --no-run | exit0；3b+dirty，编译输入SHA与最终1829相同 |
| 默认并发source两次 | 每次153 passed/0 failed/6 ignored/12 filtered，12.68s，exit0；两次间未改源码/输入 |
| real Core 1/8/20正常关停 | 各1 passed/170 filtered；逐channel成功ping；1/8/20次OS句柄退出、PID消失、worker finished/joined全true、4个handle槽归零 |
| real Core 20并发取消 | 1 passed/170 filtered；20/20 kill与wait成功；逐channel独立Drop/资源退出检查通过 |
| fault sidecar 20真实管道阻塞 | exit101，0 passed/1 failed/170 filtered；20/20 stdin write timed out，writer/reader未结束；Drop后20/20进程/worker/handle回收检查通过；peak=0、reaped=0、remaining=0，未触32，AC3 BLOCKED |
| cargo check --locked --offline | exit0 |
| packaged/模型/GUI/安装包 | NOT_RUN；本head未新建冻结sidecar，不继承e34旧12通过 |

计数：171测试=旧166+5压力；默认running159=153可执行+6ignored（旧perf1+专用stress5），packaged12显式filtered。压力每个独立进程exact选择，170filtered不等于全套通过。本轮共12次前置/编译/套件/场景/check执行（包含第一次错误cmd包装）；详见SUMMARY真实条目，禁止只用文字数量替代记录。

## DSH r1 Findings处置（待独立复审）

- R001：确定性child锁握手、测试持锁600ms（生产250ms等预算不改）和fallback分支观测；新条件全套连续两次通过。仅支持当前head测试隔离/调度改善，不证明生产taskkill在所有负载下可靠，不据此改预算或抹去r1两败。
- R002：真实错误包络、耗时、未完成worker观测、回收证据已补；但真实peak0未达32，accepted/refused/holder的容量压力路径未触发，不能宣称验证。当前注入可被cancel/kill解除只是观察与代码解释，不足以断言所有真实I/O都不可能形成unreaped worker，更不授权为凑数修改生产。
- R003：每个实际测试自有进程的独立内核句柄+创建时间+退出信号，以及逐worker flags/handle槽已补并通过；观察是本channel持有的管道/重复线程句柄，不是全机handle总数或系统ACL证明。生产registry容量拒绝路径未触及，其handle转移仍未验证。
- R004：holder继承同一Arc registry；cfg(test)锁失败计数证明释放前实际等待，释放后同registry注册，并显式reap；默认两轮均通过。
- R005：owner读槽/holder继承失败panic；无静默超时改用全局。生产仍固定进程global；独审需核查所有cfg(test)选择分支。
- R006：Box::leak已去，Arc guard显式reap；正常测试未报remaining。异常展开分支仍会记录未回收并释放Arc，不能将日志等同所有异常场景已证明无detach，交独审核查。
- R007：20/20取消kill/wait断言，Drop与OS对象退出分开核验，通过。

## 当前Gate与下一步

AC2有实测满足证据；AC1修订待独立真实性复核；AC3容量门槛未满足，本Task与父升级均不可批准；AC4新head/包/Appointment准备完成，等待独审。不得把四个Core场景PASS变成总Gate PASS。

下一步DeepSeek Harness按r2/APPOINTMENT.md只读复审新head，逐条核对R001..007及接收修正，并对剩余饱和门槛提供后续范围建议；旧r1原字节保留。若需要生产预算/registry/holder变化，必须另冻Task；不为使测试达到32而自动释放生产更改。Core ENV-2仍proposed/V2–V5未定义。

不push、不done、不改源main/父候选/系统ACL；不清理资源。
