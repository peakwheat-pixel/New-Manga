# M2-SFX-CORRECTION-EXPORTER：纠错样本导出器（T5c）

只读扫描 SQLite `regions`+`region_revisions` revision 链的类型纠错事件（AC1），
经资格判定（AC3）后以 T1a `sfx-data-infra/sample@1` manifest + YOLO seg 双形态
导出（AC4），产物可被 T1a `sfx_data_infra` 直接消费（AC6）。

- Task 合同：`doc/tasks/M2-SFX-CORRECTION-EXPORTER.md`
- 判据来源：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` rev 1.4 §5.4（改标/撤销/
  origin/review_state 语义）
- 纪律：零 src 修改；SQLite 只读（`mode=ro` + `PRAGMA query_only=ON`，镜像
  `src/infrastructure/sqlite/connection.py:367-374`）；依赖零新增（stdlib + 既有
  PIL + 复用 T1a `sfx_data_infra`）。

## 用法

```bash
# 在本目录（experiments/M2-SFX-CORRECTION-EXPORTER）下，dev venv=T1.1.1-impl-py312
python -m sfx_correction_exporter --help
python -m sfx_correction_exporter selfcheck
python -m sfx_correction_exporter export \
  --db  "C:/Users/49745/AppData/Roaming/com.newmanga.m2rc1.desktop/data/library.db" \
  --out training_data/sfx-corrections \
  --registry training_data/sfx-v1/manifest.full.json \  # 可选：T1a 已册 manifest（去重+组继承）
  --yolo-scope main                                     # YOLO seg 范围：main（默认，仅正集）| all
```

### --yolo-scope（DSH r1 P2-1）

YOLO seg 树（训练直读树）默认只含正集：`main` = 仅 `annotation_status=complete`
样本入 `labels/<split>/`；辅助集（partial）不混入，避免未经几何确认的样本静默
进入训练集。`--yolo-scope all` 显式把辅助集混入 YOLO 树（正集+辅助集全量，
与 manifest 双册无关——manifest 始终双册输出，scope 只影响 YOLO 树内容），
选择混入由调用方显式 opt-in 并在 export-summary 的 `export.yolo_scope` 登记。

输出（`training_data/` 整树 gitignored，Git 只进摘要）：

```
training_data/sfx-corrections/
├── manifest.json            # 正集：annotation_status=complete
├── manifest-auxiliary.json  # 辅助集：annotation_status=partial（可选入训练）
├── dataset.yaml             # names 顺序逐字 = SFX_CLASS_MAP（T0 P3-6 硬约束）
├── images/<split>/...       # 页图副本
└── labels/<split>/...       # YOLO seg：<sfx_id> x1 y1 x2 y2 ...（归一化）
```

## 冻结语义（AC1 识别规则）

判据全部锚定契约 §5.4 与生产写路径（`src/application/editing/service.py:130-134`
max+1 单调 revision_no；`:222-241` `_commit_user_or_raise`；`:550-572` restore）：

- **事件**：链上第 j≥2 笔 `origin=user` revision，`snapshot.region_type` ≠ 前笔。
  首笔是创建不是纠错；`origin=machine/imported` 的类型变化不是纠错（计数上报）；
  `origin=restored` 的类型回退是撤销动作本身，不构成事件。
- **存活 (a) 未被撤销**：其后不存在 `origin=restored` 且 `region_type == type_before`
  的 revision（显式回退到改标前类型即撤销——被撤销纠错不入册）。
- **存活 (b) 未被改判**：链末笔 `region_type == type_after`（用户 settled 终判与
  该事件一致；被后续改标取代的中间判断不作 GT）。
- 排除：纯几何/文本/reading_order 用户编辑（类型未变，天然非事件）；软删除
  region 整链跳过（计数上报）。

## 冻结资格阈值（AC3，`eligibility.CONSTANTS`）

| 规则 | 冻结值 |
|---|---|
| `GEOMETRY_CONFIRM_RULE` | v1：complete ⟺ 链首笔 origin=user（用户自建）或链上存在用户几何编辑；否则 partial（机器检出几何未被用户触碰）。读法登记（DSH r1 P3-2）：restore 至已改标 revision 读作用户背书该 revision 几何（用户在 restore 选项中主动回退到该状态），但现实现不单独以 restore 背书触发 complete——`geometry_confidence` 判别用例钉住现读法=partial，语义重裁定留 T2 |
| `PARTIAL_ROUTING` | partial 不入正集，落 `manifest-auxiliary.json` 辅助集（训练侧可选入） |
| `DEDUP_LEVEL` | exact+box-exact（复用 T1a `find_duplicates`，`image_loader=None`；感知层级不启用——跨集感知比对需外部素材树，纠错样本位于用户库页） |
| `LICENSE_RULE` | `user_ruling_2026-10-04_训练质量效率优先_许可降权备案: 全备案不阻断`（每样本携带 license 备案块，永不因许可丢样本） |
| `EXPORTABLE_TARGET` | 仅 sfx 向纠错（T1a `BOX_CLASSES=("sfx",)`）；非 sfx 向事件照实识别、资格层排除计数 |
| `SURVIVAL_UNDONE_RULE` | v1 保守读法（DSH r1 P3-1）：链上其后任一 origin=restored 且 region_type==type_before 即判撤销；撤销后经 restore 复活已改标 revision 的终态纠错因此被保守丢弃——**保守误杀，非契约 §5.4 唯一读法**（fixture rgO2 显式钉住该期望，语义重裁定留 T2） |

partial 映射理由（DSH r1 P3-3）：partial 判据 = 「类型人工确认（用户改标 revision，
origin=user）+ 几何机器产出（未被用户触碰）」。不落 T1a `pseudo`（模型产出、
完全无人工确认）的理由：改标本身是用户的显式类型判断，样本对类型监督信号有效，
只是几何未经用户确认——故以 `partial` 落辅助集保留信号，既不丢弃也不冒充
complete；与 `pseudo`（连类型都无人工背书）保持分界。

## 登记的设计取舍

- **provenance.type=asset_case**（非 derived）：T1a `derived` 触发 split 继承语义
  （parent_sample_id 缺失 → 孤儿派生全落 train，破坏分组隔离）；user library 页即
  素材案例，以 `source=revision_chain_correction` 标记区分。
- **组键**：cases.json 映射成功 → T1a `derive_group_key_from_case`（与已册样本同组
  同 split，隔离继承）；否则 `user-library/<book_id>`。页映射判据 = source_filename
  茎 == `f"{source_id}.png"` 茎（复刻 T1a `importers.page_filename_for_case`）。
- **框几何取链末笔 settled 状态**：存活规则 (b) 保证终态类型 == 事件 type_after，
  settled 几何 + settled 类型 = 一致 GT；改标 revision 几何与前笔一致（契约 §5.4）。
  provenance 另登记 `geometry_from_revision_no`（settled 几何来源 revision，
  DSH r1 P4-5）。
- **polygon<4 点（空/三点）回退 bbox 四角**并在 `quality_note` 登记（T1a
  BoxAnnotation 要求 ≥4 点）。bbox 按**生产 xywh 语义**（`BBox.as_tuple()` =
  `(x, y, width, height)`，entities.py:72-73）展开四角，复用 T1a
  `importers.bbox_to_polygon`（DSH r1 P1-1 修正：旧实现误把 xywh 当 xyxy 读；
  `tests/test_samples.py` 的 rgN 重算期望 + rgO 判别用例钉住，旧读法下必红）。
- **乐观冲突角例不可观测**（DSH r1 P4-3 登记于报告 §5）：expected_revision
  拒绝笔由写入端保证不落 revision 行（不产生事件），导出端无从也无需观测。
- **已登记的保守角例**：撤销后经 restore 复活已改标 revision 的终态纠错——
  判据 (a) 保守误杀（见 `SURVIVAL_UNDONE_RULE`，fixture rgO2 显式钉住期望=
  不存活）；DSH r1 P3-2 的 restore 背书几何读法登记见 `GEOMETRY_CONFIRM_RULE`
  （rgO3 判别用例钉住现读法）。T5b 集成后的真库冒烟由集成方补跑。

## fixture（15 region 矩阵）

`fixture.build_fixture_db`：生产冻结 DDL（v1–v4 原样执行）+ 混合链（基本纠错/
被撤销/纯几何/纯文本/机器改标/二次改标取代/撤销再纠错/用户自建/几何编辑后
restore/纯顺序/非 sfx 向/软删除/BJ13 映射页/纯 bbox/撤销后 restore 复活角例）。
几何全部页内（64×48，DSH r1 P4-4）且 bbox 为生产 xywh 语义。场景与逐条期望见
`tests/test_scanner.py` 模块 docstring；红绿证据在
`verification/M2-SFX-CORRECTION-EXPORTER/evidence/`。
