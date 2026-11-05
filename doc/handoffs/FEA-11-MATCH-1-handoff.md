---
task_id: FEA-11-MATCH-1
author: fea12-dsim-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2d9a4a219
delivery_head: b4ad109da
status: in_review
---

# Handoff — FEA-11-MATCH-1（页匹配 pixel profile 提取与旧库 fixture）

- Task：`doc/tasks/FEA-11-MATCH-1.md`（status: `in_review`；Owner=`fea12-dsim-impl`；Lead=`lead`）
- 交付日期：2026-11-06（Asia/Shanghai）
- 交付基线：`base_commit 2d9a4a219`（释放点）；实际父提交 `9bf3fcb42`（docs-only closeout 补充）；**未 push**
- 交付实现 commit：`7bd8efe47`（`src/application/sources/scanner.py` + `matcher.py`）
- 交付测试 commit：`2d61e43c3`（`tests/fea11/test_source_match.py` 新增 19 用例；W1 `test_source_scan.py`；W1b `test_source_sync.py` + `test_source_relink.py`）
- 交付修正 commit：`b4ad109da`（C8 收紧：decoder params 必须是 canonical JSON **对象**；非对象/非法 JSON → `incomparable`，不伪装 `{}`；+ 非对象回归用例）
- 交付 head（实现+测试）：`b4ad109da`；证据/卡面/本 Handoff 为紧随其后的文档提交
- 环境：Windows 11 / Python 3.14.6 / Pillow 12.3.0（既有 pin）/ SQLite v8 / 无新依赖、无 schema/migration 改动
- 范围依据：`doc/tasks/FEA-11-MATCH-1.md`（AC-M1…M6、C1–C12、L-M1…L-M7）、`doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md` §A、`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §5.2/§5.3/§7.3

## 1. 交付结果（逐项对照 AC）

| AC | 结果 | 交付内容 |
|---|---|---|
| AC-M1 profile 提取/持久化/降级 | **MET** | 变更容器路径下对可解码 entry 产出完整 `pixel-digest/1`：`sha256(ASCII("WxH")+b"\x00"+RGB)`（EXIF 转置后 W/H、`orientation=1`、8-bit RGB 逐行）、`decoder="referenced-import"`/`decoder_version="1"`（DSH 2026-11-06 C9 裁决）、冻结 canonical params 对象、`params_digest=sha256(canonical JSON object)`（修复原 `scanner.py:545-555` 双重编码缺陷）；取字节仅走 `read_entry_bytes` 严格校验路径；逐 entry C10 降级（加密→`encrypted`、格式/损坏/非法 EXIF/预算→`unsupported`、无 `content_digest`→`missing_evidence`），grant/lease/identity/integrity 错误仍 typed 上抛；apply 后 `source_entries` 落库非空 profile 且与 live candidate canonical params 一致。证据：`tests/fea11/test_source_match.py` 7 用例（独立 Pillow 复算 + 固定 golden `53b800d9…` + EXIF 1–8/镜像/非法 9 + DB 快照零写 + apply 持久化）。 |
| AC-M2 7 维可比性 | **MET** | `_profiles_comparable` = algorithm+decoder+decoder_version+canonical params+width+height+orientation 全等；params 按 canonical 对象比较（键序/空白等价），非对象 JSON 一律不可比；`unique_pixel` 仅两侧各 1 次且可比；`changed` 仅双侧完整可比且像素不同；`_publication_relation` 两条分支（几何相等 / 唯一字节 `old_geometry=(None,None)` 兜底）均断言。 |
| AC-M3 重复 pixel occurrence | **MET** | occurrence 统计纳入 `pixel_digest`（与 `content_digest`/`locator` 同口径、按侧独立）；任一侧 ≥2 整组 `ambiguous/duplicate_group`；唯一字节分支不绕过重复 pixel 组；1:2/2:1/重名/同像素交叠均有矩阵；scan→plan→apply 全链（defer 零发布、旧 binding 保持 `needs_confirmation`、PageId/人工数据零变化）。 |
| AC-M4 旧证据降级 + counterpart-less 修正 | **MET** | 旧行无 profile（含真实 v7 W/H-only）或 profile 不可比 → `ambiguous/missing_old|incomparable`，绝不 `unique_pixel`、绝不 `changed/direct`；唯一允许的免重算等价 = 唯一 `content_digest` 相等（先排除重复组）→ `unique_pixel`；无跨侧候选的重复成员：旧→`missing/none`、新→`added/none`（`ambiguous` 永远双侧非空，C-17 §5.3）；不从新图伪造旧证据。判别力：真实 v7 导入后字节改变成员由改前 `changed/direct` 改为 `ambiguous/missing_old`，字节同一成员仍 `unique_pixel`。 |
| AC-M5 生产 v7 fixture + 独立 match 测试 | **MET** | `test_source_match.py` 19 用例覆盖：①纯 matcher 单测（rows in/classified pairs out，无 DB 无文件）；②scan 级集成（真实 zip + 真实 HMAC grant + 真实严格读）；③scan 只读（16 表全表快照前后相等）；④两代 resync（导入后第二代起像素匹配可达）；⑤apply 保留 canonical params + scan 丢失时 apply typed 失败且零内容/绑定/profile 提交。真实 v7 fixture：`MigrationRunner(conn, default_migrations()[:7])` 建 v7 → 真实 `ReferencedImportPlanner`/`ReferencedImportRuntime` 导入真实 zip → 迁 v8 → scan/match；旧行形态诚实（`pixel_digest/algorithm IS NULL`、bound entry 有 W/H 且 `decoder_name` 非空、非 bound 成员 W/H NULL）。W1/W1b 窄批按 DSH 2026-11-06 执行，断言未放宽。 |
| AC-M6 契约/门禁零漂移 | **MET** | 见 §2：pins 18/18、check.ps1 PASS、全量 **3202 passed / 10 skipped**（基线 3183/10）、`doc/plan`/`doc/contracts`/`apps`/`schema.py`/`migrator.py`/`requirements.txt`/`pyproject.toml` 零 diff、无新依赖；`.NET` **NOT_RUN**（`apps/**` 零 diff）。 |

## 2. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 隔离测试 | `C:/Python314/python.exe -m pytest tests/fea11 -q -p no:cacheprovider` | Python 3.14.6；`b4ad109da` | **PASS**（107 passed） | `verification/FEA-11-MATCH-1/logs/pytest-fea11.log` |
| 本卡测试 | `C:/Python314/python.exe -m pytest tests/fea11/test_source_match.py -q -p no:cacheprovider` | 同上 | **PASS**（19 passed） | `logs/pytest-match.log` |
| 全量 | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | 同上 | **PASS**（**3202 passed, 10 skipped**） | `logs/pytest-full.log` |
| 基线 | 同全量，于释放 head `71e4b42b4` clean tree | 同上 | **3183 passed, 10 skipped** | `logs/pytest-baseline.log` |
| 治理门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-MATCH-1.md`；`... verify_pins.ps1` | 仓库根 | **PASS**；**PASS (18/18)** | `logs/gates.log`、`logs/verify-pins.log` |
| 范围 | `git diff --name-only 2d9a4a219..HEAD -- doc/plan doc/contracts apps`；`... -- schema.py migrator.py requirements.txt pyproject.toml` | 同上 | **空（0 域外 diff）** | `logs/static-diff.log` |
| .NET | NOT_RUN | — | `apps/**` 零 diff、无 C# 变更；不得写 PASS | `EV.md` §1 |

## 3. 范围与冻结契约

- 只改 `allowed_paths`：`scanner.py`、`matcher.py`、`tests/fea11/test_source_match.py`、W1 `test_source_scan.py`、W1b `test_source_sync.py`/`test_source_relink.py`（`test_source_sync_storage.py` 经共享 helper 自动恢复，未改行）、本卡、Handoff、`verification/FEA-11-MATCH-1/**`。
- 未改：C-17/C-15/C-08/ADJ-001/M2-C1 任何字节、v1–v8 迁移 SQL/checksum、`schema.py`、`apps/**`、`service.py`/`ports.py`/`core_assembly.py`/`referenced/**`、治理指针（STATUS/PLAN/LEDGER）、依赖清单。
- DSH 裁决登记：2026-11-06 窄批 W1b（夹具补真实 pixel profile；不改断言）；2026-11-06 C9 常量更正（`referenced-import/1` 含 `/` 违反 C-17 §5.2/§5 ID 规则 → `referenced-import` + `1`，契约字节未动）。

## 4. 残余 limitation（未变化）

L-M1 PDF 不产 profile；L-M2 导入路径不写 profile（首次 resync 不能像素匹配，第二代起可达）；L-M3 `service.py::_entries_from_target` 保真缺陷（未扩 `service.py`；live scan 丢失即 typed `SOURCE_PLAN_STALE`，本卡已加零提交测试）；L-M4 旧证据重算未实现；L-M5 无解码诊断计数；L-M6 性能未优化（仅登记）；L-M7 EXIF 镜像不可区分 + 非全不透明 alpha 不产 profile + 不宣称“所有可解码图必有 profile”。

## 5. Review 就绪

- 独立上下文 Reviewer 建议重点：①AC-M1 冻结常量/EXIF 转置/params canonical 与 C-17 §5.2 逐项对照（含 C9 修正是否只属卡级常量）；②AC-M2 判别力（同 pixel/同 W/H 仅 orientation 或 params 不同 → 必须 `incomparable`）；③AC-M3/AC-M4 与 C-17 §5.3 非空组合守卫、totals 语义变化（预期行为变更 #2/#5）；④AC-M5 真实 v7 fixture 是否确由生产迁移+真实导入生成、scan 只读快照、两代 resync、scan 丢失零提交；⑤门禁复跑（pins/check/全量 ≥3202 或 ≥3183）。
- 作者未自审；`.NET` NOT_RUN 需 Review 侧确认为合法口径（`apps/**` 零 diff）。
- 推荐下一步：Lead 派发独立上下文 Review → r1 findings 处置 → DSH 集成 closeout（填 `integration_commit`、STATUS/PLAN/LEDGER 指针、canonical evidence/closeout 状态）。
