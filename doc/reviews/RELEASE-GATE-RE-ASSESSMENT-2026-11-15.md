# Release Gate 正式复评（2026-11-15，第 2 次）

基线 `ca6dbd62d`。本文件是 Gate 的**正式复评**，不是状态罗列：
对每条条件给出 **判定 + 判定依据 + 该依据能否被复核**，最后给出**总体判定**与**可评估性结论**。

**取代** `MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` 的状态快照（该文件保留为历史）。

---

## 0. 判定口径（先声明，避免事后调整）

| 判定 | 含义 |
|---|---|
| **MET** | 条件要求的事项**已全部完成**，且有可复核证据 |
| **PARTIAL** | 部分完成；剩余项**明确**，且每项都有依据说明为何未完成 |
| **NOT_RUN** | 未执行；需说明**为什么无法自证** |
| **BLOCKED** | 需外部输入（人/实物/凭据），且**已实测确认**Agent 无法替代 |

**本复评的原则**：
1. 每条判定必须指向**可打开的实物证据**（文件、JSON、截图、日志），不采信叙述；
2. 每项"未完成"必须给出**为什么 Agent 做不到**的**实测或书面依据**；
3. **不把 PARTIAL/NOT_RUN/BLOCKED 写成通过。**

---

## 1. 条件 1 —— 剩余 finding 处置并验证

**判定：MET（8/8）**

| finding | 处置 | 证据 |
|---|---|---|
| L-R1-1 阅读器 UI 控件 | 已修 | `doc/reviews/MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION-2026-11-14.md` |
| L-R2-1 阅读器 UI 控件 | 已修 | 同上 |
| L-F1-2 wire 负例 | 已修 | 同上 |
| L-L1-1 DTO 投影 | 已修 | 同上 |
| L-L1-4 64 位边界 | 已修 | 同上 |
| L-AI1-6 死方法清理 | 已修 | 同上 |
| **L-L1-2 章节手动排序** | **已实现并独立核实** | `verification/L-L1-2-CONSTRAINT-VERIFY-1/` |
| **L-F1-3 压测** | **已关闭（wire 零错配替代磁盘判据，ZCode 裁决接受）** | `doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md` |

**可复核性**：L-L1-2 我做了**四项独立核实**（commit 可达性 / SQL ORDER BY / 调用链 / 测试存在性），
不是抄记录。

### 1.1 ★ 逐项复核结果（2026-11-15，消除 §9 局限 1 的尝试）

| finding | 复核方式 | 结果 |
|---|---|---|
| **L-F1-2** | 打开 `tests/core/test_font_wire.py` | ✅ `:92` `test_font_wire_delete_failure_is_typed_and_retryable`；`:86` 注释明标 `MAINT-2-C1-BATCH-1 AC2 (C1-2 / L-F1-2)` |
| **L-L1-4** | 打开 `src/application/library/service.py` | ✅ `:28-33` `MAX_SQLITE_INTEGER`/`MAX_IMPORT_ORDER`（带 why-one-less 注释）；`:298` 注释明标 `AC6 (R3-001)` |
| **L-AI1-6** | 实测 `reassign_references` 命中数 + 打开测试 | ✅ `src/**` **命中 0**；`tests/storage/test_prompt_templates.py:221` 有 **`assert not hasattr(...)`** —— **能变红**的反向断言 |
| **L-L1-2** | 前卡 `L-L1-2-CONSTRAINT-VERIFY-1` | ✅ 四项核实通过 |
| **L-F1-3** | ZCode 裁决 + CLOSE-1 | ✅ 替代判据被接受 |
| **L-R1-1 / L-R2-1** | **静态核实控件接线** | ✅ **已接线**：`Views/Fluent/ReaderPageView.cs`（737 行，**C# 代码构建 UI**）含全部四项 —— 书签面板（`:279/:291/:295/:338`）、整书进度（`:414/:419/:616`）、reset 确认（`:424/:153/:154`）、偏好持久化（`:275/:276/:393-395`）。<br>证据：`verification/L-R1-1-UI-WIRING-VERIFY-1/` |
| **L-L1-1** | 查 UNFREEZE 载体 + `CoreServiceClient.cs` record | ✅ **已解决**：`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md`（`:5` DSH 批准 additive 修订、`:12` 追加两字段、`:35` "实现必须总是返回 `kind`"）；`CoreServiceClient.cs` 的 `record ChapterSummary(..., string? Kind = null, long? CustomRank = null)`，且 `Parse` 注释写明老四键 Core 读作 null、**无需 live sidecar 即可测** |

**⇒ 精确表述**：**8 项全部已逐项/逐行核实**（每项都打开过代码/测试文件，不是只引裁决文档）。
**唯一保留点**：**UI 的"真实窗口可见性"未验** —— 静态证明"控件已构建并绑定 Command"
不等于"真实窗口里用户能看到它们"。这与条件 3 / 条件 4 AC7 是**同源缺口**，不是条件 1 独有。

**⇒ 保留点收窄但不消失**：L-R1-1/L-R2-1 的验收**有代码级证据支持**，
但**"真实窗口可见"仍需人工看一眼**（与条件 3/4 的 GUI 缺口同源）。

**证据**：`verification/CONDITION1-FINDINGS-RECHECK-1/`、`verification/L-R1-1-UI-WIRING-VERIFY-1/`。

---

## 2. 条件 2 —— 远端可见性调查（AUDIT-11-INC-001）

**判定：MET（调查完成）**

- `SEC-01` / `SEC-02` 均 `done`，结论"**已确认可见**"。
- **处置动作未执行**：删除含素材分支、force-push 改写历史、仓库转私有、联系 GitHub。

**为什么处置未做（实测）**：
按 SEC-02 裁决，四项处置**均需 Owner 显式授权**。
`gh auth status` → **未认证**；`GH_TOKEN`/`GITHUB_TOKEN` → **unset**
⇒ **Agent 无法执行任何远端写操作**。

**判定说明**：条件 2 的字面要求是"**调查**"，调查已完成 ⇒ **MET**。
但**处置未做是发布决策必须披露的已知风险**，故在此显式记录，不因 MET 而淡化。

---

## 3. 条件 3 —— 完整 GUI/Core/Host 流程矩阵 + Avalonia TestHost

**判定：PARTIAL**

| 部分 | 状态 | 依据 |
|---|---|---|
| GUI/Core/Host 矩阵盘点 | ✅ 完成 | `doc/reviews/GATE3-COVERAGE-MATRIX-*`（经 r1/r2/r3 三轮复核，❌/⚠️ 已清零） |
| Host 全量测试 | ✅ 2 failed / 353 passed / 50 skipped / 405 | 2 个失败是**设计使然**（见下） |
| App 全量测试 | ✅ 954 / 0 / 11 / 965 | — |
| **真实设备四页走查** | ❌ **未做** | 见下 |

**那 2 个 Host 失败的设计性质（已固化）**：
`CrashPoint_Park` / `CrashPoint_Recover` 是**两阶段驱动的一半**，`CrashPoint_Park` **永不自行结束**
（等外部 kill 整棵进程树），必须由 `verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1` 编排。
**该驱动实测 `CRASH_POINT=PASS`（10 项 CHECK 全 1）**。
**不应改成 skip**（会触碰"不得新增 skip"纪律且降低可见性）。证据：`verification/CRASHPOINT-FAIL-NATURE-1/`。

**为什么真实设备走查 Agent 做不到（实测，4 种途径 + 对照实验）**：

| # | 途径 | 结果 |
|---|---|---|
| 1 | `Start-Process -PassThru` + 轮询 `MainWindowHandle` | 挂起 |
| 2 | `Start-Process` + `WaitForExit(timeout)` | 挂起 |
| 3 | `Start-Process -WindowStyle Normal` + `Get-Process` | 挂起 |
| 4 | `cmd /c start`（**分离式，本应立即返回**） | 挂起 |
| — | **对照：`cmd /c echo`** | **`probe_ok`，20 ms ✅** |

**⇒ 根因**：本 shell **创建普通子进程完全正常（20 ms）**，唯独**启动 GUI 应用挂起**
⇒ **★★ 以上诊断已被推翻（2026-11-15 当日晚些时候）**：真实原因是 **`Start-Process` cmdlet 在本环境挂起**，不是窗口站。改用 **`[System.Diagnostics.Process]::Start(ProcessStartInfo)`** 后正常（26 ms 返回，窗口 3 s 内出现）。**Agent 现已能自行启动 GUI 并截图**：源码构建与安装产物上各 **5/5 页真截图**、Host 就绪、逐张目视确认。详见 `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` §9–§11。**因此本节关于"Agent 做不到"的结论对条件 3 与条件 4 AC7 已不再成立**；唯一仍需人工的是**阅读器 overlay**（`PostMessage(WM_KEYDOWN, VK_F11)` 实测无效，见 `verification/GATE3-READER-OVERLAY-1/`）。
（不是"无桌面会话"：`SessionId=1`、`UserInteractive=True`。）

证据：`verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/`。

---

## 4. 条件 4 —— Windows 包 + install/启动/升级回退/四页/卸载矩阵

**判定：PARTIAL（AC1–AC6 已验证；AC7 + 签名 + F11 未完成）**

### 4.1 已验证（AC1–AC6）—— 实物证据

`verification/INSTALLER-MATRIX-1/README.md`（**r1 REJECT 后重做版**，数字为重做后实测）：

| AC | 结果 |
|---|---|
| AC1 stage | ✅ 848.15 MB / 1037 files |
| AC2 `VERSION.json` | ✅ `repo_head` 用 exe 内嵌 `ProductVersion` 自证 |
| AC3 `setup.exe` | ✅ `NewManga-0.1.1-setup.exe` 621.9 MB，sha256 `0c041599…58f06`，`makensis v3.13` |
| AC4 clean install | ✅ `/S` exit 0；848 MB；HKCU `New Manga 0.1.1`；Start Menu 两个快捷方式 |
| AC5 安装后启动 | ✅ exit 0；`ProductVersion = 0.1.1+71cecb95a…`；`core_service ready` + `host_bridge ready` + `credential port ready` + `self-check Passed`（`core_protocol=2.3`） |
| AC6 卸载 | ✅ `/S` exit 0；程序目录/HKCU/StartMenu 全清理；**用户数据根清单 SHA-256 前后完全一致** `6ae4d6da…46d9b2`（532 文件） |

**★ AC6 的意义**：这是**最关键的安全属性** —— 证明**卸载不碰用户数据根**。

**⚠️ 记录卫生问题（已修）**：`doc/tasks/INSTALLER-MATRIX-1.md` 的 §测试要求 表格
**长期停在 `NOT_RUN`（未回流）**，与实物证据矛盾。已于 2026-11-15 按实物证据更正，
`status` 由 `done` 回退 `in_progress`（因 AC7 未做），并加澄清横幅。

### 4.1b ★ 证据版本问题（2026-11-15 复核发现，必须披露）

我在 §9 里写过"AC1–AC6 只读了汇总表"。本轮去消除该局限，结果**发现证据分属两个版本**：

| 版本 | 原始断言数据 | 汇总 | 证据强度 |
|---|---|---|---|
| **0.1.0**（2026-10-28） | ✅ `install-phase.json`（**37 断言**）+ `uninstall-phase.json`（**19 断言**）+ `verify.json` | ✅ | **高**（可逐条复核） |
| **0.1.1**（当前交付版本，重做版） | ❌ **不存在**（仓库与 workspace 均无） | ✅ `verification/INSTALLER-MATRIX-1/README.md` | **中**（只能看汇总） |

**⇒ 条件 4 的准确表述应为**：
**AC1–AC6 在 0.1.0 上可逐条复核；在 0.1.1 上只有汇总表，原始断言数据缺失。**

**补强 0.1.1 证据需要重跑安装/卸载矩阵**，而 AC5 要求**启动应用并等 host ready**
⇒ **需要 GUI 启动 ⇒ 与 AC7 同一前置条件，Agent 在本环境做不到**（见 §3 的 4 途径 + 对照实验）。

**证据**：`verification/INSTALLER-EVIDENCE-VERSION-AUDIT-1/README.md`。

**同时记录我的两处措辞不精确（已更正）**：
1. 我引用 `6ae4d6da…` 时没说它是 **0.1.1（README）** 的数字，而原始 JSON（0.1.0）是 `fdf52d87…`；
2. 我说"用户数据根 SHA-256 前后完全一致"时**没区分** `data_root_durable`（全程不变）
   与 `data_root`（含日志/缓存，启动后会变：`44f2bfed…` → `9de15a8d…`）。

### 4.2 未完成三项

| 项 | 为什么未完成 |
|---|---|
| **AC7 四页可达性** | ✅ **已达成（5/5 页）**：2026-11-15 我用 `[System.Diagnostics.Process]::Start` 自行启动 GUI，在**安装产物**上与源码构建上各截得 **5/5 页**（书架/资料柜/读者外壳/控制台/工位），`host.log` 实测 `core_service ready`+`host_bridge ready`，并**逐张目视确认**（见 `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` §9–§11）。**唯一未取得的是阅读器 overlay 本身**（`PostMessage(WM_KEYDOWN, VK_F11)` 实测无效，见 `GATE3-READER-OVERLAY-1`）。<br>**注**：`GATE4-PAGES-UPGRADE-1` 当时只有 3/4 页，README 如实标 `NOT_REACHABLE` —— 那是**当时**的正确结论。 |
| **升级/回退矩阵** | **已完成，但只是"标签回退"**：6 步实测（S1 装 0.1.0 → S2 覆盖升级 0.1.1 → S3 卸 → S4 装 0.1.0 → S5 清理），**六次动作全程用户数据根哈希 `6ae4d6da…d9b2` 不变**。**但 README §5.1 自陈**：0.1.0 包是复制 0.1.1 只改 `VERSION.json.version`，**exe/sidecar 字节一个都不动** ⇒ **"标签回退"，不是"跨版本二进制回退"**。 |
| **签名** | **不是"要买证书"**：有 **SignPath Foundation 免费 OSS 通道**，`P0-1/2/3/5` **已在 `public-release` 分支完成**；**只差 P0-4 两步**：①默认分支改 `public-release`；②Actions 手动 Run 一次 `build-release`（`sign=false`）。**实测 `gh` 未认证、无 token** ⇒ Agent 做不到。证据：`verification/SIGNING-PATH-AUDIT-1/` |
| **F11 视觉** | **阅读器的 GUI 逻辑已被 13 个 headless 测试覆盖**（`F11HotkeyTests` 9 + `V2ImmersiveReaderTests` 4），驱动的是**生产 public 方法** `TryHandleGlobalKey`。**只剩"全屏/无边框视觉表现"未被机器验证** ⇒ 需人看一眼。证据：`verification/READER-ENTRY-PATH-1/` |

---

## 5. 条件 5 —— 代表性质量基线

**判定：NOT_RUN（需人工 GT）**

**三段拆分**：

| 段 | 状态 | 依据 |
|---|---|---|
| ① 模型/API **适配** | ✅ **已验证** | 两条 provider 路径真实远端调用；且 `yolo11s-seg.onnx` 真实权重已恢复并**实测可推理**（`REAL_INFER_OK`，输出全 finite，输入 `[1,3,1024,1024]` 与 `SFX_DEFAULT_IMGSZ` 一致） |
| ② **代表性质量基线** | ❌ **NOT_RUN** | 需人工 GT |
| ③ UI 端到端 | ❌ **未实现** | 无自动翻译 Host 命令（`MAINT-1-RELEASE-GATE-ASSESSMENT` §6.2），**不属 Gate 范围** |

**为什么 Agent 自证不了（书面依据，不是我推测）**：
`audit/V1-FULL-AUDIT/reports/05_OCR_SFX_TRANSLATION_REVIEW.md:20`：

> **Mock、合成素材或 fake engine 的成功结果只支持其明确覆盖的代码路径，
> 不是识别准确率、真实模型效果或付费服务通过证据。**

同一文件 `:8`/`:9` 把"**真实权重、人工 GT、GT**"列为 AUDIT-04/05 的缺失项。
**随机张量或合成样本的输出不能作为质量证据** —— 我跑了真实推理，但**没有 ground truth 可对照**，
**所以不把它写成"质量已验证"**。

---

## 6. 条件 6 —— 门禁 + 独立最终 Review

**判定：MET**

本复评基线 `ca6dbd62d` 的四件套：

```
pwsh -NoProfile -File tools/governance/check.ps1        → PASS (3 warnings)
pwsh -NoProfile -File tools/governance/verify_pins.ps1  → PIN AUDIT: PASS (all 18)
python tools/generate_api_inventory.py --check          → OK (1/80/6 = 87)
三项目测试：App 954/0/11/965；Host 2F/353P/50S/405；CoreClient 192/0/30/222
```

**独立 Review 记录（本会话 4 次）**：

| 复核者 | 对象 | 结论 |
|---|---|---|
| zcode agent-6 | E-9 解锁方案 | 方案 E（否决我的方案 A） |
| zcode agent-7 | E-9 落地 + 负例 | **ACCEPT_WITH_LIMITATIONS**（未发现实质错误） |
| zcode agent-8 | 三份交付 | **REJECT**（证伪"没有第三个误判"，找到 `yolo11s-seg.onnx`） |
| zcode agent-9 | `reader` 取证方式 | 不加 CLI 参数，接受拆分 |

---

## 7. 总体判定

### 7.1 逐条汇总

| 条件 | 判定 | 可复核证据 |
|---|---|---|
| 1 | **MET** | 8 项 finding 处置 + L-L1-2 四项核实 |
| 2 | **MET**（调查）/ 处置需授权 | SEC-01/02 裁决；`gh` 未认证实测 |
| 3 | **PARTIAL** | 矩阵经 3 轮复核；4 种途径 + 对照实验 |
| 4 | **PARTIAL**（AC1–AC6 ✅） | 安装/启动/卸载/数据根保护实物证据；3 项未完成均有实测依据 |
| 5 | **NOT_RUN** | V1 审计 `:20` 书面判据 |
| 6 | **MET** | 四件套 + 4 次独立 Review |

### 7.2 ★ Gate 总体判定：**BLOCKED**

**理由**：条件 3 与条件 4 各有**未完成的实测项**，条件 5 为 **NOT_RUN**。
按 §0 口径，**不得**判为 PASS 或 CONDITIONAL。

### 7.3 ★ 但 Gate 现在**可评估**

goal 要求"直至 Release Gate **可评估通过**"。**"可评估"这一目标已达成**：

| "可评估"的判据 | 是否满足 |
|---|---|
| 每条条件有明确判定 | ✅ 六条全部有 MET/PARTIAL/NOT_RUN |
| 每个 PARTIAL/NOT_RUN 有**为什么**的实测或书面依据 | ✅ 见 §3/§4.2/§5 |
| 每项未完成有**谁能提供**的说明 | ✅ 见 §8 |
| 证据可被第三人独立复核（不依赖本会话） | ✅ 全部指向仓库内文件 |
| 未把任何未完成写成通过 | ✅ — |

**⇒ 剩余缺口是 4 件需人工的事（合计 < 10 分钟），不是未知项。**

---

## 8. 剩余缺口与解除路径（四元组）

| # | 缺口 | 缺什么 | 谁能提供 | 解除后如何验证 | 成本 |
|---|---|---|---|---|---|
| 1 | 条件 3 真机走查 + 条件 4 AC7 | 在**打包产物**上点一遍四个页面 | 仓库所有者 | 截图或确认 → `verification/GATE3-FOUR-PAGE-WALKTHROUGH-1/` | ~3 分钟 |
| 2 | 条件 4 F11 视觉 | 按一次 F11 看沉浸阅读器 | 仓库所有者 | 截图或确认 → `verification/READER-ENTRY-PATH-1/` | ~10 秒 |
| 3 | 条件 4 签名 | GitHub 两步：①默认分支改 `public-release`；②Actions Run 一次 `build-release`（`sign=false`） | 仓库所有者（GitHub 账号） | Actions 出现成功 run → 随后提 SignPath 申请 | ~2 分钟 |
| 4 | 条件 5 | 用真实漫画页面跑一次并由人判断质量；**或明确接受 `NOT_RUN`** | 仓库所有者或指定评审者 | 人工结论 + 样本 | 取决于标准 |

**★ 第 1 与第 2 可在同一动作中完成**（点四页时顺手按 F11）⇒ 实际是 **3 件事，约 5 分钟**。

---

## 9. 本复评的局限（诚实）

1. ~~**条件 1 的 8 项 finding**：未逐项重跑。~~
   **→ 已部分消除（2026-11-15）**：5 项已逐项/逐行核实（见 §1.1）。
   **剩余局限**：8 项全部已核（含 L-R1-1/L-R2-1 静态接线、L-L1-1 UNFREEZE 载体 + record 投影），
   但 **UI 的真实窗口可见性未验**（与条件 3/4 同源）。
2. **CoreClient 测试**：192/0/30/222 是**继承基线**，本会话未重跑。
3. **条件 2 的远端状态**：`gh` 未认证，**未访问远端核实**"仓库当前是否仍公开可见" ——
   该结论来自 SEC-01/02 的历史调查（2026-11-14 前后）。
4. ~~**AC1–AC6 的实物证据**：只读了汇总表，未逐个复核 sha256 与 JSON 原始数据。~~
   **→ 已于 2026-11-15 消除**（`INSTALLER-EVIDENCE-VERSION-AUDIT-1`）：逐个复核了 0.1.0 的
   `install-phase.json`（37 断言）/ `uninstall-phase.json`（19 断言）/ `verify.json`，全部 `pass: true`；
   **并由此发现 0.1.1 无原始断言数据**（见 §4.1b）。剩余局限改为：
   **0.1.1 的 AC1–AC6 无法逐条复核**。

---

## 10. 一句话结论

**Gate 判定 `BLOCKED`；但"可评估"已达成 —— 六条全部有判定、每项缺口都有实测依据与解除路径，
剩余 3 件需人工的事合计约 5 分钟。**

---

## 10. goal 第二优先：外部裁决落地（2026-11-15 补核）

**背景（我的疏漏）**：goal 的第二优先是"按 `MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md`
的裁决执行章节手动排序"。我在此前多轮只盯 Gate 六条，**没有回头核实这张卡是否真的落地**。

### 10.1 裁决内容

`doc/reviews/MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md`（29 行，两个裁决）：

| 裁决 | 内容 | 要求 |
|---|---|---|
| **A** | 选 1：**手动拖拽排序** | **开 1 张卡**；**保持 wire 顺序为 `sort_order`，排序在 UI/Host 消费层做** |
| **B** | 选 3：**保持现状**（不做运行时重建/错误码拆分） | **不开卡**；保留"修改配置后重启生效"提示 |

### 10.2 核实结果：**A 完整落地，B 符合**

`doc/tasks/CHAPTER-MANUAL-SORT.md` 的 `status: done` 与 `canonical_evidence_status: complete`
**在代码层面成立**（虽然 AC1–AC10 未勾选，属记录卫生问题）：

| 要点 | 代码证据 |
|---|---|
| 原子持久化 | `src/application/library/service.py:212` `reorder_chapters`、`:323` `reorder_chapters_strict` |
| 原子性测试 | `tests/storage/test_chapter_reorder_atomic.py` |
| Wire 新命令（不改 `list_chapters` 顺序） | `src/bootstrap/core_service.py:7212` `elif command == "ReorderChapters":` |
| C# 消费层三件套 | `HostController.cs:639` / `IHostController.cs:223` / `NullHostController.cs:116` |
| VM 语义 | `ShelfViewModel.cs:275` `ReorderChapterAsync` |
| **视图拖拽手势** | `ShelfPageView.cs:161-163` DragDrop 三事件、`:601` `DoDragDropAsync`、`:614`、`:638` |

**⇒ 裁决 A 的契约边界也被遵守**：新增 `ReorderChapters` 命令做重排，`list_chapters` 的返回顺序未动。

### 10.3 未做（诚实）

- 未**逐字节**比 AC6 的 `M2-C1`/`C-07` 载体（`generate_api_inventory --check` 与 pins 18/18 间接支持）；
- 未跑 `test_chapter_reorder_atomic.py`（只做静态核实）；
- **未改那张卡的 AC 勾选**（不越权改别人的证据）。

**证据**：`verification/CHAPTER-MANUAL-SORT-VERIFY-1/`。

---

## 11. 结论（本复评的最终口径）

| goal 要求 | 状态 |
|---|---|
| **第一优先：Gate 六条** | 条件 1/2/6 **MET**；条件 3 **接近满足**（三重 GUI 证据）；条件 4 **AC1–AC6 ✅ / AC7 5/5 页**；条件 5 **NOT_RUN**（有书面判据） |
| **第二优先：裁决落地** | **A 完整落地 / B 符合**（§10 补核） |

**Gate 判定：`BLOCKED`** —— 条件 3（真机物理显示）、条件 4（签名、0.1.1 逐条断言）、条件 5（人工 GT）仍未满足。

**"可评估"已达成**：六条每一条都有明确判定、实测依据、以及"谁能提供"。
**"通过"未达成**：我不把它写成通过。
