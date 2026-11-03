---
task_id: FEA-08
author: DSH（Lead/Integrator 直接实施 R3；Codex 已担任 impl-r2 Reviewer，ZCode 额度未恢复；DSH 不自审，impl-r3 Review 交 Codex 新独立上下文）
kind: handoff
delivery_scope: impl-r2 changes_requested（P1=3/P2=4）处置；H6 判据/矩阵/原子 staging/门禁原始日志；无生产代码改动
delivery_commit: 见 Task 卡 delivery_head（R3 证据 commit）
---

# FEA-08 R3 返修 Handoff（R3 → impl-r3 Review / DSH 集成）

## 1. 交付概览

- **目标**：处置 `doc/reviews/FEA-08-impl-r2.md`（Codex，changes_requested P0=0/P1=3/P2=4）全部 findings；不改变冻结 scope、不产生产代码。
- **写域**：`verification/FEA-08/**`、`doc/research/FEA-08-source-capability.md`、`doc/handoffs/FEA-08-*.md`、`doc/tasks/FEA-08.md`（登记）；产品路径 `src/apps/experiments/tests/packaging/scripts/tools` 零 diff（`src_changes=0`）。未 push。
- **实施者**：DSH（Integrator 直接实施）。Review 独立性：impl-r3 必须由未参与 R3 实现的独立上下文执行（Codex 新会话；DSH 主会话不得自审）。

## 2. P1 处置

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I2-001**（EV-F08-43 仍 pin 旧 commit；pin_selfcheck 只信 index） | `pin_selfcheck.py` 重写：**逐行读取 Task 表登记的 commit**，用 `git cat-file -p <commit>:<path>` 原始字节校验，并叠加 stage-index blob 与干净 checkout 四方校验；R3 全部 67 项在 R3 证据 commit 上重 pin（变更文件不再沿用旧 commit）。 | `logs/pin-verify.log`（commit 列逐行 OK）；Task 卡 EV 表 |
| **F08I2-002**（H6 规范像素 digest 未绑尺寸，2×6 vs 3×4 误 exact） | `canonical_pixels()` digest 升级为 `sha256("WxH\0" + RGB bytes)`（含 exif_transpose 后尺寸）；`match_single_image` 显式记录 `size_a/size_b/size_mismatch/exact_blocked_by_size_mismatch`，尺寸不同不得 exact；PDF 渲染 digest 同样绑定渲染尺寸；新增反例 fixture `img_dims_a.png`(2×6)/`img_dims_b.png`(3×4)（像素字节序列相同）与场景 **M19** → `candidate` + 断言 `assert_not_exact/assert_size_mismatch/assert_canonical_differs`。 | `results/h6_results.json` M19；`fixtures/img_dims_a|b.png` |
| **F08I2-003**（容器只比内容多重集，重复同图不同名误 exact） | `match_container` 增加**成员身份唯一映射**：内容多重集相等 + 成员名集合可对齐 → exact；**重复内容但成员身份（名/ordinal）不同 → `needs_confirmation`**（`duplicate_content_ambiguity`）；仅重命名（名集合不同、内容唯一）→ `needs_confirmation`；重复名不同内容仍 candidate。新增反例 fixture `book_dupcontent_a/b.zip`（四成员内容全同、名 a/b vs c/d）与场景 **M20** → `needs_confirmation` + 断言。 | `results/h6_results.json` M20 |

## 3. P2 处置

| Finding | 处置 | 证据 |
|---|---|---|
| **F08I2-004**（非 NTFS 分支 evidence 继承污染） | 每个卷分支显式赋值 `h4_ev/h5_ev/h6_ev`；USB/SMB → mocked，Cloud → inferred；MD 表改为逐能力展示 `状态（来源）` + 三列现状。 | `results/capability_matrix.{json,md}` |
| **F08I2-005**（derive 缺必需断言，变异仍 PASS） | `derive_ntfs()` 改为消费语义断言集：strict 拦截断言（S1/S2/S3a/S3b/S5c/S6/S7 + writer blocked）、S4 mixed 对照组、S5a/b 字段自洽、H5 R3/R5b/R6b 分支事实、H6 M3/M5/M7/M16 蓝帧反证/M17/M18/M19/M20 断言；任一失败即降级（矩阵 JSON 记 `derivation_assertions`）。 | `matrix.py`、`results/capability_matrix.json` |
| **F08I2-006**（staging 先破坏旧 Canonical、失败留混合证据） | `run_all.py` 重写为**原子晋升**：fixtures/结果/日志先在 workspace 构建并全部校验，通过后备份旧集再晋升（逐文件/目录 journal）；任一失败**回滚旧 Canonical**，失败原因只写 workspace `out/run_all_failure.json`（不冒充成功日志）；tmp 清理移入 `finally`。 | `run_all.py`、`results/run_all_log.json` |
| **F08I2-007**（门禁原始输出未版本化、skip 无来源） | 新增 `gates_capture.py`：build/test/pins/四 PNG/禁止 diff/安全搜索的**完整原始输出**（命令、EXIT、cwd、shell、解释器、耗时）入库 `logs/gates-raw/**`；`logs/test-skip-inventory.md` 逐项列出 **57/57 skip**（测试标识、源文件:行、属性、原因）；`gates.log` 改为摘要 + 原始日志指针 + 环境快照；全量测试 attempt1 偶发失败保留原始日志（`02-test-attempt1.log`），重跑通过并透明记录。 | `logs/gates.log`、`logs/gates-raw/**`、`logs/test-skip-inventory.md` |

## 4. 门禁（R3；原始输出 `logs/gates-raw/**`）

- build：0 warning / 0 error（EXIT=0；`gates-raw/01-build.log`）。
- 无过滤全量：**1292 passed / 0 failed / 57 skipped**（EXIT=0；attempt1 项目既有偶发 flake 已留档，重跑通过；`gates-raw/02-test.log`）。
- check.ps1：**PASS(3 warnings)**（EXIT=0；`gates-raw/03-check.log`）；pins：**15/15**（`gates-raw/04-freeze-pins.log`）。
- 旧 FEA-06 四 PNG 未变（`gates-raw/05-fea06-png.log`）；禁止范围 diff 空（src_changes=0；`gates-raw/06-forbidden-diff.log`）；代码路径清空类 API 调用=0（`gates-raw/07-clearing-api-search.log`）。
- Canonical Evidence：67/67 四方 pin 一致（`logs/pin-verify.log`）；未 push。

## 5. 复现

```powershell
python G:\CODEX\New Manga.workspace\FEA-08\prototype\run_all.py                # 全链（会重写 verification/FEA-08 证据；失败回滚）
python G:\CODEX\New Manga.workspace\FEA-08\prototype\h6_run.py --fixtures G:\CODEX\New Manga\verification\FEA-08\fixtures
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase1
python G:\CODEX\New Manga.workspace\FEA-08\prototype\gates_capture.py --phase2
git add verification/FEA-08
python G:\CODEX\New Manga.workspace\FEA-08\prototype\pin_selfcheck.py
```

## 6. 风险与遗留

1. **测试 flake**：全量测试存在项目既有偶发失败（Host/CoreClient 时序/sidecar 类），R3 采集时 attempt1 两轮各出现一例（不同测试），重跑通过；建议另行登记 repo 级稳定性债务（不属 FEA-08 范围）。
2. **产品牌面未决**：AES ZIP 需 pyzipper(MIT)（LIMITED(pyzipper)）；IFileOperation per-item sink 未实跑；USB/SMB/云无硬件；R8 真实取消不可无人值守触发（LIMITED(mocked)）。
3. **判定边界**：重复同图“同成员名+同序”时仍按重复名歧义给 candidate（保守）；生产实现需保留成员 identity/ordinal 与 occurrence 映射（报告 §8-8）。
4. 本 Task 不产生产代码；SQLite/DB 不在范围；原生 200% DPI/a11y 无关。

## 7. 下一步

impl-r3 独立 Review（Codex 新会话）→ approved 后 DSH 集成验证（build/全量/check/pins/四 PNG/禁止 diff + 证据复核）→ 关闭 FEA-08（Resource Manifest/Closeout）→ 释放 FEA-09（引用源与导入）scope。**不 push。**
