# P15-CORE-1C 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15-CORE-1C（`settings_network_profiles_test` 六阶段连接测试；rev 2.7 / 用户裁决 A1） |
| Owner | Codex（`/codex-dispatch` CLI，`danger-full-access`） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 实现 `52b0974ad`；HEAD `faa37493d`（Handoff + 验证 + 证据） |
| 基线 | `5f5431b87` |
| 结论 | **approved** |

## 1. 我**亲自复跑**

| 套件 | 我的实测 |
|---|---|
| `python -m pytest tests/core -q -p no:cacheprovider`（py312 venv） | **508 passed, 1 warning** ✓（1B 后基线 **440** → **+68**，零回归；增量来自**参数化反例**而非宽松断言） |

## 2. 逐项验证

| # | 验证项 | 结果 |
|---|---|---|
| V1 | 范围 | **PASS**：`src/infrastructure/network/profile_test.py`（新）、`settings_commands.py`、`core_service.py`、`core_assembly.py`、测试、Task/Handoff + **10 份证据**；**无越界**（未改契约/apps/Schema/依赖） |
| V2 | **A1 红线（本次核心）** | **PASS**：`provider_profile_id` 列入**必需字段集**（L260）、`_nonempty` 拒绝空/缺失（L264）、必须解析到 Profile（L267）；**并有专门测试** `test_network_profile_test_invalid_or_unresolved_target_is_invalid_request`（参数化 field/value）与 **`test_network_profile_test_missing_target_never_returns_passed`**（参数化 payload）——**"无目标却报 passed"的假阳性被测试钉死** |
| V3 | **唯一目标 / 不回退** | **PASS**：目标恒为 Provider endpoint；`test_network_profile_test_proxy_failure_never_attempts_direct` 与 `..._proxy_failure_stops_every_mode`（参数化 mode）覆盖"代理失败**绝不尝试直连**"；`direct_fallback_used` 恒 false |
| V4 | **六阶段判定矩阵** | **PASS**：`test_network_profile_test_mode_and_not_applicable_matrix`（参数化）覆盖 5 模式判定；`..._system_proxy_route_runs_proxy_stage`、`test_network_probe_system_direct_is_not_applicable_without_connecting`（**不连接**即 not_applicable）、`test_network_probe_rejects_unoffered_socks5_authentication`、`test_network_probe_uses_the_selected_proxy_and_classifies_its_own_handshake` |
| V5 | **失败语义与脱敏** | **PASS**：`test_network_profile_test_failure_stops_later_stages_and_sanitizes_result`——失败阶段保留、后续 `not_run/upstream_stage_failed`、**结果脱敏**；HTTP 阶段 `test_network_profile_test_http_probe_uses_same_authority_and_provider_auth_without_leaking_secret`（**同 authority** + 不泄露 Secret）与 `..._does_not_follow_cross_authority_redirect`（**不跨 authority 重定向**）；ProviderAuth `..._missing_or_rejected_fails_without_retry`（**不重试/不切换**） |
| V6 | **§9 封闭投影** | **PASS**：沿用 `SettingsSurfaceError` 四字段（category/phase/action/message_key），失败只作稳定类别/阶段/动作 |
| V7 | **协议 minor** | **PASS**：`_P15_PROTOCOL_MINOR = 7` 未改回；沿用 1A/1B 同一分发机制 |
| V8 | 不越界改 1A/1B | **PASS**：改动为**新增** test 命令与探针模块；1A/1B 命令语义未动；1A/1B 的既有测试仍全绿（508 含全部） |
| V9 | **测试替身与外连限制（关键诚实项）** | **PASS（范例级）**：Handoff L49/L77 **明确声明**"**测试没有真实 DNS/TCP/TLS/HTTP/ProviderAuth 外连**；生产探测能力只由标准库调用实现，**本次没有真实网络连通性验证**"；并有专门测试 `test_network_profile_test_real_probe_pipeline_is_stubbed_and_secret_free`（**显式 stub 真实探针流水线**） |
| V10 | 实现限制如实 | **PASS**：Handoff 登记"仅支持 `openai-compatible` / `openai-compatible-vision` 等 adapter；unsupported adapter 在 **HTTP 阶段**报安全错误"——**未夸大** |
| V11 | 证据 | **PASS**：10 份（含**聚焦**与**全量**两份 pytest 日志 + command/environment/exit-code + `canonical-hash-verification.txt` + 资源清单），可复现 |

## 3. 结论：**approved**

1C 精确实现了契约 §5.2（rev 2.7 / A1）的全部硬边界：**参数必填 + 不可解析即 `INVALID_REQUEST`**、**无目标绝不报 `passed`**（两条专门测试钉死）、唯一目标为 Provider endpoint、5 模式 × 6 阶段判定、失败即停并脱敏、不跨 authority 重定向、ProviderAuth 不重试、§9 封闭投影；**测试全部使用可注入替身**并**如实声明未做真实连通性验证**——这正是我提示中要求的诚实项。**我复跑 508 passed**，零回归。

## 4. closeout 记录项

1. **pin 复算（RV-P15-04）**：Owner pin 以其工作树 LF 计算 → closeout 须在**主仓库**按规范磁盘字节复算。
2. **DAG 效果**：1C 关闭 → **P15 设置面的 Core 链（1A/1B/1C + FU1 契约）全部完成** → 下一环为 **P15-HOST-1**（Tauri host 侧注册 **17 条**设置命令并与 Core 2.7 配对）。
3. **必须传导给 P15-HOST-1 的验收项**：`BindProfileCredential`/`ClearProfileCredential` 在 Core 侧可被受信 Host 调用（正确），但**契约要求其不注册为 WebView 可调用** → host 侧须证明"**仅 Host 可达**"（测试或扫描证据）。
