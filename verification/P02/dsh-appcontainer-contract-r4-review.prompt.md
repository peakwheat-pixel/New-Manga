# P02 AppContainer 隔离契约 r4 非作者只读 Review

你是 DeepSeek Harness，担任 P02 的非作者 Reviewer。请只审查文档，不修改文件，不做本机 OS preflight，不访问 registry/ACL，不创建 profile，不执行 probe、build、Cargo、Tauri、PyInstaller 或产品测试。

## 固定审查对象

- 项目根：`G:\CODEX\New Manga`
- branch/HEAD/tree：`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / `c25d051a4b9a0bd9773b50170e100f575ea19f2b`
- 契约：`verification/P02/appcontainer-isolation-contract-r4.md`，预期 SHA-256=`F025A2671FA16EB317C04C457C75BBD6A29D16A753FF146BCAD4AF244A591F49`
- Task：`doc/tasks/P02.md`，预期 SHA-256=`C7959EF931D7D937B885267D400553AADE1E9D40E3FA0A2B47CB18486D15138C`
- r3 报告：`verification/P02/dsh-appcontainer-contract-r3-review.stdout.md`，SHA-256=`50EA7BACBC1F64B6E835F39CF1519CA42EFD6BA4FB91A31C843B597A20388117`
- Codex r3 adjudication：`verification/P02/codex-appcontainer-contract-r3-adjudication.md`

先说明当前工具是否能独立复算 SHA-256 / 文件字节数。能复算才报告 `object_binding=VERIFIED` 并列出实际值；不能则明确 `object_binding=NOT_VERIFIED`，不可把 dispatch 声明当成自己的复算，也不可因此伪称 exact-object Review。仍可注明自己实际阅读路径并作内容 Review。

## Review 范围

逐项检查 r4 的实际条文及与 P02 Task 的一致性，特别是：

1. P1-01：目标 private registry 的创建前不存在性在公开文档缺少精确 key/view 与 absent-state 无副作用 API。r4 将其定为 `UNPROVABLE / BLOCKED`，禁止猜 key、调用可能创建/初始化 storage 的 API 和创建 profile。判断这是否充分 fail-closed；列出任何权威文档若能支持其他结论。
2. P1-02/P1-03：系统对象 DACL 的 `SYSTEM_ACL_UNREADABLE` 与 `SYSTEM_ACL_MISSING` 区分；scratch 仅新建 exact leaf；MIC 拒绝不冒充 AppContainer/DACL 隔离证据。
3. P2-01..08：Python user-site 两个变量及回读、负向 control 的父链/label、`AccessCheck` 字段和 `WRITE_DAC`/`WRITE_OWNER`、精确 scratch canary 路径、WER 检测面但不读取 dump 内容、冻结 exclusion manifest、契约 hash 的 object-binding 限制。
4. P3-09..16：禁止提权/take-ownership；术语与 moniker 固定；restore 后逐字段比较；表外只读；`ERROR_ALREADY_EXISTS` fail-closed；未来 MIC control；`.task-envs` / `.worktrees` sibling 路径边界。
5. 检查 r4 的 addendum 是否确实优先并消除所有复制自 r3 的冲突表述；路径、继承、错误分支、恢复条件、输出例外与 Gate 条件是否可执行且没有未枚举写入。
6. 判断是否仅允许进行“无 profile、无 ACL/label/registry 修改、无真实写探针”的纯测量 OS preflight；这不等于 profile/create/build/AC 批准，也不关闭 `private_registry_absence=UNPROVABLE / BLOCKED`。

不得把 r3 的 finding counts 改写成 r4 结果。输出 Markdown：实际读了哪些对象、object binding 状态、decision（`APPROVED` / `APPROVED_WITH_CONDITIONS` / `CHANGES_REQUESTED` / `NOT_VERIFIED`）、新增 P0/P1/P2/P3 counts、逐条 findings（严重度/路径/触发/影响/最小修正）、r3 finding disposition 是否成立、允许与禁止的下一步、未覆盖范围。若 shell/API 不可用，忠实说明；不得声称 OS 状态已测量。
