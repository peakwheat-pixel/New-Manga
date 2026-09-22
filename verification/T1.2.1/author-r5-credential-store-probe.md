# T1.2.1 R5 Author Probe — B-003 production credential-store injection

- 作者：ZCode；日期：2026-09-22
- 授权：R5 指令（"基于 39dbbf7，仅修改 src/bootstrap/app.py、必要的装配测试、verification/T1.2.1/** 和 Handoff。将现有 credential store 注入生产 StdlibTransport，保留 best-effort None fallback，补充 assembly-level test 与本地 authenticated-proxy probe"）
- 基线：39dbbf7（R4 代码 HEAD）；本验证跑于 R5 工作区（delivery HEAD 见 Handoff §10）
- 环境：Windows 10.0.26200 x64；venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（Python 3.12）；shell Git Bash

## 1. 修改面（src/bootstrap/app.py，三处）

1. **新增 `_credential_store()`**：try-import `WindowsCredentialStore` 并构造；任何异常（模块缺失、非 win32、advapi32 加载失败、构造失败）→ `None`。这是 B-003 要求的 best-effort None fallback 的唯一定义点。
2. **`_credential_resolver(store=None)` 重构**：复用 `_credential_store()`（或接受装配传入的同一实例），行为与 R4 前等价（`resolve_credential(ref).reveal()`，逐次异常吞掉返回 None）。
3. **装配点注入**：`credential_store = _credential_store()` 局部变量同时喂给：
   - `transport = StdlibTransport(credential_store=credential_store)`（B-003 主目标）；
   - `_credential_resolver(credential_store)`（providers 用同一 vault）;
   - `SettingsViewModel(credential_store=credential_store)`（顺带统一：原先此处是独立的 `try/except ImportError` 构造点，构造失败（非 ImportError）会让整个装配崩溃，与 best-effort 语义不一致——见 §4）。
4. **`AppServices` 新增尾部字段 `transport: StdlibTransport | None = None`**（同 R1 `settings_vm` 先例）：让装配结果可观测（装配测试与 probe 的观察点）；headless 手工构造不受影响。

未改动：ports、Schema、依赖、QML、`infrastructure/transport/stdlib.py`（`credential_store` 参数与 `_proxy_password` 消费点均为既有代码，tests/network 已覆盖）。

## 2. Assembly-level tests（tests/core/test_transport_credential_assembly.py，4 项全绿）

```
$ PYTHONPATH=src python -m pytest tests/core/test_transport_credential_assembly.py -q
....  [100%]
4 passed in 0.83s
```

- `test_assembled_transport_carries_the_production_credential_store` — 生产装配后 `services.transport` 是 `StdlibTransport` 且 `_credentials` 是 `WindowsCredentialStore` 实例。**修复前红**：`AppServices` 无 `transport` 字段（AttributeError）。
- `test_transport_still_assembles_when_the_vault_cannot_be_constructed` — monkeypatch vault 构造抛 RuntimeError → `_credential_store()` 返回 None，装配仍成功，`transport._credentials is None`。**修复前红**：SettingsViewModel 的旧构造点只捕 `ImportError`，RuntimeError 使装配崩溃（见 §4）。
- `test_credential_store_returns_none_when_the_module_cannot_import` — `sys.modules` 置 None（import 失败）→ None。
- `test_credential_resolver_shares_the_assembly_store` — resolver 与装配共享同一 store（真 vault roundtrip：store → resolve == 原文）；构造失败时返回 None（providers 报 MISSING_CREDENTIAL 而非启动失败）。

fail-closed 对照面（既有，未改）：`tests/network/test_transport_local.py::test_missing_proxy_credential_is_config_error_not_network` —— 无 store/凭据缺失时 transport 抛 `MissingCredentialError`，不静默直连。

## 3. Authenticated-proxy probe（全生产链，真 vault）

脚本：`G:/CODEX/New Manga.task-envs/T1.1.1-work/b003_probe.py`（临时，不入库）。
链路：`assemble_services` → 真 `WindowsCredentialStore` 写随机 ref 凭据 → 本地 `ControlledProxyServer(mode="forward", username, password)` + `LocalTargetServer` → 持久化 `pipeline_defaults` 行（provider profile → network profile(mode=http, credential_ref) + `{"translate": PROFILE_ID}` 绑定）→ **二次 `assemble_services`** → `registry.resolve("translation", PROFILE_ID)`（R3 投影路径）→ provider 的生产 client `complete()`。

```
$ python b003_probe.py
[1] assembled transport carries WindowsCredentialStore
[1] settings VM shares the same vault: True
[2] wrote proxy credential to the real vault: NewManga/proxy/b003-probe-<rand>
[3] target=http://127.0.0.1:1510/v1/chat/completions
[3] proxy=http://127.0.0.1:1611 (forward, basic auth)
[4] persisted pipeline_defaults row (profile + network + binding)
[5] re-assembled; second transport also carries the real vault
[6] registry resolved profile 'b003-probe-profile' -> slot network_profile='b003-proxy'
[7] complete() raised (recorded): ProviderInvalidOutput: PROVIDER_INVALID_OUTPUT:
    provider response is not an OpenAI-compatible completion: KeyError('choices')
[8] proxy forwarded with EXACT expected Proxy-Authorization
[8] target saw: GET /v1/chat/completions
PROBE PASS: production transport authenticated the proxy from the real Windows vault (B-003 closed).
[cleanup] vault credential NewManga/proxy/b003-probe-<rand> deleted: True
```

- **决定性证据 [8]**：`proxy.forward_auth_headers == ["Basic base64(user:password)"]` 且 `auth_failures == 0` —— 密码只存在于真 Windows Credential Manager（随机 ref，finally 删除），生产 `StdlibTransport` 在 send 时经 `_proxy_password → resolve_credential` 解出并构造认证头。401/407 凭据从不落 settings JSON。
- [7] 的 `ProviderInvalidOutput` 是预期噪音：`LocalTargetServer` 返回非 chat-completion JSON；`_raise_for_status` 已通过（200），认证与转发链路完整。证据点在 [8] 与 target 收到的请求。
- `allow_proxy_failure_direct_fallback=False`：代理认证失败不可能被静默降级为直连。
- 脱敏：输出仅含随机 ref 与端口；凭据值（`probe-pass-<rand>`）不出现在任何日志，probe 结束即从 vault 删除。

## 4. 顺带修正：装配内重复 vault 构造点

修改前 `assemble_services` 内有两处独立 vault 构造：transport/providers 用 R4 前的 `_credential_resolver()`（内联构造，`except Exception`），SettingsViewModel 用另一段 `try/except ImportError`（app.py 845-849）。后者在 vault **构造**失败（如 advapi32 损坏，非 ImportError）时让整个装配崩溃，违反 best-effort 语义。R5 统一收口为单一 `_credential_store()`：一次构造、一个 fallback 语义、三个消费者共享同一实例（probe [1] 断言 `settings_vm._credentials is transport._credentials`）。该段位于授权文件 src/bootstrap/app.py 内，未扩产品范围。

## 5. 修复前后行为对照

| 场景 | 修复前（39dbbf7） | 修复后（R5） |
| --- | --- | --- |
| 带 credential_ref 的网络 profile + 已装配 transport | `_proxy_password` 抛 `MissingCredentialError`（"no credential store was provided"），代理认证不可能成功 | 从共享 vault 解出密码，Proxy-Authorization 正确（probe [8]） |
| vault 打开失败（非 ImportError） | 装配崩溃（SettingsViewModel 构造点只捕 ImportError） | `_credential_store()` → None，装配成功；provider 侧报 MISSING_CREDENTIAL、transport 侧该 profile 报 MissingCredentialError（fail-closed 逐请求） |
| providers 的 API-key resolver | 独立构造 vault | 同一实例（少一次构造，语义单一） |
