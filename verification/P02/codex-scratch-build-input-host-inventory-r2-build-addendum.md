# P02 Build Gate 输入清单增补 r2（Build-only Git + Smoke/Build 共用 VS/SDK）

- 记录时间：2026-10-09（Asia/Shanghai）。Owner=Codex；范围=verification/P02/**。本清单为未来 Build Gate 固定只读工具链输入，不授权 build，也不改 Smoke XML：Git for Windows 两个根只属于 Build；Visual Studio BuildTools、Installer 与 Windows SDK 根已在 Smoke 内，属于 Smoke/Build 共用只读映射。
- 证据来源：本机非提权 PowerShell 的只读文件属性、版本、SHA-256 检查。Build 启动前必须再次检查实际 HostFolder 的完整 manifest、reparse points、文件数、大小和 hash；值变化即 BLOCKED/Review pending。

## Git for Windows（Build config only）

| HostFolder | SandboxFolder | 证据 |
|---|---|---|
| C:\Program Files\Git\cmd | C:\P02\inputs\git\cmd | git.exe 2.52.0.windows.1，46,480 bytes，SHA-256=3CBD024D9D11EF08BD6A0CB5A973613C50825B4952BC6006F3F4222F436091E5 |
| C:\Program Files\Git\mingw64 | C:\P02\inputs\git\mingw64 | 运行时支持树；其中 mingw64\bin\git.exe 2.52.0.windows.1，4,321,168 bytes，SHA-256=FC0F1CAE1304FCDCF4D0749F421C5ED21471EFC856301F92F56D4B844BE84363 |

以上 HostFolder 均需 ReadOnly=true，当前冻结的 r3 Smoke config 不含这两个 Git roots。Build 阶段的独立 config 需加这 2 项并单独冻结/Review config hash。Guest PATH 需加入 C:\P02\inputs\git\cmd 与 C:\P02\inputs\git\mingw64\bin；GIT_EXEC_PATH 指向 C:\P02\inputs\git\mingw64\libexec\git-core。preflight 必须确认 git --version 与上述版本一致，git -C C:\P02\scratch rev-parse HEAD 返回固定 source commit。Git 不读取、不映射 user profile、global config、凭据；若本机包装器要求未登记的 Git 目录/配置，立即 BLOCKED。

## Visual Studio / Windows SDK（Smoke 与未来 Build 共用只读映射）

BuildTools、Installer 与 SDK 根目录已在 Smoke mapping 表中列出，是 Smoke 与未来 Build 的共用只读 HostFolder；Build config 复用这些路径，不另加重复映射。此前把这些根标为 Build-only 是本文件的文案错误。

| 工具 | Host path（映射至同路径） | 版本 | 大小 | SHA-256 |
|---|---|---|---:|---|
| cl.exe | C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe | 19.44.35221.0 | 677,968 | 6CADDDCA8C19E76991BBB44DFF2EAB5CAB6807F9145E8BCE9A800235A5975E51 |
| link.exe | C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\link.exe | 14.44.35221.0 | 3,252,808 | 85DFBEB6E52282FBC4F34C015709754677FD170F11768C7098FAB913A6C570DF |
| rc.exe | C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\rc.exe | 10.0.26100.8249 | 55,736 | 65DB0D7B4F10BA0F55973FD9356543A556DA9EC1C777A0C05F05A0329C8A100A |
| mt.exe | C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\mt.exe | 10.0.26100.8249 | 1,972,672 | FB1AB75294B78619BD6AC8CADF30CB95BEFBC7324703CBE2654EF800DDD2BF4D |

BuildTools release directory=14.44.35207; Windows SDK version=10.0.26100.0. HostFolder roots are ReadOnly=true, shared between Smoke and future Build, and must be verified recursively before Build. Do not rely on host PATH, host environment variables, or guest VS registry discovery.

## 固定的 Build guest 环境

Build config 通过后，在 guest 执行前按上表固定以下环境（都只指向既有只读映射）：

- VCToolsInstallDir=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\
- WindowsSdkDir=C:\Program Files (x86)\Windows Kits\10\
- WindowsSDKVersion=10.0.26100.0\
- PATH 前置 Git cmd/mingw64\bin、MSVC bin\Hostx64\x64、Windows SDK bin\10.0.26100.0\x64。
- INCLUDE 固定为 MSVC include 与 SDK Include\10.0.26100.0 下的 ucrt、shared、um、winrt、cppwinrt。
- LIB 固定为 MSVC lib\x64 与 SDK Lib\10.0.26100.0 下的 um\x64、ucrt\x64。
- GIT_EXEC_PATH 固定为上述 guest Git mapping 的 mingw64\libexec\git-core。

Build preflight 要记录 guest where.exe git/cl.exe/link.exe/rc.exe/mt.exe 的绝对路径、版本与 SHA-256，并与本清单逐项匹配；同时记录 Git HEAD/tree、cargo -Vv、rustc -Vv 及有效 PATH/INCLUDE/LIB 的 path-only 结果。任何工具缺失、路径/哈希不符、链接库目录缺失或实际 cargo/link 解析未验证，均为 BLOCKED；不能依赖 %USERPROFILE%、注册表探测或 host 安装状态猜测。

这些共用 VS/SDK roots 在 Smoke 与 Build 中各映射一次；仅 Git for Windows 两个根为 Build-only mappings。Build config 因 Git、配置字段和资源门槛不同而单独冻结/hash；不得重复添加 VS/SDK roots。


## Separate Build config gate

This inventory supports a future separately reviewed Build config. The two Git for Windows roots are Build-only; the Visual Studio BuildTools, Installer, and Windows SDK roots listed above already exist in the r3 Smoke config and are shared read-only inputs. Reuse each shared HostFolder mapping once; do not duplicate it. Do not add the Build-only Git roots to Smoke. Each config, its distinct fields/resource limits, canonical bytes/hash, PATH/INCLUDE/LIB and tool-resolution evidence requires its own preflight and independent Review before any product build. No observed host path/version/hash in this addendum proves the guest can resolve the toolchain; guest resolution remains `NOT_VERIFIED` until an authorized Build Gate.
