# ZCode 书面裁定：安装包许可证声明与 Gate 条件 4 证据资格（2026-11-17）

- **裁定者**：ZCode（桌面版内置 CLI，`--mode plan --json`，只读仓库；未改任何文件）
- **派发与采纳**：DSH 2026-11-17 派发；正文为**原文逐字落盘**，采纳记录见文末
- **被裁决问题**：`L-IM-7`（base 变体内置 632 MB 权重却声明 GPL-3.0-or-later）
- **对象**：`G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1/stage/NewManga-0.1.1-win-x64`
- **ZCODE_EXIT**：0（usage：input 91,408 / output 12,448 tokens）

---

事实核实完成（只读，未改任何文件）。以下为书面裁定。

---

# 裁定书：`NewManga-0.1.1-win-x64` stage 的许可证声明与 Gate 证据资格（L-IM-7 范畴）

- **裁定者**：ZCode（独立裁决，只读仓库事实，未修改任何文件）
- **日期**：2026-11-17
- **对象**：workspace 中 stage `NewManga-0.1.1-win-x64`（VERSION.json 声明 variant=base / license=GPL-3.0-or-later，实际内置 3 个 ONNX 共 632,552,582 B）

## TL;DR（大白话）

1. **Q1**：这个包现在**不能**声明 GPL-3.0-or-later。仓库自己已有硬规则（`package.ps1`）：只要包里有权重，整体就按 AGPL-3.0 声明；三个权重的上游许可在台账里全是「待核实」，核实清零前 GPL 声明非法。
2. **Q2**：**发布阻塞（P0）**，不是「文档待更新」。NOTICE/LICENSE_AUDIT 是装进安装包、给每个接收方看的合规文件，写「不含权重」实际装了 632MB 权重 = 虚假许可披露，仓库加严护栏已实测拒绝此 stage。
3. **Q3**：**No**。Gate 条件 4 的既有裁定要求证据绑定「最终安装包 hash」；Q1/Q2 修复必然重打包，现在跑的矩阵对最终包无证据效力，且该 stage 连自家护栏都过不了。

---

## Q1：license 应声明什么？

### 结论

**不得声明 GPL-3.0-or-later。** 当前唯一可立即执行的合法声明是 **AGPL-3.0**；另一条合法路径是**先移除权重回归真 base**（则 GPL-3.0-or-later 维持）。不存在「variant=base + 内置 632MB 权重 + license=GPL-3.0-or-later」这个第三状态。

### 可执行判定规则（确定性，无「看情况」）

按顺序执行，落到哪个分支就是哪个结论：

| 步骤 | 判定 | 结论 |
|---|---|---|
| R1 | 逐文件枚举 stage `app/core-sidecar/models/`（sha256 入 manifest），查 `THIRD_PARTY_LICENSES.md` §3 台账 | — |
| R2 | 任一随包权重登记为「已核实 AGPL-3.0」 | 包级 license = **AGPL-3.0** |
| R3 | 随包权重 = 0 | 包级 license = **GPL-3.0-or-later** |
| R4 | 存在权重且台账含「[待核实]」 | **禁止声明 GPL-3.0-or-later**；只允许两态：保守声明 **AGPL-3.0**（立即可执行），或**发布阻塞**直至核实清零后按 R2/R3 归位 |

本案落在 **R4**（rtdetr-v2-fixed、manga-ocr encoder/decoder 三项台账均为 [待核实]）。`package.ps1` 现行实现（含权重即 AGPL-3.0）是 R2–R4 的保守化封装，在待核实清零前**不得放宽**。

### 依据

1. **仓库边界规则**：`AGENTS.md:58` — "产品按 GPL-3.0 开源分发（若集成 AGPL-3.0 组件如 Ultralytics，则整体按 AGPL-3.0 声明）。引入新依赖……必须先确认许可兼容并在 Task 中记录"。随包分发 632MB 权重属"集成组件"的最重形态；未确认兼容即不得按 GPL 声明。
2. **仓库已固化的判定实现**：`apps/desktop-avalonia/scripts/package.ps1:146-150` — "$licenseDeclaration=if($modelsBundled){'AGPL-3.0'}else{'GPL-3.0-or-later'}"（AGPL-RELEASE-1 AC2/AC4）。按此规则，本 stage 含 models 目录 ⇒ 应得 AGPL-3.0；stage 里实际的 GPL 声明是**手工改写的产物**（`doc/tasks/INSTALLER-METADATA-CONSISTENCY-1.md:48-49` 实测认定 "读起来是手工改写"；`PACKAGE-VERSION-JSON-DERIVED-1.md:43` 认定 "被手工补过"），不是生成器干净输出。
3. **随包声明体系自身**：仓库根 `NOTICE.md:7-10` — base = "不含模型权重" ⇒ GPL-3.0-or-later；含权重 ⇒ AGPL-3.0。本 stage 的组合同时违反该表的两行。
4. **待核实登记**：`THIRD_PARTY_LICENSES.md:37-39`（rtdetr = "Apache-2.0（HF 模型卡）[待核实，不阻断本卡]"；manga-ocr 两项 "MangaOCR 上游 [待核实，不阻断本卡]"）、`:51`（"[待核实] 项……在下一次发行 Gate 前补成一手结论"）。
5. **不裁上游法律结论**：三个权重上游许可的真实属性（Apache-2.0 是否成立等）——**证据不足，本裁定不予认定**；R4 的阻塞正来自这一空缺，这也是为何保守声明 AGPL-3.0 与阻塞核实是仅有的两个合法出口。

### 影响面

- `VERSION.json` 的 `license`/`bundled_weights_license` 字段（生成器侧已由 `PACKAGE-VERSION-JSON-DERIVED-1` 修复为磁盘派生，但 license 派生规则维持现状即可，无需改代码——本案是 stage 被手工污染，非规则错）；
- `NOTICE.md` 变体表、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md:9-10,20-21`、`THIRD_PARTY_LICENSES.md` §3；
- `packaging/nsis/installer.nsi:33,73`（NSIS 许可页直接展示 NOTICE.md，文案同错则同改）；
- 若保留权重：variant 语义与 stage 命名（`-models` 后缀体系）需对齐，否则护栏 `tools/ci/verify-package-manifest.ps1` 会继续拒绝。

---

## Q2：NOTICE/LICENSE_AUDIT 与实物不一致，定性 + severity？

### 结论

**发布阻塞（P0/Blocker），不是"文档待更新"。** 其中可拆两层：

- (a) 随包合规文件与实物矛盾（"base 不含权重" vs 实含 632,552,582 B）——**P0**；
- (b) rtdetr/manga-ocr 上游许可「待核实」——单看是 **P1**（`THIRD_PARTY_LICENSES.md:51` 已承诺下次发行 Gate 前补一手结论）；与 (a) 叠加后整体按 P0 处置。

### 依据

1. **severity 口径**：`doc/08_ACCEPTANCE_CRITERIA.md:50-56` — P0/Blocker："禁止发布"；`:69-75` — P1："正式 Release 前必须通过"；`:86-88` — P2 可延期但须免责披露。虚假合规披露无法靠 Release Notes 免责，P2 路径不适用；它是拟分发物本身的合规真实性问题，须显式阻断，故高于 P1。
2. **NOTICE/LICENSE_AUDIT 不是普通文档**：`package.ps1:103-112` 逐字节 SHA-256 校验复制进 stage；`build-installer.ps1:89-105` 强制在场、缺失即 throw；`installer.nsi:33` 许可页直接展示 NOTICE.md——即安装者会在许可页看到与包内容相反的承诺。
3. **矛盾量级**：非笔误级——声称 0 权重 vs 实际 632,552,582 B（包体积主体），接收方据此无法履行任何上游义务；叠加 version 0.1.0 vs 0.1.1、1,041 条 manifest 幽灵条目（L-IM-8 五条 FAIL，`doc/tasks/INSTALLER-MATRIX-1.md:182-189`）。
4. **护栏已按 blocker 行事**：加严后 `verify-package-manifest.ps1` 对该 stage "FAILED with 5 problem(s) / EXIT=1"，`build-installer.ps1:151` fail-closed "refusing to build the installer"（`INSTALLER-METADATA-CONSISTENCY-1.md:124-133`）。

### 处置方式

1. **立即**：该 stage 维持"不可发布、不可作 Gate 证据"标记；历史证据字节保留不覆盖（与 L-IM-8 处置一致），由护栏负责拒绝它。
2. **修复二选一**（与 Q1 联动，方向取舍属用户产品裁决）：
   - **方向 A（保留权重随包）**：先兑现 `THIRD_PARTY_LICENSES.md:51` 承诺完成三权重一手许可核实 → 按核实结论定包级 license（核实期间保守 AGPL-3.0）→ 同步改 NOTICE 变体表 / LICENSE_AUDIT / THIRD_PARTY_LICENSES §3 / installer.nsi 许可页文案 → variant 与 stage 命名对齐 → 由 `package.ps1` 干净重建，禁止手工补 VERSION.json 字段。
   - **方向 B（回归 base 语义）**：从 base stage 移除权重重打包，GPL-3.0-or-later 维持，NOTICE 小改即可。
3. 每处声明改动按 `AGENTS.md:58` 在 Task 中记录。

---

## Q3：Q1/Q2 未解决前，能否作为 Release Gate 条件 4 的证据？

### 结论

**No。** 且注意：即使 Q1/Q2 之后解决，也必须在新包字节上重跑——旧结果不可沿用。

### 理由

1. **证据绑定要求**：条件 4 最低证据为"固定当前产品 commit 和安装包 hash"、真实 Windows 环境执行、"模拟结果或 dry-run 不可替代"（`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md:57`；条件原文 `audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:28`）。Q1/Q2 修复必然改变包内容（NOTICE/VERSION.json/manifest/可能权重集与 stage 名）并重打包——现在跑出的矩阵对最终包 hash 不构成绑定证据。
2. **升级/回退子项不可解释**：条件 4 含跨版本升级/回退，该 stage 自身 version 0.1.1 vs manifest 0.1.0、1,041 条不存在条目（L-IM-8 五条 FAIL），升级矩阵在此包上的结果无法归因。
3. **过不了自家护栏**：加严护栏对该 stage EXIT=1、build-installer fail-closed——一个被发布护栏拒绝的 stage 不能进入 Gate 证据记录。
4. **既有裁定链一致**：`INSTALLER-MATRIX-1` AC8/L-IM-5 已明确"不得声称条件 4 满足"，条件 4 归 `RELEASE-GATE4-SIGNED-MATRIX-1`（proposed，要求真机 + 真实 Authenticode 签名 + 跨版本二进制升级回退）。
5. **允许的用途**：仅限**机制演练**（脚本流程、护栏行为验证），且须如实标注 non-evidentiary——`INSTALLER-MATRIX-1` 已按此定位收口，本次裁定不变更其结论。

---

## 证据不足清单（不裁）

- 三个 ONNX 权重上游许可的真实法律属性（Apache-2.0 / 其他是否成立）——台账自标 [待核实]，本裁定不推测。
- stage 内 `VERSION.json` 手工改写的责任归属——仓库文档仅认定"手工改写"事实，无 author 证据。

## 推荐下一步

本裁定对应 `INSTALLER-MATRIX-1.md:196` 登记的 **L-IM-7（许可证，需裁决）** 与 `INSTALLER-METADATA-CONSISTENCY-1.md:135` 边界（"未改许可证声明（L-IM-7 另行裁决）"）。建议：由 DSH 将本裁定处置落进 L-IM-7（方向 A/B 的选择属用户产品裁决），随后释放后续卡链：三权重一手许可核实 → `package.ps1` 干净重打包 → `RELEASE-GATE4-SIGNED-MATRIX-1`（仍为 proposed，须真实签名 + 真机矩阵）。在此之前，**无需对 stage 本身做任何字节改动**（护栏已阻断，历史证据保留）。

---

## DSH 采纳记录（2026-11-17）

本裁定**全文采纳**，并据此执行：

1. **Q1 采纳**：`license=GPL-3.0-or-later` 与随包 632,552,582 B 权重不相容 —— 该声明**非法**；合法出口只有两个：
   ① 保守声明 **AGPL-3.0**（可立即执行）；② 移除权重回归真 base（则维持 GPL-3.0-or-later）。
   判定规则按裁定书 R1–R4 执行（本案落在 **R4**：权重台账三项均为「待核实」）。
2. **Q2 采纳**：定为 **P0 / 发布阻塞**（随包 `NOTICE.md` / `LICENSE_AUDIT.md` 对接收方作出与实物相反的许可承诺）。
   该 stage 标记为**不可发布、不可作 Gate 证据**；**不覆盖**历史字节，由加严后的护栏负责拒绝（实测 8 条 FAIL）。
3. **Q3 采纳**：该包**不能**作为 Release Gate 条件 4 的证据；即使 Q1/Q2 修复后，也必须**在新包字节上重跑**矩阵。
   ⇒ 条件 4 的既有等待项从「缺证书」扩展为「**先产出合规新包 + 再签名 + 再跑矩阵**」。
4. **未裁决部分**：权重上游许可的**法律属性**（Apache-2.0 是否成立等）—— 裁定书写明「证据不足」，DSH 亦不认定。
5. **方向 A/B 属用户产品裁决**（保留权重随包 vs 回归 base 语义），已在
   `doc/tasks/LICENSE-VARIANT-DECLARATION-1.md` 登记为阻塞项，等用户选向。

**边界**：本裁定与采纳都**不改变** `Technical Gate=NOT_SATISFIED`，也**不构成**任何发布验收。

---

## 第二次调用（2026-11-17，请求 ZCode 直接选向）—— **返回不完整**

DSH 按「需要人工裁决的事项一律交 Codex 或 ZCode」的授权，再次调用 ZCode，要求它在方向 A（保留权重 + 声明 AGPL-3.0）
与方向 B（移除权重 + 维持 GPL-3.0-or-later）之间**直接选定**。`ZCODE_EXIT=0`，但 `response` 字段只有 **236 字符**，
正文（预期包含 Q1 选择 + Q2 执行清单 + Q3 影响）**被截断**，只有前导段完整返回。前导段原文：

> 复核完毕，两个关键修正已确认：① `package.ps1:156-167`（VERSION-JSON-GUARD-ALIGN-1 F-PVD-02 修复）**已经**写入 `app_build` 段，
> 子代理的「缺 app_build」结论过时，不构成依赖；② `installer.nsi:60/:72/:73/:103` 四处硬编码 base/GPL 文案——即使打进 models stage 文案也是错的，
> 这是 A 方向下唯一必须动代码的点。事实链已闭合，出裁决。

### 可从这 236 字符采纳的两条（DSH 已独立核实 ② 的行号）

1. **`app_build` 缺口已被修复**（`package.ps1` 现写 `app_build`，见 `VERSION-JSON-GUARD-ALIGN-1`，实测 `GUARD_EXIT=0`）——
   ZCode 认为 reviewer-pvd 的 F-PVD-02 结论已过时，**不再是依赖**。
2. **`packaging/nsis/installer.nsi` 有 4 处硬编码 base/GPL 文案**（`:60`/`:72`/`:73`/`:103`）：
   即使把 models 内容打进 stage，安装器界面的许可文案仍是错的 ⇒ **方向 A 下必须改这 4 处**（不只是改 `NOTICE.md`）。

### 未完成

**方向 A/B 的选择仍未取得**。`LICENSE-VARIANT-DECLARATION-1` 保持 `blocked`。
下次调用应改用不带 `--json` 的输出或更短的提示词，避免正文被截断。

