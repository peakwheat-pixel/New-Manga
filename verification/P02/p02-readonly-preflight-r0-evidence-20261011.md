# P02PRE-R0 受控只读取证结果

## 身份、范围与基线

- Task：`P02PRE-R0`；Owner/Author：`Codex /root`；非作者 Reviewer：`DeepSeek Harness`（待 dispatch 与独立 Review）；Integrator/adjudicator：`Codex /root`。
- 用户授权：2026-10-11 Asia/Shanghai；只允许 manifest 中已冻结、可证明为无副作用的 getter/query。此授权不是新 waiver，不代表 Gate PASS，也不解除 Build Barrier。
- 执行基线：repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`；common-dir=`G:/CODEX/New Manga/.git`。
- 同轮安全 NUL Git snapshot：`git --no-optional-locks -c core.fsmonitor=false -c core.quotepath=false status --porcelain=v1 -z --untracked-files=all --no-renames --ignore-submodules=none`，exit `0`，512 records；`.git/index` SHA-256=`214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C`，与此前快照相同。没有 reset、clean、stash、覆盖、删除、commit。
- 主要同进程采集窗口 UTC=`2026-10-10T23:16:33.9414550Z`（identity）至 `2026-10-10T23:16:34.2092070Z`（查询结束）。随后仅为校验 `HOMEDRIVE + HOMEPATH` 组合，另一个同用户/SID 且无 thread impersonation 的 PowerShell 进程于 `2026-10-10T23:17:30.4412666Z` 运行 `Path.GetFullPath`。
- manifest=`verification/P02/p02-readonly-preflight-r0-manifest-20261011.md`；r6 source=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`。

## 风险裁决与 Gate 原值

`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；必须原样记录：`technical condition unmet; user explicitly accepted residual risk`。

该风险豁免仍仅覆盖“必须在创建前无副作用证明目标 private registry storage 不存在”。本次 R0 授权没有扩大豁免。profile=`NOT_CREATED`；ACL/registry=`NOT_MODIFIED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`（尚未执行，不是失败）。

## 实际执行调用与结果

| 调用 | 实际范围/结果 |
|---|---|
| `WindowsIdentity.GetCurrent(false/true)` | 在主要查询进程 PID=`12280` 中首先执行。name=`HOME-MY\49745`；SID=`S-1-5-21-2196946971-914346751-4210154634-1001`；authenticated=`true`；authenticationType=`CloudAP`；impersonationLevel=`None`；thread identity present=`false`。与 r6 固定身份匹配；无 thread impersonation，继续查询。没有读取或输出 token handle。 |
| `Environment.GetEnvironmentVariable(String)` | 仅查询 manifest 冻结的 35 个环境变量，Process target；未读取任何变量指向的文件/配置/凭据。 |
| `Path.GetFullPath(String)` | 对已设置的冻结路径变量做词法归一化；没有把结果作为 filesystem canonical identity。另验证 `HOMEDRIVE + HOMEPATH = C:/Users/49745`，与 `USERPROFILE` 一致。 |
| `Get-Item -LiteralPath -Force` | 仅查询 manifest 的 42 个精确目标对象：17 `PRESENT`，25 `ABSENT`，0 查询错误。未递归列出 scratch 或输入目录。 |
| `Get-Acl -LiteralPath` | 对上述 17 个存在且 leaf 非 reparse 的精确对象读取 Owner/SDDL；17 成功，0 失败。没有计算 effective access，也没有写权限试探。 |
| `RegistryKey.OpenBaseKey + OpenSubKey(path, false)` | 仅 `RegistryView.Default` 两个 LocalDumps 候选：HKLM=`PRESENT`、HKCU=`ABSENT`；未枚举 values/subkeys。 |
| `Get-ChildItem -LiteralPath -Force` | 仅三个 WER 候选目录的直接子项：10、11、63 项。只记 name/type/length/last-write；未打开、复制或哈希 dump。 |
| `Get-FileHash -LiteralPath -Algorithm SHA256` | 仅固定 13 项文档与 `.git/index`，查询前/后各一次；13/13 hash 一致。仅为固定文档子集，不是 r6 完整动态 protected-invariants inventory/hash。 |

### 执行过程中的脚本/输出异常

- 首次路径批次在调用 `Get-Item` / `Get-Acl` 前因 helper 定义顺序错误而中止；不作为路径结果。
- 下一次更正后的路径批次没有捕获到 stdout；不采用其结果。
- 随后有一个路径诊断批次包含精确对象及其父组件，工具返回内容被截断，无法确认该次逐对象输出。它调用的是只读 `Get-Item`/`Get-Acl`，但父组件集合未冻结枚举；因此该批次不作为证据，并在 Review 中明确审查此范围偏差。最终作为证据的同进程批次仅查询下表 42 个冻结精确对象。
- 首次 WER 目录批次因 PowerShell 数组优先级错误，将三个路径拼成一条无效路径，回报 `ABSENT`；该结果不是三个候选目录的查询。随后在主要同进程批次按三个精确路径重新查询。
- 本轮工作区检查开始时 Codex 另执行一次普通 `git status --porcelain`，未在该次命令前紧邻 hash `.git/index`；后续安全 NUL status 与固定 index SHA 相同，但不回溯证明前次调用无副作用。该命令属于 Codex 治理状态读取，不属于主要 R0 OS 查询进程。
- 上述异常均未调用写 API；可用记录中没有观察到系统/项目状态写入。未恢复、删除、清理或重试任何文件/状态。
- 在 Codex 编排中另用 `Get-Content`/`rg` 读取治理/manifest 文档；这些文档检索不属于 P02PRE OS 查询进程。主要 R0 OS 查询进程未调用外部程序、P/Invoke、`Add-Type` 或其他子进程。

## 当前 Process environment 观测

以下为 35 项变量的实际 process value 与词法归一化。`HOMEDRIVE`、`HOMEPATH` 单独结果只是片段，不是实际组合路径；正确组合是 `C:/Users/49745`。不能将 host 值当作未来 controller/LPAC child 的 environment readback 或写入闭包证据。

| 名称 | Process 值 | 路径变量 | 词法 `Path.GetFullPath` |
|---|---|---:|---|
| `LOCALAPPDATA` | `C:\Users\49745\AppData\Local` | 是 | `C:\Users\49745\AppData\Local` |
| `TEMP` | `C:\Users\49745\AppData\Local\Temp` | 是 | `C:\Users\49745\AppData\Local\Temp` |
| `TMP` | `C:\Users\49745\AppData\Local\Temp` | 是 | `C:\Users\49745\AppData\Local\Temp` |
| `APPDATA` | `C:\Users\49745\AppData\Roaming` | 是 | `C:\Users\49745\AppData\Roaming` |
| `USERPROFILE` | `C:\Users\49745` | 是 | `C:\Users\49745` |
| `HOME` | `(unset)` | 是 | — |
| `HOMEDRIVE` | `C:` | 是 | `C:\` |
| `HOMEPATH` | `\Users\49745` | 是 | `G:\Users\49745` |
| `PYTHONPYCACHEPREFIX` | `(unset)` | 是 | — |
| `PYTHONDONTWRITEBYTECODE` | `(unset)` | 否 | — |
| `PYTHONUSERBASE` | `(unset)` | 是 | — |
| `PYTHONNOUSERSITE` | `(unset)` | 否 | — |
| `TRITON_CACHE_DIR` | `(unset)` | 是 | — |
| `PYINSTALLER_CONFIG_DIR` | `(unset)` | 是 | — |
| `TORCH_HOME` | `(unset)` | 是 | — |
| `TORCHINDUCTOR_CACHE_DIR` | `(unset)` | 是 | — |
| `TORCH_EXTENSIONS_DIR` | `(unset)` | 是 | — |
| `XDG_CACHE_HOME` | `(unset)` | 是 | — |
| `XDG_DATA_HOME` | `(unset)` | 是 | — |
| `HF_HOME` | `(unset)` | 是 | — |
| `HF_HUB_CACHE` | `(unset)` | 是 | — |
| `HF_ASSETS_CACHE` | `(unset)` | 是 | — |
| `HF_XET_CACHE` | `(unset)` | 是 | — |
| `HF_TOKEN_PATH` | `(unset)` | 是 | — |
| `HF_HUB_DISABLE_IMPLICIT_TOKEN` | `(unset)` | 否 | — |
| `TRANSFORMERS_CACHE` | `(unset)` | 是 | — |
| `PIP_CACHE_DIR` | `(unset)` | 是 | — |
| `UV_CACHE_DIR` | `(unset)` | 是 | — |
| `CARGO_HOME` | `(unset)` | 是 | — |
| `CARGO_TARGET_DIR` | `(unset)` | 是 | — |
| `NPM_CONFIG_CACHE` | `(unset)` | 是 | — |
| `NPM_CONFIG_USERCONFIG` | `(unset)` | 是 | — |
| `GIT_CONFIG_GLOBAL` | `(unset)` | 是 | — |
| `GIT_CONFIG_NOSYSTEM` | `(unset)` | 否 | — |
| `GIT_TERMINAL_PROMPT` | `(unset)` | 否 | — |

## 冻结的 42 个精确路径查询

`PRESENT` 对象上的 `reparsePoint=false` 仅描述最终对象；祖先组件、file ID、hardlink、ADS 与 canonical identity 未证明。ACL SDDL 原文逐条记录；其中出现写能力 mask 不等于有效 token access 结论。绝不对保护目录写入或测试权限。

| 精确对象 | 状态 | 类型 | 属性 | leaf reparse | ACL 查询 | Owner | SDDL（只读原始值） |
|---|---|---|---|---:|---|---|---|
| `C:\Users\49745\AppData\Local\Programs\Python\Python312` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1200a9;;;S-1-15-3-600613-1-2-1351910295-3487206863-273920555)(A;OICIIOID;GXGR;;;S-1-15-3-600613-1-2-1351910295-3487206863-273920555)(A;OICIID;FA;;;SY)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;S-1-5-21-2196946971-914346751-4210154634-1001)` |
| `G:\CODEX\New Manga.task-envs\m2ac5-build` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `E:\Program Files\nodejs` | PRESENT | Directory | Directory | false | READ | BUILTIN\Administrators | `O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-15-3-600613-1-3-1876781482-3709679024-1580391142)(A;OICIIOID;GA;;;S-1-15-3-600613-1-3-1876781482-3709679024-1580391142)(A;OICIID;0x1200a9;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;OICIID;FA;;;SY)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;S-1-5-21-2196946971-914346751-4210154634-1001)` |
| `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools` | PRESENT | Directory | Directory | false | READ | BUILTIN\Administrators | `O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `C:\Program Files (x86)\Microsoft Visual Studio\Installer` | PRESENT | Directory | Directory | false | READ | BUILTIN\Administrators | `O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `C:\Program Files (x86)\Windows Kits\10` | PRESENT | Directory | Directory | false | READ | NT AUTHORITY\SYSTEM | `O:SYG:SYD:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `C:\Program Files\Git\cmd` | PRESENT | Directory | Directory | false | READ | BUILTIN\Administrators | `O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `C:\Program Files\Git\mingw64` | PRESENT | Directory | Directory | false | READ | BUILTIN\Administrators | `O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)` |
| `G:\CODEX\P02-scratch-build-source` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\frontend\node_modules` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\frontend\dist` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\src-tauri\target\core-sidecar` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\src-tauri\target\pyinstaller-work` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\src-tauri\gen\schemas` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\P02-scratch-build-source\apps\desktop\src-tauri\permissions\autogenerated` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\P02-scratch-build-source\verification\P02\cargo-target` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\npm-cache` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\cargo-home` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\tmp\appdata` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\tmp\home` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\python-cache` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\pyinstaller-config` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\smoke-readonly-probe` | PRESENT | Directory | Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-control` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-deny-control` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\lpac-write-control\p02-lpac-write-canary-20261010.bin` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga` | PRESENT | Directory | ReadOnly, Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;OICI;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;OICI;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\New Manga.worktrees` | PRESENT | Directory | ReadOnly, Directory | false | READ | HOME-MY\49745 | `O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\manifest-reference.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\preflight.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\pre-protected-files.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\pre-authorized-outputs.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\create-result.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\post-isolation.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\post-protected-files.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\post-authorized-outputs.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\comparison.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |
| `G:\CODEX\New Manga\verification\P02\p02-owner-risk-waiver-evidence-20261010\incident.json` | ABSENT | — | — | — | NOT_QUERIED | — | `—` |

观察汇总：

- r6 只读输入根：12/12 `PRESENT`，均成功读取对象元数据与 ACL。ACL 读取是对象级证据，不证明 future AppContainer 有效读/写权限。
- 13 个 scratch output leaf：11 个 `ABSENT`；`apps/desktop/src-tauri/gen/schemas` 与 `apps/desktop/src-tauri/permissions/autogenerated` 为 `PRESENT`。R0 未列举这两个目录内容，因此不能证明 r6 要求的“empty or absent”。
- 三个 canary leaf：`smoke-readonly-probe`=`PRESENT`；`lpac-write-control`、`lpac-write-deny-control`=`ABSENT`。唯一正向 canary 文件=`ABSENT`。未做任何写入或权限测试。
- protected/evidence path：主仓、worktrees root=`PRESENT`；r6 evidence root 与其十个固定目标文件均=`ABSENT`。这是当前精确路径状态快照，不保证未来 API 时刻仍然不存在。
- 多个 SDDL 含 `AU` ACE，部分 mask 为 `0x1301bf`；不能据此推断 LPAC 实际 access。此处需要未来在固定真实 token 上的安全访问/拒绝证据。

## 冻结的 WER 候选目录直接子项元数据

采样不是 future controller 的安全 T0，也没有枚举 WER policy values、per-image/global policy、registry view alternatives、dump destination、expanded path、实际 reader/helper 或 API-created profile 的新目录。由于现有 dump/directory 项目确实存在，不能把这些当前候选解释为未来 crash dump 一定写入或不会写入的位置。

| 候选目录 | 子项名称 | 类型 | 长度（文件） | LastWriteTimeUtc |
|---|---|---|---:|---|
| C:\Users\49745\AppData\Local\CrashDumps | `git.exe.47924.dmp` | File | 631425 | 2026-09-13T11:14:46.7476717Z |
| C:\Users\49745\AppData\Local\CrashDumps | `IconExp.exe.45704.dmp` | File | 2722000 | 2026-09-12T07:57:27.3854356Z |
| C:\Users\49745\AppData\Local\CrashDumps | `NVIDIA Broadcast.exe.10648.dmp` | File | 604054177 | 2026-09-11T13:12:52.5065872Z |
| C:\Users\49745\AppData\Local\CrashDumps | `NVIDIA Broadcast.exe.11560.dmp` | File | 40173730 | 2026-09-12T11:47:59.0798326Z |
| C:\Users\49745\AppData\Local\CrashDumps | `python.exe.31380.dmp` | File | 5310717 | 2026-09-11T04:30:18.0174295Z |
| C:\Users\49745\AppData\Local\CrashDumps | `python.exe.36724.dmp` | File | 5307457 | 2026-09-11T04:30:35.8115666Z |
| C:\Users\49745\AppData\Local\CrashDumps | `python.exe.45992.dmp` | File | 2626557 | 2026-09-19T08:49:45.8153721Z |
| C:\Users\49745\AppData\Local\CrashDumps | `python.exe.7732.dmp` | File | 5305325 | 2026-09-11T04:31:10.4951350Z |
| C:\Users\49745\AppData\Local\CrashDumps | `QQ.exe.45948.dmp` | File | 9563066 | 2026-09-13T11:17:00.4292237Z |
| C:\Users\49745\AppData\Local\CrashDumps | `webview_support_browser.exe.42576.dmp` | File | 6195467 | 2026-09-16T12:35:46.4110178Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_116_252f5bba26ede1fd2fd6282b3582596a465914_00000000_e90dfb5a-a8dd-44c7-8ca0-59acad730919` | Directory | — | 2026-10-10T20:32:23.1375468Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_116_7c40cfb78427ab856d1a6edc778922fed386d2_00000000_06fcb79e-ccd2-466b-bc0c-e5ae291fef62` | Directory | — | 2026-10-10T20:32:23.0847757Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_116_a4cd499e36af851fd914ab39ec591d21d932e5c4_00000000_943a9053-b912-44b8-bec2-90c62cbc1208` | Directory | — | 2026-10-10T20:32:23.0347120Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_116_e42457ca7bc3c610fa6174ed5169c4298a773d2_00000000_04f0340c-ac24-436a-80e5-94f33c06deae` | Directory | — | 2026-10-10T20:32:22.9997136Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_117_bdb1effc8331fabff4ffffd9c589f9fd21e516_00000000_13bd6f3c-80a5-40dd-9814-d435de447f9b` | Directory | — | 2026-10-10T20:32:23.0514018Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_141_9d557966ba7548b4215c8327b2196c542bb67179_00000000_97ae1483-5b55-4b8c-9862-0fa1aa532605` | Directory | — | 2026-10-10T20:32:23.0164530Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_141_b9ec20d61d33311acd10abec8616bf9093bc9b13_00000000_9ecbec1b-2736-4924-b175-59415beac77f` | Directory | — | 2026-10-10T20:32:23.0681141Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_141_da863cc1c3a9ff791df5d3e741e2d9ba3797bd5_00000000_2a47f34b-2f6f-4028-a134-7c8facbc82e3` | Directory | — | 2026-10-10T20:32:22.9814714Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_141_ee7b412488a64cc36a8d5b2c7d951c04d2eef67_00000000_598538a1-90f9-4094-85ee-c8f68099a3c3` | Directory | — | 2026-10-10T20:32:23.1192593Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `Kernel_1a8_57f07d87e3f91b49fe232dde72bf1889154fd0_00000000_36cced1f-83b0-4de1-ab57-0dccbed4053b` | Directory | — | 2026-10-10T20:32:23.1014853Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportQueue | `a1f57455-8af6-49ae-bc92-4f60b1c1d6f4` | File | 0 | 2026-08-08T13:10:26.2137749Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_0a27b85d-5d54-4966-a5e1-50c61d9095a0` | Directory | — | 2026-09-29T00:31:04.9110664Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_0c2cd102-1fe6-42b1-aa3b-eb8fd477d281` | Directory | — | 2026-09-30T00:31:26.7592955Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_139d5da2-6a56-4d55-b9f5-568d05111cab` | Directory | — | 2026-09-28T03:29:20.6480139Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_20b36176-ad22-4327-afa5-cce9d1983b1e` | Directory | — | 2026-09-28T03:29:27.5752099Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_25f9ebc4-dc82-449a-8cde-8ed25db0cfdf` | Directory | — | 2026-09-28T03:30:13.7223609Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_36496ca4-c272-4b87-a06a-b5526e63e83c` | Directory | — | 2026-09-28T03:29:08.1013536Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_3e113e80-b1cb-47dd-b53c-b556f6b75096` | Directory | — | 2026-09-29T00:30:27.0597326Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_3eae99cc-94e1-41ab-8bfd-4f0ea932cd32` | Directory | — | 2026-09-29T00:30:54.0690818Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_416ba212-6ada-4226-b12b-9e614bb3eee5` | Directory | — | 2026-09-30T00:31:59.3968238Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_451d340d-f40f-4a02-a2d9-b5c8be131af6` | Directory | — | 2026-09-28T03:30:01.0149633Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_4d27d9b0-2b5e-4986-8907-bd3d0d414f7b` | Directory | — | 2026-09-29T00:30:48.5992336Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_621fd2cc-0afc-45cd-bd8f-2f4a73a7a8ca` | Directory | — | 2026-09-29T00:31:10.4348250Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_6a81e71c-48f0-4b85-b55f-1e3cd7b0494c` | Directory | — | 2026-09-30T00:32:05.7692888Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_727cc88a-7a06-4f1c-b736-5a08b79165c2` | Directory | — | 2026-09-29T00:30:32.3835093Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_801a44aa-c436-4ed6-b32b-28969e4f94cd` | Directory | — | 2026-09-28T03:29:34.7852624Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_872b3409-5fd9-40dc-aaca-53701bf687dc` | Directory | — | 2026-09-29T00:30:59.6054505Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_8d4e321a-5cc6-437b-8d63-55f573777b9d` | Directory | — | 2026-09-28T03:29:47.7055763Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_a7c8946b-1df5-4a24-8e22-2dee09a00186` | Directory | — | 2026-09-29T00:30:37.7064175Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_a82c2605-437d-4207-95a0-96aa02b983fa` | Directory | — | 2026-09-30T00:32:18.7904843Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_afc288ce-101d-43f6-a049-23a3442a999b` | Directory | — | 2026-09-30T00:32:12.2226477Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_bd0d40bf-515c-4411-83cb-af8b1fcebcae` | Directory | — | 2026-09-30T00:31:38.9257081Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_be8e253d-b63b-4b9a-abd2-855d64902548` | Directory | — | 2026-09-30T00:31:20.5176961Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c1b54d11-2ba6-4ea4-ab38-f138ae2e45bb` | Directory | — | 2026-09-28T03:29:14.4464419Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c2c1b63b-682d-4145-a71c-d9ce01c02a6c` | Directory | — | 2026-09-28T03:30:08.1098735Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c4cf169a-9387-4cf5-a49c-0875afc182f2` | Directory | — | 2026-09-30T00:31:32.6750445Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_ca7c8a76-1960-4ad2-b614-865fd8b8ecee` | Directory | — | 2026-09-28T03:29:41.2742998Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_cba88770-b652-47b5-a8bd-c56469a0ab6a` | Directory | — | 2026-09-28T03:28:59.9743632Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_d0cde7c8-20c4-46a0-8424-a7cbea33a08a` | Directory | — | 2026-09-29T00:30:21.8002206Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_df492d7d-653b-4df7-83ce-a455dcea2cdd` | Directory | — | 2026-09-30T00:31:46.2239366Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e28952e0-8a22-4086-9c6a-dbf6409107c1` | Directory | — | 2026-09-30T00:31:52.5302113Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e2f73159-d221-4d94-be99-a9c1b6970a76` | Directory | — | 2026-09-28T03:29:54.6951457Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e87f7a10-3217-4b9b-b054-ed51f2797cfc` | Directory | — | 2026-09-29T00:30:43.2392631Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `AppHang_explorer.exe_99e2b031e6dddf259f8a81d89270bed39b55776_f32e9b07_c037e330-a16e-4d64-921e-d139983b6cba` | Directory | — | 2026-09-24T02:02:55.7392518Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `Critical_10.0.26100.9441__fec76a833170a95749465064335b469514df6ecc_00000000_4a4e019d-bd8d-4192-a5da-7ab139364512` | Directory | — | 2026-10-04T17:08:47.4003404Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `Critical_10.0.26100.9539__4aa07db12c38ead69a39ba6e89673bd3cd2d82f_00000000_9e3feb21-c220-4a50-8440-56ad6c68ec10` | Directory | — | 2026-10-04T17:11:54.1904695Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_Acquisition;setu_10a9e1b77f1cfb41be5a53b1622d97a95e136fc_00000000_868cf961-8ec0-4c13-b6ea-24ebacd3d15a` | Directory | — | 2026-10-10T03:02:00.3258465Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_020897c6-6aec-4130-9c3d-3a32c220f856` | Directory | — | 2026-09-27T02:40:08.4688300Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_081b0e82-cdc7-4e7b-8d0e-6a7e892e6880` | Directory | — | 2026-09-27T02:40:05.5958991Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_0c7d0971-c525-4b35-8ad4-1bf349f59d82` | Directory | — | 2026-09-28T00:53:42.6059660Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_aff38167-cca1-4740-9d68-52defadfb5bb` | Directory | — | 2026-09-24T02:13:52.6179062Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_b0453351-0ace-454c-a401-f23c27764f9f` | Directory | — | 2026-09-28T00:53:46.4746686Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_ced2de43-28f4-478b-8203-20c9d71104d8` | Directory | — | 2026-09-26T03:36:10.7476358Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_0a950a75-8930-4072-b3bd-2fca431f7ee1` | Directory | — | 2026-10-09T00:37:24.5775229Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_0e45ecab-4ebc-48b8-a226-cd1a4c0e3ea7` | Directory | — | 2026-10-09T16:05:05.4997680Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_2ab47d7b-985e-4a0f-9e56-8146f66dbcfe` | Directory | — | 2026-10-09T00:38:03.0301143Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_73ad3f92-1290-49ce-adf5-07b4778d2cad` | Directory | — | 2026-10-09T02:27:03.0907183Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_8df36713-7755-40d5-b409-4e30d2aa0c57` | Directory | — | 2026-10-09T16:05:09.4428265Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_c536896b-6ab9-4afa-816e-de369ac376b5` | Directory | — | 2026-10-09T02:27:06.1403241Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_f0bab6a2-4d2e-4db4-b512-c1c653c14060` | Directory | — | 2026-10-08T12:41:28.3903364Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_fc29130d-8759-44e9-9da5-eb91c5ad7492` | Directory | — | 2026-10-08T12:41:31.7786632Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_23920e8a-810f-4bfe-a56b-1bb23a950b79` | Directory | — | 2026-10-04T14:21:34.6960307Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_6576fc77-3ca7-4524-8f2f-e95d6ee8003a` | Directory | — | 2026-10-06T12:31:38.5402461Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_785f4bfc-1fc3-40e2-a849-56083221561f` | Directory | — | 2026-10-06T12:31:34.2947450Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_7b649f07-5a9b-4c8b-9d8b-9956a151599b` | Directory | — | 2026-10-06T16:43:58.0181697Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_c0409289-6f79-49a5-8f64-f391308d8f11` | Directory | — | 2026-10-04T14:21:38.6167579Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_f5ab8ccb-5285-4034-9ec8-5d2a257fd272` | Directory | — | 2026-10-06T16:43:53.6089444Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_0fed71b5-2f58-4c16-a6ec-b3e2c21022fe` | Directory | — | 2026-09-30T10:01:20.7707434Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_1e44f95d-1b46-4bb6-9f83-faa42c1c94d6` | Directory | — | 2026-09-30T10:57:32.5285622Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_81d46a04-63c2-43fc-8e84-01375d72e536` | Directory | — | 2026-09-30T10:01:27.3352393Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_msedgewebview2se_9e6316f94d964e7fac18ab9bfebf707866e85_00000000_ddeaca41-43eb-4592-b218-5161713cf0ab` | Directory | — | 2026-09-29T04:50:15.3883374Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_Update;MoUpdateO_2dd07164693f3daeb07c71931301f91b72b4037_00000000_b195c1db-526a-4765-830b-bbe7d31359a0` | Directory | — | 2026-10-02T16:36:56.5639161Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_Update;MoUpdateO_9562b866f34ec3cfbb3a18b337a6b6638b5ac048_00000000_2c933f8f-ab12-4fd7-9c4b-2fce4ab5228b` | Directory | — | 2026-10-02T16:40:13.7697670Z |
| C:\ProgramData\Microsoft\Windows\WER\ReportArchive | `NonCritical_Update;UsoClient_8a6ddfd8a3fdc7f8c5e8c5332fc6ad23f5c8ae7_00000000_7709780c-122a-4b4c-82a1-bea197cb1a80` | Directory | — | 2026-09-24T02:13:05.7159121Z |

## 固定文件 hash 前/后对照

| 固定对象 | 查询前 SHA-256 | 查询后 SHA-256 | 结论 |
|---|---|---|---|
| `AGENTS.md` | `46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501` | `46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501` | 一致 |
| `doc/REBASELINE_PLAN.md` | `ABC9EFBE1FBA22F106D1CBCE6C537FDB3C760FAEE331A1B14447882AC925964E` | `ABC9EFBE1FBA22F106D1CBCE6C537FDB3C760FAEE331A1B14447882AC925964E` | 一致 |
| `doc/00_INDEX.md` | `5F183225A9C3464E2F1FDA2852032A07F93FEF75A8540AE0B823FDA72F40EB39` | `5F183225A9C3464E2F1FDA2852032A07F93FEF75A8540AE0B823FDA72F40EB39` | 一致 |
| `doc/STATUS.md` | `1163E219025AA158601E8D20F19A8E3E1E2A4AEF5D1CED0BA83909DC1C6B1C7A` | `1163E219025AA158601E8D20F19A8E3E1E2A4AEF5D1CED0BA83909DC1C6B1C7A` | 一致 |
| `doc/09_COLLABORATION.md` | `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D` | `DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D` | 一致 |
| `doc/tasks/P02.md` | `4B34107A1C3A8042D86236B8B2CDDAC33533D0CBF51B399A0BB66EDCCEAEB9B4` | `4B34107A1C3A8042D86236B8B2CDDAC33533D0CBF51B399A0BB66EDCCEAEB9B4` | 一致 |
| `doc/tasks/P02PRE-R0.md` | `FB7E6D98098EF433C901179E7A441D371D22E7024DF8F629AC88149859AC7641` | `FB7E6D98098EF433C901179E7A441D371D22E7024DF8F629AC88149859AC7641` | 一致 |
| `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md` | `C3CDC95EED8B2C6AC3550266F97877CC074C53E63199C9151B67320C700F32A8` | `C3CDC95EED8B2C6AC3550266F97877CC074C53E63199C9151B67320C700F32A8` | 一致 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` | `626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE` | 一致 |
| `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md` | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` | `A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8` | 一致 |
| `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md` | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` | `01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159` | 一致 |
| `verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md` | `15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F` | `15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F` | 一致 |
| `.git/index` | `214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C` | `214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C` | 一致 |

主要窗口内固定 13 项 hash 全部一致：文档子集未观察到变化；`.git/index` 前/后值相同。该证据不涵盖主仓/scratch 的动态完整 protected-invariants 文件集合、每个文件/hash/security descriptor/streams，也不能补足 M11 或此前任何缺失的紧邻 hash。

## P02PRE 剩余条件分类

| 条件 | 分类 | 证据与范围限制 |
|---|---|---|
| 本次 PowerShell 进程的 user/SID/线程 impersonation | `PASS_WITH_EVIDENCE` | 当前执行进程与 r6 固定 name/SID 匹配且无 thread impersonation；不覆盖未来 controller token、PID 绑定、elevation、token ID/authentication ID 或 AppContainer SID。 |
| 当前 Process 冻结环境变量、TEMP/cache 字符串、HOMEDRIVE+HOMEPATH | `PASS_WITH_EVIDENCE` | 35 项已读；`HOME` 与缓存变量均 unset；组合 HOME 与 `USERPROFILE` 一致。future child environment/Python/TEMP/cache 实际解析与写入闭包仍未证明。 |
| 12 个只读输入根的精确 leaf 元数据/ACL | `PASS_WITH_EVIDENCE` | 精确路径均存在，Owner/SDDL 已记录；reparse ancestor、file ID 和 future LPAC 的有效访问仍未证明。 |
| 13 个 scratch leaf 的当前存在状态 | `PASS_WITH_EVIDENCE` | 11 个 absent，2 个 present；该类只描述当前 leaf 状态。 |
| 当前必须 empty-or-absent 的两个已存在 scratch leaf | `REQUIRES_ACTIVE_TEST` | R0 不读取目录内容；r6 的完整 output inventory/empty 条件尚未验证。 |
| canary leaf ACL 的正/负权限行为及真实 token write boundary | `REQUIRES_ACTIVE_TEST` | 只读 ACL 不等于 AccessCheck 或真实 OS 写拒绝/成功结果；R0 明确禁止写试探。 |
| r6 evidence root 与十文件当前精确 absence | `PASS_WITH_EVIDENCE` | 11 个固定目标均 absent；没有证明未来调用前路径身份/并发/新鲜度。 |
| appcontainer profile folder exact path / pre-create absence | `NOT_SAFE_FOR_R0` | 正式合同未证明 getter 无副作用；路径未知，不猜路径、不调用 getter。 |
| private registry absence | `UNPROVABLE` | 技术状态保持原值；用户唯一 waiver 仍为 `WAIVED_BY_OWNER`，R0 没有读目标 private registry storage，也不以 waiver 伪作 PASS。 |
| 详细 token/elevation/LPAC capability 与实际子进程 token | `NOT_SAFE_FOR_R0` | `GetTokenInformation` P/Invoke、`Add-Type`/native handle 查询未包含于冻结安全 scope。 |
| path ancestry/canonical identity/file ID/hardlink/ADS 与 full protected-invariants pre/post hash | `UNPROVABLE` | 最终对象属性和固定 13 项文档 hash 已测；祖先身份、流、文件 ID、动态主仓/scratch inventory/hash 未测。 |
| 当前 WER 候选对象的有限观察 | `PASS_WITH_EVIDENCE` | HKLM key present、HKCU key absent；三个固定目录直接子项分别 10/11/63。 |
| 实际 WER policy/view/destination、future T0 安全引导顺序 | `UNPROVABLE` | 候选范围不穷尽 reader/view/destination；未读 policy values；R0 snapshot 不能替代“任何 Phase A 读取前的 T0”。 |
| controller/probe 可执行映像、模块、子进程/COM/broker/WER 短命进程及 build descendants 的强制闭包 | `REQUIRES_ACTIVE_TEST` | 本轮没有启动 API/probe/build 或子进程，因而没有动态 OS 执行证据。 |

## 安全边界与禁止项确认

本 Task 未调用 `CreateAppContainerProfile`、`DeleteAppContainerProfile`、`GetAppContainerFolderPath`、`GetAppContainerRegistryLocation`、任何 AppContainer/profile API、registry/ACL/file write、protected path access/write probe、P/Invoke、`Add-Type`、Windows feature/Sandbox 查询或修改、build、Cargo、AC1–AC7；未读 dump 内容/哈希、漫画/用户文件、数据库、Lock、Revision、凭据或模型内容。profile 仍 `NOT_CREATED`，ACL/registry 仍 `NOT_MODIFIED`。

## Review 与当前结论

- Owner delivery=`EVIDENCE_CAPTURED_WITH_TOOLING_DEVIATIONS / REVIEW_REQUIRED`；本报告不自审，未标 Task DONE。
- 非作者 Reviewer=`DeepSeek Harness`；Review 状态=`PENDING_DISPATCH`。Review 必须核对 capture、manifest 范围、脚本缺陷披露、状态/hash pins 与分类；Integrator/Codex 再单独 adjudicate。
- 总体 `P02PRE=BLOCKED`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；AC1–AC7=`BLOCKED / NOT_RUN`。此次只读取证没有放行任何 Gate。

## 机器可读完整 capture

```json
{
  "identity": {
    "atUtc": "2026-10-10T23:16:33.9414550Z",
    "pid": 12280,
    "name": "HOME-MY\\49745",
    "sid": "S-1-5-21-2196946971-914346751-4210154634-1001",
    "authenticated": true,
    "authenticationType": "CloudAP",
    "impersonationLevel": "None",
    "threadIdentityPresent": false,
    "threadIdentityName": null,
    "threadIdentitySid": null
  },
  "environment": [
    {
      "name": "LOCALAPPDATA",
      "value": "C:\\Users\\49745\\AppData\\Local",
      "isPath": true,
      "fullPath": "C:\\Users\\49745\\AppData\\Local",
      "pathError": null
    },
    {
      "name": "TEMP",
      "value": "C:\\Users\\49745\\AppData\\Local\\Temp",
      "isPath": true,
      "fullPath": "C:\\Users\\49745\\AppData\\Local\\Temp",
      "pathError": null
    },
    {
      "name": "TMP",
      "value": "C:\\Users\\49745\\AppData\\Local\\Temp",
      "isPath": true,
      "fullPath": "C:\\Users\\49745\\AppData\\Local\\Temp",
      "pathError": null
    },
    {
      "name": "APPDATA",
      "value": "C:\\Users\\49745\\AppData\\Roaming",
      "isPath": true,
      "fullPath": "C:\\Users\\49745\\AppData\\Roaming",
      "pathError": null
    },
    {
      "name": "USERPROFILE",
      "value": "C:\\Users\\49745",
      "isPath": true,
      "fullPath": "C:\\Users\\49745",
      "pathError": null
    },
    {
      "name": "HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HOMEDRIVE",
      "value": "C:",
      "isPath": true,
      "fullPath": "C:\\",
      "pathError": null
    },
    {
      "name": "HOMEPATH",
      "value": "\\Users\\49745",
      "isPath": true,
      "fullPath": "G:\\Users\\49745",
      "pathError": null
    },
    {
      "name": "PYTHONPYCACHEPREFIX",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "PYTHONDONTWRITEBYTECODE",
      "value": null,
      "isPath": false,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "PYTHONUSERBASE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "PYTHONNOUSERSITE",
      "value": null,
      "isPath": false,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "TRITON_CACHE_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "PYINSTALLER_CONFIG_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "TORCH_HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "TORCHINDUCTOR_CACHE_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "TORCH_EXTENSIONS_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "XDG_CACHE_HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "XDG_DATA_HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_HUB_CACHE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_ASSETS_CACHE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_XET_CACHE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_TOKEN_PATH",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "HF_HUB_DISABLE_IMPLICIT_TOKEN",
      "value": null,
      "isPath": false,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "TRANSFORMERS_CACHE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "PIP_CACHE_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "UV_CACHE_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "CARGO_HOME",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "CARGO_TARGET_DIR",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "NPM_CONFIG_CACHE",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "NPM_CONFIG_USERCONFIG",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "GIT_CONFIG_GLOBAL",
      "value": null,
      "isPath": true,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "GIT_CONFIG_NOSYSTEM",
      "value": null,
      "isPath": false,
      "fullPath": null,
      "pathError": null
    },
    {
      "name": "GIT_TERMINAL_PROMPT",
      "value": null,
      "isPath": false,
      "fullPath": null,
      "pathError": null
    }
  ],
  "paths": [
    {
      "path": "C:\\Users\\49745\\AppData\\Local\\Programs\\Python\\Python312",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2025-11-23T04:15:35.2883249Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;0x1200a9;;;S-1-15-3-600613-1-2-1351910295-3487206863-273920555)(A;OICIIOID;GXGR;;;S-1-15-3-600613-1-2-1351910295-3487206863-273920555)(A;OICIID;FA;;;SY)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;S-1-5-21-2196946971-914346751-4210154634-1001)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga.task-envs\\m2ac5-build",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-09-30T15:01:28.2985341Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga.task-envs\\M2-DOCTR-QUAL-C4\\weights\\ogkalu-comic-text-and-bubble-detector",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-09-30T06:57:52.2922905Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga.task-envs\\M2-SFX-DETECT\\weights-v2b",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-10-05T15:39:43.3049878Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "E:\\Program Files\\nodejs",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-08-11T13:50:15.8274340Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "BUILTIN\\Administrators",
      "sddl": "O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "C:\\Users\\49745\\.rustup\\toolchains\\stable-x86_64-pc-windows-msvc",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-09-05T10:11:24.4973430Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-15-3-600613-1-3-1876781482-3709679024-1580391142)(A;OICIIOID;GA;;;S-1-15-3-600613-1-3-1876781482-3709679024-1580391142)(A;OICIID;0x1200a9;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;OICIID;FA;;;SY)(A;OICIID;FA;;;BA)(A;OICIID;FA;;;S-1-5-21-2196946971-914346751-4210154634-1001)",
      "error": null
    },
    {
      "path": "C:\\Program Files (x86)\\Microsoft Visual Studio\\2022\\BuildTools",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2025-11-23T03:48:46.2743319Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "BUILTIN\\Administrators",
      "sddl": "O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-07-14T02:28:52.9612650Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "BUILTIN\\Administrators",
      "sddl": "O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "C:\\Program Files (x86)\\Windows Kits\\10",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-07-14T02:35:46.7337384Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "NT AUTHORITY\\SYSTEM",
      "sddl": "O:SYG:SYD:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "C:\\Program Files\\Git\\cmd",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2025-12-18T10:20:50.0139288Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "BUILTIN\\Administrators",
      "sddl": "O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "C:\\Program Files\\Git\\mingw64",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2025-12-18T10:20:37.0268420Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "BUILTIN\\Administrators",
      "sddl": "O:BAG:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;ID;FA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;CIIOID;GA;;;S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)(A;OICIIOID;GA;;;CO)(A;ID;0x1200a9;;;AC)(A;OICIIOID;GXGR;;;AC)(A;ID;0x1200a9;;;S-1-15-2-2)(A;OICIIOID;GXGR;;;S-1-15-2-2)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-10-09T20:18:58.9630936Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\frontend\\node_modules",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\frontend\\dist",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\src-tauri\\target\\core-sidecar",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\src-tauri\\target\\pyinstaller-work",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\src-tauri\\gen\\schemas",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-10-09T20:18:57.7666233Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\apps\\desktop\\src-tauri\\permissions\\autogenerated",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-10-09T20:18:57.7696588Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\verification\\P02\\cargo-target",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\npm-cache",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\cargo-home",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\tmp\\appdata",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\tmp\\home",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\python-cache",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\pyinstaller-config",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\verification\\P02\\tmp\\smoke-readonly-probe",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "Directory",
      "length": null,
      "lastWriteUtc": "2026-10-09T22:41:51.2625268Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\verification\\P02\\tmp\\lpac-write-control",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\verification\\P02\\tmp\\lpac-write-deny-control",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\P02-scratch-build-source\\verification\\P02\\tmp\\lpac-write-control\\p02-lpac-write-canary-20261010.bin",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "ReadOnly, Directory",
      "length": null,
      "lastWriteUtc": "2026-10-10T07:31:57.9068622Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:AI(A;OICI;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;OICI;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga.worktrees",
      "state": "PRESENT",
      "kind": "Directory",
      "attributes": "ReadOnly, Directory",
      "length": null,
      "lastWriteUtc": "2026-10-10T07:04:24.2055323Z",
      "reparsePoint": false,
      "aclState": "READ",
      "owner": "HOME-MY\\49745",
      "sddl": "O:S-1-5-21-2196946971-914346751-4210154634-1001G:S-1-5-21-2196946971-914346751-4210154634-1001D:(A;ID;FA;;;BA)(A;OICIIOID;GA;;;BA)(A;ID;FA;;;SY)(A;OICIIOID;GA;;;SY)(A;ID;0x1301bf;;;AU)(A;OICIIOID;SDGXGWGR;;;AU)(A;ID;0x1200a9;;;BU)(A;OICIIOID;GXGR;;;BU)",
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\manifest-reference.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\preflight.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\pre-protected-files.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\pre-authorized-outputs.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\create-result.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\post-isolation.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\post-protected-files.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\post-authorized-outputs.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\comparison.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    },
    {
      "path": "G:\\CODEX\\New Manga\\verification\\P02\\p02-owner-risk-waiver-evidence-20261010\\incident.json",
      "state": "ABSENT",
      "kind": null,
      "attributes": null,
      "length": null,
      "lastWriteUtc": null,
      "reparsePoint": null,
      "aclState": "NOT_QUERIED",
      "owner": null,
      "sddl": null,
      "error": null
    }
  ],
  "registry": [
    {
      "atUtc": "2026-10-10T23:16:34.1934991Z",
      "object": "HKLM\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting\\LocalDumps",
      "view": "Default",
      "state": "PRESENT",
      "writableRequested": false,
      "error": null
    },
    {
      "atUtc": "2026-10-10T23:16:34.1955967Z",
      "object": "HKCU\\SOFTWARE\\Microsoft\\Windows\\Windows Error Reporting\\LocalDumps",
      "view": "Default",
      "state": "ABSENT",
      "writableRequested": false,
      "error": null
    }
  ],
  "wer": [
    {
      "atUtc": "2026-10-10T23:16:34.2036199Z",
      "object": "C:\\Users\\49745\\AppData\\Local\\CrashDumps",
      "state": "ENUMERATED_DIRECT_CHILDREN",
      "childCount": 10,
      "children": [
        {
          "name": "git.exe.47924.dmp",
          "kind": "File",
          "length": 631425,
          "lastWriteUtc": "2026-09-13T11:14:46.7476717Z"
        },
        {
          "name": "IconExp.exe.45704.dmp",
          "kind": "File",
          "length": 2722000,
          "lastWriteUtc": "2026-09-12T07:57:27.3854356Z"
        },
        {
          "name": "NVIDIA Broadcast.exe.10648.dmp",
          "kind": "File",
          "length": 604054177,
          "lastWriteUtc": "2026-09-11T13:12:52.5065872Z"
        },
        {
          "name": "NVIDIA Broadcast.exe.11560.dmp",
          "kind": "File",
          "length": 40173730,
          "lastWriteUtc": "2026-09-12T11:47:59.0798326Z"
        },
        {
          "name": "python.exe.31380.dmp",
          "kind": "File",
          "length": 5310717,
          "lastWriteUtc": "2026-09-11T04:30:18.0174295Z"
        },
        {
          "name": "python.exe.36724.dmp",
          "kind": "File",
          "length": 5307457,
          "lastWriteUtc": "2026-09-11T04:30:35.8115666Z"
        },
        {
          "name": "python.exe.45992.dmp",
          "kind": "File",
          "length": 2626557,
          "lastWriteUtc": "2026-09-19T08:49:45.8153721Z"
        },
        {
          "name": "python.exe.7732.dmp",
          "kind": "File",
          "length": 5305325,
          "lastWriteUtc": "2026-09-11T04:31:10.4951350Z"
        },
        {
          "name": "QQ.exe.45948.dmp",
          "kind": "File",
          "length": 9563066,
          "lastWriteUtc": "2026-09-13T11:17:00.4292237Z"
        },
        {
          "name": "webview_support_browser.exe.42576.dmp",
          "kind": "File",
          "length": 6195467,
          "lastWriteUtc": "2026-09-16T12:35:46.4110178Z"
        }
      ],
      "error": null
    },
    {
      "atUtc": "2026-10-10T23:16:34.2060242Z",
      "object": "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportQueue",
      "state": "ENUMERATED_DIRECT_CHILDREN",
      "childCount": 11,
      "children": [
        {
          "name": "Kernel_116_252f5bba26ede1fd2fd6282b3582596a465914_00000000_e90dfb5a-a8dd-44c7-8ca0-59acad730919",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.1375468Z"
        },
        {
          "name": "Kernel_116_7c40cfb78427ab856d1a6edc778922fed386d2_00000000_06fcb79e-ccd2-466b-bc0c-e5ae291fef62",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.0847757Z"
        },
        {
          "name": "Kernel_116_a4cd499e36af851fd914ab39ec591d21d932e5c4_00000000_943a9053-b912-44b8-bec2-90c62cbc1208",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.0347120Z"
        },
        {
          "name": "Kernel_116_e42457ca7bc3c610fa6174ed5169c4298a773d2_00000000_04f0340c-ac24-436a-80e5-94f33c06deae",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:22.9997136Z"
        },
        {
          "name": "Kernel_117_bdb1effc8331fabff4ffffd9c589f9fd21e516_00000000_13bd6f3c-80a5-40dd-9814-d435de447f9b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.0514018Z"
        },
        {
          "name": "Kernel_141_9d557966ba7548b4215c8327b2196c542bb67179_00000000_97ae1483-5b55-4b8c-9862-0fa1aa532605",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.0164530Z"
        },
        {
          "name": "Kernel_141_b9ec20d61d33311acd10abec8616bf9093bc9b13_00000000_9ecbec1b-2736-4924-b175-59415beac77f",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.0681141Z"
        },
        {
          "name": "Kernel_141_da863cc1c3a9ff791df5d3e741e2d9ba3797bd5_00000000_2a47f34b-2f6f-4028-a134-7c8facbc82e3",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:22.9814714Z"
        },
        {
          "name": "Kernel_141_ee7b412488a64cc36a8d5b2c7d951c04d2eef67_00000000_598538a1-90f9-4094-85ee-c8f68099a3c3",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.1192593Z"
        },
        {
          "name": "Kernel_1a8_57f07d87e3f91b49fe232dde72bf1889154fd0_00000000_36cced1f-83b0-4de1-ab57-0dccbed4053b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T20:32:23.1014853Z"
        },
        {
          "name": "a1f57455-8af6-49ae-bc92-4f60b1c1d6f4",
          "kind": "File",
          "length": 0,
          "lastWriteUtc": "2026-08-08T13:10:26.2137749Z"
        }
      ],
      "error": null
    },
    {
      "atUtc": "2026-10-10T23:16:34.2085287Z",
      "object": "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive",
      "state": "ENUMERATED_DIRECT_CHILDREN",
      "childCount": 63,
      "children": [
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_0a27b85d-5d54-4966-a5e1-50c61d9095a0",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:31:04.9110664Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_0c2cd102-1fe6-42b1-aa3b-eb8fd477d281",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:26.7592955Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_139d5da2-6a56-4d55-b9f5-568d05111cab",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:20.6480139Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_20b36176-ad22-4327-afa5-cce9d1983b1e",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:27.5752099Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_25f9ebc4-dc82-449a-8cde-8ed25db0cfdf",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:30:13.7223609Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_36496ca4-c272-4b87-a06a-b5526e63e83c",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:08.1013536Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_3e113e80-b1cb-47dd-b53c-b556f6b75096",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:27.0597326Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_3eae99cc-94e1-41ab-8bfd-4f0ea932cd32",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:54.0690818Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_416ba212-6ada-4226-b12b-9e614bb3eee5",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:59.3968238Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_451d340d-f40f-4a02-a2d9-b5c8be131af6",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:30:01.0149633Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_4d27d9b0-2b5e-4986-8907-bd3d0d414f7b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:48.5992336Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_621fd2cc-0afc-45cd-bd8f-2f4a73a7a8ca",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:31:10.4348250Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_6a81e71c-48f0-4b85-b55f-1e3cd7b0494c",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:32:05.7692888Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_727cc88a-7a06-4f1c-b736-5a08b79165c2",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:32.3835093Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_801a44aa-c436-4ed6-b32b-28969e4f94cd",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:34.7852624Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_872b3409-5fd9-40dc-aaca-53701bf687dc",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:59.6054505Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_8d4e321a-5cc6-437b-8d63-55f573777b9d",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:47.7055763Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_a7c8946b-1df5-4a24-8e22-2dee09a00186",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:37.7064175Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_a82c2605-437d-4207-95a0-96aa02b983fa",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:32:18.7904843Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_afc288ce-101d-43f6-a049-23a3442a999b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:32:12.2226477Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_bd0d40bf-515c-4411-83cb-af8b1fcebcae",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:38.9257081Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_be8e253d-b63b-4b9a-abd2-855d64902548",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:20.5176961Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c1b54d11-2ba6-4ea4-ab38-f138ae2e45bb",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:14.4464419Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c2c1b63b-682d-4145-a71c-d9ce01c02a6c",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:30:08.1098735Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_c4cf169a-9387-4cf5-a49c-0875afc182f2",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:32.6750445Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_ca7c8a76-1960-4ad2-b614-865fd8b8ecee",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:41.2742998Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_cba88770-b652-47b5-a8bd-c56469a0ab6a",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:28:59.9743632Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_d0cde7c8-20c4-46a0-8424-a7cbea33a08a",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:21.8002206Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_df492d7d-653b-4df7-83ce-a455dcea2cdd",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:46.2239366Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e28952e0-8a22-4086-9c6a-dbf6409107c1",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T00:31:52.5302113Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e2f73159-d221-4d94-be99-a9c1b6970a76",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T03:29:54.6951457Z"
        },
        {
          "name": "AppCrash_gchsvc.exe_ddc08a57a1c4faca22fc30ea3c2ea535b3fbf1_0167f4ec_e87f7a10-3217-4b9b-b054-ed51f2797cfc",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T00:30:43.2392631Z"
        },
        {
          "name": "AppHang_explorer.exe_99e2b031e6dddf259f8a81d89270bed39b55776_f32e9b07_c037e330-a16e-4d64-921e-d139983b6cba",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-24T02:02:55.7392518Z"
        },
        {
          "name": "Critical_10.0.26100.9441__fec76a833170a95749465064335b469514df6ecc_00000000_4a4e019d-bd8d-4192-a5da-7ab139364512",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-04T17:08:47.4003404Z"
        },
        {
          "name": "Critical_10.0.26100.9539__4aa07db12c38ead69a39ba6e89673bd3cd2d82f_00000000_9e3feb21-c220-4a50-8440-56ad6c68ec10",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-04T17:11:54.1904695Z"
        },
        {
          "name": "NonCritical_Acquisition;setu_10a9e1b77f1cfb41be5a53b1622d97a95e136fc_00000000_868cf961-8ec0-4c13-b6ea-24ebacd3d15a",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-10T03:02:00.3258465Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_020897c6-6aec-4130-9c3d-3a32c220f856",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-27T02:40:08.4688300Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_081b0e82-cdc7-4e7b-8d0e-6a7e892e6880",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-27T02:40:05.5958991Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_0c7d0971-c525-4b35-8ad4-1bf349f59d82",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T00:53:42.6059660Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_aff38167-cca1-4740-9d68-52defadfb5bb",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-24T02:13:52.6179062Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_b0453351-0ace-454c-a401-f23c27764f9f",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-28T00:53:46.4746686Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_3b10b5b04029a6e2d9be19318f6bee71c28029_00000000_ced2de43-28f4-478b-8203-20c9d71104d8",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-26T03:36:10.7476358Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_0a950a75-8930-4072-b3bd-2fca431f7ee1",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T00:37:24.5775229Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_0e45ecab-4ebc-48b8-a226-cd1a4c0e3ea7",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T16:05:05.4997680Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_2ab47d7b-985e-4a0f-9e56-8146f66dbcfe",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T00:38:03.0301143Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_73ad3f92-1290-49ce-adf5-07b4778d2cad",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T02:27:03.0907183Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_8df36713-7755-40d5-b409-4e30d2aa0c57",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T16:05:09.4428265Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_c536896b-6ab9-4afa-816e-de369ac376b5",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-09T02:27:06.1403241Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_f0bab6a2-4d2e-4db4-b512-c1c653c14060",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-08T12:41:28.3903364Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_ab656ed3b47dd697992d81536a7af51dadfa9d_00000000_fc29130d-8759-44e9-9da5-eb91c5ad7492",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-08T12:41:31.7786632Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_23920e8a-810f-4bfe-a56b-1bb23a950b79",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-04T14:21:34.6960307Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_6576fc77-3ca7-4524-8f2f-e95d6ee8003a",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-06T12:31:38.5402461Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_785f4bfc-1fc3-40e2-a849-56083221561f",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-06T12:31:34.2947450Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_7b649f07-5a9b-4c8b-9d8b-9956a151599b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-06T16:43:58.0181697Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_c0409289-6f79-49a5-8f64-f391308d8f11",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-04T14:21:38.6167579Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_cec0441169b83bbdc55410a5851c81251570e040_00000000_f5ab8ccb-5285-4034-9ec8-5d2a257fd272",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-06T16:43:53.6089444Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_0fed71b5-2f58-4c16-a6ec-b3e2c21022fe",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T10:01:20.7707434Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_1e44f95d-1b46-4bb6-9f83-faa42c1c94d6",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T10:57:32.5285622Z"
        },
        {
          "name": "NonCritical_MicrosoftEdgeUpd_f3e29554c0ac6cef2a1bb87aca562aa73bc235ae_00000000_81d46a04-63c2-43fc-8e84-01375d72e536",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-30T10:01:27.3352393Z"
        },
        {
          "name": "NonCritical_msedgewebview2se_9e6316f94d964e7fac18ab9bfebf707866e85_00000000_ddeaca41-43eb-4592-b218-5161713cf0ab",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-29T04:50:15.3883374Z"
        },
        {
          "name": "NonCritical_Update;MoUpdateO_2dd07164693f3daeb07c71931301f91b72b4037_00000000_b195c1db-526a-4765-830b-bbe7d31359a0",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-02T16:36:56.5639161Z"
        },
        {
          "name": "NonCritical_Update;MoUpdateO_9562b866f34ec3cfbb3a18b337a6b6638b5ac048_00000000_2c933f8f-ab12-4fd7-9c4b-2fce4ab5228b",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-10-02T16:40:13.7697670Z"
        },
        {
          "name": "NonCritical_Update;UsoClient_8a6ddfd8a3fdc7f8c5e8c5332fc6ad23f5c8ae7_00000000_7709780c-122a-4b4c-82a1-bea197cb1a80",
          "kind": "Directory",
          "length": null,
          "lastWriteUtc": "2026-09-24T02:13:05.7159121Z"
        }
      ],
      "error": null
    }
  ],
  "hashesPre": [
    {
      "path": "AGENTS.md",
      "sha256": "46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501",
      "state": "HASHED"
    },
    {
      "path": "doc/REBASELINE_PLAN.md",
      "sha256": "ABC9EFBE1FBA22F106D1CBCE6C537FDB3C760FAEE331A1B14447882AC925964E",
      "state": "HASHED"
    },
    {
      "path": "doc/00_INDEX.md",
      "sha256": "5F183225A9C3464E2F1FDA2852032A07F93FEF75A8540AE0B823FDA72F40EB39",
      "state": "HASHED"
    },
    {
      "path": "doc/STATUS.md",
      "sha256": "1163E219025AA158601E8D20F19A8E3E1E2A4AEF5D1CED0BA83909DC1C6B1C7A",
      "state": "HASHED"
    },
    {
      "path": "doc/09_COLLABORATION.md",
      "sha256": "DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D",
      "state": "HASHED"
    },
    {
      "path": "doc/tasks/P02.md",
      "sha256": "4B34107A1C3A8042D86236B8B2CDDAC33533D0CBF51B399A0BB66EDCCEAEB9B4",
      "state": "HASHED"
    },
    {
      "path": "doc/tasks/P02PRE-R0.md",
      "sha256": "FB7E6D98098EF433C901179E7A441D371D22E7024DF8F629AC88149859AC7641",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md",
      "sha256": "C3CDC95EED8B2C6AC3550266F97877CC074C53E63199C9151B67320C700F32A8",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md",
      "sha256": "626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md",
      "sha256": "A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md",
      "sha256": "01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md",
      "sha256": "15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F",
      "state": "HASHED"
    },
    {
      "path": ".git/index",
      "sha256": "214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C",
      "state": "HASHED"
    }
  ],
  "hashesPost": [
    {
      "path": "AGENTS.md",
      "sha256": "46357DC8FA0153429C394C057BF5E51A76EF34BD6B11DACCDDC272CB90E53501",
      "state": "HASHED"
    },
    {
      "path": "doc/REBASELINE_PLAN.md",
      "sha256": "ABC9EFBE1FBA22F106D1CBCE6C537FDB3C760FAEE331A1B14447882AC925964E",
      "state": "HASHED"
    },
    {
      "path": "doc/00_INDEX.md",
      "sha256": "5F183225A9C3464E2F1FDA2852032A07F93FEF75A8540AE0B823FDA72F40EB39",
      "state": "HASHED"
    },
    {
      "path": "doc/STATUS.md",
      "sha256": "1163E219025AA158601E8D20F19A8E3E1E2A4AEF5D1CED0BA83909DC1C6B1C7A",
      "state": "HASHED"
    },
    {
      "path": "doc/09_COLLABORATION.md",
      "sha256": "DAFBD1F65DFCE967F50561926C9CC92F2A7DAAE826C33F375A549573372ECD9D",
      "state": "HASHED"
    },
    {
      "path": "doc/tasks/P02.md",
      "sha256": "4B34107A1C3A8042D86236B8B2CDDAC33533D0CBF51B399A0BB66EDCCEAEB9B4",
      "state": "HASHED"
    },
    {
      "path": "doc/tasks/P02PRE-R0.md",
      "sha256": "FB7E6D98098EF433C901179E7A441D371D22E7024DF8F629AC88149859AC7641",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md",
      "sha256": "C3CDC95EED8B2C6AC3550266F97877CC074C53E63199C9151B67320C700F32A8",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md",
      "sha256": "626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md",
      "sha256": "A8C0C124C5EEF391CDBB44CA20B1169CFABC99E94C92E0C1AC798450E7DAF9A8",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md",
      "sha256": "01E556448BA2A5CF1E68F28A0C91D1FDD71EE28EB2CB5ED583983348BFFE9159",
      "state": "HASHED"
    },
    {
      "path": "verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md",
      "sha256": "15736303C3241E0C14106EFCAFB8583DF719A566D1879B7A7144B6D079A04A1F",
      "state": "HASHED"
    },
    {
      "path": ".git/index",
      "sha256": "214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C",
      "state": "HASHED"
    }
  ],
  "counts": {
    "paths": {
      "PRESENT": 17,
      "ABSENT": 25
    },
    "wer": [
      {
        "object": "C:\\Users\\49745\\AppData\\Local\\CrashDumps",
        "state": "ENUMERATED_DIRECT_CHILDREN",
        "childCount": 10
      },
      {
        "object": "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportQueue",
        "state": "ENUMERATED_DIRECT_CHILDREN",
        "childCount": 11
      },
      {
        "object": "C:\\ProgramData\\Microsoft\\Windows\\WER\\ReportArchive",
        "state": "ENUMERATED_DIRECT_CHILDREN",
        "childCount": 63
      }
    ],
    "hashesEqual": true
  }
}
```

