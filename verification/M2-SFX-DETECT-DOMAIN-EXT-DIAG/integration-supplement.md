# M2-SFX-DETECT-DOMAIN-EXT-DIAG 集成补充记录（2026-10-04，收口遗漏补登）

## 背景

本 Task 存在两个会话的并行交付链（author 均为 peakwheat-pixel，git 不可区分会话身份）：

- **Owner 链（本会话派发的 ZCode 子 agent）**：claim `303d7e14` → delivery `87a8bc34` → 文档收尾 `cc2109ac` → DSH r1 `changes_requested`（0×P0，1×P1+4×P2+3×P3+3×P4）→ 返修 `d849c967`+`3952a00f`（11 条闭合）→ DSH r2 `approved`（定点 10/10 闭合核对）。
- **编排链（并行编排会话）**：独立 DSH crosscheck r1 `approved_with_conditions` @tip `3952a00f`（两链并存裁决，import 于 `9cd512d7`）→ 集成 merge `7dd5e5ff` → close `1627f36a`（post-merge 三套件 611+1skipped 0 failed EXIT=0、STATUS/PLAN 收口、三裁决问题移交登记）。

两链发现高度重合、互为印证（crosscheck 报告对 rework 数字声明逐项抽查属实）。本补登不重做集成，仅闭合编排链 close commit 的三处遗漏并登记 Owner 链独有证据。

## 补登内容（本 commit）

1. **Task frontmatter 流转 done**：close commit 宣称 Task done 但 frontmatter 仍 `in_progress`；本 commit 补 `status: done` + `integration_commit: 7dd5e5ff` + 双链 reviewed_head 终态。
2. **DSH r1/r2 报告原字节 import**（Owner 链证据，crosscheck 报告引用该链但报告本体未入库）：
   - `doc/reviews/M2-SFX-DETECT-DOMAIN-EXT-DIAG-87a8bc34-dsh-r1.md`（r1 changes_requested，SHA-256=`0e39e2c0033190931f26dd66f4871eb2946e88be81a200c2d6e630133b3104dd`）
   - `doc/reviews/M2-SFX-DETECT-DOMAIN-EXT-DIAG-d849c967-dsh-r2.md`（r2 approved 定点复核，SHA-256=`e6c8b6d025eaec187b4739d1426fc209ae9384aae15b64e171316bf5c7d1d9e1`）
3. **运行级集成复现**（闭合 crosscheck NOT_VERIFIED 1/2）：集成方在 merge head 代跑 `experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py`（venv=`task-envs/M2-TA3-B-ocr`，EXIT=0）：L1 各页各 conf 档 sfx_count、L2/L3 各参照框 `sfx_box`+`best_sfx_score` 判定字段与入库 raw **逐值一致**（临时输出目录比对，未覆盖入库证据）；权重 `yolo11s-seg.onnx` sha256 pin 运行时校验通过（`_build_engine` 内建校验）。
4. **PLAN mermaid DEXT 节点同步**：表格行已 done 但 mermaid 节点仍标 ready/黄色；本 commit 改为 done 并入绿色 class。

## 未处置项（披露）

- 主仓库 untracked `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/post-merge-pytest.log`：与 close commit 已入库同名文件内容等价（仅行序/编码差异），为编排链集成时的冗余原件副本；按「不擅自 clean」纪律留原样，可随时手动删除。
- 会话身份不可判定（git author 统一），与 crosscheck P1-1 裁决口径一致。

## 移交裁决三问（随集成移交，见报告 §5）

1. **用户裁决①**：是否维持现状+产品侧缓解（方案⑤，短期首选；缓解=BJ 域 sfx 疑似框的 speech 译文标记 UI 切片，另行释放、Qoder 主责）。
2. **用户裁决②**：方案③ chiqui7 fine-tune 的 AGPL 衍生权重许可取舍（比原权重分发争议更尖锐）。
3. **Codex 契约裁决**：region 创建跨 provider 重叠仲裁的契约授权（`core_assembly.py` `_create_detected_region` 无仲裁→召回修复不闭合误路由乱译损害；属契约面，须 Codex 立范围）。
