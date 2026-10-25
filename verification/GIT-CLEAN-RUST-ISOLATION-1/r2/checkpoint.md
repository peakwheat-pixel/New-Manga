# r2 恢复点

Codex已冻结r2范围；DSH r1 blocked，7项均open。新隔离副本起点3b03536，待ZCode认领；未执行r2测试、未产生新head。旧r1的55文件SHA全部匹配。当前以SCOPE.md及Task为准。

## 2026-10-24 r2 认领（ZCode / Owner，第二轮）— 追加

- 认领：按 `r2/SCOPE.md` 与 `dsh-review-r1.md`（head `3b035365682db0965bbde4b0a6113e3e000ae7e7`，blocked）执行 R001–R007 测试侧修订。用户授权 auto。不自审、不派其他 Agent。
- 实际环境：r2 实现仓库 `…/GIT-CLEAN-RUST-ISOLATION-1/source-r2`，`.git/HEAD` → `codex/git-clean-rust-isolation-r2`，ref=`3b03536…`（=r1 交付 head，与 SCOPE 一致），累计 base `e34a90d…`，无 remote；旧 `source/`（r1）只读。本会话仍无 Bash permission client（按用户指令不再探测）：git 写/二进制执行/mkdir/rm/重定向一律不做，仅文件读写编辑；Codex 代跑编译/测试/提交并给新 head Appointment。
- 写入面：`source-r2` 的 `library_bridge.rs`、`multichannel_stress_tests.rs`（main.rs 预计无改动）；主仓仅 r2 RESULT/HANDOFF/本 checkpoint 与 Task 认领记录；workspace 仅 `r2-runner/`。

### 七项处理方案（定案）

- **R001**：只动测试——确定性握手（lock_holder 拿锁后 mpsc 发信号，主线程收到才 shutdown，消除 30ms sleep 猜测）；持锁 300→600ms 覆盖高负载步骤 1–3（仍 <1500ms deadline；断言全部原样：elapsed<3s、is_child_reaped、tasklist 双杀）；新增观测：断言 `last_shutdown_error()` 含 "triggering fallback OS termination"（证明真实走 fallback 分支；失败消息带该快照以判别 deadline 耗尽 vs try_wait 失败 vs 竞争窗口错过）。生产 taskkill 250ms/fallback/join 预算零改动；不重跑旧 3b 同条件全套。
- **R002**：机制结论（静态确认）：writer `write_all` Err 即 break（library_bridge.rs 2243–2255）、reader 同理；生产 `cancel_active_pipes`（CancelSynchronousIo+CancelIoEx 双机制，1550–1577）与 child 终止（管道破裂）都会在 bounded join 窗口内解除管道阻塞——**真实管道阻塞在当前生产语义下机制性不产生 unreaped worker**（即生产"不泄漏 worker"的设计目标）。修订：注入前后完整观测（round_trip 错误码/耗时、is_writer/reader_finished、Drop 后 joined 标志=handle 归属、registry names 快照、peak）；保留 `peak>=32` 不放宽；预期实跑大概率 <32 → 按 SCOPE 如实 AC3 饱和 BLOCKED，机制说明写入 RESULT；不用假 worker/延迟凑数。
- **R003**：每 channel ChildIdentity{idx,pid,spawn_utc,argv/tempdir 标记}；清理后 tasklist 断言全部 PID 消失（轮询 2s）；线程账本（scope-join 计数、sampler join、reader/writer joined 标志、registry remaining+names）；accepted/refused 以 names 快照+joined 标志+`[shutdown]` 日志行统计口径区分；不把 registry==0 等同 OS 回收。
- **R004**：`spawn_persistent_holder` 增 cfg(test) 继承——调用线程持 override 时经 thread-local 把测试 registry 传入 holder 线程，holder track 与测试 track 共享同一受测 registry（生产 holder 仍全局；not(test) 无此代码）。ac1 重写：持锁期先 spawn holder（轮询 registry 快照证明等待中未注册），再释放锁，断言同一 registry 注册成功；收尾 owner 视角 reap；删除 `reap_unreaped_workers_global`。
- **R005**：registry 选择重构为 `with_unreaped_registry`（闭包短借 Arc）：thread-local 显式 > 全局槽(owner 匹配) > 全局 static；槽读失败且当前线程 IN_REGISTRY_TEST → panic fail-closed；无标志（生产/后台）→ 全局。guard.acquire 显式验证槽写入。cfg(not(test)) 版直接 `f(&UNREAPED_WORKER_REGISTRY)`，行为零变化。
- **R006**：guard 持 `Arc<Mutex<Vec<UnreapedWorker>>>` 替代 Box::leak；drop=显式 reap 自己的 registry（join finished，bounded）→ 记录剩余 → 清槽（验证）→ 清标志 → 放互斥 → Arc 释放；panic 展开同样执行。
- **R007**：新增 `#[cfg(test)] pub fn kill_and_wait_for_test()` 返回 (kill Result, wait Result)；取消场景分别断言"取消成功"与"Drop 完成"+PID 消失；`kill_for_test` 保留。

### 状态

- 2026-10-24：r2 认领完成；R001/R002 机制已静态确认（见上）；开始修改 source-r2（尚未完成任何文件修改；无测试执行，Codex 代跑）。
- 2026-10-24（交付）：**r2 修订完成（代码+运行器+文档；本会话未编译未运行，全部交 Codex 代跑）**。修改文件：
  - `source-r2/apps/desktop/src-tauri/src/library_bridge.rs`：①隔离区重构（TestRegistry=Arc 别名、TEST_THREAD_REGISTRY/IN_REGISTRY_TEST thread_local、with_unreaped_registry 两版：test 版继承→槽(owner)→全局+fail-closed；not(test) 版 inline f(&全局)）；②track 主体闭包化（语义零变化）；③spawn_persistent_holder cfg(test) 继承（R004）；④count/reap 改 with_、删 reap_unreaped_workers_global；⑤kill_and_wait_for_test 新增（R007）；⑥RegistryTestGuard 重构（Arc 所有权、槽安装/清除均验证、drop 显式 reap+账本，R005/R006）；⑦ac1 重写（持锁 spawn holder→等待证明→同 registry 注册→reap_now 断言 remaining==0，R004）；⑧child_lock 测试握手化（mpsc 信号+600ms 持锁+fallback 分支判别断言，R001）；ac2/ac4 仅受益于 guard 改动（无需改文本）。
  - `source-r2/apps/desktop/src-tauri/src/multichannel_stress_tests.rs`：整体重写（ChildIdentity/tasklist PID 消失断言、线程账本、unreaped_worker_names 归属快照、kill_and_wait_for_test 分立断言、fault 场景错误包络/阶段耗时/writer-reader 未结束证据/逐 channel Drop 计时/pre-drop joined 标志、peak>=32 保留并内嵌机制说明；R002/R003/R007）。修复了 r1 版的一个新发现 bug：cancel 线程不能向主线程 thread_local ledger push（改为 join 返回值收集）。
  - `workspace/r2-runner/run-rust-default-parallel-r2.ps1`、`run-stress-scenarios-r2.ps1`（新路径，均未执行）。
  - main.rs 未改（模块已在 3b 注册）。
- 待 Codex：编译（cargo test --no-run）→ 若有编译错误按设计意图最小修 → commit 新 head → 新 head 上默认并发两次 + 五场景 + （可选）child_lock 单测诊断运行 → 回填 r2 RESULT 七项表 → 新 Appointment DSH。
