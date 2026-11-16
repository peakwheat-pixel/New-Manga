# HUMAN-REQUIRED 清单（2026-11-15，r1 复核后修订）

**生成者**：DSH（Lead / Architect / Integrator）
**依据**：`verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md`（72 条 `blocked` 逐条判定）、
`doc/reviews/FINAL-HANDOFF-2026-11-15.md`。

**这份清单只列「Agent 无法完成」的事**——需要物理设备、人眼判断或外部账号凭据。

## 数字对账（r1 复核 P2-01 要求）

| 口径 | 数字 | 说明 |
|---|---:|---|
| 72 条 `blocked` 中判为 `HUMAN` | **5** | `MICA-FIX-1` AC1/AC3、`FEA-07-AC5-NATIVE-1` AC-N1/N3/N4 |
| 非 `blocked` 但仍需人做的事 | **3** | `FINAL-HANDOFF-2026-11-15` 未关闭项：F11、GitHub 发布、质量基线 |
| 合并为清单项 | **5** | H-01（MICA 2 条）、H-02（FEA-07 3 条）、H-03（F11）、H-04（GitHub）、H-05（质量基线） |

> **2026-11-16 更新（本文件按 append-only 演进，上表保留原快照）**：
> 1. `H-01` 的覆盖范围由 `MICA-FIX-1` AC1 + AC3 扩展为 **AC1 + AC2（判定部分）+ AC3** ——
>    AC2 的人眼判定半由 `HUMAN-VS-AGENT-SPLIT-2026-11-16.md:29` 并入，已写进 H-01 步骤 6；
> 2. 新增 **`H-10` 阅读器 overlay（F11）视觉确认** —— Gate 条件 3 的唯一剩余项
>    （注意与 `H-03` 的**资料柜** F11 是不同页面）；
> 3. `H-08` 的「签名需要代码签名证书」表述**已过时并更正**：实际走 SignPath Foundation 免费 OSS 通道，
>    只差 `H-04` 的两步 GitHub 操作；且「没有可分发包」缺口已由 `RELEASE-PACKAGE-BUNDLE-1` 关闭。
> 4. 六条 Gate 条件的逐条剩余动作与人侧最小集映射，见
>    `doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` §8。

> 其余 67 条 `blocked` **不在此清单**：`ARCHIVE` 15（对象已退役）、`WITHDRAWN` 6（方案撤回）、
> `RERUN` 10 / `DOC` 9 / `IMPL` 22（Agent 可做）、`MECHANISM_NA` 5（要求本身不适用）。

---

## H-01 Mica 材质真机验收（覆盖 `MICA-FIX-1` AC1 + **AC2（判定部分）** + AC3）

- **为什么必须人做**：Mica 透明效果只能人眼看；且**必须同时拍到窗口与桌面壁纸**才能对比。
  现有 `titlebar-solid.png` 经独立复核确认是 ChatGPT 桌面应用全屏窗口（画面内无 NewManga），
  `two-wallpapers.json` 的 `titlebar_pixel = -1`（取色失败）——两张证据都不成立，必须重采。
- **最小步骤**：
  1. 在 **Windows 11** 上启动已安装的 NewManga（≥ 0.1.1）；
  2. 记录窗口的可辨识身份：**任务管理器里 NewManga 进程名/PID**，或窗口标题栏截图（用于证明不是别的应用）；
  3. 桌面设为**纯色壁纸** → 截一张（画面须同时包含**窗口标题栏边缘 + 一部分壁纸**，能看出透出）；
  4. 桌面设为**图案壁纸** → 同位置再截一张；
  5. 两张图放入 `verification/MICA-FIX-1/mica/`，命名 `real-solid.png` / `real-pattern.png`；
  6. **AC2 的判定部分**（2026-11-16 由 `HUMAN-VS-AGENT-SPLIT-2026-11-16.md:29` 并入）：
     AC2 要求「启动时输出 `ActualTransparencyLevel` 与 `WindowMaterialKind`，证明拿到 Mica 而非回退 None」。
     其中**代码实现已存在**（`apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:1032`），
     缺的是**原始启动日志/诊断输出**与**人眼判定「确实拿到了 Mica」**。请在截图同一轮里：
     - 用 `--diagnostics` 启动（或按既有诊断路径）并**保留原始日志文件**，
       一并放入 `verification/MICA-FIX-1/`；
     - 用一句话回答：**「材质确实生效（Mica）/ 回退到 None」** —— 这是人的判定，不是日志能替代的。
     （若日志能自证 `material=Mica`、`actual=Mica` 且来自**本次真实启动**，Agent 可据此把 AC2 的
     证据部分补齐；但「人眼确认材质生效」仍要你这一句。）
  7. **AC3 的环境限制**：若你只有 Windows 11、没有 Win10 或不支持 Mica 的环境，请明确回复
     「无 Win10 环境」——此时 AC3 保持 `blocked` 并记录为环境不可得，**不要**假装核对过。
- **预估**：约 3 分钟（无 Win10 环境时更短）。
- **完成后**：DSH 把 AC1 改判 `verified` 并补 pin；**AC2 按日志 + 判定结果改判**；AC3 视回复决定 `verified` 或保留 `blocked`。

## H-02 真机多屏验收（覆盖 `FEA-07-AC5-NATIVE-1` AC-N1 + AC-N3 + AC-N4）

> **2026-11-16 收窄（ADJ §7.21）**：`FEA-07-AC5-NATIVE-1` 的 AC-N2 / AC-N5 经独立复核（`reviewer-fea07b`，
> ACCEPTED 带 limitation）已收口，**已取证**的部分不再需要人做：7 组混合 DPI 拖动、OS 级拔屏 + 重插回 4K、
> 逐屏缩放 UIA、PerMonitorV2 exe 证据、窗口持久化探测、中文 IME 组合输入、快捷键不重复执行、
> 74 张真桌面截图、逐案例 JSON 与恢复点 JSON（详见该卡尾 L-N1…L-N5）。
> 本项因此**由 3 大项收窄为下面 3 个小项**，且**不得再扩展**回已取证的范围。

- **为什么必须人做**：需要真实的双屏 + 多档 DPI 组合；「无模糊/无错位」是主观视觉判断；
  物理拔屏与恢复点还原必须真的动手。
- **已有**：4K 100/125/150/175/200 × 2K 100/125/150 共 **7/15** 组合通过
  （`verification/FEA-07-AC5-NATIVE-1/matrix-summary.json`）；物理拔屏/重插已有**自动化脚本**证据。
- **最小步骤（收窄后只剩 3 项）**：
  1. **剩余 8 组（AC-N1）**：按 `doc/tasks/FEA-07-AC5-NATIVE-1.md` 的组合表补测剩余组合
     （若表不完整，就以「4K × 2K 的 15 组全矩阵」为准，做没做过的那些）；
     每组记录「窗口无模糊 / 无错位」是/否 —— 这一条是**主观判断**，机器断言替代不了。
  2. **物理拔屏（AC-N3）的人工复核**：自动化脚本已验 `unsaved-edit-unplug-*.json`；
     请**亲手**做一次「有未保存内容 → 物理拔副屏」，确认 fail-closed（不丢数据）与
     「拔后主窗最小化、恢复后回原几何」与脚本记录一致。
  3. **恢复点还原（AC-N4）**：按卡面恢复点清单逐项确认窗口位置/尺寸/所在屏是否还原；
     卡面明记「恢复点按用户决定保留原生 2K」，请确认该决定是否仍然有效。
- **预估**：约 20 分钟。
- **完成后**：DSH 按结果改判 AC-N1/N3/N4，并把新证据登记进 Canonical Evidence。

## H-03 资料柜 F11 全屏（`FINAL-HANDOFF` 未关闭项 1）

- **为什么必须人做**：需要人在真实窗口按键并观察全屏切换与退出后状态恢复。
- **最小步骤**：
  1. 启动已安装的 NewManga；
  2. 依次点开**书架、工作台、阅读器、设置**四个一级页面各一次（确认基本可达）；
  3. 进入「资料柜」，按 `F11` → 观察是否进入全屏；
  4. 再按 `F11` → 观察是否退出且布局恢复；
  5. 回复「成/不成 + 截图」。
- **预估**：约 2 分钟。

## H-04 GitHub 默认分支与发布工作流（`FINAL-HANDOFF` 未关闭项 2）

- **为什么必须人做**：`gh auth status` 未认证，`GH_TOKEN` / `GITHUB_TOKEN` 未设置 ——
  Agent 没有仓库写权限，无法改默认分支或触发 Actions。
- **最小步骤**：
  1. GitHub 仓库页 → **Settings → General → Default branch** → 改为 `public-release`
     （注意：**不是** Settings → Branches，那是分支保护规则）；
  2. **Actions → `build-release` → Run workflow**，参数 `version=0.1.1`、`sign=false`；
  3. 把 run 链接或截图回复 DSH。
- **预估**：约 5 分钟。

## H-05 质量基线判断（`FINAL-HANDOFF` 未关闭项 3）

- **为什么必须人做**：这是**验收尺度**的取舍，不是技术事实。
- **背景**：`FINAL-HANDOFF-2026-11-15` §4 第 3 项要求「对质量基线做判断，或明确接受 `NOT_RUN`」。
  当前 `App.Tests` 有可信基线（955 passed / 0 failed / 11 skipped），但部分端到端项是 `NOT_RUN`。
- **最小步骤**：回复一句二选一 ——
  （a）「接受当前基线，`NOT_RUN` 项不作为发布阻断」；或
  （b）「`NOT_RUN` 项必须先补跑，再谈发布」。
- **预估**：1 分钟。

---

## 已从本清单**移除**的项（r1 复核 P1-02）

- **原 H-04「P20 内存阈值裁决」**：`P20-MEM-OPT-1` 是旧 Tauri/WebView2 卡（`allowed_paths` 含 Tauri 侧、
  证据是 `m2rc1-desktop`/`msedgewebview2` 进程），AD-002 已退役该壳；卡内 `:93-95` 已记录
  「AC2 经 2026-10-18 用户裁决后无需实施」。**再让用户二选一属重复**。
  该卡 3 条 `blocked` 已归入 `ARCHIVE`（对象在当前架构不存在），不需要人再做任何事。

---

## 怎么用

- **人**：H-01 → H-03 → **H-10** → H-04 → H-05 约 12 分钟；H-02 另需 20 分钟；H-08 另需 30 分钟。
- **Agent**：其余 67 条 `blocked` 里，**41 条可由 Agent 闭合**（`RERUN` 10 / `DOC` 9 / `IMPL` 22），
  另有 `MECHANISM_NA` 5 条待 DSH 裁决是否改判 `not-applicable`。
- 本清单**不阻塞**目标 A（四件套）与目标 C（其余技术债）的推进。

---

## 6. Release Gate 侧的人侧输入（2026-11-15 补充）

以下三项来自 `RELEASE-GATE-DISPOSITION-1` 的六条判定，是 **Gate 解锁不可替代的人工环节**。
编号接续上文。

### H-06 远端可见性检查（Gate 条件 2：`AUDIT-11-INC-001`）

- **为什么必须人做**：`gh auth status` 未认证、`GH_TOKEN`/`GITHUB_TOKEN` 未设置 —— Agent 无远端访问凭据。
- **最小步骤**：任选其一 ——
  （a）在 GitHub 网页侧确认目标仓库的**可见性**（public / private / internal）并截图回传；
  （b）给 Agent 配置只读 token（`GH_TOKEN`），由 Agent 执行只读查询。
- **预估**：约 2 分钟。

### H-08 Windows 安装矩阵 + 签名（Gate 条件 4）

- **为什么必须人做**：clean install / 升级回退 / 卸载需要真实用户环境（注册表、文件系统、快捷方式）。
- **签名不是「要买证书」**（2026-11-16 更正，原表述过时）：`verification/SIGNING-PATH-AUDIT-1/README.md`
  已查明走 **SignPath Foundation 免费 OSS 通道**，且 `P0-1/2/3/5` 已在 `public-release` 分支完成；
  **只差 P0-4 两步 GitHub 操作**（见 `H-04`，约 2 分钟）。`unsigned` 是当前设计，
  `build-installer.ps1` 把 `authenticode_status` 记入 `build-info.json`。
- **Agent 能做的前置（已完成）**：`verification/RELEASE-PACKAGE-BUNDLE-1/README.md` 已用正规脚本
  `apps/desktop-avalonia/scripts/package.ps1 -WithModels` 产出**含 sidecar 的可分发 portable 包**
  （1,038 文件 / 827.6 MB / zip sha256 `6a97d2e4…`），并通过真实窗口启动验证
  （窗口 `New Manga`、`core_service ready`+`host_bridge ready`、self-check `Passed`、DB 创建）；
  独立复核者另从零启动两次（含不传 `--sidecar-dir` 的回退路径）。
  ⇒ **「没有可分发包」的缺口已关闭**，剩下的是**安装矩阵**本身。
- **最小步骤**：拿到该 zip 后，在一台 Win11 机器上做：全新安装 → 启动 →
  **跨版本二进制**升级 → 回退 → 四页可达 → 卸载；记录每步结果。
  注意 `INSTALLER-MATRIX-1` 自陈其「升级/回退」是**标签回退**（0.1.0 包复制 0.1.1 只改 `VERSION.json`，
  exe/sidecar 字节不动）⇒ 这一步要用**两个真正不同的二进制**才算过。
- **预估**：约 30 分钟（含下载与两次安装）。

### H-10 阅读器 overlay（F11）视觉确认（Gate 条件 3 唯一剩余项）

- **为什么必须人做**：阅读器 F11 全屏/无边框的**视觉表现**无法用 headless 测试代替。
  逻辑侧已被 13 个测试覆盖（`F11HotkeyTests` 9 + `V2ImmersiveReaderTests` 4，驱动生产 public 方法
  `TryHandleGlobalKey`），证据 `verification/READER-ENTRY-PATH-1/`；
  `verification/GATE3-READER-OVERLAY-1/` 实测 `PostMessage(WM_KEYDOWN, VK_F11)` **无效**，Agent 无法自行触发。
- **注意与 `H-03` 的区别**：`H-03` 是**资料柜**的 F11 全屏，本项是**阅读器 overlay**，是两个不同页面。
- **最小步骤**：
  1. 启动已安装的 NewManga，进入阅读器并打开一本漫画/一个页面；
  2. 按一次 `F11`；
  3. 观察：是否进入全屏、是否无边框、退出后布局是否恢复；
  4. 截图（进入全屏后一张 + 退出后一张）放入 `verification/GATE3-READER-OVERLAY-1/`，
     命名 `real-overlay.png` / `real-restored.png`；并回一句「成/不成」。
- **预估**：约 10 秒 + 截图。
- **完成后**：DSH 把条件 3 的对应子项改为已验并更新 `RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md` §3。

### H-09 翻译质量基线或「接受有边界限制」（Gate 条件 5）

- **为什么必须人做**：质量达标需要**人工 GT**；无 GT 不得宣称准确率达标。
  另外「Owner 明确接受有边界限制」这句本身就是人的决定。
- **已有**：产品自身 `OpenAiTranslationProvider` + `StdlibTransport` 对 DeepSeek 的一次真实翻译
  （`deepseek-chat`、763/738ms、`valid_protocol=True`、`region-1 → 你好，你好吗？`、
  `region-2（sfx, ドガ）→ 轰`），证据 `verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`。
- **最小步骤**：二选一 ——
  （a）提供 20–50 条代表性 region 的人工标准译文（可给一个文件），Agent 跑对比并出报告；
  （b）明确一句「接受当前有边界限制，不以质量基线作为发布阻断」。
- **预估**：约 1 分钟（选 b）；选 a 取决于 GT 准备量。
