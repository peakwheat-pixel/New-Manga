# P02 Process Isolation Host Input Inventory r1

- Captured: 2026-10-09 (Asia/Shanghai), read-only host inspection.
- Scope: path existence, installed tool versions, and selected executable hashes. No package install, build, network probe, Sandbox, or content modification.
- Planned unique writable HostFolder: G:\CODEX\P02-scratch-build-source. Test-Path returned false; recheck immediately before creation. A preexisting path blocks the task; do not choose another path without review.
- Repository source remains G:\CODEX\New Manga at live commit 549a6544f0be1eec66c09ece393fd1a409f10bf3 with 203 dirty/untracked entries. The planned clone must contain only commit 7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a and its committed tree.

## HostFolder map to freeze in the pre-start manifest

| Purpose | HostFolder (exact current path) | SandboxFolder | Access |
|---|---|---|---|
| Task scratch clone | G:\CODEX\P02-scratch-build-source | C:\P02\scratch | ReadOnly=false, the only writable mapping |
| Python base interpreter | C:\Users\49745\AppData\Local\Programs\Python\Python312 | same exact path, required by pyvenv.cfg | ReadOnly=true |
| Pinned sidecar venv | G:\CODEX\New Manga.task-envs\m2ac5-build | C:\P02\inputs\python-venv | ReadOnly=true; pass this guest path as -PythonExe |
| Detector weights | G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector | C:\P02\inputs\weights\detector | ReadOnly=true; pass this guest path as -WeightsSource |
| SFX weights | G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b | C:\P02\inputs\weights\sfx | ReadOnly=true; pass this guest path as -SfxWeightsSource |
| Node/npm | E:\Program Files\nodejs | C:\P02\inputs\nodejs | ReadOnly=true; invoke its npm.cmd explicitly |
| Rust stable MSVC toolchain | C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc | C:\P02\inputs\rust-toolchain | ReadOnly=true; use its exact cargo.exe/rustc.exe paths |
| Visual Studio Build Tools | C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools | same exact path | ReadOnly=true |
| Visual Studio Installer (vswhere) | C:\Program Files (x86)\Microsoft Visual Studio\Installer | same exact path | ReadOnly=true |
| Windows SDK | C:\Program Files (x86)\Windows Kits\10 | same exact path | ReadOnly=true; inventory contains SDK 10.0.26100.0 |

All listed HostFolders existed at capture time. The pre-start manifest must recheck every path, bind exact HostFolder/SandboxFolder/readonly values, hash the files actually read by the pinned build, enumerate sizes and hashes for mapped files, and reject reparse points that escape their mapped root. No whole user profile, AppData root, root checkout, shared .git, credentials, or Agent worktree is mapped.

## Offline cache inputs

- npm config get cache returned C:\Users\49745\AppData\Local\npm-cache; the directory exists. Seed only its _cacache contents into the clone’s verification/P02/npm-cache; never copy .npmrc or logs. Record source and destination inventories and hashes.
- C:\Users\49745\.cargo\registry exists. C:\Users\49745\.cargo\git did not exist at capture time. Seed only existing registry and git cache trees into clone verification/P02/cargo-home; exclude .cargo/credentials*, .cargo/config*, and bin. If locked Cargo inputs are absent, stop before build; never enable network.
- These source cache locations are pre-start copy inputs only; they are not HostFolder mappings. Python packages are read from the pinned read-only venv. Do not map package caches or user profile folders into Sandbox.
- Package-cache coverage is not proved by directory presence. The later Build Gate must bind the copied cache tree hashes and use npm ci --offline plus cargo build --locked --offline; a missing package stops inside scratch.

## Selected current executable identities

| File | SHA-256 | Size |
|---|---|---:|
| C:\Users\49745\AppData\Local\Programs\Python\Python312\python.exe | 15b41a488c356c0e331facdea6c836a6cec021f12d5fde9844e7ca4a1aa0361a | 103192 |
| G:\CODEX\New Manga.task-envs\m2ac5-build\Scripts\python.exe | 864530d708039551a2c672ddd65e5900fbc08b0981479679723a5b468f8082bc | 274712 |
| E:\Program Files\nodejs\node.exe | 3331e1ffe19874215472217c5e94f5a0c6d8e18c4ac7111d3937aa0ad5e9b4a5 | 91694408 |
| E:\Program Files\nodejs\npm.cmd | 21b46c69ad6e2f231f02a9e120f4ba6c8e75fef5a45637103002eab99f888ab8 | 538 |
| Rust stable cargo.exe | c37545ec61d48d31bdefce53280ecab61c4ea54eaace372fac6a0316c6e165d9 | 31435776 |
| Rust stable rustc.exe | ca9988af88b1463f6857fdfe909299fee50a63260b3e5f7dbcb5b4d3318b27bc | 110592 |
| C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat | 6b516d8fcf543c14b2d861e1f45661e0029230fe0dc48e86ce78522801822209 | 39 |
| C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe | c54f3b7c9164ea9a0db8641e81ecdda80c2664ef5a47c4191406f848cc07c662 | 469456 |

The venv pyvenv.cfg is Python 3.12.3, include-system-site-packages=false, home=C:\Users\49745\AppData\Local\Programs\Python\Python312; the base/venv hashes match the previously pinned plan values at capture time. Current host versions: Node v24.15.0, npm 12.0.1, Rust 1.98.1 (x86_64-pc-windows-msvc). cl.exe and link.exe were not in the interactive host shell PATH; VS Build Tools and Windows SDK roots exist, but guest toolchain resolution is not verified.

## Evidence limits and next recheck

- No recursive directory hash or secret scan was performed in this read-only inventory; the later pre-start manifest must perform both and pin selected build inputs. This Markdown file is only a path/version observation, not approval to create mappings or launch Sandbox.
- wsb host shell earlier reported version 0.8.107.0 and no running session; the DSH restricted shell could not access its temp path. Recheck in the actual non-elevated interactive host PowerShell used for smoke.
- Containers-DisposableClientVM feature state remains UNKNOWN because the read-only feature query requires elevation. Do not elevate or enable the feature; without current proof that it is enabled, smoke stays BLOCKED.

\n