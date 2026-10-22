你是 New Manga 项目的独立 Reviewer DeepSeek Harness。请对 Codex 编写的 P02 AppContainer 隔离契约 r3 做 exact-object 只读 Review。Codex 是作者；你是非作者 Reviewer。不得修改任何文件，不得创建/查询/删除 profile，不得改 ACL/label/registry，不得运行 host/process probe、Windows Sandbox、Smoke、Build、Cargo、Tauri、PyInstaller 或产品测试。

## 固定对象与绑定

- 仓库根：`G:/CODEX/New Manga`；branch=`main`；base HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`，tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- 契约：`verification/P02/appcontainer-isolation-contract-r3.md`，预期 SHA-256=`30FA3DC10B5C84982018D0558B1262520615EDD17D5137335B808AF7429C3CC4`。
- Task：`doc/tasks/P02.md`，预期 SHA-256=`74E3766600C75A41A0B4B18806BB2C494AB67305959846BB74082BC20B13CDE4`；重点绑定新增 `PROJECT_ORCHESTRATION_AUTHORIZATION / AppContainer 精确隔离范围` 段落。
- 前轮 DSH Review：`verification/P02/dsh-appcontainer-contract-r2-review.stdout.md`，decision=`NOT_VERIFIED`，内容等同 `CHANGES_REQUESTED`，P0/P1/P2/P3=`2/5/8/7`。
- Codex adjudication：`verification/P02/codex-appcontainer-contract-r2-adjudication.md`。逐项审阅 dispositions 与 r3 是否落实；不要将 Codex 的 SHA 复算视为 Reviewer 的 SHA 复算。

若你具备 shell/哈希工具，独立计算 r3 与 Task 的 SHA-256/字节数并与上方绑定值比较；若不能，明确 `object_binding=NOT_VERIFIED`，不要称 exact-object Review 已验证。不能计算 hash 不等于内容 mismatch。

## Review 范围

逐项检查 r3 是否消除/控制 r2 finding：C-00、R2-01…R2-22。尤其审查：

1. r3 授权的输入/祖先/Windows system ACL 零修改边界，以及 scratch/profile 精确 ACL/Low-label 变化与逐对象恢复是否可实施且可逆。
2. MIC/DACL 区别、`TokenIntegrityLevel`/`TokenMandatoryPolicy`、Low label、`WRITE_DAC`/`WRITE_OWNER` 证据；不得把 `AccessCheck` 的 DACL 允许当作真实写成功。
3. profile/private registry 创建前只读不存在性检查是否有可执行、非猜测的依据；若无可用方法，要求清楚阻断，不能绕过前置条件。
4. P02 Task:79 Smoke alias 与独立 `verification/P02/tmp/lpac-write-control/` canary 语义是否分离；Task:81 两个 generated directories 的 tracked-file 例外是否保留。
5. 路径别名、reparse、ADS/hardlink、祖先遍历、旧 TSV/203 条数过度声明、dirty/untracked SHA 范围与“未知即阻断”。
6. Job Object completion-port 子进程证据、handle snapshot、token 字段、WER/LocalDumps、cache 环境闭包，以及零 capability 的能力否决设计。
7. 当前 P02 状态是否仍如实为 profile=`NOT_CREATED`、ACL/registry=`NOT_MODIFIED`、OS preflight=`NOT_RUN`、hook/cache/child-process=`BLOCKED / NOT_VERIFIED`、Build Gate=`BLOCKED`、build=`NOT_AUTHORIZED / NOT_RUN`、Hard Build Barrier=`EFFECTIVE`、AC1–AC7=`BLOCKED / NOT_RUN`。

依赖事实时只引用 Microsoft 一手文档，指出契约里的具体条款/路径和最小修正。不要为了让任务继续而假定权限、profile registry 路径、文件闭包或清理成功。Review 只批准文档，不代表 OS 测量或 Gate 放行。

## 输出

请以中文撰写完整 Review：实际能力与 object binding、scope 覆盖、逐项 findings（ID、级别、路径/条款、影响、最小修正）、findings 总数、是否可以进入无 profile/无 ACL 变化的只读 OS preflight、未覆盖风险，以及末尾的 `APPROVED` / `CHANGES_REQUESTED` / `NOT_VERIFIED`。明确报告 SHA 绑定能力。保持只读。
