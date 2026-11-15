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
⇒ **GUI 进程无法在本 shell 的窗口站/桌面上下文中完成初始化**。
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
| **AC7 四页可达性** | 需在**打包产物**上逐页导航 ⇒ **需 GUI 启动** ⇒ 同 §3 的根因，Agent 做不到。**且未用 headless 证据冒充。** |
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

1. **条件 1 的 8 项 finding**：我核对了处置裁决与 L-L1-2 的实现，但**未逐项重跑每项 finding 的原始验证步骤** ——
   这部分依赖既有 review 记录（可在 `MAINT-1-GATE-CONDITION-1-FINDING-ADJUDICATION` 中追溯）。
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
