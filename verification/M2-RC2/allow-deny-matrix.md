# M2-RC2 命令面授权/拒绝矩阵（RC2-AC1，F-03）

- 被审计面：`apps/desktop/src-tauri`（invoke handler、capability/ACL、CSP）+ Core 控制桥 wire（`host_bridge.py`）+ WebView 消费端（`client.ts`）。
- 边界层次（按 WebView 调用穿越顺序）：
  1. **Tauri ACL**（`capabilities/m2rc1-commands.json`，inlined plugin `m2rc1-commands`）：只授权 `main` 窗口调用声明的 7 个命令；其它窗口/来源在 ACL 层拒绝。
  2. **运行时注册 allowlist**（`main.rs::command_allowlist`，`generate_handler` 条件注册）：生产模式（无 `M2RC1_PROBE_OUT`）只注册 3 个生产命令；probe 模式额外注册 4 个 probe 命令。未注册的命令在"命令不存在"层面拒绝。
  3. **命令形状**（Rust 参数，编译期）：`issue_resource_url(resource_id, revision)` 无 TTL 参数；`register_catalog` 已从代码中删除。
  4. **Core wire 形状**（`core_bridge.rs::build_issue_params` + `host_bridge.py`）：issue 请求只含 `resource_id`/`revision_fingerprint`；`rel_path`/`scope_class` 参数为 typed 拒绝（`REF_MALFORMED`）。
  5. **Core/SQLite catalog authority**（`catalog_store.py`）：resource_id → (scope_class, rel_path) 只能由 loader/产品 Core 写入；写入时校验 scope class 与 rel-path gate；未编目的 id 在 issue 时 fail-closed（`RESOURCE_NOT_CATALOGED`）。
  6. **Core TTL 策略**（`service.py`）：`ttl_seconds` 只允许缩短（≤0 或 > 默认 300 s → `REF_MALFORMED`），滑动续期总是回到 ruled default。
- 测试证据：Rust `main.rs::tests`（allowlist 矩阵、wire 形状、真实 sidecar 拒绝）、pytest `test_catalog_authority.py`（17 项）、vitest `commandSurface.test.ts`（7 项矩阵）、E2E `run_e2e.py`（probe D-01..D-03 + interactive IP-1..IP-6/IA-1）。

## 命令矩阵（WebView → host）

| 命令 | 生产模式（无 probe env） | probe 模式（`M2RC1_PROBE_OUT`） | 拒绝层 | RC1→RC2 变化 |
|---|---|---|---|---|
| `issue_resource_url` | **ALLOW**（无 TTL 形状） | **ALLOW**（无 TTL 形状） | — | TTL 参数移除（RC1 有 `ttlOverride`） |
| `revoke_ref` | **ALLOW** | **ALLOW** | — | 不变 |
| `revoke_resource_refs` | **ALLOW** | **ALLOW** | — | 不变 |
| `probe_config` | DENY（未注册） | ALLOW | 运行时 allowlist | RC1 生产也注册 → 收敛 |
| `probe_write_results` | DENY（未注册） | ALLOW（仅写 `M2RC1_PROBE_OUT` 指向的证据文件） | 运行时 allowlist | 同上 |
| `probe_exit` | DENY（未注册） | ALLOW | 运行时 allowlist | 同上；interactive 页不再调用它 |
| `probe_issue_url`（新） | DENY（未注册） | ALLOW（显式 TTL，仍受 Core ≤default 限制） | 运行时 allowlist + Core | RC1 的 TTL 注入面的 probe 专用替代 |
| `register_catalog` | **DENY（任何模式；代码已删除）** | **DENY（代码已删除）** | 编译期（命令不存在） | **RC1 全模式注册 → RC2 全模式移除** |

## 参数注入面矩阵

| 注入尝试 | 入口 | 结果 | 证据 |
|---|---|---|---|
| OS rel_path（合法值） | `register_catalog` | 不可达：命令已删除 | `register_catalog_exists_on_no_surface`（Rust）；IP-1/D-01（E2E）；vitest 矩阵 |
| OS rel_path（traversal） | bridge issue `params.rel_path` | `REF_MALFORMED`（Core-owned 参数拒绝） | `test_issue_with_rel_path_param_refused`、`test_issue_with_traversal_rel_path_param_refused` |
| `scope_class: user-source` | bridge issue `params.scope_class` | `REF_MALFORMED`；store 写入层 `REF_SCOPE_DENIED` | `test_issue_with_scope_class_param_refused`、`test_user_source_scope_refused_at_write` |
| 未编目 resource_id | bridge issue | `RESOURCE_NOT_CATALOGED`（fail-closed；空 catalog 存储时全部拒绝但 ping/shutdown 仍响应） | `test_issue_unknown_resource_fail_closed`、`test_fail_closed_without_catalog_source`、Rust `real_core_sidecar_denies_uncataloged_and_extended_ttl` |
| 任意 TTL（延长） | 生产 issue 形状 | 不可达：命令无 TTL 参数；E2E IP-6/D-02 证明 `ttlOverride` 键被忽略后引用仍可服务 | `issue_wire_never_carries_path_or_ttl`（Rust）；IP-6/D-02（E2E） |
| 任意 TTL（probe 命令） | `probe_issue_url`（仅 probe 模式） | TTL ≤ 0 或 > 默认 300 s → `REF_MALFORMED`（Core service 层） | `test_issue_with_ttl_above_default_refused` 等 4 项；Rust 真实 sidecar 999999 s 拒绝 |
| 伪造 catalog 行 | catalog store | 只能经 loader/产品 Core 写入；`user-source` scope 与 traversal rel_path 写入即拒绝 | `TestCatalogStoreValidation`（5 项） |

## Core wire（host ⇄ sidecar）变化摘要

- RC1 issue：`{resource_id, revision_fingerprint, rel_path, scope_class?, ttl_seconds?}`——host 携带路径。
- RC2 issue：`{resource_id, revision_fingerprint[, ttl_seconds (probe only)]}`——路径由 Core 从 SQLite catalog 解析；`rel_path`/`scope_class` 出现即 `REF_MALFORMED`。
- 该变化是 F-03"由 Python Core/SQLite 持有 catalog authority"的直接实现；Contract 1.1 §10.1 T5.2 的信任边界（host 为可信层、拿到 issue-time facts）不变。

## Interactive（生产模式）E2E 判定协议

生产模式 WebView 无 `probe_write_results`（无写通道）、无 `probe_exit`（无退出命令），`window.close()` 在 WebView2 默认被脚本策略阻止，且本机栈上无论 Tauri 的 `window.title()` 还是 Win32 窗口标题都不跟随 `document.title`（均有实测记录）。矩阵结果**按设计无法离开页面**——这正是收敛面的直接后果。因此 interactive 阶段的 gate 建立在外部可观察事实之上：

- **allowlist 自报对照**：host 启动时向 stderr 打印 `[m2rc2-allowlist] <mode>:<commands>`（来源与条件注册同一函数 `command_allowlist`）。runner 在两个阶段分别对照：production 必须恰好为 `issue_resource_url, revoke_ref, revoke_resource_refs`；probe 必须恰好再加 4 个 probe 命令。
- **存活观察（IP-4 的外部证据）**：进程在整个观察窗内存活 = WebView 无法触发退出。
- **结果文件缺席（IP-3 的外部证据）**：interactive 阶段不产生 probe 结果文件。
- **IP-1/IP-2/IP-5/IP-6 的直接断言**由以下层共同承载：Rust 编译期（命令不存在/无参数形状）、probe 阶段真实 WebView 的 D-01（register_catalog invoke 被拒）与 D-02（ttlOverride 惰性）、vitest 客户端矩阵、pytest Core 拒绝矩阵。
- 页面内置的 IP/IA 矩阵保留为**页面自检与屏幕可见的回归指示**，不作为 gate 通道。

## 诚实边界

- 本矩阵描述的是本切片实现并测试的边界；**不构成产品级安全声明**（S1-B3/B8 仍 NOT_RUN）。
- capability/ACL 授权的是 `main` 窗口（当前单窗口产品形态）；多窗口/远程内容面属产品化后续。
- probe 模式命令面是为证据 runner 保留的特权面：它依赖主机环境变量（`M2RC1_PROBE_OUT`），不是 WebView 可切换的状态。
