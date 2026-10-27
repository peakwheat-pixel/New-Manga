# CREDENTIAL-PORT-1 报告：Host 凭据管理器端口（解除 2 条 BLOCKED）

- Task: `doc/tasks/CREDENTIAL-PORT-1.md`（team task-43）；Branch/Worktree: `task/CREDENTIAL-PORT-1` /
  `G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1`
- Base: 卡面 `e30149258`；按 Lead 指示基于当前 HEAD **`e6c2db84f`** 开分支（含 NS-WIRE-B2 的 64/2）。
- 未 push；未改 Python Core 语义/协议/旧壳；未碰真实用户数据；**secret 未写入任何日志/DB/证据/测试快照**。

## 0. 结论

| AC | 判定 | 要点 |
|---|---|---|
| AC1 端口设计 | **MET** | `ICredentialStore`（Exists/Store/Read/Delete/Enumerate）+ `WindowsCredentialStore`（advapi32 `CredReadW/CredWriteW/CredDeleteW/CredEnumerateW`，`CRED_TYPE_GENERIC` + `PERSIST_LOCAL_MACHINE` + UTF-16LE，与冻结 Core 的 `infrastructure.credentials.windows` 字节兼容）+ `ICoreCredentialBridge`/`CoreCredentialBridge`（Bind/Clear minor 7）；两段式协议见 §1 |
| AC2 接线 | **MET** | `credential_put`：校验 target/intent/secret → Core 侧 conflict 检查 → 铸造 `NewManga/{provider\|proxy}/{owner}/{32hex}` ref（与 Core `make_credential_ref` 同格式）→ 写 OS vault → `BindProfileCredential`；**失败必删 vault 条目（无孤儿）**。`credential_clear`：`ClearProfileCredential`（Core 清 ref 并删 vault）→ Host 再按前缀清扫残留（`orphans_removed` 证据）。两条均 `HostLocal` IMPLEMENTED，失败全部 typed |
| AC3 安全 | **MET** | secret 仅存在于 App→Host 命令 payload 与 OS vault；Core 只拿 ref；secret 长度上限 4096；错误码/证据不含 secret（evidence 用 `owner_hash` 而非 ref）；单测+集成+verification 目录扫描均无 marker secret；Host 日志不含 secret |
| AC4 验证 | **MET** | 7 个新测试：6 个 fake store/bridge 单测 + 1 个**真实 sidecar + 真实 Windows Credential Manager** 全链（put→vault 读取验证→Core 绑定→列表 configured→clear→vault 空→列表 missing→conflict/not-found typed→泄漏扫描）；证据 `evidence/credential-port.json` |
| AC5 门禁 | **MET** | test.ps1 **189/189**；pytest **4F/2771P/9S**（3 个既有 flaky + 1 个并发负载 flake，单独重跑 PASS → 0 新增）；`--check` PASS；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff |

## 1. AC1 两段式协议（与旧 Tauri `settings_bridge.rs:288-350` 对齐）

```
put(target, intent, secret):
  Host: target ∈ {provider_api/profile_id, proxy_auth/network_profile_id}; intent ∈ {create, replace}
  Host: Core settings_*_profiles_list → credential_state
        (intent=create 且已配置) 或 (intent=replace 且未配置) → typed CREDENTIAL_CONFLICT
  Host: ref = NewManga/{provider|proxy}/{owner}/{16 random bytes hex}   // 与 Core make_credential_ref 同前缀
  Host: WindowsCredentialStore.Store(ref, secret)                        // CRED_TYPE_GENERIC / LOCAL_MACHINE / UTF-16LE
  Host→Core: BindProfileCredential { target, credential_ref: ref }       // Core 校验 ref 归属 + has_credential
  失败：Host 删除 ref 的 vault 条目（无孤儿）→ typed 错误
  成功：{"state":"configured"}

clear(target):
  Host→Core: ClearProfileCredential { target }   // Core 清 profile.credential_ref 并删除 vault 条目
  Host: enumerate NewManga/{kind}/{owner}/ 并删除残留（defense in depth）
  成功：{"state":"missing"}
```

- Host 从不把 secret 发给 Core；Core 的 provider 运行时通过自己的 `WindowsCredentialStore` 按 ref 解析（同一 OS vault）。
- `ICredentialStore` 的 `Read`/`Enumerate` 仅给测试/取证用（生产路径只 Store/Delete）。

## 2. AC2/AC3 安全核对

| 检查 | 结果 |
|---|---|
| secret 出现在 host 日志 | **无**（集成测试扫描 `options.LogDirectory` 全部文件） |
| secret 出现在 credentials 证据 | **无**（evidence 仅 operation/target_kind/owner_hash/state/orphans_removed） |
| secret 出现在 verification/ | **无**（提交前全目录扫描，0 命中） |
| 失败留孤儿 | 单测：bind 抛错后 fake vault 空；集成：unknown profile 后前缀 0 条 |
| 错误泄露 secret | typed code 列表（INVALID_ARGUMENTS/CREDENTIAL_CONFLICT/CREDENTIAL_NOT_FOUND/CREDENTIAL_STORE_UNAVAILABLE/CREDENTIAL_BIND_FAILED/CREDENTIAL_CLEAR_FAILED），消息不含 payload |
| Core 拿到 secret | **否**（只收到 `credential_ref`；wire 帧由 Core bind 回显 state） |
| 未放宽其他通道 | 无改动（TileChannel/资源通道/HostBridge 未动） |

## 3. 代码改动

| 文件 | 改动 |
|---|---|
| `src/NewManga.Host/Credentials/ICredentialStore.cs`（新） | 端口抽象 + `CredentialTarget`（wire/`VaultPrefix` 与 Core 完全一致）+ typed 异常 |
| `src/NewManga.Host/Credentials/WindowsCredentialStore.cs`（新） | Win32 凭据管理器实现（读/写/删/枚举；缓冲清零；错误码映射） |
| `src/NewManga.Host/Credentials/CoreCredentialBridge.cs`（新） | Core 侧 bridge：profiles list（conflict 检查）+ `BindProfileCredential`/`ClearProfileCredential`（minor 7）+ Core 错误 → typed 映射 |
| `src/NewManga.Host/HostCredentialCoordinator.cs`（新） | put/clear 编排、ref 铸造、失败清理、证据 |
| `src/NewManga.Host/HostRuntime.cs` | 构造 credential port（不依赖 host-control session）；dispatcher 合成 HostLocal handler（credential→Grants） |
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 2 条命令从 NOT_SUPPORTED/BLOCKED → HostLocal IMPLEMENTED；66/0；删除 BLOCKED 理由表 |
| `tests/NewManga.Host.Tests/CredentialPortTests.cs`（新） | 6 单测 + 1 真实全链 |
| `tests/NewManga.CoreClient.Tests/Commands/{CommandParityContractTests,CommandIntegrationTests,CommandWiringB1Tests,CommandWiringB2Tests}.cs` | 计数 64/2 → 66/0；B2 的 BLOCKED 断言改为 HostLocal IMPLEMENTED |

## 4. AC4 证据

- 单测（fake）：ref 格式/绑定、intent 冲突、bind 失败清理、clear 清扫、非法参数、前缀与 Core 一致、secret 不泄漏。
- 集成（真实）：`[HostSidecarFact]` + 冻结 sidecar（`FINAL-VALIDATION-1/sidecar-copy`）+ 真实 Windows Credential Manager：
  `put` → vault 1 条且可读回 marker（证明 UTF-16LE 字节兼容）→ Core 列表 `configured` → 重复 create `CREDENTIAL_CONFLICT`
  → `clear` → vault 0 条 + Core 列表 `missing` → unknown profile `CREDENTIAL_NOT_FOUND` 且无孤儿。
- 证据：`verification/CREDENTIAL-PORT-1/evidence/credential-port.json`（`put_state=configured`、`clear_state=missing`、
  `vault_ref_format_matched=true`、`vault_entries_after_clear=true`、`secret_leak_scan_clean=true`）。

## 5. AC5 回归

| 门 | 结果 |
|---|---|
| `scripts/test.ps1` | **189/189 passed, 0 skipped**（CoreClient 61 / Host 53 / App 75；较基线 182 新增 7 = 本 Task 测试） |
| pytest | **4F / 2771P / 9S**：3 个既有 flaky（detection_manga_real ×2、workbench pause）+ `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（并发重负载下进程 kill 计时 flake；单独重跑 **PASS 4.21s**）→ **0 新增失败** |
| `extract-command-surface.py --check` | **PASS**（66 命令零漂移） |
| registry | **66 IMPLEMENTED / 0 NOT_SUPPORTED** |
| `check.ps1 -TaskPath` | PASS |

## 6. 遗留 / NOT_RUN

1. **App UI 未接线**：Avalonia 设置页尚无凭据输入/清除入口；本 Task 交付命令面（HostLocal）+ 端口。App 交互输入/安全输入框需独立 UI Task（旧壳用 CredUI 对话框；新 Host 由 App 收集 secret 后走 `credential_put`）。
2. proxy_auth（网络代理口令）走同一端口与 Core 目标，已由单测覆盖；真实集成用 provider_api 链（网络 profile 创建+代理绑定属另一批）；
3. identity/翻译等既有遗留不变；`doc/STATUS.md`/PLAN/LEDGER 指针由 DSH 收口。
4. 需独立 Review（Owner 不得自审）；并发 EXPORT-E2E-CLOSE-1 只改验证脚本，无文件冲突。
