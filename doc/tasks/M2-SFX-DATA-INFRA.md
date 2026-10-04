---
id: M2-SFX-DATA-INFRA
title: "SFX 训练数据基础设施：provenance/哈希/去重/分组隔离/标注状态/可恢复 manifest+合成渲染 PoC（T1a；零 src；不等底座）"
kind: feature
status: ready
approval: user_ruling_2026-10-04_训练质量效率优先_许可降权备案
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权）
depends_on: [M2-SFX-DETECT-DOMAIN-EXT-DIAG]
base_commit: 74fa71e9
branch: agent/zcode/M2-SFX-DATA-INFRA
worktree: G:/CODEX/New Manga.worktrees/M2-SFX-DATA-INFRA-zcode
integration_commit: null
---

# M2-SFX-DATA-INFRA：训练数据基础设施（底座无关）

## 来源与目标

V1 训练的数据层地基（Codex 方案第 4/5 点落地）：不管底座选谁，数据生产/隔离/追溯的规矩先冻结并工具化。**只做基础设施+合成 PoC，不做批量生成**（批量数据生产=后续 Task，待 T0 路线定案+标注 schema 冻结）。

## Acceptance Criteria

- [ ] AC1 样本 manifest schema 冻结：每样本记录=图引用（路径+sha256）/框（多边形+类）/标注状态 `complete|partial|pseudo|synthetic`/provenance（来源 case_id 或合成参数或 revision 链）/split 键/created_at。schema 文档+JSON Schema 或 dataclass 双落地。
- [ ] AC2 分组隔离拆分器：按**作品/来源组**划分 train/val/test（同底图及派生样本强制同集合——裁切/增强/合成的派生继承 split 键）；BJ13/14/15 预留「历史挑战集」单列位；划分一次冻结可复现（seed+manifest 锁定）。**test 集对 V1 训练保持不可见**（工具层面隔离：训练数据构建器不得读 test 分组）。
- [ ] AC3 去重与校验：图级感知哈希+框级精确哈希双去重；manifest 原子写+读回校验（可恢复：中断后重跑不产生半写状态——KO-FULLRUN env 事故教训）。
- [ ] AC4 合成渲染 PoC（Codex 第 4 点）：程序渲染管线最小实现——文字图层（毛笔体/艺术字字体）→旋转/透视/弯曲/遮挡**同步作用于图像与标注**（几何与 mask 由渲染参数直接产生=精确 GT，非 AI 生成后标注）；产 ≥20 个 PoC 样本+GT 验证断言（标注与渲染参数互算一致）；AI 整图生成若引入则标 `pseudo` 不入 GT。**标注目标口径冻结**：sfx 实例包络（含遮挡推断）vs 字形像素——定案并写入 schema 文档。
- [ ] AC5 既有资产导入器：BJ13/14/15 七参照框+BJ06 八自证框+ogkalu-sfx-frames 43 region（标 `pseudo`）导入新 schema（含各自质量标注），存量素材一键入册。
- [ ] AC6 零 src；工具 CLI 可运行（--help/自检命令 EXIT=0）；数据本体落外部树 gitignored，Git 只进代码/schema/manifest 摘要与哈希。

## 允许修改范围

`experiments/M2-SFX-DATA-INFRA/**`、`verification/M2-SFX-DATA-INFRA/**`、Task/Handoff。外部数据树（如 `training_data/sfx-v1/`）新建于 gitignored 区。

## 禁止范围

`src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`test_assets/**` 既有 manifest（只读导入）。

## 测试要求

| 场景/AC | 计划步骤 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC2 派生同集合 | 构造同底图派生样本断言 split 键一致 | venv | PASS（9 tests，含挑战集单列/builder 禁 test/组键规则） | red-run.log（先行红）→ green-run.log |
| AC3 中断恢复 | kill 后重跑 manifest 完整 | venv | PASS（4 tests，子进程 replace 前 `os._exit(1)` 注入：旧版完好+重跑完整+tmp 清理） | red-run.log → green-run.log |
| AC4 GT 互算 | 渲染参数↔标注往返一致断言 | venv | PASS（6 tests；forward∘inverse max err 2.27e-13 px；遮挡不裁包络；渲染逐像素确定） | red-run.log → green-run.log |

## 依赖、风险与阻塞

无硬依赖（与 T0/T5a 并行）。风险：合成分布与真实域差距→PoC 阶段做 BJ13 真图对照目检登记（不阻塞，登记差距）。**已登记**：合成横排 AR 2.3–4.5 vs BJ13/14/15 真竖排 0.4–0.5，系统字体非毛笔体——PoC 只声明管线正确性；批量生产需竖排+艺术字体源+页级尺度（见 data-infra-report.md §BJ13 对照）。

## 交付与运行记录

- delivery_head：`ecb39e67ff8eba63bf0586beaa00291b76bc29fc`（链：claim 339f11a0 → red 037a44cf → green 673c3c1f → data ecb39e67；status 保持 in_progress 待 Review）
- 数据产出：82 样本/71 图/206 框入册（导入 7+8+43、合成 24；拆分 challenge 7/train 39/val 31/test 5 @seed 20261004，fingerprint a02fed3d…）；数据本体在 gitignored `training_data/sfx-v1/`，Git 只进摘要 `experiments/M2-SFX-DATA-INFRA/manifest_summary.json`
- 遗留：ogkalu 11/43 空框负证据以 pseudo 空框入册（schema 冻结允许，review 待确认）；val 组样本级不均（12 组切片 8/2/2）
- Handoff：`doc/handoffs/M2-SFX-DATA-INFRA-zcode-delivery-20261004.md`。Review：尚无（待 DeepSeek Harness r1）
- 报告：`verification/M2-SFX-DATA-INFRA/data-infra-report.md`（含 AC 证据、红绿记录、BJ13 对照、验证记录）
