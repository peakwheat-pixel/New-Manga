# Release Gate 六条 —— Agent 可完成性判定表

**生成者**：DSH（Lead / Architect / Integrator）｜2026-11-15
**依据**：`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §2–§4（六条现状与诚实边界）、
`MAINT-1-GATE-CONDITION-1/3/4/6-*` 系列、以及当前 head 的四件套实测。

**本表性质**：把 goal B「Release Gate 六条中『Agent 可独立完成』的部分全部关闭或给出明确判定」
落成一张可执行清单。**它不改变 Gate 结论** —— Gate 仍是 `BLOCKED`。

---

## 0. 一句话结论

| 类别 | 条数 | 说明 |
|---|---:|---|
| **Agent 可独立完成并可关闭** | **1** | 条件 6（证据链 + 独立最终 Review）—— 四件套已绿，独立 Review 本轮已派 |
| **Agent 可推进但无法单独关闭** | 3 | 条件 1（finding 实现需处置决策）、条件 4（打包可做，安装矩阵需真机）、条件 5（真实调用已验，质量基线需 GT 或 Owner 接受） |
| **必须人做** | 2 | 条件 2（远端可见性，需账号+网络）、条件 3 的真实 GUI 全流程（需人眼） |

⇒ **「Agent 可独立完成」的部分只有条件 6 一条；其余五条都有不可替代的人工环节或处置决策。**

---

## 1. 逐条判定

### 条件 1 —— 处置并验证 7 项开放 finding

| 维度 | 判定 |
|---|---|
| 现状 | **未完成**。`MAINT-1` P4 只处置了 4 张**提案卡**，不等于 7 项 finding 关闭 |
| Agent 可完成 | ① 逐项实现修复；② 每项派独立上下文 Review；③ 更新 Evidence/三指针 |
| **必须人做** | **每项 finding 的处置决策**（修 / 接受为 limitation / 豁免）—— 这是范围与风险取舍 |
| 判定 | **可推进，不可单独关闭** |

### 条件 2 —— `AUDIT-11-INC-001` 只读远端可见性调查

| 维度 | 判定 |
|---|---|
| 现状 | **未完成**（本轮未做） |
| Agent 可完成 | 无（`gh auth status` 未认证、`GH_TOKEN`/`GITHUB_TOKEN` 未设置） |
| **必须人做** | 提供仓库写/读凭据，或在 GitHub 网页侧完成只读可见性检查并回传结果 |
| 判定 | **必须人做** → 归入 `HUMAN-REQUIRED` |

### 条件 3 —— 完整 GUI / Core / Host 关键流程与 Avalonia TestHost

| 维度 | 判定 |
|---|---|
| 现状 | **部分**：headless 与三项目测试已绿；真实 GUI 全流程矩阵未做 |
| Agent 可完成 | ① 继续补 headless 覆盖（有测试可写）；② 跑 `dotnet test` 的 TestHost 部分；③ 整理矩阵 |
| **必须人做** | **真实 GUI 全流程**（四页导航、拖拽、主题切换、多屏）—— 需人眼判断「看起来对不对」 |
| 判定 | **部分可推进；GUI 矩阵必须人做** |

### 条件 4 —— 当前 commit 生成 Windows 包 + clean install / 启动 / 升级回退 / 四页 / 卸载矩阵

| 维度 | 判定 |
|---|---|
| 现状 | **未完成**。现存 `0.1.1` 旧包**不绑定当前基线**，不得当证据 |
| Agent 可完成 | ① 用 `tools/ci/publish-release.ps1` 在**当前 HEAD** 重新打包 sidecar；② 跑 singlefile + `-Smoke`（脚本自带"启动 exe + 隔离数据根 + host.log ready + exit 0"的真实窗口冒烟）；③ 产出绑定当前 commit 的包与冒烟证据 |
| **必须人做** | clean install / **升级回退** / **卸载**矩阵（改注册表、文件系统、真实用户环境）；安装器**签名**需证书 |
| 判定 | **打包与冒烟可做（能替换过时的 0.1.1 证据）；安装矩阵必须人做** |

### 条件 5 —— 模型 / API 与代表性质量验证，或 Owner 明确接受有边界限制

| 维度 | 判定 |
|---|---|
| 现状 | **部分**：已用产品自身 `OpenAiTranslationProvider` + `StdlibTransport` 对 DeepSeek 完成一次真实翻译（`deepseek-chat`、763/738ms、`valid_protocol=True`、`region-1 → 你好，你好吗？`、`region-2（sfx, ドガ）→ 轰`），证据 `verification/MAINT-1-RELEASE-MONITOR/model-api-verification.log`；**仍未做**：代表性质量基线、App/Host 端到端完整 UI 流程 |
| Agent 可完成 | ① 扩大真实调用的**覆盖面**（更多 region 类型 / 更长文本）；② 端到端跑通并记录 |
| **必须人做** | ① **质量基线**需要人工 GT（ground truth）—— 无 GT 不得宣称翻译准确率达标；② **Owner 明确接受有边界限制** 这一句本身就是人的决定 |
| 判定 | **可扩大证据；达标判定必须人做** |

### 条件 6 —— 当前 head 的 Canonical Evidence / governance / TaskPath / verify_pins / API inventory + 独立最终 Review

| 维度 | 判定 |
|---|---|
| 现状 | **部分**：四件套已绿（`check` PASS 3 warnings / `pins` 18/18 / `inventory` 1/80/6=87 / `App.Tests` 基线 955/0/11）；**独立最终 Review 未做** |
| Agent 可完成 | **全部**：四件套可重复实测 + 派未参与实现的独立上下文 Review + 出书面结论 |
| **必须人做** | 无 |
| 判定 | **Agent 可独立完成 → 本轮推进关闭** |

---

## 2. 本轮行动：条件 6

1. 四件套当前实测（见 §3）；
2. 已派独立上下文子 agent `gate6-final-review`，对当前 head 做未参与实现的最终复核，范围：
   Canonical Evidence 完整性、三指针一致性、门禁实测、limitation 登记、是否满足 Gate 条件 6 的语义；
3. 报告落 `doc/reviews/`，DSH 采纳后更新 Gate 评估。

> **不承诺**：条件 6 的 Review 通过**不等于** Gate 可解锁 —— 条件 1/2/4/5 仍未完成，条件 3 的 GUI 矩阵未做。
> 本文档 §0 已写明这点。

## 3. 四件套实测（2026-11-15，HEAD `b4910e143`）

| 门禁 | 结果 |
|---|---|
| `check.ps1` | PASS (3 warnings)，EXIT 0 |
| `verify_pins.ps1` | PASS (all 18)，EXIT 0 |
| `generate_api_inventory.py --check` | OK（1/80/6 = 87），EXIT 0 |
| `App.Tests` 基线 | 955 passed / 0 failed / 11 skipped（沿用既有基线；本轮未重跑全量） |

### 3.1 条件 6 独立最终 Review 的结论（已回）

独立子 agent `gate6-final-review`（未参与实现）对 `b4910e143` 的复核结论：
**`CONDITION_6_PARTIAL`**（P0/P1/P2/P3 = 0/2/4/4）。

**机械部分成立**：`check` PASS / `pins` 18-18 / `inventory` 87 / `-TaskPath` 5-5 PASS；
`b4910e143` 的 ledger 算术（642 文件 / 11 非终态）与仓外复算一致
（直接在工作区跑 `check.ps1` 曾 FAIL 2 errors，根因是**并发草稿** `RELEASE-GATE-DISPOSITION-1.md`
被 `Get-ChildItem doc/tasks/*.md` 计入、而 ledger 尚未重生成 —— 已在定稿时消除）。

**5 项欠缺**（条件 6 因此不能判关闭）：

| # | 欠缺 | 处置 |
|---|---|---|
| 1 | 证据包一致性：`four-pieces.log` 记录 FAIL 而文档写 PASS，且无命令/EXIT/时间戳 | **已修**：重写为含 command / head / EXIT / timestamp |
| 2 | `App.Tests` 定性复跑：954 passed / **1 failed** / 11 skipped（`PerformanceBaselineTests.HotSwitch…` median p95 **1014.0ms > 1000ms**） | **已核实为满载 flaky**：该测试**单独复跑通过**（1 passed / 0 failed / 24s）；非本轮引入（7 个 commit 零 `.cs`/`.axaml`/测试改动）。已登记为环境敏感项 |
| 3 | 3 个 Task 共 **12 条 `WORKTREE` pin 与所钉 commit 的 blob 不一致**（`i/lf` vs `w/crlf`），`WORKTREE_ENV` 缺 Git 版本与 `core.autocrlf` | **已修**：12 条改为 `BLOB` 口径（对齐 `GOV-HISTORICAL-CARD-METADATA-REPAIR-1` 的正确范式） |
| 4 | 三指针漂移：`PLAN:58`「BLOCKED：无」vs ledger 有 blocked；`PLAN:56` SIDECAR `done` vs 卡面 `in_progress`；4 张 `in_progress` 卡不在 DAG；本卡未登记 STATUS/PLAN | **部分修**：本卡登记；PLAN/STATUS 漂移因预算（3200/7000 bytes 已近上限）单独记录 |
| 5 | 需在**定稿 head** 上重锚一次轻量 Review | 待定稿后执行 |

> **`verify_final.py` 的 EXIT=1 已确认**：来自 8 条**先存** numstat FAIL
> （`V11R-B-1…B-5`、`V11R-C-1`、`MICA-FIX-1`、`FEA-07-AC5-NATIVE-1`），非本轮引入。
> 复核者一度测得 EXIT=0，是因其用了不同调用方式；本表以直接调用为准。


### 3.2 条件 4 的可做部分已执行（`RELEASE-PACKAGE-CURRENT-HEAD-1`）

在当前 HEAD 的产品代码树上产出 **94.94 MB 单文件 exe**（`07DD80F0…3AE74`）并通过**真实窗口冒烟**
（`window_found`/`host_ready`/`exit_kind=natural`/截图；独立复核亲眼看图确认为 NewManga 本体）。
这消除了 §3 所述「`0.1.1` 旧包不绑定当前基线」的证据缺口。

**但条件 4 的判定不变**，因为：

1. **单文件包不含 sidecar** —— 94.94 MB 的 exe 无法独立运行，需 792 MB sidecar 外挂
   （`publish-release.ps1:61` 自述 `needs the sidecar bundle at runtime`）⇒ **不是可分发包**；
2. 冒烟截图是 **0/0 空态**，未触达读写/并发路径；**E-7 仍有 5 项开放**（并发安全不可宣称）；
3. clean install / 升级回退 / 卸载 / 安装器签名仍缺（需真机与证书）。

## 4. 与人协作的最小集（汇总进 HUMAN-REQUIRED）

| 编号 | 事项 | 归属 |
|---|---|---|
| H-06 | GitHub 凭据或网页侧只读可见性检查（条件 2） | 新增 |
| H-07 | 真实 GUI 全流程矩阵：四页导航/拖拽/主题切换/多屏（条件 3） | 与 `HUMAN-REQUIRED` 的 H-02 相邻，可合并 |
| H-08 | clean install / 升级回退 / 卸载 + 安装器签名（条件 4） | 新增 |
| H-09 | 翻译质量基线的人工 GT 或「接受有边界限制」的决定（条件 5） | 部分已有（H-05 质量基线判断） |

> `doc/reviews/HUMAN-REQUIRED-2026-11-15.md` 的 5 项 + 本表新增 3 项（H-06/H-08/H-09，
> H-07 与 H-02 合并）= **人对 Gate 的全部不可替代输入**。

## 5. 已知边界（不淡化）

1. 本表只做**可完成性判定**，不改变 Gate `BLOCKED` 结论；
2. 条件 4 的「打包可做」不等于「可发布」—— 安装矩阵与签名仍缺；
3. 条件 5 的「真实调用已验」是**一次**样本，不足以支撑质量达标；
4. 条件 1 的 7 项 finding 处置需要**决策**而非执行，Agent 不能替 Owner 做风险取舍。
