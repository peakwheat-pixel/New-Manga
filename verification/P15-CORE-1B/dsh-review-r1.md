# P15-CORE-1B 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15-CORE-1B（设置面 Core 实现 B：G22 凭据面 + G23 Network CRUD/默认/解析，**不含** test 命令） |
| Owner | Codex（`/codex-dispatch` CLI，`danger-full-access`） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 实现 `6cf3c8209`；HEAD `075bcbad8`（Handoff + 证据收尾） |
| 基线 | `c27965911` |
| 结论 | **approved** |

## 1. 我**亲自复跑**

| 套件 | 我的实测 |
|---|---|
| `python -m pytest tests/core -q -p no:cacheprovider`（py312 venv） | **440 passed, 1 warning** ✓（1A 后基线 **420** → **+20** 新测试，零回归） |

（Owner 归档日志同为 **440 passed**；其 `pytest-core-first-attempt.log` 记录了 `1 failed, 436 passed`，**如实保留**且随后修复——正向证据纪律。）

## 2. 逐项验证

| # | 验证项 | 结果 |
|---|---|---|
| V1 | 范围 | **PASS**：4 个 `src/**`/`tests/core/**` 文件 + Handoff + **8 份证据**；**无越界**（未改契约/apps/Schema/依赖） |
| V2 | **范围排他（关键）** | **PASS**：契约 8 条 Network 命令中代码**只实现 7 条**——`settings_network_profiles_test` **未实现** ✓（属 1C）；G21/G24 命令未被重写 ✓ |
| V3 | **协议 minor（防重演）** | **PASS**：`_P15_PROTOCOL_MINOR = 7` ✓；并有专门测试 **`..._require_p15_minor_seven_and_test_command_stays_absent`** 同时锁定"凭据命令需 minor 7"与"1C 命令缺席" |
| V4 | **凭据命令的 WebView 暴露** | **PASS（附交接项）**：Core 的分发集合 `_P15_SETTINGS_COMMANDS` 含 `BindProfileCredential`/`ClearProfileCredential`——**这是正确的**（受信 Host 必须能调用）；**WebView 可达性由 Tauri host allowlist 决定**，Owner 已归档 `webview-route-scan.txt`：在 `apps/desktop/src-tauri/src` 扫描两条凭据命令与 1C 命令 → **零命中**（exit 1）✓。**须在 P15-HOST-1 显式验收**该二命令**仅 Host 可达**（见 §4） |
| V5 | 处置语义：Network | **PASS**：模式/endpoint 组合（HTTP/HTTPS/SOCKS5 必需且 scheme 相符；Direct/System 必须 null）、**拒绝内嵌凭据**、`verify_tls` 默认 true + `confirm_disable_tls_verification` 必填于关闭、`allow_proxy_failure_direct_fallback` 默认 false、**默认选择仅由专用命令写**、解析顺序 Provider→Global→System→Direct —— 均有对应测试（含 `default_and_resolver_precedence`、`delete_rejects_global_and_provider_references`、`delete_rejects_protected_run_snapshot_reference`） |
| V6 | 处置语义：凭据（红线） | **PASS**：**从不返回 `CredentialRef`**（`..._never_returns_reference`）；**替换失败保留旧绑定并清理新引用**（原子性）；**清除后不得解析到其他 Provider**（`..._does_not_resolve_to_another_provider`）；**代理失败默认不重试直连**（`..._does_not_retry_direct_by_default`）；代理凭据**按 Profile 作用域且无 Secret** |
| V7 | §9 封闭投影 | **PASS**：沿用 1A 的 `SettingsSurfaceError`（仅 category/phase/action/message_key 四字段） |
| V8 | 既有命令零变化 | **PASS**：改动为**新增**命令与集合成员；`settings_get`/`settings_update_section` 及 1A 的 G21/G24 语义未动；测试计数 407→420→**440** 全绿 |
| V9 | 证据 | **PASS**：8 份（含 `pytest-core.log`/`.exit-code.txt`/`.command.txt`/`.environment.txt`、首跑留档、`webview-route-scan.txt`、`resource-manifest.json`），可复现且如实 |

## 3. 结论：**approved**

1B 在 1A 的同一机制上实现了 G22/G23 的冻结命令面：**范围排他严格**（未越入 1C，也未重写 1A）、**协议 minor 直接取 7**（吸收了 1A 的集成期教训）、**安全红线逐条有反例测试**（内嵌凭据、TLS 确认、代理失败不直连、凭据不返回引用、原子替换、清除不换 Provider）、**WebView 暴露有专门扫描证据**。**我复跑 440 passed**，与 Owner 日志一致。

## 4. 交接项（**P15-HOST-1 必须显式验收**）

`BindProfileCredential` / `ClearProfileCredential` 在 **Core 侧必须可被受信 Host 调用**（正确），但**契约要求它们"不注册为 WebView 可调用命令"**。该禁令的落实点是 **Tauri host 的 allowlist/`generate_handler!`**，属 **P15-HOST-1** 范围。→ **P15-HOST-1 的 AC 必须包含**：这两条命令**仅**走受信 Host→Core 路由，**不得**出现在 `PRODUCTION_COMMANDS`/probe/AC1 的 WebView 面；并须有**测试或扫描证据**证明零 WebView 注册（可复用本次的 `webview-route-scan.txt` 方法）。

## 5. closeout 记录项

1. **pin 复算（RV-P15-04）**：源码/测试/证据 pin 由 Owner 在其工作树以 LF 计算 → closeout 须在**主仓库**按规范磁盘字节复算。
2. **DAG 效果**：1B 关闭 → 解除 **P15-CORE-1C** 的前置（同为 `core_service`/`core_assembly` 写范围 → 串行最后一环）→ closeout **同步释放 P15-CORE-1C**。
