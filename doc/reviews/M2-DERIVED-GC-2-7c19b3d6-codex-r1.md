```yaml
task_id: M2-DERIVED-GC-2
reviewer: Codex（非作者）
reviewed_head: 7c19b3d6
base_commit: ad75fadc
decision: changes_requested
findings:
  total: 9
  P0: 0
  P1: 3
  P2: 6
  P3: 0
  P4: 0
```

## Verdict

**`changes_requested`**。有三项 P1 尚未闭合：初始化预检可能误绑定旧 catalog、namespace 锁文件有 reparse 替换竞态，以及 G7 分发迁移 Gate 未有可核验的阻断证据。其余 NOT_VERIFIED 项也不能按通过处理。

固定审查 `7c19b3d6`。目标 worktree 当前 HEAD 已到 `9538ff2c`，且有未提交的生成文件；以下仅依据固定 commit，不把这些工作区改动计入审查。

## G1–G7 与 R4-A1/A2

| 项目 | Verdict | 证据摘要 |
|---|---|---|
| G1 来源 | **PASS（静态）** | Core 按 `revision_no`、`managed_path` 唯一匹配 `TRANSLATED` revision；catalog 与 origin 同事务登记，loader 重绑会清除来源资格。 |
| G2 生命周期 | **PASS（实现）/部分未核验** | 只在成功 revoke 后 mark；使用独立连接且 `timeout=0`。测试仅断言耗时 `<2s`，不能单独证明零等待，见 F-04。 |
| G3 静默窗口 | **FAIL / NOT_VERIFIED** | 共享/独占的 CreateFileW share 组合静态上兼容，但锁路径在检查与打开之间可被替换；测试也没有证明两个独立共享持有者能并存，见 F-02、F-05。 |
| G4 保护与回收 | **PASS（静态）** | 检查、删除和 metadata 更新顺序符合代码中的保护逻辑；未执行测试。 |
| G5 安全与恢复 | **部分通过 / NOT_VERIFIED** | 句柄式校验、先删文件再删 metadata 的路径静态看符合设计；没有真实活跃读取句柄阻止 GC 删除的判别测试，见 F-06。 |
| G6 回归与隔离 | **FAIL / NOT_VERIFIED** | RC2 interactive gate 和 AC5 CS-L1 均有实际 FAIL；全量 pytest 日志的命令与矩阵声明不一致，见 F-07、F-08。 |
| G7 启用边界 | **本机单版本部分成立；分发迁移 NOT_VERIFIED** | 新协议锁的单版本实验可支持本机机制结论；不能证明非协作旧 runtime 已退出，也不能证明分发 Gate 会阻止不安全启用，见 F-03。 |
| R4-A1 | **部分吸收** | 新库初始化与 run2 路径有覆盖，但初始化测试未使用真实旧 schema，不能闭合“旧/未知历史拒绝”。 |
| R4-A2 | **PASS** | 历史冻结 probe 没有纳入本 Task Gate 或被改写。 |

CreateFileW 的 share 检查是双向的：新请求必须符合既有句柄的 share mode，既有请求也必须符合新句柄的 share mode。因此两个 `GENERIC_READ` 共享句柄配 `FILE_SHARE_READ|FILE_SHARE_WRITE` 在静态推演上兼容；独占打开配 `share=0` 会与共享读取冲突。锁文件打开没有使用 `FILE_FLAG_OPEN_REPARSE_POINT`，检查后再按路径打开仍可能跟随替换后的 reparse point。[Microsoft CreateFileW 文档](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)

## Findings

### F-01 — P1：初始化预检可能把有历史数据的旧 catalog 当成空库

位置：[catalog_store.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:176>)、[同文件](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/catalog_store.py:227>)

`initialize_namespace` 在获取独占锁之前运行预检。预检先数 `resource_catalog`，再查询 `preview_lifecycle`；旧版 schema 没有后者，查询抛出 `OperationalError` 时，异常分支把**两个计数都清零**。这样旧 catalog 即使已有资源行，也可能被当成空 catalog 绑定。`immutable=1` 预检也不能替代锁内重读核验。

现有 [测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:296>) 用新版初始化器建表后删 namespace 行，没有模拟旧版缺少 lifecycle 表的真实库。

**建议处置：** 在锁保护下检查已知 schema 和各表数据；未知 schema、旧历史行、WAL 状态无法确认时拒绝绑定。新增真实旧 schema 与未知 SQLite 文件用例，断言均不写入、不绑定。

### F-02 — P1：锁文件的 reparse 检查与打开之间存在竞态

位置：[handle_resolver.py](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/infrastructure/resource_channel/handle_resolver.py:526>)

`_open_lock_handle` 先按路径做 reparse 检查，随后以 `CreateFileW` 打开路径；打开未使用 `FILE_FLAG_OPEN_REPARSE_POINT`，也未对返回句柄核验最终路径与身份。若两步之间 lock path 被 junction/symlink 替换，进程可能锁住另一个对象，而其他进程锁住原位置，导致租约分裂。

现有 reparse 测试覆盖 derived root 和候选删除文件，没有覆盖 lock path 本身的替换竞态。

**建议处置：** 通过已核验的目录/文件句柄打开，并检查返回句柄的 reparse 属性与最终身份后才认可租约；增加 Windows 锁路径替换测试。

### F-03 — P1：G7 的“分发迁移 Gate 不豁免”尚无可核验的阻断效果

位置：[GC 设计 §2.3](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/doc/contracts/M2_DERIVED_PREVIEW_GC_DESIGN.md:70>)、[Core 启动 sweep](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/src/bootstrap/core_service.py:1761>)、[G7 边界记录](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g7-enablement-boundary.md:39>)

设计要求无法可靠检测的旧非协作进程必须经受控全退出迁移证明，否则 sweep 保持禁用。当前 Core 在取得新协议独占锁后即运行 sweep；旧版 runtime 不持这把锁，仍可能有尚未打开的有效 grant。G7 记录称分发检查不影响本次实现启用，但没有提交分发阻断证据。普通 DB 行或文件写入也不会自动改变用于身份核验的 OS file identity。

因此，“本机单版本机制可运行”不能推出“分发迁移安全”。边界文件关于本机无旧版本存量的陈述，无法核验为所有目标安装环境的事实。

**建议处置：** 把旧版本全退出证明明确设为分发前阻断条件，并补上可审计的执行证据；未满足前不得启用会删除文件的 sweep。确认并记录旧 catalog 的迁移或拒绝启动策略。

### F-04 — P2：G2 的耗时断言不能单独证明零 busy wait

位置：[测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_catalog_authority.py:469>)

实现明确使用独立连接和 `timeout=0`，但测试用耗时 `<2s` 作为证据；这个阈值仍允许小于两秒的等待，无法独立判别严格零等待要求。

**建议处置：** 保留代码级 `timeout=0` 核查，并让测试断言锁争用时立即得到 busy 结果；测试名称和报告不要将 `<2s` 写成零等待实测。

### F-05 — P2：没有证明多个独立进程可同时持有共享租约

位置：[租约测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_handle_resolver.py:252>)

现有子进程用例证明一个共享持有者会阻止独占者；另一个独占阻止共享的用例在同一进程执行。未找到两个独立进程同时成功取得共享租约的实测。

**建议处置：** 增加双共享持有者进程用例，再验证两者都退出后独占者可获取。

### F-06 — P2：缺少活跃读取句柄阻止 GC 删除的判别测试

位置：[删除句柄测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/m2_resource_channel/test_handle_resolver.py:366>)、[GC 测试](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/tests/core/test_derived_gc.py:372>)

测试覆盖 reparse 候选拒删、current 翻转等路径，但没有构造 GC 删除期间仍被 reader 持有的读取句柄。该场景的 sharing violation 与“reader 打开时遇到 writer”测试并不等价。

**建议处置：** 用真实 reader 句柄保持打开，运行回收并断言文件与 metadata 保留；关闭 reader 后再确认回收可继续。

### F-07 — P2：RC2 与 AC5 runner 的已登记漂移仍使 Gate 为 FAIL

位置：[Task 登记](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/doc/tasks/M2-DERIVED-GC-2.md:42>)、[RC2 runner](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-RC2/run_e2e.py:309>)、[AC5 runner](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/packaging/m2ac5/run_clean_start_e2e.py:504>)

RC2 的 9 条 `PRODUCTION_EXPECTED` 与 AC5 的 protocol minor 3 都可在 release 快照核实为 RC-4 前的旧期望；当前记录分别显示 interactive-production-surface FAIL、CS-L1 FAIL。这不是 GC-2 新代码导致的漂移，但不能记作 Gate PASS。

**建议处置：** 同意交独立 debt Task 修复这两项旧期望；本次验证记录保持 FAIL，直到独立 Task 完成并重新验收。

### F-08 — P2：验证日志与最终审查 head 不完全匹配

位置：[pytest 日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/pytest-full.log:1>)、[矩阵](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/g1-g7-matrix.md:12>)、[AC5 runner 日志](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2/raw/packaged-runners.log:28>)

pytest raw 首行记录的是若干目录的子集命令，而矩阵声称 `tests/` 全量；1 个 skip 没记录原因。`diff-check.log` 绑定较早 head；本次只读执行 `git diff --check 5896db8c..7c19b3d6` 返回 1，报告归档 raw 的行尾空白和末尾空行。AC5 主 runner 日志记录修正前结果；后续 JSON 能看到 AC1/Z2 PASS、L1 FAIL，但没有与最终 runner 变更对应的完整命令、head、stdout 和 exit code。

**建议处置：** 用明确命令、固定 head 和完整原始输出重建验证记录；保留原始日志字节时，将代码 diff 检查与归档日志格式检查分开记录。

### F-09 — P2：存在超出 `allowed_paths` 的修改，且 runner 改动超出窄授权

位置：[Task allowed_paths](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/doc/tasks/M2-DERIVED-GC-2.md:72>)、[超范围 Task 文件](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/doc/tasks/M2-DERIVED-GC-2-DESIGN.md:1>)、[超范围 verification 文件](<G:/CODEX/New Manga.worktrees/DERIVED-GC-2-zcode/verification/M2-DERIVED-GC-2-DESIGN/completion.md:1>)

固定 diff 改动了 `doc/tasks/M2-DERIVED-GC-2-DESIGN.md` 和 `verification/M2-DERIVED-GC-2-DESIGN/**`，不在本 Task 的允许路径。AC5 runner 虽在路径允许列表中，但授权限定为 fixture 初始化 flag/root 参数；新增 AC1 prebind gate 及 CS-Z2 排除 `.preview-lifecycle.lock` 的比较集合超出字面窄范围。产品 schema、ports、React、`acceptance_bridge.py`、`ac1_bridge.rs`、公共 grant 语义、依赖和 packaging spec 在固定 diff 中未触碰；`363265b1..7c19b3d6` 的 `src/apps` 差量为空。

**建议处置：** 移除超范围提交，或先由 Codex 在 Task 中明确追认允许路径和窄范围增补，再重新提交审查。

## 三项登记事项

1. **RC2 9 条期望、AC5 minor 3：同意交独立 debt Task。** release 快照证明两项均是此前已有漂移；但当前 Gate 结果仍是 FAIL，不能据此关闭 G6。
2. **两项 fixture 语义修正：语义上接受，授权上待追认。** AC1 fixture 在首次初始化前预绑定符合设计 §2.3；CS-Z2 将协议锁文件列入白名单符合冻结位置要求，且没有降低用户 fixture 文件字节恒等保护。它们仍超出当前 runner 窄授权，需记录追认。
3. **runner 产物归档：最终树合规。** 固定 diff 未改写 M2-AC5/M2-RC2/M2-RG1 历史 raw，产物归档在任务自己的 raw 目录，符合 P3-9(b) 先例。中间搬运及 restore 操作本身无法从最终树独立复原核验。

## 只读核查命令与关键结果

以下命令使用 `git -c safe.directory=... -C ...` 指向指定 worktree，均为只读：

- `status --short --branch`、`rev-parse --show-toplevel --git-common-dir HEAD`、`log --oneline --decorate -8`：确认目标分支、common dir、当前 HEAD `9538ff2c` 和未提交生成文件；审查仍固定在 `7c19b3d6`。
- `diff --stat ad75fadc..363265b1`、`diff --stat ad75fadc..7c19b3d6`：分别为 47、62 个路径；固定 head 相对 `363265b1` 新增的 `src/apps` 差量为空。
- `diff --name-status 363265b1..7c19b3d6 -- src/apps`：空输出。
- `diff --check 5896db8c..7c19b3d6`：EXIT=1，来自已归档 raw 日志的行尾空白和末尾空行。
- `diff --name-status 5896db8c..7c19b3d6 -- verification/M2-AC5 verification/M2-RC2 verification/M2-RG1`：只改 RC2 runner；历史 raw 未改。
- `git grep -n ... 7c19b3d6 -- <相关路径>`、`git show 7c19b3d6:<文件>`、`git show 5896db8c:<runner>`：核对调用点、测试和 release 快照中的旧期望。

**未执行：** pytest、cargo test、打包 runner 与 Windows 动态租约/句柄复现。用户明确要求不要运行可能写入仓库的命令；本次仅做只读审查。实际目标环境中是否存在旧 runtime 存量也无法从这些源码和日志独立确认。

协作复核已由 `scope_evidence` 与 `spec_review` 两个非作者审阅代理完成；只读环境未提供可核验的 token 用量。

**推荐下一步：** 不关闭 Task。请 ZCode 修复 F-01/F-02，明确落实 F-03 的分发阻断条件；补齐 F-04 至 F-06 的判别证据，重建 F-08 验证记录。Codex 追认或撤销 F-09 超范围改动后，再交新的非作者 Reviewer 复核。