# P02 进程级隔离候选：Windows AppContainer

状态：`PROPOSED / NOT_AUTHORIZED / NOT_TESTED`；本文件只记录设计候选，不修改 P02 Task/allowlist，不授权创建 profile、探测主机、运行 isolation smoke 或构建。

日期：2026-10-10（Asia/Shanghai）

## 背景与边界

P02 的 static hook/cache/递归 import/子进程写路径闭包无法由清单证明，P02 Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`。2026-10-10 用户裁决免去 Windows Sandbox Feature 查询、安装、启用、启动及 guest 验证，但没有豁免隔离和写入保护。

Windows AppContainer/LPAC 是 Windows 提供的 OS security token 与 ACL/capability 隔离边界，可限制文件、注册表、进程和网络访问；它不是 Windows Sandbox/Hyper-V VM，不能声称具备相同虚拟机边界。候选目的只是证明本机 PyInstaller build 及其 hook/import 子进程在系统级访问控制下受限于精确输入和 scratch 写入范围。

## 候选执行模型

1. Codex-only launcher 以独立 AppContainer profile 创建低权限进程，使用 `STARTUPINFOEX`/`PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES` 启动。默认不授予网络 capability；只按清单显式给予读工具链/输入和写 scratch 所需的最小 ACL。LPAC 可作为审查选项，但不预先承诺，因为兼容性及额外能力要求尚未实测。
2. 进程树覆盖 PyInstaller 主进程、`collect_submodules` isolated worker、hook/import 子进程及其后代。Microsoft 文档称 unpackaged AppContainer 进程使用 `CreateProcess` 时 child 通常继承 parent token；正式 smoke 仍须采集并验证每个相关进程的 `TokenIsAppContainer` 与 Package SID，不能只以 launcher 自身 token 证明整棵树隔离。
3. 对构建输入（源码 clone、Python/toolchain、依赖与本次实际执行的 hook 文件）给予只读访问；仅为本次新建、固定路径的 scratch clone/build/cache/target 目录给予写权限。把 `TEMP`、`TMP`、Python bytecode、PyInstaller、Torch、Hugging Face 等缓存变量明确重定向到 scratch；对未知/未映射路径 fail closed。
4. 以受保护 source/user-data/root 路径的 ACL 访问拒绝探针、scratch 内可写探针、全进程树 token 记录、测试前后受保护文件 manifest/hash、最终 cache/env 列表和完整 process tree 构成真实隔离证据。探针只尝试打开既有目标，不创建或改写受保护数据；build 仍需独立 Build Gate。
5. 如任一子进程不在 AppContainer 中、任一未登记路径可写、deny probe 未被操作系统拒绝、profile/ACL 不匹配或出现未知 cache 目录，smoke=`BLOCKED / FAIL`，不得运行 PyInstaller 或 Cargo/Tauri。

## 明确的未决范围

- `CreateAppContainerProfile` 创建 per-user/per-app profile；Windows 为其 profile 路径设置专属 ACL，并为容器重定向 `LOCALAPPDATA`、`TEMP`、`TMP` 到 profile 下的 `AC`/`Temp` 目录。profile 还包含 per-user/per-app registry storage。它们位于 P02 当前 scratch-only allowlist 之外。
- 因此该候选需要一个窄的新增 host-state scope：仅限本次运行唯一命名、确认不存在、可精确识别的 P02 AppContainer profile 及其私有 registry；不得给予 `%LOCALAPPDATA%`、整个用户目录或通用 temp 根的写权限。清理只可删除本次确认由任务创建的 profile；遇到已存在 profile 即阻塞并保留现场。
- 本 profile scope 超出当前 P02 Codex-only scratch boundary，当前用户授权不自动扩大它。本 proposal 的设计审查完成后，仍须由 Codex 给出精确 ACL/path/cleanup contract；是否接受该 profile scope 由用户决定。没有 scope 决定前不得创建 profile 或进行任何会在此路径写入的 smoke。
- 未证实 PyInstaller/Torch/Hugging Face 在实际环境中可在此 capability/ACL 集合内正常运行；没有运行主机探针或 build。兼容性、process descendants、registry/profile writes 和网络 deny 都仍是待验证项。

## 当前结论

此方向技术上值得进一步评审，不能据此清除 Hard Build Barrier。现有 P02 Gate 证据和 hook/cache audit 仍是当前事实；只有该设计经 DSH exact-head Review、profile scope 经用户明确决定、Codex-only preflight/smoke 获准并取得真实 OS deny/write boundary 证据后，Build Gate 才可能重新评估。

## Microsoft 一手资料

- [AppContainer isolation](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-isolation)：文件、注册表和网络访问可依最小授权控制；隔离进程可显式取得特定资源访问。
- [Launch an AppContainer](https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer)：`STARTUPINFOEX` 与 security capabilities 的启动流程；profile、`LOCALAPPDATA`/`TEMP`/`TMP` 路径和 LPAC 差异。
- [AppContainer for legacy apps](https://learn.microsoft.com/en-us/windows/win32/secauthz/appcontainer-for-legacy-applications-)：非打包 AppContainer 子进程通常继承 parent token；须在实际 process tree 中验证。
- [CreateAppContainerProfile](https://learn.microsoft.com/en-us/windows/win32/api/userenv/nf-userenv-createappcontainerprofile)：profile 为 per-user/per-app，包含 folders 与 registry storage；重复 profile 返回 `ERROR_ALREADY_EXISTS`。

## Review 请求

请 DeepSeek Harness 以只读方式审查本文件，重点回答：AppContainer/LPAC 是否能构成合适的 OS isolation candidate；profile 与 registry 写入是否已诚实暴露为 scope delta；子进程 token、文件/缓存 ACL、网络能力和 deny/write probes 的证据是否足以作为后续 smoke 设计；是否存在让此方案不值得进入 scope review 的技术缺口。结论只能评价设计候选，不得批准 P02 build、修改 Task/allowlist 或宣称 Gate PASS。
