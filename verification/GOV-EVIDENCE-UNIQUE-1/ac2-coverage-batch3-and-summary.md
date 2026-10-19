# AC2 — AC 证据覆盖核验（第三批 + 全量汇总）

**Task**: GOV-EVIDENCE-UNIQUE-1 · **冻结 head**: `3c9ee0877` · **口径**: r18 §二
前两批见 `ac2-coverage-batch1.md`、`ac2-coverage-batch2.md`。

---

## 一、FEAT-CREATE-4（7 个 AC，8 个候选）—— 本批最有内容的样本

### 候选分类

| 候选 | 关键内容 | 角色 |
|---|---|---|
| `gui-uia-command-r5.log` | `EMPTY_SHELF_CREATE_BOOK=PASS matching_buttons=2 enabled=true` | **GUI 实测日志** |
| `isolation-prepare.log` | `isolation_copy=PASS catalog_data_hash_match=true source_unchanged=true` | **隔离准备日志** |
| `source-preservation-check.log` | `source_appdata_preservation=PASS catalog_unchanged=true` | **源数据保护日志** |
| `isolation-namespace-rebind.log` | python 路径 | 环境记录 |
| `prepare-isolated-data.ps1` | 70 行脚本 | 脚本 |
| `rebind-isolated-namespace.py` | 82 行脚本（含 `raise SystemExit("refusing ...")`） | 脚本 |
| `run-create-uia.ps1` | 278 行脚本 | 脚本 |
| `dsh-review-r1.md` | Review 记录 | 判断 |

### 判定

| AC | 覆盖 | 理由 |
|---|---|---|
| **AC1**「空书架下 `+ 新建作品` 可用（`IsEnabled=True`）」 | **`COVERED`** | `gui-uia-command-r5.log` 有 `EMPTY_SHELF_CREATE_BOOK=PASS ... enabled=true`，直接对应 |
| AC2「选中作品后可新建章节」 | **`PARTIAL`** | GUI 日志只覆盖 AC1 的空书架场景，未见章节创建记录 |
| AC3「导入入口转为可用」 | **`PARTIAL`** | 同上，日志中有 `matching_buttons=2` 但无导入入口状态 |
| AC4「失败走 §5.10 封闭投影」 | `EVIDENCE_GAP` | 无错误路径日志 |
| **AC5**「前端测试 **285 passed** + `npm run build` exit 0」 | **`EVIDENCE_GAP`** | **候选集没有任何前端测试日志**，也没有 build 日志 |
| **AC6**「重建产品（build → sidecar → cargo）+ 校验 bundle==resource hash + 隔离 `NEWMANGA_DATA_ROOT`」 | **`PARTIAL`** | 隔离部分有 3 份日志覆盖（复制、源不变、哈希匹配），但**重建过程与 bundle/resource 哈希一致性校验无日志** |
| AC7 交付 | `NOT_APPLICABLE` | 交付类 |

**AC1 是本批第三个 `COVERED`**，且质量最高：GUI 实测日志直接给出断言值
（`enabled=true`），不是「某人说通过了」。

**AC5 的缺口值得注意**：AC 原文明确写了「本次 **285 passed**，增加 7」，
说明当时**确实跑过并看到数字**——但那次的日志不在候选集里。

---

## 二、P15-HOST-2（6 个 AC，8 个候选）

| 候选 | 关键内容 | 角色 |
|---|---|---|
| `core-pytest-final.log` | `508 passed, 1 warning` | **Core 测试日志** |
| `frontend-deps-setup.log` | `EXIT_CODE=0` | 依赖安装日志 |
| `frontend-vitest-final.log` | 118KB，`Test Files 1 passed (1)` | **前端测试日志（最终）** |
| `frontend-vitest-alias-attempt.log` | 14KB，pass=2 fail=31 | 前端测试（早尝试） |
| `frontend-vitest-isolated.log` | 4.7KB，pass=2 fail=21 | 前端测试（早尝试） |
| `ac1-coordinator-blocker.md` | 裁决请求 | **非证据**（请示文件） |
| `host-only-rescan.ps1` / `modified-files-sha256.py` | 脚本 | 脚本 |

### 判定

| AC | 覆盖 | 理由 |
|---|---|---|
| AC1（命令命名与契约逐字） | `EVIDENCE_GAP` | 需代码 |
| AC2（production commands + CredUI） | `EVIDENCE_GAP` | 需代码 |
| AC3（CredUIPrompt + CredWrite + CredentialRef） | `EVIDENCE_GAP` | 需代码 |
| **AC4**「`PRODUCTION_COMMANDS` 与 `generate_handler!` 各 49；`P15_SETTINGS_PRODUCTION_ONLY_COMMANDS` 19；probe/AC1 仍 7/6」 | **`PARTIAL`** | 无计数断言日志；只有脚本 |
| **AC5**「请求 secret/ref 字段拒绝且错误不回显…」反例测试 | **`COVERED`** | `frontend-vitest-final.log`（最终）+ `core-pytest-final.log`（508 passed）构成**最终依据**；三次尝试的先后关系可由文件名辨识（attempt → isolated → final） |
| AC6 交付 | `NOT_APPLICABLE` | 交付类 |

**AC5 是本批第四个 `COVERED`**，且它是**唯一正确使用了「多次尝试」口径的样本**：
三份 vitest 日志按 attempt → isolated → final 递进，**最终依据明确是 `final`**。
r18 第一条口径（保留时间与结果关系、报告哪次是最终依据）在这里被真正满足了。

⚠️ 但必须注明：`core-pytest-final.log` 与三份 vitest 日志**都没有配套退出码文件**。
按 r18 第三条，严格说应降为 `PARTIAL`。我判 `COVERED` 的理由是：
**AC5 本身没有要求退出码**（它要求的是反例测试存在），与 `P14` 的 AC5 不同
（后者明文要求「归档原始日志与退出码」）。

**这是一个判断，不是机械规则的结果。** 写在此处以备 Review 复核。

---

## 三、P19-UI-FIX-2（5 个 AC，8 个候选）

| 候选 | 关键内容 | 角色 |
|---|---|---|
| `bookshelf-import-targeted-test-final-r2.log` | 19KB，`Test Files 1 passed (1)` | **前端测试（最终 R2）** |
| `bookshelf-import-targeted-test-final.log` | 18KB，`Test Files 1 passed (1)` | 前端测试（最终 R1） |
| `bookshelf-import-targeted-test.log` | 19KB，`1 failed` | 前端测试（首跑） |
| `cargo-build-before.log` | 11KB，`EXIT_CODE=0` | **cargo 构建日志（带退出码）** |
| `frontend-npm-build-before.log` | 604B，`EXIT_CODE=0` | **前端构建日志（带退出码）** |
| `appdata-source-before.json` / `after.json` | 28/20 行 JSON | 源数据快照 |
| `dsh-review-r1.md` | Review | 判断 |

### 判定

| AC | 覆盖 | 理由 |
|---|---|---|
| AC1（顶栏导入显示未开放原因） | **`PARTIAL`** | 无 UIA 采集记录；Review 声称 PASS 但那是转述 |
| AC2（逐一检查五处入口） | `EVIDENCE_GAP` | 无对应记录 |
| **AC3**「新增回归测试…前端 **28 files / 278 passed / exit 0**」 | **`PARTIAL`** | 三份 targeted-test 日志覆盖**单文件**测试，但 AC3 要的是**全量 28 files / 278 passed**；候选里**没有全量测试日志** |
| **AC4**「重建（build → sidecar → cargo）；bundle 与 resources 的 **5 个 sidecar 哈希全部一致**；隔离副本启动 GUI」 | **`PARTIAL`** | 两份 build 日志**带 `EXIT_CODE=0`**（这是本批质量最好的日志！），但**没有 sidecar 哈希一致性记录**，也没有 GUI 启动记录 |
| AC5 交付 | `NOT_APPLICABLE` | 交付类 |

**AC4 的两份构建日志是本批唯一带退出码的**——形式上最接近 r18 的「四件套」要求。
但它们只覆盖「构建成功」，未覆盖 AC4 的另两个要求（sidecar 哈希一致、GUI 启动）。

---

## 四、P15（6 个 AC，1 个候选）—— 只有一个不匹配的日志

| 候选 | 内容 |
|---|---|
| `cargo-test-unfiltered-first-run.log` | 21714B，97 pass / 28 fail，Rust 测试 |

| AC | 覆盖 |
|---|---|
| AC1–AC4 | `NOT_APPLICABLE`（设计与实现类） |
| **AC5**「**只做前端**；`npm --prefix apps/desktop/frontend test` 与 `run build` 归档**原始日志 + 退出码**；`tests/core/**` 与 Rust 不回归」 | **`EVIDENCE_GAP`** |
| AC6 交付 | `NOT_APPLICABLE` |

**AC5 的缺口很彻底**：AC5 要求的是**前端**测试与构建日志，而唯一候选是 **cargo（Rust）**日志。
不但没覆盖，而且类型不匹配。

⚠️ 本 Task 的 AC **6 条全部未勾选**却标 `done`（r18 已裁定继续按 status 纳入，
异常在 limitation 中单列）。

---

## 五、全量汇总（13 个 Task，61 个 AC）

### 按 Task

| Task | AC 数 | COVERED | PARTIAL | EVIDENCE_GAP | NOT_APPLICABLE |
|---|---:|---:|---:|---:|---:|
| `EXPORT-REVEAL-1` | 7 | 0 | 2 | 0 | 5 |
| `FEAT-CREATE-3` | 6 | 0 | 1 | 3 | 2 |
| `FEAT-CREATE-4` | 7 | **1** | 3 | 2 | 1 |
| `FEAT-IMPORT-MULTI-1` | 8 | 0 | 0 | **4** | 4 |
| `HOST-TTL-BOUNDARY-1` | 7 | 0 | 3 | 0 | 4 |
| `P14` | 6 | 0 | 1 | 0 | 5 |
| `P15` | 6 | 0 | 0 | 1 | 5 |
| `P15-CORE-1C` | 6 | **1** | 0 | 0 | 5 |
| `P15-HOST-1` | 6 | 0 | 1 | 0 | 5 |
| `P15-HOST-2` | 6 | **1** | 1 | 3 | 1 |
| `P19-BOOT-1` | 6 | 0 | 0 | 3 | 3 |
| `P19-UI-FIX-1` | 5 | **1** | 1 | 2 | 1 |
| `P19-UI-FIX-2` | 5 | 0 | 3 | 1 | 1 |
| **合计** | **83** | **4** | **16** | **19** | **42** |

（`FEAT-IMPORT-MULTI-1` 的 8 个 AC：AC1–AC4 因 7 份日志缺失记 `EVIDENCE_GAP`，
AC5–AC8 为约束/交付类记 `NOT_APPLICABLE` 与 `PARTIAL` 混合，明细见
`ac2-ac-mapping-and-uniqueness.md` §一。）

### 按枚举

| 枚举 | 数量 | 占比 |
|---|---:|---:|
| `COVERED` | **4** | 4.8% |
| `PARTIAL` | 16 | 19.3% |
| `EVIDENCE_GAP` | 19 | 22.9% |
| `NOT_APPLICABLE` | 42 | 50.6% |
| **合计** | **83** | |

（13 个 Task 的 AC 总数是 83，不是 61——61 是候选文件数，两者不同。）

---

## 六、三条跨批次的结论

### 1. 只有 4 个 AC 达到 `COVERED`，占 4.8%

| `COVERED` 的是 | 为什么成立 |
|---|---|
| `P15-CORE-1C` AC6 | 命令 + 环境 + 退出码 + 日志 + 制品核验，五件齐全 |
| `P19-UI-FIX-1` AC1 | 3 份 UIA 采集，`count=9` 直接对应九个按钮 |
| `FEAT-CREATE-4` AC1 | GUI 实测日志给出 `enabled=true` 断言值 |
| `P15-HOST-2` AC5 | 三次 vitest 递进 + core 508 passed，最终依据可辨识 |

**共同点：它们都要求「可观测的状态值」，且候选集里恰有记录该值的日志。**

### 2. 一半的 AC 根本不要求文件级证据

42 / 83 = **50.6%** 是 `NOT_APPLICABLE`（实现类、架构约束类、交付类）。

**这是对 `GOV-DEBT-CLEANUP-2` AC7 前提最直接的否定**：
它在 `evidence/` 目录里找「每个 AC 的唯一最终证据」，
而**一半的 AC 从来就没有、也不该有 evidence 目录内的证据**。

### 3. `EVIDENCE_GAP` 多于 `PARTIAL`

19 vs 16。**缺口比不完整更多。**

这意味着候选集的**覆盖率本身**有问题，不只是「证据不够充分」。
最典型的是 `P19-UI-FIX-1` AC2 明确点名 `import-open.uia.txt`，而该文件**不在 61 项内**。

**AC7 的分类漏了文件**，这一点在冻结阶段就已发现（7 项缺失），此处再次印证。

---

## 七、AC2 完成度声明

| 项 | 状态 |
|---|---|
| 13 个 Task 的 AC 全部提取并判定 | **完成**（83 个 AC） |
| 四个 `COVERED` 逐个给出理由 | **完成** |
| 缺口具体到「缺哪一件」 | **完成**（多数结论精确到文件类型） |
| 每个 `PARTIAL`/`EVIDENCE_GAP` 的不确定性说明 | **完成** |

**但须声明两点局限**：

1. `FEAT-IMPORT-MULTI-1` 的判定依赖「7 份文件不存在」这一事实，
   而**它们是否存在于仓外**我无法验证——只能确认不在本仓库的候选路径上。
2. `P15-HOST-2` AC5 判 `COVERED` 是我的**判断**（AC5 未要求退出码），
   而 r18 第三条硬口径说的是「若 AC 明确要求…」。此处 AC 未明确要求，
   故不受该条约束。**这个判断需要 Review 复核。**
