# CREDENTIAL-PORT-1 Handoff（Host 凭据管理器端口）

- Task: `doc/tasks/CREDENTIAL-PORT-1.md`（team task-43）
- Branch: `task/CREDENTIAL-PORT-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-PORT-1`
- Base: 卡面 `e30149258`；实际基于 Lead 指定的当前 HEAD **`e6c2db84f`**
- Delivery head: `e414673a3`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改 Python Core 语义/协议/旧壳；**secret 未写入日志/DB/测试快照/提交**。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 端口设计 | **MET** | `ICredentialStore` + `WindowsCredentialStore`（CredRead/Write/Delete/Enumerate，GENERIC/LOCAL_MACHINE/UTF-16LE，与核心实现字节兼容）+ `ICoreCredentialBridge`；两段式协议见 REPORT §1 |
| AC2 接线 | **MET** | `credential_put`/`credential_clear` 由 BLOCKED → **HostLocal IMPLEMENTED**（66/0）；put 写 vault→BindProfileCredential，失败删条目无孤儿；clear 走 Core 清除+Host 前缀清扫；失败 typed |
| AC3 安全 | **MET** | secret 只走 App→Host→OS vault；Core 只拿 ref；证据用 owner_hash；日志/证据/verification 扫描无 secret；secret ≤4096；错误 info 无 secret |
| AC4 验证 | **MET** | 7 新测试（6 fake 单测 + 1 真实 sidecar+真实 Windows Credential Manager 全链）；证据 `evidence/credential-port.json` |
| AC5 门禁 | **MET** | test.ps1 **189/189**；pytest **4F/2771P/9S**（0 新增，sandbox flake 单独重跑 PASS）；`--check` PASS；check.ps1 PASS；pin；本 Handoff |

## 2. 代码改动

| 文件 | 改动 |
|---|---|
| `src/NewManga.Host/Credentials/ICredentialStore.cs`（新） | 端口 + `CredentialTarget`（wire 形状/`NewManga/<kind>/<owner>` 前缀与 Core 一致）+ typed 异常 |
| `src/NewManga.Host/Credentials/WindowsCredentialStore.cs`（新） | advapi32 P/Invoke（read/write/delete/enumerate；缓冲清零；win32 错误映射） |
| `src/NewManga.Host/Credentials/CoreCredentialBridge.cs`（新） | profiles list（create/replace 冲突判定）+ Bind/Clear（minor 7）+ Core 错误→typed |
| `src/NewManga.Host/HostCredentialCoordinator.cs`（新） | put/clear 编排、ref 铸造、失败清理、`<log>/credentials/*.json` 证据 |
| `src/NewManga.Host/HostRuntime.cs` | credential port 构造（不依赖 host-control session）+ HostLocal handler 合成 |
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 2 条 → HostLocal IMPLEMENTED（66/0），删除 BLOCKED 理由表 |
| `tests/NewManga.Host.Tests/CredentialPortTests.cs`（新） | 6 单测 + 1 真实全链 |
| `tests/NewManga.CoreClient.Tests/Commands/...` | 计数 64/2 → 66/0；B2 BLOCKED 断言改为 HostLocal IMPLEMENTED |

未改：`src/**`（Python）、Host wire 协议、旧壳；未覆盖任何既有产物。

## 3. 安全设计要点（Record Decision 摘要）

1. **Core 零 secret**：Core 只收到 `credential_ref`；凭证解析仍由 Core 自己的 `WindowsCredentialStore` 完成。
2. **ref 与 Core 同构**：`NewManga/{provider|proxy}/{owner}/{32 lowercase hex}`，满足 Core `_credential_ref_owned` 校验（旧 Tauri 同格式）。
3. **无孤儿**：put 在 `BindProfileCredential` 失败时删除刚写入的 vault 条目；clear 在 Core 清除后再按前缀清扫。
4. **证据最小化**：只记 operation/target_kind/SHA-256(owner) 前 16 hex/state/orphans_removed；不记 ref、不记 secret。
5. **typed 失败**：INVALID_ARGUMENTS、CREDENTIAL_CONFLICT、CREDENTIAL_NOT_FOUND、CREDENTIAL_STORE_UNAVAILABLE、CREDENTIAL_BIND_FAILED、CREDENTIAL_CLEAR_FAILED。

## 4. 复现

```powershell
# 7 个测试（6 单测 + 1 真实 sidecar/vault）
$env:NEWMANGA_CORECLIENT_SIDECAR_DIR='G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\sidecar-copy'
$env:NEWMANGA_EVIDENCE_DIR='...\task-envs\CREDENTIAL-PORT-1\evidence'
dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Debug `
  --filter "FullyQualifiedName~CredentialPortTests"
# 全仓门禁
pwsh -File apps/desktop-avalonia/scripts/test.ps1 -SidecarDirectory <copy> -EvidenceDirectory <private>
```

集成测试会在当前用户 Windows Credential Manager 写入随机 marker（`NewManga/provider/<临时 profile>/…`），
结束时删除并清理临时数据根；marker 不是真实凭据。

## 5. 遗留 / NOT_RUN

1. **App UI 未接线**：Avalonia 设置页尚无凭据输入/清除控件（本 Task 交付命令面+端口；旧壳是 CredUI 对话框）。
   建议下一个 UI Task：安全输入框/掩码 + 调用 `credential_put`/`credential_clear`，不落明文。
2. proxy_auth 分支仅单测覆盖（同端口/同 Core 目标）；真实集成用 provider_api 链。
3. 旧 BLOCKED 理由表已删除；历史 NS-WIRE-B2 证据保持不变（其集成计数在本次测试更新后为 66/0，已在 REPORT 记录）。
4. `doc/STATUS.md`/PLAN/LEDGER 指针由 DSH 收口。
5. 需独立 Review（Owner 不得自审）；并发 EXPORT-E2E-CLOSE-1 只改验证脚本，无冲突。
