# M2-TA3-B2 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-TA3-B2`；链：release `69137837`（base=`521d0bdd`）→ `b7806dac`(AC5 精修) → `67fe590a`(探针+runner+评测) → `3c8801b7`(run 产物, 交付实体) → `81e5ad81`(AC 回填+handoff, r1 被审头) → 返修 `614be825`+`7922a3fc`(r2 被审头) → 集成修正（本 commit）
- Review 链：DSH r1 **`changes_requested`**（1×P1 R1 + 5×P2 + 7×P3 + 2×P4；`doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md`，sha256 `80b1301d…b53c`）→ **集成方定案 R1 机制 + git 门禁** → Owner 返修 R1-R15（14 closed + R14 集成方定案）→ DSH r2 收敛（R1-R15 逐条 closed，新问题仅 N1 一处 P2 + N2-N8 P3/P4；`doc/reviews/M2-TA3-B2-7922a3fc-dsh-r2.md`，sha256 `86da0f79…6730`）→ 集成修正闭合

## 集成方定案（r1 闭合清单 1-2）

1. **git 门禁/R14**：merge-base(521d0bdd, 81e5ad81)=`521d0bdd`，线性链；两口径 diff 均 53 文件（Task 文件两区间均变动故同数）；`diff --check` EXIT=0；禁改面零；porcelain 干净。Owner 自检范围与交付范围重合。
2. **R1 机制（P1 裁决基础）**：实算 `BJ02-translated.png` 与 `BJ02.rerun-translated.png`（mtime 相差 25 分钟的两个独立文件）sha256 **逐位相同**（`5c74a4f0…`）；读 `run_qualification.py:510-557` 定案——export 复制的是 **Run1（TRANSLATE_ALL）渲染落盘产物**，Run2（RETRANSLATE_REGION_FULL）只更新 DB revision 不触发重渲染。推论：BJ02 PASS 语义=Run1 页面级全链（含 remote 批量翻译）两次独立 run 逐位一致；K11 export 差异根因在 Run1 内部（OCR 已排除 0/13，scratch db 已清理无法事后逐层隔离）；Run2 译文浮动 7/11 是独立 remote 采样观察、不进入 export。Owner 按此重写 §5/F5。

## 集成修正闭合（DSH r2 新问题 + 运行时项）

| # | 项 | 处置 |
|---|---|---|
| N1(P2) | Task AC3 行旧叙事 | 本 commit 重写（Run1 语义定案叙事 + 独立复算 11/11→**13/13** + F5 裁决点指向） |
| N2(P3) | quality-report:58 行号失效 | →`764-765,851-852`（注明 R2/R13 插入后偏移） |
| N3(P4) | handoff:39 出库理由回潮 | 改「仓库树外兄弟目录、与 .gitignore 无关」+ manifest 指针 |
| N4(P4) | 复现命令缺 verify_exports.py | handoff §2 补命令 |
| N7(P4) | stdout/stderr 未 scrub | `run_qualification.py` stage() 与 `translate_probe.py` stderr 落 `scrub_secrets()` |
| **wrapper ndarray 适配**（OCR-FIX 联动，r1 集成清单 7） | **`paddle_e2e_probe.py` wrapper `ocr()` 加 ndarray 直通分支**（M2-OCR-PADDLE3X-1 已在 main：注入 engine 收 BGR ndarray；本分支 merge 前 adapter 传 bytes——wrapper 双兼容，新旧 checkout 均可跑） |

## 运行时复跑（r2 NOT_VERIFIED 清单）

| # | 项 | 结果 |
|---|---|---|
| 1 | git 事实：`diff --check 81e5ad81..7922a3fc` EXIT=0、返修 15 文件、porcelain 干净（Owner 自检复核） | PASS |
| 2 | **R1 三方并排留档**：集成方实算 BJ02 双侧=`5c74a4f0…8759037`（逐位相同）、K11=`2c5dee05…3064835`/`86ff9aa7…3064842`（不同=AC3 FAIL 事实）↔ `pixels-manifest.json` 同值 ↔ `rerun-compare.json` 同值——三处逐位一致 | PASS |
| 3 | `verify_exports.py` 集成方复跑：**n=13 all_match=True**（11 首跑+BJ02.rerun+K11.rerun）+ manifest n=126/87,573,189 bytes——与 Owner 声称一致；复跑仅 generated_at 变化（内容稳定性实证） | PASS |
| 4 | R4 K09 复跑（F2 一级证据）：**不执行**，F2 维持推断口径（r2 已 closed 接受推断） | 登记不执行 |
| 5 | R11 计量：token 无 usage 字段维持 estimated（usage 落盘=runner 增强候选） | 登记不执行 |
| 6 | 集成门禁：本 Task 零 src/tests 改动；post-merge 三套件复跑见 merge commit 后记录 | 见下 |

**N5/N6/N8（P4）登记后续**：rerun-compare 合并写入的旧格式兼容与 note 字段保留；反事实口径进工件注记；phase2-plan superseded 交叉注。三工作表+G2 50 行 GT 审核=用户侧并行项（非关闭条件），像素外部树需保持存活。

## 裁决移交（不由集成方自裁，交用户/Codex 下轮）

1. **建议 A**：webtoon 长条漫检测支持（ogkalu 0 候选 ×6 case=全链 Gate 最大单因；实施前先补适配器可观测值 n_text_raw/n_bubble/tensor 尺寸）
2. **建议 B**：大图导入 allocation limit（Qt 256MB 上限拒 K07/K09/K10）
3. **F5**：确定性 Gate 在 remote 翻译下的重定义（候选：reading_order 对齐译文相似度）
4. **F4**：detect 冒烟口径措辞统一
5. SFX→translate 产品入口需求（生产 SfxPolicy 默认 SKIP 导致 AC4 SFX 示例 n=0）

## 集成 commit 清单

- `doc/reviews/M2-TA3-B2-81e5ad81-dsh-r1.md` / `M2-TA3-B2-7922a3fc-dsh-r2.md`（原字节 import）
- `verification/M2-TA3-B/integration-phase2.md`（本文件；与阶段一 integration.md 分离）
- `doc/tasks/M2-TA3-B2.md`（N1 AC3 行 + status done + delivery_head 7922a3fc/R14 注记）
- `verification/M2-TA3-B/quality-report.md`（N2 行号）
- `doc/handoffs/M2-TA3-B2-3c8801b7.md`（N3/N4）
- `experiments/M2-TA3-B/paddle_e2e_probe.py`（wrapper ndarray 适配）、`run_qualification.py`/`translate_probe.py`（N7 scrub）
- `phase2/export/export-hash-recompute.json` + `phase2/pixels-manifest.json`（复跑 generated_at）
