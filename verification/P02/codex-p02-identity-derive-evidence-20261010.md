# P02：原始 SID Derive 命令结果留证

记录时间：2026-10-10。本文把此前已完成的只读 PowerShell 命令结果从 Codex 会话记录转存为可审查项目证据；本次没有重跑 OS/API。

## 来源与调用

- Codex thread=`01a1248e-52cb-7ab2-97c4-4804958180f9`。
- 已完成 command execution item=`exec-32c3f8d1-ad76-4fca-8649-f0b13f73f7c3`，turn=`01a12662-d7c5-7ab2-adb7-c55d8ac74766`。
- 宿主进程为 PowerShell 7；通过 `userenv.dll` P/Invoke 调用 `DeriveAppContainerSidFromAppContainerName`，参数为 moniker `NewManga-P02-LPAC-20261010-cddff584`。命令同时记录当前 Windows 身份、进程路径及 PID，并用 `FreeSid` 释放 API 分配的 SID。
- 命令状态=`completed`，exit code=`0`。SID 派生不创建 profile，亦不证明 profile 或 registry 存在/缺失。

## 逐字保留的 stdout

```json
{"CurrentIdentity":"HOME-MY\\49745","CurrentUserSID":"S-1-5-21-2196946971-914346751-4210154634-1001","IsAuthenticated":true,"IsSystem":false,"IsAdministrator":false,"Moniker":"NewManga-P02-LPAC-20261010-cddff584","DeriveHRESULT":"0x00000000","AppContainerSID":"S-1-15-2-834207331-3580931408-3204344528-2661602853-1083380287-3953930862-2134818854","ProcessId":19360,"ProcessImage":"C:\\Program Files\\PowerShell\\7\\pwsh.exe"}
```

## 身份裁定

唯一与该完成命令 stdout 一致的 AppContainer SID 为：

`S-1-15-2-834207331-3580931408-3204344528-2661602853-1083380287-3953930862-2134818854`

`...2661600285...` 是 manifest r1 的转录错误，不是另一次 API 结果。r1 原文保留供审计；r2 已更正并引用本文。执行时仍须重新检查当前调用者、moniker 与新派生 SID，且以 `EqualSid` 验证 Create 返回值及实际 token；本文不替代运行时身份检查。
