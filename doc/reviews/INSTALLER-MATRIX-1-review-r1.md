# INSTALLER-MATRIX-1 Review r1（独立只读复核）

- **verdict**：**REJECT**（本 head；机制结论可复用，元数据/来源字段必须返修后重审）
- **审查者身份与来源**：DSH 独立上下文 fresh subagent `review-installer`（由 root agent `lead` 派发；本会话未参与 INSTALLER-MATRIX-1 的实现、返修、Handoff 或证据生成，未参与任何前置 Task）
- **被审 head**：`71cecb95a10c42ffe02d1396ab065e1fc9c43ca9`（`feat(gate4): 安装/卸载矩阵跑通`），基线 `fe7da5d9261e999de714519e393a4b9c28ba3fa6`
- **审查方式**：只读。未重装/卸载、未改产物、未 `git add/commit/push/reset/checkout`。唯一写入 = 本文件。
- **审查时间**：2026-11-15T04:45Z 起（Asia/Shanghai）

---

## 0. 结论先行

1. **被问的三组哈希/尺寸全部为真**：我逐项重算，`NewManga.App.exe`、`core_service.exe`、`setup.exe` 的 sha256 与字节数与声明**完全一致**；stage 汇总（1037 files / 889,352,697 B）与 `stage.manifest_sha256=f195677a…339a` 也被我用 `build-installer.ps1` 同款算法**逐字节复现**。
2. **但 `repo_head` 不可信**：`app_build.repo_head=fe7da5d92` **是错的** —— 该 exe 内嵌 `ProductVersion=0.1.1+5dda04437d68baf304b4364a3a73f9dfa217d943`，且 `verification/RELEASE-PACKAGE-PROBE-1/manifest-summary.json` 记录的 `git_head` 就是 `5dda04437…`（18:56Z 生成）；`fe7da5d92` 直到 20:33Z 才存在。两 head 之间有 **7 个 `apps/desktop-avalonia/**` 文件变更（其中 3 个产品源文件）**，因此这个包**不含**当前 head 的传输层改动。
3. **"逐字节未变"没有依据**：证据只有"文件数 + 总字节"，没有文件清单/哈希；`data-root-before.txt` 记的是**污染前**的 524 files / 210,443,772 B，**不是** AC6 的 before（532 files / 967,726,273 B）。AC6 卡面自己要求"文件清单+哈希对比"，未做。
4. **staleness 已经不是风险，是既成事实**：包内 `app/VERSION.json` 与 `package-manifest.json` **仍是 2026-10-28 的 0.1.0 副本**（版本、sidecar head、exe hash 全旧），与新的根 `VERSION.json` 自相矛盾；且包里实际装了 **632.6 MB 三份 ONNX**，而 `VERSION.json` 声明 `models_bundled:false` / "base package ships NO models" / `bundled_weights_license:"none"`。
5. **没有守卫**：仓库内没有任何脚本/测试重算 `VERSION.json` 与产物并比对；`build-installer.ps1` 只计算 stage 指纹、不校验元数据。**如果今后 stage 内容变了而 `VERSION.json` 没更新，不会有人发现** —— 本次就是一例（见 §5）。

---

## 1. 我重算的哈希与文件清单（实际值 vs 声明值）

命令：`Get-FileHash -Algorithm SHA256` + `(Get-Item).Length`；stage 指纹按 `apps/desktop-avalonia/scripts/build-installer.ps1:129-141` 的算法重算（`相对路径\t字节\tsha256`，按 FullName 排序，`\n` 连接 + 尾部 `\n`，UTF-8）。

| 对象 | 实测 | 声明（来源） | 判定 |
|---|---|---|---|
| `stage\app\NewManga.App.exe` | sha256 `ea01c8c77358f35b0f15f43a0a496dfd3bf1a0e1b472adf9c55c65f0a28c76ed`，**99,554,850 B**，mtime `2026-11-14T18:55:55.5447135Z` | `VERSION.json app_build.exe_sha256/exe_bytes`（同值） | ✅ **完全一致** |
| `stage\app\core-sidecar\core_service.exe` | sha256 `6050881163753d32eca2fb1c0c824d9de7852bf62fb808926f5b6fc74a6b52ee`，**400,098 B**，mtime `2026-11-14T19:16:55.3503345Z` | `sidecar_build.core_service_sha256/_bytes/_built_at_utc`（同值） | ✅ **一致（含 mtime）** |
| `out\NewManga-0.1.1-setup.exe` | sha256 `3e6dcb1f6d8d03c268e6a75c6d6afc6ab52cfe0e91c70a54e1e15f37b796650a`，**652,083,323 B** | README §1 / `build-info.json` | ✅ **一致** |
| stage 汇总 | **1037 files / 889,352,697 B**（848.15 MiB） | `build-info.stage.file_count/bytes` | ✅ |
| stage 指纹 `manifest_sha256` | **`f195677a3d18d9b09eef6a928a0df8a94bbb179145968182bd611905fa28939a`** | `build-info.stage.manifest_sha256` | ✅ **逐字节复现** |
| `install_size_kb` | `ceil(889,352,697/1024) = 868,509` | `build-info` | ✅ |
| `C:\Program Files (x86)\NSIS\makensis.exe` | sha256 `4ec390d0f96f9728507fbc2f4e91311dd90bfc6c8ddfe2159357b3651ae151c0`（2,560 B） | `build-info.toolchain.makensis_sha256` | ✅ |
| setup 签名 | `Get-AuthenticodeSignature` → **NotSigned** | README §6 / build-info | ✅ |
| 用户数据根（当前） | **532 files / 967,726,273 B** | README AC6 "532 files / 967,726,273 B" | ✅ **数字一致** |
| `app_build.repo_head` | exe 内嵌 `0.1.1+5dda04437d68baf304b4364a3a73f9dfa217d943`；probe manifest `git_head=5dda04437…`；exe 构建于 18:55:55Z，`fe7da5d92` 提交于 20:33:42Z | `fe7da5d9261e999de714519e393a4b9c28ba3fa6` | ❌ **不一致** |
| `sidecar_build.repo_head` | `git cat-file -t 6ad457c62ac1264fc8fa82267b06b90cb78f8b50` → **`bad object`**（不是仓库对象）；短哈希 `6ad457c62` 可解析为 `6ad457c625f1551c538b8cc33d5c35798893bfde`（2026-11-15T03:11:38+08:00） | 同一 40 hex 串 | ❌ **完整哈希不存在**（短哈希正确） |
| 仓库内二进制 | `git ls-files verification/INSTALLER-MATRIX-1` = **5 个文本文件**（README/build-info/data-root-before/2 日志） | — | ✅ **无 exe/setup 入库** |
| `startup.log` 的 `[Binding]` | **10 行**：8×`IsEnabled`、1×`ActiveTabLabel`（均指向 `StudioPageViewModel`）+ 1×`'Source'→'CurrentPage.Image'`（Image，Value is null，**不是** StudioPageViewModel） | "6 条以上 / 两类 / 全部指向 StudioPageViewModel" | ⚠️ 数量保守但"全部指向"不成立 |

**关键旁证（stage 指纹算法可信）**：我用同一算法重算得到 `f195677a…339a`，与 `build-info.json` 完全一致；`install_size_kb=868509` 也与 NSIS 日志 `/DINSTALL_SIZE_KB=868509` 一致。这说明**字节级测量本身是诚实、可复现的**——问题不在"量"，在"标注来源"。

---

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC1 stage 就绪** | **PARTIAL / FAIL（来源）** | 结构、体积、许可内容齐全（1037 files / 848.15 MiB 复现）；但 ①`app/NewManga.App.exe` **不是"当前 head 的 publish 产物"**（是 `5dda044` 的，见 §3-F01）；②stage 是 2026-10-28 旧 `AGPL-RELEASE-1` 0.1.0 stage 的**整树复制**：21 个文件仍是旧 mtime，其中 `install.ps1`/`uninstall.ps1`/`UPGRADE.md`/`MANUAL_VERIFY.md` **内容与仓库当前版本不同**，`app/VERSION.json`/`package-manifest.json` 仍是 0.1.0 |
| **AC2 `VERSION.json` 真实** | **FAIL** | 三项实测哈希/尺寸为真（见 §1），但 `app_build.repo_head` 是假的；`sidecar_build.repo_head` 的 40 hex 不是仓库对象；包内另有**两份**与根 `VERSION.json` 冲突的陈旧元数据（`app/VERSION.json`、`package-manifest.json`）；`models_bundled:false` 与实物相反 |
| **AC3 `setup.exe`** | **PASS** | setup 存在、652,083,323 B / `3e6dcb1f…650a` 复现；NSIS 日志总尺寸 652,083,323 一致；`makensis` 路径与 sha256 与 `build-info` 一致；`NotSigned` 属实；`INSTALL_SIZE_KB` 与实际一致（卡面 R3 已规避） |
| **AC4 clean install** | **PASS_WITH_LIMITATION** | **当前残留状态**支持"已装过并已清干净"：`%LOCALAPPDATA%\Programs\NewManga` 不存在、HKCU 无 `New Manga` 卸载项、Start Menu 无相关快捷方式；`.nsi` 的 `File /r`+`WriteUninstaller`+`WriteRegStr`+`CreateShortCut` 与其声明一致。**限制**：`/S` 安装的 exit code、NSIS 自写的安装日志（`$TEMP\NewManga-install-0.1.1.log`）**均未留存，现已不存在**；"exit 0"是声明 |
| **AC5 安装后启动** | **PASS_WITH_LIMITATION** | **可证是安装目录里的 exe**：`smoke2\logs\core_service.stderr.log` 的权重候选路径含 `C:\Users\49745\AppData\Local\Programs\NewManga\app\core-sidecar\...`（由 sidecar 自身位置推导），且 smoke2 日志中**无任何 stage 路径**；`core_service ready`/`host_bridge ready`/`self-check status=Passed`/capabilities 17 条均实见。**限制**：①证据来自**第二次、隔离空数据根**（`--data-root=smoke2\data`）的运行，不是真实数据根；②第一次（真实数据根）运行的 `smoke\logs\host.log` **只有 3 行、无 ready**，未在证据中披露；③"exit 0"无留存 |
| **AC6 卸载 + 用户数据根** | **PASS_WITH_LIMITATION** | 程序目录/HKCU/Start Menu 已被清理（当前实测）；数据根 **532 files / 967,726,273 B 复现一致**，且该根内**最新 mtime = 2026-11-14T20:43:12Z（library.db）**，运行/卸载窗口（≥20:43:32Z）之后**无任何写入**；`.nsi` 卸载段（L151-180）确实**不含** `%APPDATA%\com.newmanga.desktop`。**限制**：①"逐字节未变"无依据（只有 count+bytes，无清单/哈希）；②卡面要求的"文件清单+哈希对比"未做；③`data-root-before.txt` 记的是**污染前**状态，不是 AC6 的 before；④before 值只存在于散文里，无工件 |
| **AC7 四页可达性** | **PASS（NOT_RUN 恰当）** | `git ls-files verification/INSTALLER-MATRIX-1` 只有 5 个文本文件，**无任何截图/图像**；README §5 明确说明"未在打包产物上逐页导航"，并主动声明"headless 四帧证据不能替代"。**没有用 headless 冒充** |
| **AC8 不虚报** | **PASS（字面）** | 二进制全在 workspace/`%LOCALAPPDATA%`，仓库无二进制；README §6 与 commit 都写"条件 4 仍不完整"（sidecar 缺 SFX 权重、unsigned、升级/回退未做）。但包内元数据的虚假声明按 §3-F01/F02/F03 记账 |

---

## 3. Findings

> 无 P0。理由：本卡明确**不**声称条件 4 满足，且机制结论（安装/启动/卸载/数据根）本身已被我独立复现；下述 P1 均可定点返修。

### F-01（P1）`app_build.repo_head` 与二进制不符；包落后当前 head 的 3 个产品源文件
- 实测：exe `ProductVersion = 0.1.1+5dda04437d68baf304b4364a3a73f9dfa217d943`；`verification/RELEASE-PACKAGE-PROBE-1/manifest-summary.json` 的 `git_head` 同为 `5dda04437…`，`artifact_sha256` 就是 `EA01C8C7…76ED`。
- 时间线：exe mtime `18:55:55Z`；`fe7da5d92` 提交于 `20:33:42Z`；`stage/VERSION.json` 改写于 `20:36:08Z`。⇒ 作者在写元数据时用 `git rev-parse HEAD`（=fe7da5d92）填了"构建 head"，而 exe 是 1 小时 40 分前按 `5dda044` 打出来的。
- 差异不是纯文档：`git diff --name-only 5dda04437 fe7da5d92` 有 7 个 `apps/desktop-avalonia/**`，其中产品源码 3 个：`src/NewManga.CoreClient/Bridge/HostBridgeClient.cs`、`src/NewManga.CoreClient/CoreServiceClient.cs`、`src/NewManga.CoreClient/Transport/SidecarProcess.cs`（其余 4 个是测试）。
- 影响：这张卡验证的是 `5dda044` 的包；**PIPE-EXCLUSIVE-TRANSPORT-1 收口后的传输层改动不在包里**。AC1/AC2 都因此不成立。
- 返修：把 `app_build.repo_head` 改成 `5dda04437…`（并加 `packaging_head` 区分），或在冻结 head 重新 publish 并重跑矩阵。

### F-02（P1）包内两份元数据是 0.1.0 陈旧副本，与根 `VERSION.json` 自相矛盾
- `stage\app\VERSION.json`：`version=0.1.0`、`sidecar_build.repo_head=7f0d1dae…`、`core_service_sha256=bde2d866…`、`core_service_bytes=399492`，mtime **2026-10-28T05:16:49Z**。
- `stage\package-manifest.json`：`package=NewManga-0.1.0-win-x64`、`1968 files`、`225,701,934 B`；对新 exe 记 `9aeeb5ed…/30,234,828 B`、对 sidecar 记 `bde2d866…/399,492 B` —— **与实际文件全部不符**；mtime **2026-10-28T05:16:59Z**。
- 根 `VERSION.json` mtime 是 `20:36:08Z`，被改过；这两份**没被改**。`package.ps1:125` 本来会 `Copy-Item` 覆盖 `app/VERSION.json`，说明本 stage **不是**由 `package.ps1` 产出的。
- 影响：安装后会把这套自相矛盾的元数据一起装到 `%LOCALAPPDATA%\Programs\NewManga`（`File /r "${STAGE_DIR}\*.*"`）；`DeviceStatus.Candidates()` 优先读 `app/VERSION.json`，任何读该文件的下游都会拿到 0.1.0 的来源信息。
- 返修：重新生成（或删除）`app/VERSION.json` 与 `package-manifest.json`，并在 stage 校验里加"元数据一致性"检查。

### F-03（P1）`models_bundled:false` / "base ships NO models" 与实物相反；许可口径需裁决
- 实测 stage 内 `app/core-sidecar/models/` 有 **632.6 MB**：`detector/rtdetr-v2-fixed.onnx`（171,618,071 B）、`ocr/.../encoder_model.onnx`（343,454,249 B）、`decoder_model.onnx`（117,480,262 B）+ tokenizer/config 等。
- 而根 `VERSION.json` 写 `sidecar_build.models_bundled:false`、`models:"separated: base package ships NO models…"`、`bundled_weights_license:"none (no model weights in this variant)"`、`license:"GPL-3.0-or-later"`。`AGPL-RELEASE-1` 的口径是 **models 变体 = AGPL-3.0**、base = GPL-3.0-or-later；现在等于**以 base 的许可声明分发了带权重的包**。
- 影响：分发包元数据失真 + 许可声明与实物不符（须由 DSH 裁决是"改元数据"还是"把 models 从 stage 里剔掉"）。
- 返修：二选一并重跑 `package.ps1`（`-WithModels` 决定 `/XD models`）。

### F-04（P1）sidecar 的 `repo_head` 是"声明而非证据"
- `sidecar_build.repo_head = 6ad457c62ac1264fc8fa82267b06b90cb78f8b50`：`git cat-file -t` → **bad object**；短哈希 `6ad457c62` 唯一解析到 `6ad457c625f1551c538b8cc33d5c35798893bfde`（2026-11-15T03:11:38+08:00）。⇒ **40 位值写错了，短哈希对**。
- 支撑面只有三条弱证据：`doc/tasks/SIDECAR-REBUILD-1.md:14 base_commit: 6ad457c62`、`verification/SIDECAR-REBUILD-1/README.md:3` 的同一基线、以及 `core_service.exe` mtime `19:16:55Z`（晚于该 commit 的 19:11:38Z，时序上成立）。
- **缺失**：`verification/SIDECAR-REBUILD-1/` 里**没有** `core_service.exe` 的 sha256、也没有 `build_sidecar` 的构建日志（只有 README 引用的一段文字）；我在全 `verification/**` 里搜 `605088116…52ee` 只命中本卡 README。⇒ 没有把"这份字节"绑到"那次构建/那个 head"的任何工件。
- 返修：补 `build_sidecar` 日志（含 `git rev-parse HEAD` 与产物 sha256）+ 修正 40 hex。

### F-05（P2）"逐字节未变"措辞过强，且 before 工件口径不对
- 证据只有 `files=532 / bytes=967,726,273` 两个**聚合量**；没有任何逐文件清单或哈希 ⇒ 无法排除"同尺寸改写/删除+重建"，**不是逐字节**。
- AC6 卡面原文要求"安装前后记录其**文件清单+哈希对比**"，未满足。
- `verification/INSTALLER-MATRIX-1/data-root-before.txt` 内容是 `files=524 / bytes=210443772`（**污染前**）、`top=` 仅顶层名，**无时间戳**；它不是 AC6 的 before（532/967,726,273）。AC6 的 before 值只出现在 README 散文里，**没有对应工件** ⇒ before/after 的"未变"只有 after 可复核。
- 建议改为："卸载前后对比：文件数 532→532、总字节 967,726,273→967,726,273；运行窗口后数据根无任何文件写入（最新 mtime 20:43:12Z）；`.nsi` 卸载段不含数据根"—— 这是可以成立的措辞。

### F-06（P2）污染后果登记的数字是中途快照，主因也被错判
- README §3 写"524 files / 210,443,772 B → **705 files / 879,396,924 B**（+181 文件、+669 MB）"，并称"新增的主要是 `derived`（170 文件 / 95.8 MB）与 `logs`（177 文件 / 8.3 MB）"。
- 实测终态与真实增量：**524→532 files（+8）**，**210,443,772→967,726,273 B（+757,282,501 B）**；`backups/` 里 **8 个 `.nmbak`**（PK/zip，内含 `library.db`）在 **20:42:34–20:43:12（约 43 秒）** 被连续写出，合计 **756,991,687 B**；`derived`(170 files/95.8 MiB) 与 `logs`(177 files/8.3 MiB) 都是**本就存在**的用户数据，不是本次新增。
- 影响：①"705/+669 MB"是备份风暴途中的快照，与沉淀终态不符；②真实后果比登记**更重**——用户库在 43 秒内被复制了 **8 份 ≈ 757 MB**（并暴露 core_service 反复执行"first writable start backup"，疑为重启循环，与 F-09 的"第一次启动未 ready"互相印证）；③"主要可再生、无损失"的评估口径因此站不住。
- 返修：按终态重写 §3 增量与归因，并把"备份风暴/重复备份"单列为发现（与 E-8 同级或更高）。

### F-07（P2）关键 exit code 与安装/卸载日志未留存
- `/S` 安装、启动、`/S` 卸载三处都只在散文里写"exit 0"；证据目录无任何标准输出/退出码记录。
- `.nsi` 自己会写 `$TEMP\NewManga-install-${VERSION}.log` / `NewManga-uninstall-${VERSION}.log`（`installer.nsi:43-44,101,155`，内含 `data_root_not_touched`/`data_root_preserved`/`shortcuts_removed` 等），**是最合适的原始证据**，但既没纳入证据目录，实测也已不存在（我在 `%TEMP%` 未找到）。
- 返修：重跑时把两份日志 + 每步 exit code 落盘进 `verification/INSTALLER-MATRIX-1/`。

### F-08（P2）没有任何"staleness 守卫"（本卡最该补的结构性缺口）
- 全仓库检索：无脚本/测试读取 `VERSION.json` 的 `exe_sha256`/`core_service_sha256` 并与实物比对（`packaging/release/verify-release.ps1`、`tools/smoke/checks/packaged.py` 均不覆盖这两个字段；App 侧只有 `DeviceStatus` 读 `devices`）。
- `apps/desktop-avalonia/scripts/package.ps1` **会**写 `sidecar_build`（含 `repo_head = git rev-parse HEAD`，L64）与 `package-manifest.json`（L131）、并复制 `app/VERSION.json`（L125）；但本 stage **没走这条管线**（F-02 已证）。
- `build-installer.ps1` 只算 stage 指纹（L129-141），**不**校验 `VERSION.json`；`-OutDir` 防仓内写入做得对，但对"元数据与 stage 不一致"无 fail-closed。
- ⇒ **结论：如果今后 stage 变了而 `VERSION.json` 没更新，不会有人发现**。应登记 staleness 并加守卫（建议：`packaging/scripts/verify-package-metadata.ps1` — 重算 exe/sidecar 的 sha256+bytes、校验 `package-manifest.json` 与 `app/VERSION.json` 的版本/hash 一致、校验 `models_bundled` 与实物一致；由 `build-installer.ps1` 在调 makensis **之前**调用，失败即中止）。

### F-09（P3）第一次（真实数据根）安装后启动未达 ready，证据未披露
- `smoke\logs\host.log` 只有 3 行，止于 `20:42:28.117 first-run backup skipped: backup already exists`，**没有** `core_service ready`/`host_bridge ready`/`self-check`；而 `smoke\logs` 下也**没有** `wire/` 目录。
- 同时 `backups/` 的 8 次写入持续到 20:43:12 —— 进程活了约 45 秒却没就绪。这与"第一次只是漏传 `--data-root`"的叙述不完全吻合：那一轮 **Host 未就绪**，且 core_service 在反复做可写启动备份。
- 返修：在 §3 中如实写明"第一次启动未达 Host ready，且触发重复备份"，不要把第一轮仅描述为数据根污染。

### F-10（P3）E-8 的描述不精确
- 实际 10 条 `[Binding]`：`IsEnabled`×8、`ActiveTabLabel`×1（9 条 = VM 缺属性，均指 `StudioPageViewModel`）+ `'Source'→'CurrentPage.Image'`×1（`Value is null`，Image 控件，**与 StudioPageViewModel 无关**）。
- README/E-8 写"6 条以上…**全部**指向 StudioPageViewModel"——数量保守（实为 9 条缺失属性类），但"全部"不成立；建议改为"9 条 VM 缺属性错误（8×IsEnabled + 1×ActiveTabLabel）+ 1 条 Image Source 为空"。
- E-8 本身**已登记**（`doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md:175`，随本 head 提交，+28 行），性质判断（静默 UI 失效、headless 抓不到）正确。

### F-11（P3）"旧 sidecar"的表述与实际不符
- 卡面 §目标/约束与 commit 都写"仍用 **2026-10-23** 的旧 sidecar"；但 `VERSION.json` 自述 `core_service_built_at_utc=2026-11-14T19:16:55Z`、head `6ad457c62`（=11-14 的重建），mtime 也是 11-14。⇒ 用的是 **11-14 重建版**（只缺 SFX 权重），不是 10-23 版。卡面、commit message 与 `VERSION.json` 三处口径不一致。

### F-12（P3）许可文件"内容一致但字节不一致"，佐证 stage 非管线产出
- `LICENSE`/`LICENSE-AGPL-3.0.txt`/`NOTICE.md` 与仓库根**按行内容完全一致**，但**字节不同**（行尾差异：stage `LICENSE` 为 CRLF、仓库为 LF；`AGPL`/`NOTICE` 相反）。
- `package.ps1:80-81` 的字节一致性守卫在本 stage 上**会抛错**。⇒ 再次证明 stage 是手工拼装。分发内容本身无实质问题，但应删除这类无谓的字节漂移，否则将来无法用哈希守卫。

### F-13（P3）元数据小瑕疵
- `verification/INSTALLER-MATRIX-1/build-info.json` 的 `task` 字段硬编码为 `"NSIS-INSTALLER-1"`（`build-installer.ps1:183`），不是 `INSTALLER-MATRIX-1`；`icon` 指向已归档的 `apps/desktop/src-tauri/icons/icon.ico`。
- 体积口径混用：README 写 "848.15 MB" 实为 **MiB**（889,352,697/1,048,576），自称 "621.9 MB" 的 setup 同理（621.88 MiB）。建议统一标 MiB。

### F-14（P3，流程）卡面自身尚未更新
- `doc/tasks/INSTALLER-MATRIX-1.md` 的"测试要求"表 5 行仍全是 `NOT_RUN`/`无`；`Canonical Evidence` 表与 `Resource Manifest` 仍为占位/待填；`status: in_progress`。
- 另外工作区有**未提交**修改（`doc/tasks/INSTALLER-MATRIX-1.md` 的 AC 勾选、`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §17、`doc/TASK_LEDGER.md` 计数），**不属于**本被审 commit。若要以 HEAD 作为交付点，这些必须一并提交；否则"AC 已勾选"这一状态本身不在被审对象里。

---

## 4. 我没有验证的面（明确边界）

1. **未重装/卸载**（只读约束）。AC4/AC6 的"当时确实发生过"只能由**当前残留状态** + `.nsi` 逻辑 + 日志 mtime 反推；`/S` 的 exit code、NSIS 安装/卸载日志无法复核（F-07）。
2. **未重跑 publish 构建**，因此不能独立证明 `ea01c8c7…` 这份字节与源码树的映射；但内嵌 `ProductVersion` 与 `RELEASE-PACKAGE-PROBE-1` manifest 已足以证明它**对应 `5dda044` 而非 `fe7da5d92`**（F-01）。
3. **未解包 setup.exe** 校验其内嵌 payload 与 stage 逐字节相同（NSIS 日志的 `Install data: 889,405,367 bytes` 与 stage 889,352,697 B 差 52,670 B，属 NSIS 头/额外脚本数据，未逐文件拆解）。
4. **未在打包产物上跑四页**（AC7 本就 NOT_RUN，我同样没有做，也没有可用截图）。
5. **未验证升级/回退**（证据自述未做；需要旧版 setup 作回退目标）。
6. **未验证 sidecar ↔ `6ad457c62` 的因果**（缺构建日志/产物哈希，F-04）。
7. **未验证污染前/卸载前的数据根字节状态**（无 before 清单/哈希；只能证明"现在 = 声明的 after"且"运行窗口后无写入"）。
8. **未验证 head 之后是否有其它 Agent 的并发写入影响**：审查期间工作区已有 3 个未提交修改（非本会话所为），我只读未碰。

---

## 5. 明确回答

### 5.1 这份矩阵能否作为**条件 4 的部分证据**？
**能，但只能作为"安装/启动/卸载机制"的部分证据，不能作为"包由当前固定 head 构建"的证据。**

- 可复用（已被我独立复现的部分）：stage 就绪与体积；三组哈希/尺寸；NSIS 打包与 `INSTALL_SIZE_KB`；安装后从**安装目录**启动并达到 `self-check=Passed` / capabilities 17；卸载后程序目录/HKCU/Start Menu 清空；数据根 **数量与字节未变**、运行窗口后无写入、`.nsi` 不含数据根删除；AC7 诚实 NOT_RUN；无二进制入库。
- 不可复用：AC1/AC2 的"来源"结论。该包的产品基础是 **`5dda044`**，落后 `fe7da5d92` 三个产品源文件；包内元数据自相矛盾且谎报"无模型"。在 F-01/F-02/F-03/F-04 修好之前，这份证据**不能**用来支撑"对**当前固定产品 commit** 的包做了矩阵"。

### 5.2 `VERSION.json` 是否可被信任？
**分两层：作为"字节清单"可信；作为"来源证明"不可信。**

- 可信：`exe_sha256/exe_bytes`、`core_service_sha256/core_service_bytes/core_service_built_at_utc` —— 三项全部与实物逐字节一致（我也复现了 stage 指纹与 `install_size_kb`）。这部分是全卡最扎实的资产。
- 不可信：`app_build.repo_head`（错，实为 `5dda044`）、`sidecar_build.repo_head`（40 hex 不存在）、`models_bundled`/`bundled_weights_license`（与实物相反）。
- 另外：**同一份包里有三个 `VERSION.json` 口径**（根=0.1.1 新值、`app/VERSION.json`=0.1.0 旧值、`package-manifest.json`=0.1.0 且 hash 全错），在清理前不能把"VERSION.json"当作单一可信事实源。

### 5.3 staleness 是否应登记？
**应登记，且建议按 P1 登记（这不是未来风险，是本次已发生的缺陷）。** 现有证据链里没有任何自动化守卫能在"stage 变了、`VERSION.json` 没变"时报警；本次已出现两份 0.1.0 元数据随 0.1.1 包分发而无人发现。建议同时：
1. 在 `doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md` 增一条 staleness 类发现（与 E-8 并列）；
2. 新增 `packaging/scripts/verify-package-metadata.ps1`（重算 + 交叉校验 + `models_bundled` 与实物一致），由 `build-installer.ps1` 在 makensis 之前调用，fail-closed；
3. 让 stage 由 `package.ps1` 一条路生成，禁止手工改 `VERSION.json`。

---

## 6. 返修清单（最小集，供 DSH 处置）

1. `app_build.repo_head` → `5dda04437d68baf304b4364a3a73f9dfa217d943`（或重新 publish 于冻结 head 并重跑矩阵）；同步修正 README §2 与 commit 叙述。
2. 删除/重生成 `stage\app\VERSION.json` 与 `stage\package-manifest.json`；加"元数据一致性"检查。
3. 裁决 `models` 归属：要么改为 `models_bundled:true` + `AGPL-3.0` 口径，要么从 stage 移除 632.6 MB ONNX 后重打包。
4. `sidecar_build.repo_head` 修正为 `6ad457c625f1551c538b8cc33d5c35798893bfde`，并补 `build_sidecar` 日志与产物 sha256。
5. 用"文件清单 + 哈希"重做 AC6 的 before/after（含时间戳），把 `data-root-before.txt` 改名/重写为真正的 AC6 before；把"逐字节未变"改成可证的措辞。
6. 按终态重写污染增量，并把"8 次重复备份 / 757 MB"与"第一次启动未 ready"单列登记（建议与 F-06/F-09 对应）。
7. 留存 `/S` 安装、启动、`/S` 卸载的 exit code 与 NSIS 安装/卸载日志。
8. 修正 E-8 的条数与"全部指向"，补登 staleness 与 `verify-package-metadata.ps1`。
9. 把工作区未提交的卡面/评估/LEDGER 改动一并提交，或明确交付点为工作区状态。
