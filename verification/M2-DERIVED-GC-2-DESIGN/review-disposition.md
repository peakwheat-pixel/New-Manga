# DSH r1 处理与真实派发记录

DSH r1 reviewed_head=4a930c611c1e7a353f5fe5584932f4cf6d8048c1，base=ab4b7c110a7c828f20d2d0787bd71144336d2e44，EXIT=0，session=session-ec7cf46a-1caf-492f-8b3e-09d4f782c667。只读 review worktree=G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN-review-r1，branch=codex/m2-derived-gc-2-design-review-r1。原 final.text UTF-8 字节保存到 doc/reviews/M2-DERIVED-GC-2-DESIGN-4a930c61-dsh-r1.md，SHA256=8815d9f5b9d7f502a33375864b7600a63b8a21032f2ec9fbfef36108289c6a44。JSONL/err/prompt 仅在本机 Codex tmp 保留，不纳入仓库。

使用真实 `dsh --profile headless --json -`，通过 stdin 自包含指令派发；并非报告 §8 自述的“用户在 worktree 直接派发/非 CLI”。此处纠正派发方式，不修改 Reviewer 原报告，也不影响其静态 finding。mount_session.py 按精确 session ID/工作区挂载 EXIT=0；desktop 下次启动可发现，不重启正在使用的 DSH；web_visibility=unverified。

Reviewer 的 shell 因 SetNamedSecurityInfoW Win32 5 不可用，命令复跑 BLOCKED；Codex 文档检查实际 executed。DSH approve_with_conditions，0 P0/P1、3 P2、2 P3、2 P4。新设计 head 必须再次真实 DSH 复核，不能沿用 4a930c61 批准。

| 条件/观察 | 作者修订（等待 r2 独立核验） |
|---|---|
| C1/F01 | production Core 唯一创建来源；channel 仅既有 retired 更新。退役嵌入既有 revoke 请求，不增第二 round-trip；mark 异常 no-op+stderr、零 busy wait/零重试，不杀 channel、不改成功 rerender。新增内部位与窄写权限明确授权。 |
| C2/F02 | 锁锚定 derived 删除域，catalog singleton namespace 与 lock 绑定 canonical+OS identity/version；双根失配两个 sweep 均禁用。store 单接线覆盖 loader/acceptance/probe/ac1/测试入口。无可靠旧 runtime 检测信号明示 UNKNOWN，G7 控制切换不足则禁用，不冒充可探测。 |
| C3/F03 | 就绪复用 core.ping；保护先于 assemble/catalog/GC。library_bridge.rs 窄授权启动 deadline=30s/自有 child 退出，失败不 spawn channel；普通 wire/业务不变。 |
| C4/F04 | 同一请求内 revision_no + outcome.managed_path 逐字匹配唯一行，存真实 revision_id；说明 purge 后 revision_no 可复用，不改 RenderOutcome/port。 |
| C5/F05/O02 | native helper 复用 handle_resolver.py，点名允许路径及现有测试；GC读+DELETE权限、窄分享、同句柄 hash/size/identity/delete，目录句柄保护，现有reader行为不变。 |
| F06 | 残留包含每会话每页最后一个未退役 key；失败/多实例/pin/unknown 可更多，不写“至多一个”假上限。 |
| F07 | 旧设计 delivery=8dd88c56；Handoff 到 reviewed_head=4a930c61 才入库，按协议后续 metadata commit 引用前一 delivery；复审恢复以 reviewed_head 为准。新 Handoff 同样区分两者。 |
| O01/O03 | K5 显式 Lock/主产品行不写；现行 M2-C1 契约仅在后继 Task 窄授权，本轮不改。 |

额外作者补强：13 条矩阵逐项实证/UNKNOWN；人工修改副本通过同核验句柄匹配 immutable revision 既有 file_hash/size；验证器断言全部改动路径在设计 allowlist。运行回收/native/产品回归均 NOT_RUN，设计审查不是回收实现验收。

## r2 与第三轮修订

真实 CLI r2 reviewed_head=3a6846758ebdb18e3ee696e0c1410aa698e43225，session=session-70171dd3-7f22-4187-b0d5-36a81232f286，EXIT=0；原报告 doc/reviews/M2-DERIVED-GC-2-DESIGN-3a684675-dsh-r2.md，final.text UTF-8 SHA256=6d601a6de0f44c465755ef7d63eb1626a4d0dd763a0bb7e374bbaaafb0900cbb。精确session挂载 EXIT=0，desktop下次启动可发现，web_visibility=unverified。DSH changes_requested：C1/C3/C4/C5/F06/F07已闭合，C2的bootstrap顺序剩余R2-01(P2)；0P0/P1。新修订仍需r3独立固定head批准。

| r2 项 | 第三轮作者修改（待 r3 核验） |
|---|---|
| R2-01 / C2 | 选择r2建议(b)：显式两段式。只读mode=ro&immutable=1 bootstrap仅读namespace hint，无DDL/写/业务/issue→关闭→取derived租约→业务连接重读identity/version/绑定一致→允许Schema/业务；缺行、WAL旧值、替换、失配拒绝，不回退无租约。loader/acceptance_bridge由默认store接线，无需改CLI；无绑定拒绝写入，受控Core/新测试显式传保护上下文才初始化，入口判别补G3。 |
| R2-A1 | G2明确WebView revoke_resource_refs及失败撤销新key不带退役位，Tauri命令表不加能力。 |
| R2-A2 | library_bridge.rs启动专用wait_startup_ping seam，正常round_trip不改；超时先回收本次child促EOF，再回收worker/锁/句柄，失效对象不交AppState，无通用调度框架。 |
| R2-A3 | mark用独立mode=rw timeout=0连接，borrow现有lease、finally关闭、零DDL/Schema/WAL变动；不改共享连接busy策略。 |
| O-R2-1/2/3 | K5 pages保护明确限定live-preview；managed_rel_path明确是拟议表字段保存既有managed_path；点名新增两个已存在store测试文件，非新测试架构。 |

## r3 与首次新库覆盖修订

真实CLI r3 reviewed_head=8557a3d4162d00dc7a985ede0dabda22809f60fd，session=session-4bc4e130-e7f0-4e9f-8ba9-6acbce86807e，EXIT=0。原final.text UTF-8 SHA256=ba2717c5a511a7ee10ee1b235483b9a005f9013db4b7e8ba294e3056235b5941；报告doc/reviews/M2-DERIVED-GC-2-DESIGN-8557a3d4-dsh-r3.md。精确session挂载EXIT=0，web_visibility=unverified。r3 changes_requested（1P2 R3-01）：bootstrap顺序已闭合，未绑定首次验收库入口剩覆盖缺口；0P0/P1。r4仍须固定新head复核。

| r3项 | 作者修订 |
|---|---|
| R3-01 | §2.3冻结现有store的initialize_namespace窄函数：只新/空自有catalog显式绑定，不删不启GC、不迁移未知旧库。catalog_loader新增可信fixture initialize-preview-namespace flag；默认已绑定路径不变。Core唯一产品迁移登记者须G7，lab/test driver先initialize再seed/spawn，解决loader先于Core/ac1无Core链。§5点名loader、_LoopHarness、两个packaged runner、两个dev verification driver；只fixture接线，历史报告/结果日志不改。§6/7明确首装红绿Gate。 |
| R3-A1 | 现有command_allowlist(false,false)仍恰好15条，无退役wrapper；WebView不得透传位。 |
| R3-A2 | timeout显式kill/wait本次child，退出child锁区再join worker/丢弃终止态channel；终止Drop不再shutdown/等待第二个5s，正常Drop不变。 |
| R3-A3 | journal/WAL只禁配置变动，允许正常事务journal写；SQLite URI以Path.as_uri归一/percent转义，stale hint拒绝不初始化。 |
| R3-A4 | 纠正bridge_and_thresholds实际:memory:，真正file-backed直接/间接fixture均点名，不给memory fixture装namespace。 |

新增fixture路径均基于本仓库只读真实调用点定位；本设计仍无生产/测试/driver代码变动，native Gate全部NOT_RUN。r4报告将原字节入库，不把作者修订表视为Reviewer已批准。
