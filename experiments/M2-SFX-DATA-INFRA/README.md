# sfx_data_infra：SFX 训练数据基础设施（M2-SFX-DATA-INFRA / T1a）

底座无关的数据生产/隔离/追溯工具（合同 AC1-AC6）。零新依赖：stdlib + PIL + numpy。
Python：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`。

```bash
cd experiments/M2-SFX-DATA-INFRA
<python> -m sfx_data_infra --help        # EXIT=0
<python> -m sfx_data_infra selfcheck     # 自检 EXIT=0
<python> -m pytest tests/ -q             # 37 tests（r1 返修后含 8 个回归测试）
<python> -m sfx_data_infra pipeline      # 导入+合成+拆分+去重+训练构建+摘要
```

数据本体（渲染 PNG+素材副本+完整 manifest）落 `training_data/sfx-v1/`（gitignored）；
Git 只进代码+schema+`manifest_summary.json`（摘要与哈希）。

## 口径冻结（AC1/AC4 决策记录）

**GT = sfx 实例包络（instance envelope，含遮挡推断），非字形像素 mask。**理由：

1. **下游对齐检测目标**：V1 监督走 4 类检测策略（T0 preflight 已定 sfx 类），检测头
   输出框/多边形；包络与检测目标直接对齐，字形像素 mask 需要分割头与逐像素标注。
2. **存量资产只有框级参考**：BJ13/14/15 参照框（approx_xyxy）、BJ06 自证框
   （detector bbox）、ogkalu 43 region（模型 harvest）都是框级。若 GT 口径=字形像素，
   这 58 个存量样本全部无法入册 GT；包络口径让它们以 `partial`/`pseudo` 分级入册，
   质量分级透明。
3. **合成管线天然产包络**：渲染参数直接 forward 出包络（精确 GT，合同 AC4 核心），
   无需从渲染图反推像素 mask（反推会引入提取误差，破坏"精确 GT"声明）。
4. **遮挡推断语义一致**：人工框被对话框/效果线遮住一半的 sfx 时习惯框全实例；
   合成渲染的遮挡贴片不裁 GT 包络，训练信号与人工习惯一致。

扩展位：schema 保留 `boxes[].occluded` 标记遮挡实例（**r1 P1-4 后已落地**：
合成遮挡样本 `occluded=True`，8 框实测）；若未来引入像素级 mask（合成可产），
以 `glyph_mask_ref` 字段扩展，不破坏包络 GT 口径。

**字体（r1 P2-12 已闭合）**：PoC 接入 TanukiMagic（たぬき油性マジック，OFL 许可，
tanukifont.com）毛笔/手写风字体。获取：`<python> -m sfx_data_infra fetch-fonts`
（= `fetch_fonts.py`，下载 zip→**双 sha256 pin 校验**（zip+解出 ttf，fail-closed 不
静默换源）→落 `training_data/sfx-v1/fonts/` 并写 LICENSE-NOTE.txt；也可手工放字体
或用 env `NEWMANGA_SFX_SYNTH_FONTS` 指目录）。`discover_fonts` 按文件名关键词
（tanuki/brush/fude/kouzan）优先选用；毛笔字体在盘时 PoC 独占使用，否则回退系统
字体（差距登记）。

**标注状态语义**（冻结）：
`complete`=人工像素级精确；`partial`=人工核验但近似框（l3 参照框/BJ06 自证框）；
`pseudo`=模型产出未经人工确认（ogkalu 43 region）；`synthetic`=程序合成精确 GT。
AI 整图生成若后续引入，必须标 `pseudo` 且不入 GT。

## 组键规则（AC2 冻结，`splits.derive_group_key_from_case`）

| 来源 | 组键 | 说明 |
|---|---|---|
| densho810 | `densho810/<卷号>`（vol03_p0056→vol03） | 同卷同作品 |
| Manga109 | `manga109/<作品名>` | 每 case 不同作品 |
| Vasyanator2 | `vasyanator2/<数据集作品id>`（724815_1→724815） | |
| peppercarrot | `peppercarrot/<E番号>`（E04P02→E04） | **同 ep 的 ja/kr 语言版共享图像底图，强制同组防泄漏** |
| 其他 | `other/<sha1(url)[:10]>` | 兜底 |

拆分（method=group-hash-rank-v2）：BJ13/14/15 无条件单列 `challenge`（挑战集，
对训练不可读）；其余组按 `sha256(seed:group)` **排序后按比例切片**（70%/15%/15%，
r1 P2-7 更正：是排序切片，非阈值分桶）。**组级钉扎 pinned**：`synthetic/poc` 显式
钉入 train（r1 P1-3——单一大合成组参与切片会被整组切进 val，train 零合成）。
派生样本（`provenance.type=derived`，`parent_sample_id`）fixpoint 继承父 split；
孤儿 derived（父不在集内）按单组切片，n<4 恒返 train。
划分 lock（seed+method+pinned+fingerprint）写入 manifest；重划需 force=True
（r1 P2-4 修复后 force 真正按新 seed 重划）。
`TrainingSetBuilder` 构造期丢弃 test/challenge 且禁止其进入 allowlist——API 表面
不存在任何取回 test/challenge 的通道；并默认排除 `provenance.negative=true` 的
空框负样本（r1 P1-2：是否使用弱负样本由 T1b 显式决策，`exclude_negative=False`
为显式开启通道）。
**登记（r1 P2-10 裁定）**：challenge 单列优先于组原子性，同组余量照常分桶
（densho810/vol03 余量在 train）——challenge 评测存在同卷上下文泄漏风险，仅用于
挑战对照，不得用于泛化声明。**登记（r1 P2-11）**：当前 test 集为 4 个 ogkalu
pseudo 样本，无人工 GT，评估价值有限；引入人工可核验 test 来源属 T1b。

## 中断恢复纪律（AC3，KO-FULLRUN env 事故教训）

manifest 写入=同目录 tmp（pid 后缀）→flush+fsync→旧文件移 .bak→os.replace 原子生效
→读回 json 校验（load_manifest 再逐样本 schema 校验）。三态恢复（r1 P2-6 修正）：
崩溃在 tmp 阶段→主路径仍是旧完整版；崩溃在两次 replace 之间→主路径短暂缺失，
`load_manifest` 自动回退 .bak 上一完整版本；残留 tmp 由 `cleanup_stale_tmp` 在
重跑前清理。

## 资产与素材根（AC5，只读）

- `verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l3-reference-crops.json`：BJ13/14/15 七参照框 → `partial`
- `verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json`：8 个 sfx region（自证框）→ `partial`；导入时对账 qual 记录的 source_sha256
- `experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json`：43 region → `pseudo`
- 素材根探测顺序：本 worktree → E2E-MATERIAL worktree（BJ13/14/15 页）→ TA2B worktree（BJ06 页）；
  可用 env `SFX_DATA_ASSET_ROOTS` 覆盖。素材只读复制进外部树 `assets/`。
