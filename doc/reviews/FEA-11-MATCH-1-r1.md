---
task_id: FEA-11-MATCH-1
reviewer: DSH 独立上下文子 agent（fea12-dsim-impl 之外的 fresh subagent；未参与本卡任何实现/夹具修复/证据生成）
session: subagent（parent session = session-8db9dae5-49df-4d09-ac62-696f0805a95c）
reviewer_kind: subagent
author: fea12-dsim-impl（DSH Agent Teams 成员；Lead `lead`）
base_commit: 2d9a4a219
reviewed_head: c12023ab6
decision: approved
---

# Review r1：FEA-11-MATCH-1（页匹配 pixel profile 提取与旧库 fixture）

## 0. 范围与执行口径

- **被审 head**：`c12023ab6`（卡/Handoff/证据；实现 `7bd8efe47`、测试 `2d61e43c3`、C8 收紧 `b4ad109da`；base `2d9a4a219`）。审查开始时 `HEAD=c12023ab6`、`git status --porcelain` 为空；审查中 main 前进到 `e0c370870`（**他卡** `docs(fea-11-host-auth-1)`，`git diff --name-only c12023ab6..HEAD -- src tests` 为空，`c12023ab6..HEAD` 仅 `doc/tasks/FEA-11-HOST-AUTH-1.md`），对本次结论无影响。
- **方式**：全程只读仓库；未 commit / stash / push / 改受跟踪文件；所有复跑、变异、探针与日志写在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-match-1\`。审查结束 `git status --porcelain` 仍为空（`HEAD=e0c370870`）。
- **依据**：`doc/tasks/FEA-11-MATCH-1.md`（AC-M1…M6、C1–C12、L-M1…L-M7）、`doc/handoffs/FEA-11-MATCH-1-handoff.md`、`verification/FEA-11-MATCH-1/**`、`doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md` §A、`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §5/§5.2/§5.3/§7.3、`doc/tasks/FEA-11.md`（AC11-3、r7 L-4、R-012）、`src/application/sources/{scanner,matcher}.py`、`tests/fea11/{test_source_match,test_source_scan,test_source_sync,test_source_relink,test_source_sync_storage}.py`、`tests/fea11/conftest.py`、`src/infrastructure/sqlite/schema.py`、`src/application/importing/referenced/{reader,scanner}.py`、`src/application/sources/{model,service}.py`。
- **视角**：Architecture（契约/分层/持久化/安全读路径）与 Verification（逐项实跑）均 `executed`；Standards/Spec 作为可选视角一并覆盖（见 §6、§7）。

## 1. 结论

**approved。P0 = 0，P1 = 0，P2 = 3，P3 = 7。**

本卡是**真实交付**而非空转：生产 scan 在变更容器路径上确实产出完整、可跨版本比较的 `pixel-digest/1` profile（EXIF 转置后 W/H、`orientation=1`、8-bit RGB、`sha256("WxH"\\0+RGB)`），修复了 v7 的双重编码缺陷；matcher 的可比性补到 7 维、重复 pixel occurrence 并入出现次数三元组、counterpart-less 成员修正为 `missing`/`added`、旧证据缺失/不可比诚实降级；并用**生产迁移 `migrations[:7]` + 真实 FEA-09 导入 + 迁 v8** 的真实 v7 旧库 fixture 做了独立 match 测试。门禁全部独立复现（fea11 107、本卡 19、全量 3202/10、pins 18/18、check.ps1 PASS 3 warnings、契约/schema/依赖/apps 零 diff）。

三条 P2 均**非阻断**：R1-01 是 AC-M4「profile 不可比 ⇒ `ambiguous`」在「同像素 counterpart 已改名」这一未覆盖边界上的行为缺口（安全性未破：不伪造 `changed`/`unique_pixel`，两行都仍需用户确认）；R1-02 是一条**测试不判别**（实现正确，变异 M6 存活）；R1-03 是证据日志 `recorded_at` 不可能为真（元数据，非内容）。无 P0/P1，故可批准；建议 closeout 前处置 R1-01/R1-02/R1-03 或登记为 limitation。

## 2. AC 判定（逐项独立核验）

| AC | 判定 | 核验要点与证据 |
|---|---|---|
| **AC-M1** profile 提取/持久化/降级 | **MET** | ①字段集合：`PixelProfile` 恰为 C-17 §5.2 的 8 个字段，我用 `validate_pixel_profile`/`validate_entry_evidence` 实测接受（`probe_dto.py`），且 `reason="budget"` 被闭集拒绝（不得新增枚举）；`decoder="referenced-import"`/`decoder_version="1"` 合法（`_ID_RE=^[^\x00-\x1f\x7f\\/]{1,128}$`），C9 裁决真属「卡级常量更正、契约字节未动」——`git diff 2d9a4a219..c12023ab6 -- doc/contracts doc/plan` 为空。②EXIF：`_exif_orientation` 先校验 1..8（bool/非 int/0/9 → `unsupported`），再 `ImageOps.exif_transpose`——与 `reader.py:174` 的 `render_entry_png` 同源约定（已读源码确认）；测试用显式 `FLIP_LEFT_RIGHT/ROTATE_180/FLIP_TOP_BOTTOM/TRANSPOSE/ROTATE_270/TRANSVERSE/ROTATE_90` 独立复算（不经 `exif_transpose`），4×3 非对称图，覆盖 1–8 + 9 + broken，且 5/6/7/8 断言 W/H 互换、2/4/5/7 断言与未镜像基线不同 → 镜像确实镜像。③W/H=转置后、`orientation` 恒 1。④digest：`sha256(ASCII("WxH")+b"\x00"+RGB)`，我独立算出的固定 golden `53b800d9…6c71` 与测试常量**逐字节一致**（`probe-golden`）。⑤params canonical：`json.dumps(PIXEL_PARAMS, sort_keys, separators, ensure_ascii=False, allow_nan=False)` 与 C8 冻结对象逐键一致；`_params_digest` 对存储字符串先 `json.loads` 再按**对象**哈希（修复 `scanner.py:545-555` 双重编码），非对象/非法 JSON → `None` → `reason="incomparable"`（绝不伪装 `{}`）；测试同时断言 digest ≠ 字符串字面量哈希。⑥Pillow `12.3.0` 硬编码常量 + `requirements.txt:12` pin 12.3.0（已核对）；⑦strict read：`read_entry_bytes` → `read_verified_bytes`（zip 场景校验容器 digest/budget，加密成员 → `SOURCE_PASSWORD_REQUIRED`），无 `open()` 源路径、无顺手缓存；grant/lease/identity/integrity 错误在 `_reason_for_import_error` 返回 `None` 时**原样上抛**（C11），测试枚举 4 个此类 code。⑧逐 entry reason：加密→`encrypted`、格式/损坏/非法 EXIF/预算→`unsupported`、无 `content_digest`→`missing_evidence`；端到端已实测 broken/alpha/超预算/无 digest（加密仅映射函数单测，见 R1-09）。⑨PDF 不产 profile（`source_kind=="pdf"` 在读字节前返回，L-M1），不宣称覆盖。⑩持久化：apply 后行含非空 `pixel_digest/algorithm/width/height/orientation/decoder_name/decoder_version/decoder_params_json`，且与 live candidate 的 canonical params 一致（测试 + `insert_source_entry_rows` 全列写入已核）。⑪totals==明细：`totals` 由**过滤后** `diff` 重算（`scanner.py:315-318`），未绑定旧项过滤已由 `test_scan_extracts_…`（旧 zip 带 unbound `pad.txt`）覆盖。 |
| **AC-M2** 7 维可比性 | **MET** | `_profiles_comparable` = `pixel_digest_algorithm + decoder_name + decoder_version + canonical params(object) + width + height + orientation` 全等；params 先解析成对象再 canonical 比较（键序/空白等价，测试用重排 JSON 证明），非对象一律不可比。`unique_pixel` 需「该像素两侧各恰 1 次」且 `len(candidates)==1 and len(comparable)==1`（比 base 的 `len(unique)==1` 更严，修掉「2 个同像素、1 个可比即配对」的旧隐患）。判别力：match 级用「同 pixel_digest、同 W/H、`orientation=6`」与「同 pixel、params `frame:1`」两例断言 `ambiguous/incomparable`（我实测 base 的 `_profiles_comparable` 缺 W/H/orientation 且比较原始字符串 ⇒ 改前确实会判 `unique_pixel`，卡面「改前 unique_pixel」陈述**属实**）。`same_content` 两分支（geometry 相等 / 唯一字节 `old_geometry=(None,None)` 兜底）均断言 relation 值。`changed` 仅双侧完整可比且像素不同 |
| **AC-M3** 重复 pixel occurrence | **MET** | occurrence 统计按侧独立纳入 `pixel_digest`（`old/new_pixel_counts`），`_is_duplicate_member` 三元组 = content_digest ∨ locator ∨ pixel；任一侧 ≥2 即整组 `ambiguous/duplicate_group`；1:2 → ambiguous+added、2:1 → ambiguous+missing、重名 → ambiguous+missing 均有断言；每个 occurrence 都产出 item；`scan→plan→preview→confirm→apply` 全链：全部 `defer`、binding 数不变、旧 binding 仍 `healthy`（此装置非 `needs_confirmation`，见 R1-12 备注）、PageId/人工零变化；「不得自动 keep/bind」由**未改动的**冻结校验器强制（`model.py:888` ambiguous 禁 keep/add；`:892` 仅 ambiguous 可 defer；`:894` missing 仅 tombstone/defer）——即使用户写 keep 也会 `INVALID_REQUEST`，非仅测试默认值。唯一字节分支的重复守卫**存在且可达**（我用 v7 无 profile 旧行 + 新侧像素重复探针实测 `ambiguous/duplicate_group`，见 §4 探针 2）；但卡面点名的判别性测试实际不判别（R1-02） |
| **AC-M4** 旧证据降级 + counterpart-less | **MET（附 R1-01 边界）** | 卡面列举的判别项全部成立：v7 W/H-only（pixel NULL）→ `ambiguous/missing_old`（我核对了 base：`_old_evidence_complete` 为真时旧代码落到 `else` → `changed/direct`，故「改前 changed/direct、改后 missing_old」**属实**）；新侧无 profile → `incomparable`；不可比 → `incomparable`；字节同一成员仍 `unique_pixel`（防回归，已断言）；counterpart-less 旧成员 → `missing/none`、新成员 → `added/none`（base 在此处会产出 `ambiguous` + 单侧 `None` 的非法 `DiffItem`，修正确实必要）；`totals` 语义变化已在卡「预期行为变更 #2/#5」登记；不从新图伪造旧证据（scan 只读、旧行只用旧列、不写旧版本）。**边界缺口**：当旧 profile 存在但不可比、且同像素 counterpart 位于**不同 locator**（改名/重排）时，输出是 `missing/none` + `added/none` 而非 `ambiguous/incomparable`（R1-01，可复现），与 C-17 §7.3 行 4「profile 不可比 → 待确认/不可验证」不一致 |
| **AC-M5** 真实 v7 fixture + 独立 match 测试 | **MET** | 真实 fixture 由生产路径生成：`MigrationRunner(conn, default_migrations()[:7])` → 真实 `ReferencedImportPlanner.plan` + `ReferencedImportRuntime.start`（真实 zip、真实 receipt 轮询至 `completed`）→ `MigrationRunner(conn, migrations).apply_pending()` 迁 v8；旧行形态断言**诚实**（全部 `pixel_digest/algorithm/orientation IS NULL`；bound entry 有 W/H 且 `decoder_name` 非空；未绑定成员 W/H 均 NULL）——未断言「所有 decoder_name 为空」，与卡面要求一致；gen2：`unchanged=1/ambiguous=1/missing=0`，`missing_old` 与 `unique_pixel` 同时出现；用户显式 bind 后新代次行带 `pixel_digest` 与 canonical params；gen3 两页 `unique_pixel`（**两代 resync 可达**，且第二代起不再依赖夹具）。纯 matcher 单测（无 DB/无文件）+ scan 集成（真实 zip + 真实签名 grant + 真实严格读）+ scan 前后快照相等 + lost-scan 零提交 + apply 保留 canonical params，五类齐全；`test_source_match.py` 19 用例我逐条核对名称与内容，非空转。 |
| **AC-M6** 契约/门禁零漂移 | **MET** | 我独立复跑：`tests/fea11` **107 passed**；`test_source_match.py` **19 passed**；全量 **3202 passed / 10 skipped**（与基线 3183/10 差 +19、skip 不变）；`verify_pins.ps1` **PIN AUDIT: PASS (all 18)**；`check.ps1 -TaskPath` **PASS (3 warnings)**；`git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps` **空**；`… -- schema.py migrator.py requirements.txt pyproject.toml` **空**（注意 `pyproject.toml` 在仓库中**不存在**，该条为空条件，见 R1-10）；`src`/`tests` 仅 6 个文件变化，`conftest.py`/`model.py`/`service.py`/`ports.py`/`core_assembly.py`/`referenced/**` 零 diff；`.NET` **NOT_RUN** 且理由成立（`apps/**` 零 diff、无 C# 变更），未写 PASS。 |

## 3. 独立复跑（本 Review 实跑，全部 EXIT 0）

| 场景 | 命令 | 结果 | 日志（仓外） |
|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | **107 passed**, 8 warnings, 2.92s | `pytest-fea11.log` |
| 本卡测试 | 同上 `tests/fea11/test_source_match.py` | **19 passed**, 0.43s | `pytest-match.log` |
| 全量 | `… -m pytest tests -q -p no:warnings --tb=no` | **3202 passed, 10 skipped**, 239.81s | `full-pytest.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)** | 终端输出 |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md` | **PASS (3 warnings)** | 终端输出 |
| 零漂移 | `git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps` / `-- schema.py migrator.py requirements.txt pyproject.toml` | **空 / 空** | 终端输出 |
| 变更域 | `git diff --name-only 2d9a4a219..HEAD -- src tests` | 6 文件（2 src + 4 tests） | 终端输出 |
| 工作树/推送 | `git status --porcelain`；`git rev-list --count origin/main..HEAD`=934；`HEAD..origin/main`=0；HEAD 非 origin/main 祖先 | **clean；未 push** | 终端输出 |
| `.NET` | NOT_RUN | `apps/**` 零 diff，合法 | — |
| 全量后副作用 | `git status --porcelain` | 空（R8 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 未被改写） | 终端输出 |

## 4. 变异/反证（仓外 `mut/`：复制 `src`+`tests`，单点精确替换，仓库零改动）

| # | 变异 | 预期被杀 | 实测 | 结论 |
|---|---|---|---|---|
| M1 | `_profiles_comparable` 去掉 orientation 维度 | 7 维单测 + match 级 orientation 判别 | `test_profiles_comparable_requires_all_seven_dimensions`、`test_changed_requires_complete_comparable_pixel_evidence` **FAILED** | **RED ✓** |
| M2 | 重复成员判定去掉 `pixel_digest` | 1:2/2:1、counterpart-less、重复组全链 | 上述 3 条 **FAILED** | **RED ✓** |
| M3 | `_params_digest` 把非对象伪装成 `{}`（C8 原 bug） | 非对象 params 用例 | `test_unparseable_params_are_incomparable_never_disguised_as_empty` **FAILED** | **RED ✓** |
| M4 | 去掉 `changed` 前的 `_profiles_comparable` 守卫 | changed 前置条件 | `test_changed_requires_complete_comparable_pixel_evidence` **FAILED** | **RED ✓** |
| M5 | 可比性比较**原始 JSON 字符串**（双重编码回归） | 键序/空白等价 | `test_profiles_comparable_requires_all_seven_dimensions` **FAILED** | **RED ✓** |
| **M6** | 让唯一字节分支**无条件**输出 `unchanged/unique_pixel`（绕过重复像素守卫） | 应杀 `test_byte_identity_does_not_bypass_a_duplicate_pixel_group` | **19 passed（全绿）** | **未杀 ✗ → R1-02** |

> M6 说明：该用例的构造（old 有 pixel + new 两个同像素 + 其一字节同一）已被**前置 duplicate pass** 完全吸收，字节分支根本不执行，故不是对该性质的有效判别。`mutation-report.log` 中 `test_source_command_parity.py` 的 2 条失败是**仓外副本**的路径产物（仓库内 107 passed 已证），不计入信号。

**探针 1（R1-01 可复现）**：`probe_incomparable.py`（纯 matcher，无 DB）

| 场景 | 实测 |
|---|---|
| 同 locator、仅 orientation 不同 | `ambiguous/incomparable` ✓ |
| **改名**（不同 locator）+ 仅 orientation 不同 | `missing/none` + `added/none` ✗（应为 `ambiguous/incomparable`） |
| **改名** + 仅 decoder params 不同（Pillow 升级语义） | `missing/none` + `added/none` ✗ |
| 改名 + 新侧无 profile | `missing/none` + `added/none`（无像素证据可关联，**这是正确的**，不算缺口） |
| 改名 + 旧侧 v7 无 profile | `missing/none` + `added/none`（同上，正确） |
| 改名 + 完全可比 | `unchanged/unique_pixel` ✓（可比时像素身份是跨 locator 的对应键） |

**探针 2（R1-02 与守卫可达性）**：`probe_byte_branch.py`

- 形态：旧行 v7（无 profile、字节 `BYTES`）+ 新侧 N1（字节 `BYTES`、像素 `Q`）+ N2（像素 `Q`，字节不同）。
- reviewed_head：`old1 -> new1 : ambiguous/duplicate_group`，`- -> new2 : added/none` → 守卫**可达且正确**。
- 施加 M6 后：`old1 -> new1 : unchanged/unique_pixel` → 守卫被绕过，而 19 用例仍全绿。

## 5. 证据/范围/纪律核对

- **sha256 pin 复算**：卡面 Canonical Evidence 10 行（EV-M1…M9 CANONICAL + EV-M10 SOURCE_PIN）**逐项复算全部 MATCH（0 mismatch）**，含 `EV.md`/`AC-MATRIX.md`/6 份日志/`changed-files.txt`/`gates.log`。
- **日志内容一致性**：`fea11 107`、`match 19`、`full 3202/10`、`baseline 3183/10`、`pins 18/18`、两份 zero-drift 空 diff 与我的独立复跑**逐项一致**；`static-diff.log` 的 `HEAD=b4ad109dabb9…`、`git status`（当时 `M` 卡 + `??` Handoff/证据）与其所在提交 `c12023ab6` 的实际情况吻合。
- **`gates.log` 诚实性**：日志**同时保留了**一次 `check.ps1` FAIL（7 个 evidence sha256 不匹配）与随后的 PASS，未隐藏中间失败；最终状态我复跑为 PASS (3 warnings)。但该「最终复跑」实为登记 EV-M10 **之前**的输出（4 warnings，含 `gates.log 未登记` warning），登记后实际为 3 warnings（R1-06）。
- **`recorded_at` 不可为真（R1-03）**：`pytest-{fea11,match,full}.log`/`verify-pins.log` 均写 `01:52`、`static-diff.log` `01:54`、`gates.log` `01:56`；而 `c12023ab6` 提交时间 `01:19:06`、文件 mtime `01:16:08–01:18:31`、本 Review 采样时刻 `01:31`。三处互斥 ⇒ 该字段非机器时间。
- **范围/纪律**：卡内 4 个提交文件全部落在 `allowed_paths`：`7bd8efe47`（`scanner.py`/`matcher.py`）、`2d61e43c3`（`test_source_match.py` 新增 + W1 `test_source_scan.py` + W1b `test_source_sync.py`/`test_source_relink.py`）、`b4ad109da`（2 src + 1 test）、`c12023ab6`（卡/Handoff/`verification/**`）。W1b **只增不删**（`git diff -U0` 检查：`test_source_sync.py`/`test_source_relink.py`/`test_source_sync_storage.py` **0 行删除**；仅 `test_source_scan.py` 删 3 行 = W1 批准的 docstring 2 行 + `changed==1` 断言）；`test_source_sync_storage.py` 经共享 `_seed_two_page_source` 自动恢复（其 `:125` 确以 `legacy_v7_evidence=False` 调用）。`a85874186`（`docs(fea-11-match-1): 指针转 in_review`，仅 STATUS/PLAN/LEDGER）与 `eb1e48a62` 同一模式，属 **Lead 指针提交**（前次 `FEA-11-AC4-GAPS-1` r1 已按此口径排除），不计入本卡 allowed_paths 结论；但请 Lead 在 closeout 记录中明示该归属（否则读者会把它当成 Owner 越界）。未 push（`origin/main` 落后 934 个提交、HEAD 非其祖先）；工作树审查前后均 clean。
- **W1b 是否「补真实 pixel profile、断言未放宽」**：**属实**。`_seed_complete_pixel_profiles` 用真实 PNG 字节按冻结参数算 digest/W/H（`ImageOps.exif_transpose` + RGB + `WxH\0` 公式），`UPDATE source_entries` 写全套列；4 个受影响测试文件的断言零删除。
- **C9 裁决记录准确性**：卡 C9、Handoff §3、EV §4 三处均写明「原 `referenced-import/1` 含 `/` 违反 C-17 §5.2 `decoder! ID` / §5 类型表，改为名字+版本两个合法 ID，属卡级常量更正、契约字节未动」；我实测 `_ID_RE` 拒绝 `referenced-import/1`、`valid_id` 接受两个新值，契约目录零 diff ⇒ 记录**准确**。
- **L-M1…L-M7 如实性**：L-M1（PDF 在读字节前返回、无 raster seam）✓；L-M2（`referenced/runtime.py` 零 diff，真实 v7 fixture 实测导入后 `pixel IS NULL`）✓；L-M3（`service.py::_entries_from_target` 确实丢 `decoder_params_json`（写 `"{}"`）与 `size_bytes`（写 0），且本卡新增的 lost-scan 测试实证该路径**不可达即 typed 失败 + 零写**）✓；L-M4/L-M5 未实现 ✓；L-M6（每 entry 重读整容器，O(n×size)，未优化）✓；L-M7 ✓。
- **AC11-3 口径**：本卡**能够**支撑「旧库 fixture/独立 match 测试」（r7 L-4 / R-012 的指定缺口）以及 AC11-3 的「两条路径 / 7 维可比性+一对一唯一 / 重复组待确认 / 旧证据降级且不伪造」四项；但 AC11-3 的字面还含 **PDF 插页**（本卡 OUT，L-M1）与「**不能**按冻结参数重算时才降级」（本卡 L-M4 未实现重算）。因此回填必须带 limitation（见 §8），否则是过度宣称。

## 6. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **R1-01** | **P2** | `src/application/sources/matcher.py:313-346`（唯一像素 pass） | 旧 profile 存在但**不可比**且同像素 counterpart 在**不同 locator**（改名/重排；现实触发=容器重打包改名，叠加 Pillow/decoder/params 变更使旧 profile 全部不可比）时，输出 `missing/none` + `added/none`，而非 AC-M4 首句与 C-17 §7.3 行 4 要求的 `ambiguous/incomparable`（待确认/不可验证）。安全性未破（不伪造 `changed`/`unique_pixel`），但用户在此场景**只能 tombstone/defer + add**，无法 `bind` 保留 PageId（`missing` 的决策闭集是 tombstone/defer，见 `model.py:894`）。 | 仓外 `probe-incomparable.log` 探针 1/2 | 最小返修（约 12 行）：在唯一像素 pass 后，对「`len(candidates)==1` 且 `len(comparable)==0` 且未配对」的旧行产出 `ambiguous/incomparable`（重复组已在更早 pass 吸收，故该条件可安全收窄）；或登记 **L-M8** 并同步卡/Handoff/EV。判别性测试：`_row("old1","001.png")` vs `_row("new1","002.png", orientation=6)` → 断言 `("ambiguous","incomparable")`，再加 params 变体。 | open |
| **R1-02** | **P2** | `tests/fea11/test_source_match.py:388-402` | `test_byte_identity_does_not_bypass_a_duplicate_pixel_group` 名不副实：其 fixture（old 有 pixel + new 两个同像素）被**前置 duplicate pass** 吸收，字节分支不执行；**M6 变异（删除字节分支重复守卫）后 19 用例全绿** ⇒ AC-M3 明确点名的「唯一字节分支也不得绕过重复 pixel 组」**无判别性测试**（实现本身正确）。 | §3 变异 M6 + `probe-byte-branch.log` | 改 fixture 为可达形态：`old = [_row("old1","001.png", pixel=None)]`（v7 无 profile），`new = [N1(字节与 old 相同, pixel=Q), N2(pixel=Q, 字节不同)]` → 断言 `("ambiguous","duplicate_group")`；M6 即变红。 | open |
| **R1-03** | **P2** | `verification/FEA-11-MATCH-1/logs/*.log` 头部 `# recorded_at` | 6 份进程日志的 `recorded_at`（01:52/01:54/01:56）晚于其所在提交 `c12023ab6`（01:19:06）、与文件 mtime（01:16–01:18）及本 Review 时刻（01:31）互斥，且 4 份共用 `01:52` ⇒ 非机器时间。不影响日志正文（命令/EXIT/结果经我复跑全部一致），但** canonical evidence 里出现不可能为真的时间戳**削弱可追溯性。 | 终端 `Get-Date`/`Get-ChildItem LastWriteTime`/`git show --format=%aI %cI` | 重新生成（或删除该字段）后重算 3–6 个 sha256 并更新卡面 pin；`check.ps1` 会机械校验。若保留，至少在 EV 注明「recorded_at 为人工标注、非机器时间」。 | open |
| R1-04 | P3 | `src/application/sources/matcher.py:24-30` | `_old_evidence_complete` 已成**死代码**（matcher/测试均无引用），且其 docstring 仍主张「width/height presence is the observable proof the entry was ever decode-verified」——正是 W1b 判定为**夹具事实错误**的命题，会误导后续读者/实现。 | `Select-String _old_evidence_complete` 仅 1 处定义 | 删除该函数或改为「W/H 只是历史导入写过尺寸，不构成 decode 证据」。 | open |
| R1-05 | P3 | `tests/fea11/test_source_match.py:238-245`；`Handoff §1 AC-M5` | 卡面 AC-M1/AC-M5 写「scan 前后**全表**快照相等」，实际比较集是 **17/40** 表（schema 40 表；缺 `reading_progress`/`rendition_cache`/`pipeline_run_targets`/`step_result_candidates`/`step_runs`/`media_artifacts` 等）；Handoff 又写「**16 表**」。数字与口径均不严谨（17 表覆盖了 source-sync 栈会触达的表，结论风险低）。 | `probe_tables.py`：schema 40 / snapshot 17，差集已列 | 用 `sqlite_master` 枚举全表做快照（一行代码），或按 AC4-GAPS-1 先例**冻结并列出**比较集，并把 Handoff 的 16 改为 17。 | open |
| R1-06 | P3 | `verification/FEA-11-MATCH-1/logs/gates.log`（标「见下（本次交付最终复跑）」的那段） | 该「最终复跑」是登记 EV-M10（gates.log 作为 SOURCE_PIN）**之前**的输出，显示 `PASS (4 warnings)`（含「evidence_dir 含未登记过程文件 gates.log」）；登记后实际为 `PASS (3 warnings)`（我复跑）。卡面/提交信息写 3 warnings，与 log 内 4 不一致。 | 我的 `check.ps1 -TaskPath` 输出 | closeout 时重跑并替换该段（warning 数会随登记状态变化），或注明「该次运行发生于 EV-M10 登记前」。 | open |
| R1-07 | P3 | `tests/fea11/test_source_match.py:891-923` | lost-scan 用例只断言「异常带 `code`」（任意 typed）与零写，未断言**具体** `SOURCE_PLAN_STALE`、也未断言「无 source_operations receipt / 无新 publication」。AC-M5⑤要求「apply typed 失败且零内容/绑定/profile 提交」，当前零写比较集已覆盖，但 typed 口径偏松。 | 测试源码 | 断言 `code == "SOURCE_PLAN_STALE"` 且 `source_operations` 无新行。 | open |
| R1-08 | P3 | `src/application/sources/matcher.py:378-379` | `changed/direct` 分支依赖前置 pass 顺序隐式保证「像素必不同」，未显式断言 `old["pixel_digest"] != new["pixel_digest"]`。当前不可达（同像素会先被 unique-pixel/duplicate pass 吸收，我已穷举 pass 顺序），但未来重排 pass 即可能误报 `changed`。 | 代码审查 + 探针 | `elif old.get("pixel_digest") == new.get("pixel_digest"): ambiguous/duplicate_group` 或加 assert。 | open |
| R1-09 | P3 | `verification/FEA-11-MATCH-1/EV.md:26`、`Handoff §1 AC-M1` | EV/Handoff 把「逐 entry C10 降级（加密→`encrypted`、格式/损坏/非法 EXIF/预算→`unsupported`、无 digest→`missing_evidence`）」写成已实证；实际端到端只覆盖后三类 + broken/alpha，`encrypted` 仅 `_reason_for_import_error` 映射单测（zip 加密成员的扫描级可达性未证）。 | 测试/EV 对照 | 补一例真实加密 zip 成员（`zipfile` 不能写加密，可用固定字节夹具或标注不可构造），否则把措辞收窄为「映射层已测」。 | open |
| R1-10 | P3 | `EV.md:19`、`Handoff §2`、`static-diff.log` | 零漂移命令把 `pyproject.toml` 列为证据之一，但仓库**不存在**该文件（`git diff -- ... pyproject.toml` 恒空）。真实依赖 pin 在 `requirements.txt:12`（`pillow==12.3.0`，已核对）。属空条件证据。 | `Get-ChildItem`/`Test-Path` | 从命令与证据表移除 `pyproject.toml`，或注明「仓库无此文件」。 | open |
| R1-11 | P3 | 卡面 AC-M5⑤ / `test_source_match.py:884-888` | `for page_id in ("p1","p2")` 断言旧 binding 仍 `healthy`；卡/Handoff 描述为「旧 binding 保持 `needs_confirmation`」。该装置只演示 defer 不发布新 binding（不影响 AC），但描述与实测状态名不一致。 | 测试断言 vs 卡面文案 | 统一文案为「旧 binding 保持原状态（本装置为 healthy）」。 | open |
| R1-12 | P3（提示，非本卡缺陷） | `src/application/sources/scanner.py:521-565` + `referenced/scanner.py:360-365` + `source_sync.py:754` | 非图片成员（如 CBZ 里的 `ComicInfo.xml`）在 `scanned.entries` 中 `content_digest=None`；`apply` 会把 candidate entries 全量 `INSERT`，而 `source_entries.content_digest` 为 `NOT NULL` ⇒ **变更容器路径下含非图片成员的 resync 可能在 apply 报 NOT NULL**。base（`2d9a4a219`）同样如此（`"content_digest": item.content_digest` 一字未改），**非本卡引入**，也不在本卡 allowed_paths 内。 | 静态代码路径（未端到端实测） | 另开探针/卡确认并修复（例如跳过未绑定且无 digest 的成员，或放宽列约束），本卡不处理。 | open（out of scope） |

## 7. Architecture / Verification 两面结论

- **Architecture：PASS（无 P0/P1）**。分层未破：profile 提取留在 application 层 `scanner.py`，字节只经既有 `read_entry_bytes`→`read_verified_bytes` 严格读路径（无 `open()`、无新端口、无 `service.py`/`ports.py`/`core_assembly.py`/`referenced/**` 改动）；DTO 形状未变（`model.py` 零 diff，闭集由冻结校验器强制）；DB 只复用既有列（`schema.py` 零 diff、无迁移/依赖）；`pixel_digest` 公式、params canonical 与 EXIF 约定均与 C-17/`render_entry_png` 同源，无「第二套解码语义」。契约字节零漂移（C-17/C-15/C-08/ADJ-001/M2-C1）。
- **Verification：PASS（关键验证齐全，2 项测试/证据粒度不足见 P2/P3）**。所有 6 道门禁独立复跑通过；AC-M1…M6 均有实跑证据；变异 6 项中 5 项精确变红、1 项暴露测试不判别（R1-02，实现正确）；`.NET` 如实 NOT_RUN。**未审到的部分**：真实 Windows 卷/跨卷/移动盘路径、真实用户库、Host/IPC 侧的 scan→plan→apply 全链（本卡只有 application 层）、PDF、`FEA-11-SCAN-1` 的定时扫描。

## 8. 残余风险

1. **R1-01 的降级口径缺口**（窄但真实）：改名 + profile 不可比时 `missing+added`；已确认不伪造证据、不自动搬人工，但会阻断「bind 保留 PageId」的路径。
2. **profile 提取成本**：zip 场景每 entry 重读整容器（L-M6 已登记，未优化；scan TTL 300s）。冻结 profile 前无实测耗时数据（L-M5 无诊断计数）。
3. **per-entry `encrypted` 分支**未经端到端验证（R1-09），且可能被容器级 typed 拒绝先行拦截。
4. **R1-12 的既有 NULL digest apply 风险**（非本卡引入，未实测）。
5. **降级语义只对「可解码 entry」成立**：非全不透明 alpha、非法 EXIF、超预算的 entry 永远无 profile（L-M7），因此这些页在后续代次仍会走 `missing_old`/`incomparable`。

## 9. Closeout 建议（DSH 专属动作，不在本 Review 内执行）

1. **findings 处置**：R1-01 → 最小返修（约 12 行 matcher + 1 条判别性测试，`matcher.py`/`test_source_match.py` 均在本卡 allowed_paths 内）**或**登记 **L-M8**（同步卡 §残余 limitation、Handoff §4、EV §5）；R1-02 → 改 fixture（test-only，`test_source_match.py` 已授权）；R1-03/R1-06 → 重跑并重签 pin（含 `check.ps1`）。三项均为小改动，可与 closeout 合并为一次 docs/test 提交。
2. **delivery_head**：建议 **`c12023ab6`**（= `reviewed_head`，含卡/Handoff/证据），并在卡面同时保留实现+C8 head `b4ad109da`；理由：与 `FEA-11-AC4-GAPS-1` 的既有口径（`delivery_head` 指向含证据的最终交付提交、另一行记实现 head）一致，避免「交付物不含取证」的歧义。若坚持现口径（`b4ad109da`），**必须**在 Closeout Record/证据表写明「交付提交 `c12023ab6`」，并让卡/Handoff/EV 三处文字一致（当前三处已一致地采用实现口径，仅需保持）。
3. **`integration_commit`**：由 DSH 在 closeout 时填最终集成/文档提交（若本 Review 与 findings 修订合并提交，则取该提交）；提交后重跑 `check.ps1` 与 `verify_pins.ps1`（新增 review 文件不影响证据 pin，但 findings 修订会改证据 sha256）。
4. **`canonical_evidence_status`**：R1-03/R1-06 修复并重新 pin 后可置 `complete`；否则保留 `pinned` 并在 EV 注明 `recorded_at` 口径。**`resource_closeout_status`**：可置 `complete`（无删除/迁移；仓外隔离根 `workspace/FEA-11/fixtures` 与 `workspace/FEA-11/review-match-1/` 按 PRESERVE/清理策略处理，`closeout_counts` 如实填 0）。
5. **AC11-3 回填（FEA-11 卡）**：建议写 **「AC11-3 = MET（由 FEA-11-MATCH-1 承接 r7 L-4：真实 v7 旧库 fixture + 独立 match 测试 + 7 维可比性/一对一唯一/重复组待确认/旧证据降级均已验证；**残留 limitation：PDF 插页像素匹配（L-M1）、旧证据按冻结参数重算（L-M4）不覆盖**）」**；若验收口径不允许 AC 带 limitation 记 MET，则应保持 **PARTIAL** 并点名上述两项，**不得**无条件写 MET。AC11-4 已由 AC4-GAPS-1 闭环（沿用既有记录）。同时在 `SCOPE-ADJ`/`TASK_LEDGER` 记本卡 delivery 与 closeout。
6. **Review 落盘**：Lead 将本报告落入 `doc/reviews/FEA-11-MATCH-1-r1.md`（frontmatter 已含 `reviewer_kind: subagent` 与 session/parent id），并把卡面 `reviewer` 字段填为本 Review 的 session/来源。

---

**decision: approved。** P0 = 0、P1 = 0、P2 = 3（R1-01 改名 counterpart 的 `incomparable` 降级缺口、R1-02 字节分支重复守卫的测试不判别、R1-03 证据 `recorded_at` 不可为真）、P3 = 7。AC-M1/M2/M3/M5/M6 **MET**，AC-M4 **MET（附 R1-01 边界；建议最小返修或登记 L-M8）**。独立复跑全部一致：fea11 **107 passed**、本卡 **19 passed**、全量 **3202 passed/10 skipped**、`verify_pins` **18/18**、`check.ps1 -TaskPath` **PASS (3 warnings)**、契约/schema/依赖/apps **零 diff**、`.NET` 如实 **NOT_RUN**；10 个 sha256 pin 逐项复算 **0 mismatch**；卡内 4 个提交全在 `allowed_paths`（W1b 只增不删、断言未放宽），未 push，工作树 clean。变异 6 项：5 项 RED、1 项（M6）暴露测试不判别；两项探针给出 R1-01/R1-02 的可复现判别场景。建议 closeout：delivery_head 取 `c12023ab6`（或保留 `b4ad109da` 并写明交付提交），R1-01/R1-02/R1-03 最小处置后回填 **FEA-11 AC11-3 = MET（带 L-M1/L-M4 limitation 注记）**。
