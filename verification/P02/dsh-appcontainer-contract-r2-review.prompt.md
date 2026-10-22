你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请对 Codex 编写的 P02 AppContainer 隔离契约 r2 做 exact-object 只读 Review。Codex 未实现此设计；你是非作者 Reviewer。不得修改任何文件，不得创建/查询/删除 profile、改 ACL/registry、运行 host/process probe、Sandbox、Smoke、Build、Cargo、Tauri、PyInstaller 或产品测试。不要把用户授权当作任何 Gate/Test 的通过证据。

## 固定审查对象

- Root：`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。
- 当前 workspace 含原作者未提交内容；不要 stage/commit/覆盖/清理。
- 契约：`verification/P02/appcontainer-isolation-contract-r2.md`，SHA-256=`8D84DA22599FA074083DCADC73119BC259F4545EC2BB7B1090EBD44687DE6963`。
- P02 Task：`doc/tasks/P02.md`，SHA-256=`4915CE24F6B540C98F5C54916F9A99951970A16733AF5CF8044FA36240D2F7A3`；只把新增的 `2026-10-10 PROJECT_ORCHESTRATION_AUTHORIZATION / AppContainer 精确隔离范围` 段落视为本 Review 的 Task 绑定对象。
- 初始设计候选：`verification/P02/appcontainer-isolation-candidate-r1.md`；其 DSH report=`verification/P02/dsh-appcontainer-design-r1.stdout.md`（此前 decision=`NOT_VERIFIED`，存在读写闭包、profile/hive、环境变量、process tree、ACL 祖先等缺口）。
- 只读 host 输入清单：`verification/P02/codex-scratch-build-preflight-hostfolders-r1.tsv`；scratch/Build allowlist=`doc/tasks/P02.md` § Codex-only local scratch-build output boundary；hook/cache 闭包限制=`verification/P02/codex-hook-cache-closure-audit-r1.md`。

## 审查内容

逐项检查 r2 是否足够精确、内部一致、对真实 Windows API/LPAC 语义准确并可实现：

1. 用户明确给出的 scope authorization 是否仅作为许可登记，并正确保留 `Build Gate=BLOCKED`、`build=NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。
2. 固定 profile moniker 的字符/长度/单次生命周期；创建前证明 profile/目录/private registry 均不存在；只对本轮 CreateAppContainerProfile 新建成功的 exact profile 做 cleanup；清理失败时保存现场。
3. LPAC opt-out、零 capability、network/registry/COM/capability 默认否决、profile local data / TEMP/TMP / private HKEY、环境重建与缓存/token path 归属是否正确；指出无法核验的 Windows API 权限/身份假设。
4. Task 中固定的 RO 根是否被精确复用；Scratch RW 是否只限列出的 Task 输出子目录与 profile；root/Owner worktree/用户漫画数据/数据库/Lock/current/pinned/凭据是否明确无 read/write；逐对象祖先遍历权限、reparse/hardlink/ADS 与 ACL 继承是否有 fail-closed 闭包。
5. `AccessCheck` 与真实写探针的设计是否足以分别证明 protected write denial 与 scratch positive write，而不触碰真实用户文件；主仓/输入前后 hashes 是否覆盖正确对象。
6. Job Object/no-breakaway/no-handle-inheritance、短命子进程 token evidence、PID 复用和未知后代 fail-closed 是否有可执行证据路径；不可验证的要求应是 blocking finding。
7. `C:\Windows\System32` 等 loader/runtime 动态读取闭包目前要求逐文件前置解析但未授权任何宽路径兜底；判断这是否是可实施的精确范围，不能通过宽泛 `Windows` 目录授权化解。
8. 依据 Microsoft 一手文档的 API/LPAC 论据是否准确。若审阅环境不能访问文档或不能独立核验 hash/Task SHA，明确标记限制，不得声称已核对。

## 输出

以 `verification/P02/appcontainer-isolation-contract-r2-review.stdout.md` 为报告中建议的目标路径（本工具调用会捕获 stdout）；本任务本身只读。先记录实际能力/对象绑定，然后列每项 finding 的 ID、级别、路径/条款、影响、最小修正。末尾给 `APPROVED`、`CHANGES_REQUESTED` 或 `NOT_VERIFIED`，并报 P0/P1/P2/P3 数量及是否能进入无 profile 创建的只读 OS preflight。不得批准 profile 创建、ACL 修改、Smoke 或 Build；报告状态对任何实际 Gate 均无提升。
