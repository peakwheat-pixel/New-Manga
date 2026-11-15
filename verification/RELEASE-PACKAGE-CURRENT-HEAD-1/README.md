# 当前 HEAD 打包 + 真实窗口冒烟 — 证据（r1 复核后修订）

Task：`RELEASE-PACKAGE-CURRENT-HEAD-1`（Owner：DSH）｜基线 `da7f88fb5`｜实现 `8997b8e23`

> **本文件据 r1 复核（APPROVED_WITH_LIMITATIONS，0/2/3/4）的 P1-01/P1-02/P2-01 修订**：
> 初版未说明「产物绑定的是父提交（但产品代码树等价）」、「单文件包**不含 sidecar**」、
> 「冒烟不覆盖功能路径」三项 —— 这些都会导致误读，现补全。

## 1. 结果

```
tools/ci/publish-release.ps1 -Mode singlefile -Smoke -SidecarDir <bundle> -EvidenceDir <本目录>
  EXIT=0，墙钟 29.3s
  publish: 1/1 PASS, 0 expected-failure(s), 0 FAIL
```

| 项 | 值 |
|---|---|
| 产物 | `NewManga.App.exe` **99,554,850 B（94.94 MB）** |
| sha256 | `07DD80F0BC5311503CCA13B299014250343152807661EA3DD002DB459B33AE74` |
| `publish_exit_code` / `publish_elapsed_ms` | 0 / 11,199 |
| `manifest.git_head` | `da7f88fb54eb34326eed4603c652038ac7677639`（**本卡父提交**，见 §2） |

## 2. 产物绑定的是父提交，但产品代码树与当前 HEAD 逐字节相同（r1 P1-01）

打包发生在 21:57:58，此时 `HEAD` = `da7f88fb5`（21:52:02 提交）；
本卡提交 `8997b8e23` 于 21:59:25 产生。所以 manifest 记的 `git_head` 是**父提交**，
**AC1「git_head == 本卡提交 sha」字面不满足**。

但两个提交的**产品代码树完全相同**：

```
git diff da7f88fb5 8997b8e23 --stat -- apps tools src core tests   → 无输出
da7f88fb5:apps tree = 039ae5113ba1b9c81563017a44271df716cdcdcf
8997b8e23:apps tree = 039ae5113ba1b9c81563017a44271df716cdcdcf   （相同）
da7f88fb5:src  tree = b02735e987e4d0dfdb28aadfd90b53b136451443
8997b8e23:src  tree = b02735e987e4d0dfdb28aadfd90b53b136451443   （相同）
```

两提交差异仅 `doc/**` + `verification/**`（9 文件），**不含任何产品代码**。

⇒ **产物实质包含当前 HEAD 的全部产品代码**；AC1 的实质要求成立，字面要求因提交时序差一步。

## 3. 冒烟结果与它**不能**证明什么（r1 P1-02c / P2-01）

`smoke-singlefile.json`：

```
window_found      = true
window_title      = "New Manga"
host_ready        = true
exit_code         = 0
exit_kind         = natural
pass              = true
```

**独立复核者用 `read_image` 亲眼看图确认**：画面为 NewManga 本体（1416×939，标题栏 "New Manga"、
导航「资料柜｜工位｜控制台」、主区「资料柜 0/0 作品」、空态「书架还是空的」、**底部两处「Host 就绪」**），
与 `host_ready=true` 独立互证。**不是假截图**（对照本项目 `MICA-FIX-1` AC1 的 ChatGPT 窗口先例）。

**能证明**：exe 能启动、真实窗口出现、Host 能 ready、能自然退出。
**不能证明**：
- **功能路径未触达** —— 截图是 **0/0 空态**，没有做任何导入/读写/译制/并发操作；
- **E-7 仍有 5 项开放**（无 `request_id` 时 fail-open、R-002 无重同步、R-005 取消失步、
  Dispose 出租约、`CoreServiceClient` 未迁到传输层租约）—— 文档原话「并发安全仍不可宣称」；
- 因此 **不得**把本次 PASS 延伸为「产品可用」或「可发布」。

**P2-01**：脚本在成功后删除 `smokeRoot`，`host.log` 已不可复核；
截图上「Host 就绪」两处文字是旁证，故未升级为 P1。

## 4. 单文件包**不含 sidecar**，不能独立分发（r1 P1-02a）

产物目录只有三项：

```
NewManga.App.exe          99,554,850 B
build-singlefile.log           2,249 B
published-singlefile.png      33,988 B
```

**没有 `core_service.exe`**。`tools/ci/publish-release.ps1:61` 自述：

> The published app needs the sidecar bundle at runtime.

本次冒烟是靠 `-SidecarDir` 指向 792 MB 的 sidecar bundle（§5）才跑起来的。

⇒ **94.94 MB 的 exe 不是可分发的完整包**：单独拿走无法运行，必须随包附带 sidecar bundle。
面向 Gate 条件 4 的正确表述是「**当前产品代码树产出的 exe 能启动、Host 能 ready、能自然退出**」，
而不是「已有可分发包」。

## 5. sidecar 来源

- 位置：`apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar/`
- 规模：**1024 文件 / 830,148,936 B（791.69 MiB）**，git-ignored
- mtime：2026-11-15 03:16:56（其基线 `6ad457c62` 于 03:11:38）
- 来源：`SIDECAR-REBUILD-1` 用 PyInstaller 重建
- **用的是当前 Core 代码**：`6ad457c62:src` 与 `da7f88fb5:src` 的 tree hash 完全相同
  （`b02735e9…`），中间 342 个文件改动**无一条落在 `src/`**

> **r1 P1-02b**：`SIDECAR-REBUILD-1` AC5 记录的 **13 个测试失败**不是「sidecar 坏了」，
> 而是暴露了 C# 客户端的 P1 竞态。其中 E-6（`list_chapters` 静默空）已由 `b202b47fb` 修复且是本包基线祖先；
> E-7 主管道窗口由 `17c744b26` 修复，但 **E-7 仍有 5 项开放**（见 §3）。
> 本次冒烟 PASS 与此无关 —— 空态启动不触达那些路径。

## 6. 边界（不淡化）

**本卡只替换「`0.1.1` 旧包不绑定当前基线」这一证据缺口**：

| 已做 | 未做（需人或不在本卡范围） |
|---|---|
| 当前产品代码树产出的 exe | clean install 矩阵 |
| 真实窗口启动 + Host ready + 自然退出 | 升级 / 回退 |
| sha256 指纹与 manifest | 卸载 |
| sidecar 可用性核证 | 安装器签名（需证书） |
| — | **可独立分发的完整包**（缺 sidecar 打包步骤） |

**Gate 条件 4 的判定不变**（仍需安装矩阵 + 签名）；**Gate 仍 BLOCKED**。

## 7. 零代码改动 / 零污染

```
git diff da7f88fb5 8997b8e23 --stat  → 仅 doc/** + verification/**（9 文件）
git status                            → clean（build 产物 git-ignored）
```

## 8. 不回归

```
check.ps1（全局）                → PASS (3 warnings), EXIT=0
verify_pins.ps1                  → PASS (all 18), EXIT=0
generate_api_inventory.py --check → OK (1/80/6=87), EXIT=0
```

## 9. 已知精度问题（r1 P3）

- `manifest.task = "V11R-PUB-1"` 是脚本硬编码，非本卡 id；
- manifest 内路径为仓库外绝对路径，JSON 非自包含；
- `SIDECAR-REBUILD-1/README.md` 记 753 MB，本卡实测 **791.69 MiB**（以本卡实测为准，差异为测量口径/后续增补）；
- `sidecar-availability.log` 的探针返回 `PROTOCOL_VERSION_UNSUPPORTED`（未带协议头），属弱证据，已被冒烟覆盖。
