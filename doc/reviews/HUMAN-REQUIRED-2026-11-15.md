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

> 其余 67 条 `blocked` **不在此清单**：`ARCHIVE` 15（对象已退役）、`WITHDRAWN` 6（方案撤回）、
> `RERUN` 10 / `DOC` 9 / `IMPL` 22（Agent 可做）、`MECHANISM_NA` 5（要求本身不适用）。

---

## H-01 Mica 材质真机验收（覆盖 `MICA-FIX-1` AC1 + AC3）

- **为什么必须人做**：Mica 透明效果只能人眼看；且**必须同时拍到窗口与桌面壁纸**才能对比。
  现有 `titlebar-solid.png` 经独立复核确认是 ChatGPT 桌面应用全屏窗口（画面内无 NewManga），
  `two-wallpapers.json` 的 `titlebar_pixel = -1`（取色失败）——两张证据都不成立，必须重采。
- **最小步骤**：
  1. 在 **Windows 11** 上启动已安装的 NewManga（≥ 0.1.1）；
  2. 记录窗口的可辨识身份：**任务管理器里 NewManga 进程名/PID**，或窗口标题栏截图（用于证明不是别的应用）；
  3. 桌面设为**纯色壁纸** → 截一张（画面须同时包含**窗口标题栏边缘 + 一部分壁纸**，能看出透出）；
  4. 桌面设为**图案壁纸** → 同位置再截一张；
  5. 两张图放入 `verification/MICA-FIX-1/mica/`，命名 `real-solid.png` / `real-pattern.png`；
  6. **AC3 的环境限制**：若你只有 Windows 11、没有 Win10 或不支持 Mica 的环境，请明确回复
     「无 Win10 环境」——此时 AC3 保持 `blocked` 并记录为环境不可得，**不要**假装核对过。
- **预估**：约 3 分钟（无 Win10 环境时更短）。
- **完成后**：DSH 把 AC1 改判 `verified` 并补 pin；AC3 视回复决定 `verified` 或保留 `blocked`。

## H-02 真机多屏验收（覆盖 `FEA-07-AC5-NATIVE-1` AC-N1 + AC-N3 + AC-N4）

- **为什么必须人做**：需要真实的双屏 + 多档 DPI 组合；「无模糊/无错位」是主观视觉判断；
  物理拔屏与恢复点还原必须真的动手。
- **已有**：4K 100/125/150/175/200 × 2K 100/125/150 共 **7/15** 组合通过。
- **最小步骤**：
  1. **剩余 8 组（AC-N1）**：按 `doc/tasks/FEA-07-AC5-NATIVE-1.md` 的组合表补测剩余组合
     （卡面 `:120` 记了未做项；若表不完整，就以「4K × 2K 的 15 组全矩阵」为准，做没做过的那些）；
     每组记录「窗口无模糊 / 无错位」是/否；
  2. **物理拔屏（AC-N3）**：先让编辑器有**未保存内容**，然后物理拔掉副屏 →
     确认应用是否 fail-closed（不丢数据）；记录拔屏后主窗是否被最小化、恢复后是否回到原几何；
  3. **恢复点还原（AC-N4）**：按卡面 `:135` 的恢复点清单，逐项确认窗口位置/尺寸/所在屏是否还原；
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

- **人**：H-01 → H-03 → H-04 → H-05 约 11 分钟；H-02 另需 20 分钟。
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

- **为什么必须人做**：clean install / 升级回退 / 卸载需要真实用户环境（注册表、文件系统、快捷方式）；
  安装器**签名**需要代码签名证书。
- **Agent 能做的前置**：用 `tools/ci/publish-release.ps1` 在当前 HEAD 重新打包 + singlefile + `-Smoke`
  （脚本自带「启动 exe + 隔离数据根 + host.log ready + exit 0」的真实窗口冒烟）——
  这能替换掉不绑定当前基线的 `0.1.1` 旧证据，但**不等于**安装矩阵。
- **最小步骤**：拿到当轮产出的 zip 后，在一台 Win11 机器上做：全新安装 → 启动 → 升级到下一个包 →
  回退 → 四页可达 → 卸载；记录每步结果。
- **预估**：约 30 分钟（含下载与两次安装）。

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
