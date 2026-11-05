---
task_id: FEA-11-MATCH-1
author: fea12-dsim-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2d9a4a219
delivery_head: e8b0b2db8
status: in_review
---

# Handoff — FEA-11-MATCH-1（页匹配 pixel profile 提取与旧库 fixture）

- Task：`doc/tasks/FEA-11-MATCH-1.md`（status: `in_review`；Owner=`fea12-dsim-impl`；Lead=`lead`）
- 交付日期：2026-11-06（Asia/Shanghai）
- 交付基线：`base_commit 2d9a4a219`（释放点）；**未 push**
- r1 交付 commits：`7bd8efe47`（实现 scanner/matcher）、`2d61e43c3`（测试/W1/W1b）、`b4ad109da`（C8 strict params）、`c12023ab6`（r1 卡/证据/Handoff）
- r1 独立上下文 Review：**approved（P0=0/P1=0；P2×3、P3×7）**，报告 `G:/CODEX/New Manga.workspace/FEA-11/review-match-1/FEA-11-MATCH-1-r1.md`（Lead 落盘 `doc/reviews/FEA-11-MATCH-1-r1.md`）
- **r2 交付 commit（实现+测试）：`e8b0b2db8`**；r2 处置 R1-01/R1-02/R1-03 + R1-04…R1-11 同批，R1-12 卡外登记；证据/卡面/本 Handoff 为紧随其后的文档提交
- 环境：Windows 11 / Python 3.14.6 / Pillow 12.3.0（既有 pin）/ SQLite v8 / 无新依赖、无 schema/migration 改动
- 范围依据：`doc/tasks/FEA-11-MATCH-1.md`（AC-M1…M6、C1–C12、L-M1…L-M7）、`doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md` §A、`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §5.2/§5.3/§7.3

## 0. r2 返修摘要（r1 Review findings 处置）

| Finding | 级别 | 处置 | 落点 |
|---|---|---|---|
| **R1-01** | P2 | 唯一像素 pass 新增 `len(candidates)==1 and not comparable` → `ambiguous/incomparable`（双侧非空）：改名/重排 + Pillow/params/decoder 变更导致旧 profile 不可比时仍可 `bind` 保留 PageId，不再 `missing+added`；判别性测试覆盖 orientation/params/decoder_version 三种改名场景，且断言不输出 `unique_pixel`/`changed`。 | `matcher.py`、`test_source_match.py::test_renamed_incomparable_counterpart_is_ambiguous_not_missing_added` |
| **R1-02** | P2 | 字节同一守卫测试改为**可达形态**（旧行 v7 无 profile → 前置 duplicate pass 不吸收；新侧一字节同一 + 一同像素成员）；删除字节分支守卫的 M6 变异现在会红（沿用 Reviewer 变异方法）。 | `test_source_match.py::test_byte_identity_does_not_bypass_a_duplicate_pixel_group` |
| **R1-03** | P2 | 6 份日志全部按真实机器时间重生成（`recorded_at=datetime.now()`），并重新签 Canonical Evidence pin；日志正文为 r2 实跑结果。 | `verification/FEA-11-MATCH-1/logs/*.log` + 卡面 Canonical Evidence |
| R1-04 | P3 | 删除 `_old_evidence_complete` 死代码及其“W/H = decode 证据”错误 docstring。 | `matcher.py` |
| R1-05 | P3 | scan 只读快照改为 `sqlite_master` **全表**枚举（当前 40 表），不再固定 17 表子集；卡/Handoff/EV 口径统一为“全表”。 | `test_source_match.py::_snapshot` |
| R1-06 | P3 | gates.log 的最终 check 复跑在 EV-M10 登记**之后**执行并记录（3 warnings，PASS）；重新签 sha。 | `logs/gates.log` |
| R1-07 | P3 | lost-scan 用例断言具体 `SOURCE_PLAN_STALE` + `details.cause=="expired"`，并显式断言 `source_operations`/`source_binding_publications` 无新行。 | `test_source_match.py` |
| R1-08 | P3 | `changed/direct` 前加显式 `pixel_digest` 不同守卫（相等 → `ambiguous/duplicate_group`；当前 pass 顺序下不可达，防御未来重排）。 | `matcher.py` |
| R1-09 | P3 | 口径收窄：`encrypted` 仅映射层单测（zip 加密成员端到端未构造），EV/Handoff 不再声称端到端已证。 | `EV.md`、本 Handoff |
| R1-10 | P3 | 从证据命令/表格移除仓库中不存在的 `pyproject.toml`；依赖证据只保留 `requirements.txt`（pin Pillow 12.3.0）。 | `EV.md`、`gates.log`、`static-diff.log`、卡 AC-M6 |
| R1-11 | P3 | 卡面/Handoff/EV 统一为“defer 不发布新 binding，旧 binding 保持原状态（本装置为 `healthy`）”，不再写 `needs_confirmation`。 | 卡 AC-M3/AC-M5、本 Handoff、EV |
| R1-12 | P3（卡外） | 不修；登记为卡外后续：非图片成员 `content_digest=None` + 变更容器 apply 全量 INSERT 的 `NOT NULL` 风险（base 已存在，不在本卡 allowed_paths）。 | 卡“残余 limitation/卡外后续”、EV §5 |

## 1. 交付结果（逐项对照 AC）

| AC | 结果 | 交付内容 |
|---|---|---|
| AC-M1 profile 提取/持久化/降级 | **MET** | 变更容器路径下对可解码 entry 产出完整 `pixel-digest/1`：`sha256(ASCII("WxH")+b"\x00"+RGB)`（EXIF 转置后 W/H、`orientation=1`、8-bit RGB 逐行）、`decoder="referenced-import"`/`decoder_version="1"`（DSH 2026-11-06 C9 裁决）、冻结 canonical params 对象、`params_digest=sha256(canonical JSON object)`（修复原 `scanner.py:545-555` 双重编码缺陷）；取字节仅走 `read_entry_bytes` 严格校验路径；逐 entry C10 降级（加密→`encrypted`、格式/损坏/非法 EXIF/预算→`unsupported`、无 `content_digest`→`missing_evidence`），grant/lease/identity/integrity 错误仍 typed 上抛；apply 后 `source_entries` 落库非空 profile 且与 live candidate canonical params 一致。**R1-09 口径**：`encrypted` 目前只有映射层单测，zip 加密成员端到端未构造。 |
| AC-M2 7 维可比性 | **MET** | `_profiles_comparable` = algorithm+decoder+decoder_version+canonical params+width+height+orientation 全等；params 按 canonical 对象比较（键序/空白等价），非对象 JSON 一律不可比；`unique_pixel` 仅两侧各 1 次且可比；`changed` 仅双侧完整可比且像素不同（R1-08 加显式守卫）；`_publication_relation` 两条分支（几何相等 / 唯一字节 `old_geometry=(None,None)` 兜底）均断言。 |
| AC-M3 重复 pixel occurrence | **MET** | occurrence 统计纳入 `pixel_digest`（与 `content_digest`/`locator` 同口径、按侧独立）；任一侧 ≥2 整组 `ambiguous/duplicate_group`；唯一字节分支不绕过重复 pixel 组（R1-02 后测试可达且判别）；1:2/2:1/重名/同像素交叠均有矩阵；scan→plan→apply 全链（defer 零发布、**旧 binding 保持原状态，本装置为 `healthy`**、PageId/人工数据零变化）。 |
| AC-M4 旧证据降级 + counterpart-less 修正 | **MET** | 旧行无 profile（含真实 v7 W/H-only）或 profile 不可比 → `ambiguous/missing_old|incomparable`，绝不 `unique_pixel`、绝不 `changed/direct`；**R1-01**：同名/跨 locator 的同一像素 occurrence 但 profile 不可比（改名/重排 + Pillow/params/decoder 变更）也降级为 `ambiguous/incomparable`（保留 bind 可能），不伪造证据；唯一允许的免重算等价 = 唯一 `content_digest` 相等（先排除重复组）→ `unique_pixel`；无跨侧候选的重复成员：旧→`missing/none`、新→`added/none`；`ambiguous` 永远双侧非空（C-17 §5.3）。 |
| AC-M5 生产 v7 fixture + 独立 match 测试 | **MET** | `test_source_match.py` 20 用例覆盖：①纯 matcher 单测（rows in/classified pairs out，无 DB 无文件）；②scan 级集成（真实 zip + 真实 HMAC grant + 真实严格读）；③scan 只读（**sqlite_master 全表**快照前后相等，R1-05）；④两代 resync（导入后第二代起像素匹配可达）；⑤apply 保留 canonical params + scan 丢失时 `SOURCE_PLAN_STALE`（cause=expired）typed 失败、零内容/绑定/profile/operation/publication 提交（R1-07）。真实 v7 fixture：`MigrationRunner(conn, default_migrations()[:7])` 建 v7 → 真实 `ReferencedImportPlanner`/`ReferencedImportRuntime` 导入真实 zip → 迁 v8 → scan/match；旧行形态诚实（`pixel_digest/algorithm IS NULL`、bound entry 有 W/H 且 `decoder_name` 非空、非 bound 成员 W/H NULL）。W1/W1b 窄批按 DSH 2026-11-06 执行，断言未放宽。 |
| AC-M6 契约/门禁零漂移 | **MET** | 见 §2：pins 18/18、check.ps1 PASS、全量 **3203 passed / 10 skipped**（基线 3183/10）、`doc/plan`/`doc/contracts`/`apps`/`schema.py`/`migrator.py`/`requirements.txt` 零 diff、无新依赖；`.NET` **NOT_RUN**（`apps/**` 零 diff）。 |

## 2. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | Python 3.14.6；`e8b0b2db8` | **PASS**（108 passed） | `verification/FEA-11-MATCH-1/logs/pytest-fea11.log` |
| 本卡测试 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_match.py -q -p no:cacheprovider` | 同上 | **PASS**（20 passed） | `logs/pytest-match.log` |
| 全量 | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 同上 | **PASS**（**3203 passed, 10 skipped**） | `logs/pytest-full.log` |
| 基线 | 同全量，于释放 head `71e4b42b4` clean tree | 同上 | **3183 passed, 10 skipped** | `logs/pytest-baseline.log` |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md`；`... verify_pins.ps1` | 仓库根 | **PASS**；**PASS (18/18)** | `logs/gates.log`、`logs/verify-pins.log` |
| 范围 | `git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps`；`... -- schema.py migrator.py requirements.txt` | 同上 | **空（0 域外 diff；仓库无 pyproject.toml，R1-10）** | `logs/static-diff.log` |
| .NET | NOT_RUN | — | `apps/**` 零 diff、无 C# 变更；不得写 PASS | `EV.md` §1 |

## 3. 范围与冻结契约

- 只改 `allowed_paths`：`scanner.py`、`matcher.py`、`tests/fea11/test_source_match.py`、W1 `test_source_scan.py`、W1b `test_source_sync.py`/`test_source_relink.py`（`test_source_sync_storage.py` 经共享 helper 自动恢复，未改行）、本卡、Handoff、`verification/FEA-11-MATCH-1/**`。
- 未改：C-17/C-15/C-08/ADJ-001/M2-C1 任何字节、v1–v8 迁移 SQL/checksum、`schema.py`、`apps/**`、`service.py`/`ports.py`/`core_assembly.py`/`referenced/**`、治理指针（STATUS/PLAN/LEDGER/reviews）、依赖清单。
- DSH 裁决登记：2026-11-06 窄批 W1b（夹具补真实 pixel profile；不改断言）；2026-11-06 C9 常量更正（`referenced-import/1` 含 `/` 违反 C-17 §5.2/§5 ID 规则 → `referenced-import` + `1`，契约字节未动）。

## 4. 残余 limitation（未变化）

L-M1 PDF 不产 profile；L-M2 导入路径不写 profile（首次 resync 不能像素匹配，第二代起可达）；L-M3 `service.py::_entries_from_target` 保真缺陷（未扩 `service.py`；live scan 丢失即 typed `SOURCE_PLAN_STALE`，本卡已加零提交测试）；L-M4 旧证据重算未实现；L-M5 无解码诊断计数；L-M6 性能未优化（仅登记）；L-M7 EXIF 镜像不可区分 + 非全不透明 alpha 不产 profile + 不宣称“所有可解码图必有 profile”。
**卡外后续（R1-12，不修）**：非图片成员 `content_digest=None` + 变更容器 apply 全量 INSERT 的 `source_entries.content_digest NOT NULL` 风险（base 已存在、不在本卡 allowed_paths，登记后续探针/修复卡）。

## 5. Review 就绪

- r1 Review approved（P0/P1=0）；r2 已按 findings 最小返修并重签全部证据 pin。建议窄面复审重点：①R1-01 改名不可比场景（3 个维度）是否 `ambiguous/incomparable`、双侧非空、不伪证；②R1-02 用 M6 变异复验（删字节分支重复守卫应使该用例红）；③R1-03 日志 `recorded_at` 是否为真实机器时间且与当前提交/mtime 一致；④R1-05 快照是否真为 `sqlite_master` 全表；⑤R1-06 gates.log 最终 check 是否在 EV-M10 登记后；⑥R1-07 是否断言 `SOURCE_PLAN_STALE`/cause=expired 及零 operation/publication；⑦R1-04/R1-08/R1-09/R1-10/R1-11 文档与代码一致性。
- 作者未自审；`.NET` NOT_RUN 需 Review 侧确认为合法口径（`apps/**` 零 diff）。
- 推荐下一步：Lead 派窄面 fresh Review → DSH 集成 closeout（填 `integration_commit`、delivery_head、STATUS/PLAN/LEDGER 指针、canonical evidence/closeout 状态；AC11-3 回填按 r1 Review §9 建议带 L-M1/L-M4 limitation）。
