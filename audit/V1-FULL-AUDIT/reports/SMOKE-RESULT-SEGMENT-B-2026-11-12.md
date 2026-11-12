# 段 B smoke `core,wire` 结果

## 执行结果

- Runner：`python audit/V1-FULL-AUDIT/tests/audit_runner.py smoke`
- 生成时 HEAD：`2a7aed313f9673b327cfbb87dbbe2cfde1269037`；branch：`main`
- started：`2026-11-12T08:45:57.725840+00:00`；elapsed：`1.783s`
- argv 限定 `--only core,wire`；原始 runner EXIT=1，程序报告 `FAIL`，不得改写为 PASS。
- 共 17 项检查：10 PASS、7 FAIL。Wire 6/6 PASS；Core 层 11 项中 4 PASS、7 FAIL。frontend 与 packaged 层为显式 SKIP（不是本次执行范围）。完整输出及两份 JSON 见 [runner log](../logs/software-smoke-segment-b-20261112T084557725697Z.log)、[smoke report](../evidence/software-smoke-report-segment-b-20261112T084557725697Z.json)、[runner evidence](../evidence/software-smoke-segment-b-20261112T084557725697Z.json)。

## ZCode 只读 adjudication

ZCode session `sess_8a2f7064-f80d-49a5-b96f-6d5ba20dd1ca`、turn `turn_576c148c-2dba-4ba5-bdad-86600ab66cf3`、trace `8af83f29-cdee-4c07-98be-f6d27f6ff120` 的原始结论见 [`smoke-result-adjudication-20261112.log`](../logs/smoke-result-adjudication-20261112.log)。ZCode 只读 smoke 产物及相关源码，未运行测试或修改文件。

- **7 项 Core 失败统一登记为 `BLOCKED-SANDBOX-GRANT` 环境/前置阻断及其级联；目前无一项能独立支持产品缺陷。** `AppContainerSandbox._grant`（`src/infrastructure/plugins/sandbox.py:276-288`）执行 `icacls <interpreter> /grant *<sid>:(RX)`；返回非零会抛 `SandboxError("cannot grant sandbox access to <name>")`。失败发生在 hook 子进程创建前，目标为 `C:\Python314\python.exe`。
- CORE-BENIGN-HOOK、CORE-FS-DENY、CORE-NET-DENY、CORE-NET-ALLOW 因 hook 未能启动而未检验其预期行为；CORE-TIMEOUT 未到超时路径；CORE-TREE-KILL 直接收到同一授权异常。CORE-AUDIT 缺少 `hook_invoked` 是级联：没有 hook 实际运行，该事件自然未产生；其余必需审计事件存在。
- `CORE-FAIL-CLOSED` PASS，验证不能完成 sandbox 授权时返回 `PLUGIN_HOOK_UNAVAILABLE` 并 fail-closed；本轮未发现 unsandboxed 执行。
- 10 项限定 PASS 为：Core 的生产装配、插件发现、状态往返、fail-closed；Wire 的 ping、插件列表、状态、错误信封、审计列表、shutdown。Wire 结果覆盖真实 Core 子进程及协议版本 `2.3`。

## 证据边界

- Core 的文件/网络隔离拒绝与允许语义、hook timeout、子进程树清理本轮均为**零证据**；不能由 10 项 PASS 推断这些安全语义通过。
- `icacls` 失败的具体错误码和底层成因未落盘，不能推断 ACL、完整性级别、安全软件或其它环境策略的具体根因。ZCode 记录的环境现象是系统级位置 `C:\Python314` 与对解释器路径设置 ACL 的产品假设不匹配；是否需要产品侧改进仍待后续 Task。
- 与 .NET TestHost 的 Win32 error 5 没有可证实共同根因：两条路径的对象和机制不同（`OpenProcess` 进程句柄 vs `icacls` 文件 DACL），不得建立同源或因果。
- suite 保留 `EXIT=1`、程序 `FAIL`，同时把 7 个失败登记为前置阻断，把 10 个真实 PASS 留作有限范围证据。此结果不映射到 AUDIT-01–14；逐项仍是 `BLOCKED-ORIGINAL-CHECKLIST-MISSING`，Release Gate 仍 `BLOCKED`。
- 前端/打包显式 SKIP；Legacy 前端、Rust desktop、npm-audit、packaged suite 不因此获得执行证据。
- 任何恢复 Core hook 检查的措施若触及 `src/**`、`tools/smoke/**` 或环境策略，超出当前 Task `allowed_paths`，须另开 Task 并由 ZCode 裁决。本轮不改 ACL/安全策略、不提权、不改 runner，也不重跑。
