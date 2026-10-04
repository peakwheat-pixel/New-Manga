已完成 r1 静态审查（沙箱内 `pwsh` 不可用，全部结论基于文件与产物静态核对；命令级验证列入缺口）。

---

# 一、AC1–AC6 逐项核实结论

| AC | 静态结论 | 关键核对结果 |
|---|---|---|
| AC1 schema 双落地 + 口径冻结 | **基本成立** | `schema.json` 与 `make_json_schema()` 逐字段手工比对**完全一致**（含 `additionalProperties:false`、枚举、required）；口径 4 条理由见 `README.md:17-38`、`schema.py:1-5`。缺口：JSON Schema 未表达"空框仅 pseudo"，`boxes` description 未写"含遮挡推断"，`occluded` 字段在真实数据中**恒为 False**（见 P1-4） |
| AC2 组键隔离 + challenge 单列 + test 不可见 | **部分成立** | 组键规则与 `cases.json` 实测吻合（K01=724815…K10=730656，densho810→vol03，peppercarrot→E04）；`manifest.full.json` 行 51/98/145/192/239/286/333 共 **7 个 challenge**；`manifest.train.json` grep `"split": "(test\|challenge)"` **零匹配**（产物级不可见成立）。缺陷：`force` 失效、fingerprint 时机、challenge 拆散同组、test 全 pseudo |
| AC3 双去重 + 原子写可恢复 | **部分成立** | crash 注入测试真实（`os.replace` 前置 `os._exit(1)`）；tmp/bak/replace 语义正确。缺陷：**perceptual 分支不可达**（P1-1）、主路径"第三态"无恢复（P2-6） |
| AC4 合成 24 样本 GT 互算 | **成立（含登记差距）** | `default_poc_params(count=24)`；point/pixel 共几何函数；`forward∘inverse` 2.27e-13 由 `cli.py:197-198` 产出；arc 离散 vs 连续差 ≤0.5px 与容差一致。字体非毛笔体已登记 |
| AC5 存量导入 7+8+43 | **静态完全核实** | `l3-reference-crops.json` 实测 BJ13(2)+BJ14(3)+BJ15(2)=**7 框**；`qual-BJ06.json` 实测 `region_type=="sfx"`=**8 个**、`source_sha256=b06c9d7d…` 与 `manifest.train.json:12` 页图 sha **逐字节一致**；`ogkalu-sfx-frames.json` 实测 **43 region / 167 box_xyxy / 11 空 detections**，与 `manifest_summary.json` 全部吻合 |
| AC6 零 src + CLI + 数据出 Git | **基本成立** | `sfx_data_infra/*` 仅 import stdlib+PIL+numpy（`importers.py` 只**读** `test_assets`/`verification`/`experiments` 的 JSON）；`help-run.log`/`selfcheck-run.log` 齐备；`training_data/sfx-v1/` 在盘且 `.gitignore:13` 覆盖。缺陷：`.gitignore` 超授权范围、`summary` 子命令崩溃 |

**额外静态闭合验证**（用 manifest 行号反推 split 组成）：`manifest.full.json` 中 val 行 4653–4919（7 个）+ 6172–12967（24 个）=31；train 39、test 5（1554–1907）、challenge 7。**合成 24 样本全部落 val，train 内合成样本数 = 0**。

---

# 二、问题清单（分级）

## P1（必须返修）

- `[P1] dedup.py:26-28,66-78 + hash.py:28-37` **感知去重分支是死代码**：`_box_set_key` 的每个元素由 `box_exact_hash(..., s.image.sha256)` 生成，故 `bk2 == bkey` ⟹ 图 sha 相同 ⟹ 命中同一 `(sha,bkey)` 并被 `seen_exact` 的 `continue` 提前截走；重压缩/缩放（sha 不同）永远无法满足 `bk2 == bkey`。AC3"图级感知哈希 + 框级精确哈希**双**去重"实际只有一条路径，`summary.dedup.perceptual_pairs` 恒为 0 不是"通过"而是"不可达"；`test_dedup.py:48` 命名含 perceptual 但只断言 exact。 → 让框指纹去掉 image sha（图级独立比较），或在 `find_duplicates` 传入外部 sha 映射并用"图不同 + 框几何相同 + dhash 近似"判定；补一条真正触发 perceptual 的测试。
- `[P1] splits.py:140-149 + cli.py:257-261` **TrainingSetBuilder 只按 split 过滤，不过滤 `annotation_status`/`provenance.negative`**，导致 43 个 pseudo（其中 **10 个空框负样本**在 `manifest.train.json`：行 546/1135/1163/2585/3146/3328/3356/3384/4308/4336）与 8 个遮挡/近似框一起作为训练 GT 进入 train/val。与 AC4/README"pseudo 不入 GT"、及报告"可加一行开关过滤"的表述冲突。 → builder 增加 `annotation_status`/`exclude_negative` 参数（默认排除空框负样本），并在 manifest 摘要中记录实际纳入状态分布。
- `[P1] cli.py:220 + report:68` **合成样本全落 val、train 零合成**：`group="synthetic/poc"` 单组经 rank 切片整组进 val（24/31=77%），train 39 全为导入样本；报告写"合成样本…只入 train/val 作辅助监督"与产物直接矛盾（辅助监督未发生在 train）。 → 将 `synthetic/poc` 显式钉入 train（或拆分为多个合成子组再切片），并在报告中如实记录合成样本的落点。
- `[P1] cli.py:204（对照 synth.py:345-352）` **遮挡样本 `occluded` 未落地**：8 个 `i%3==0` 样本 `p.occlusion is not None`，但 `BoxAnnotation(...)` 未传 `occluded`，默认 False；README:32 声称"schema 保留 `boxes[].occluded` 标记遮挡实例"与实际数据矛盾（裁决①的口径在字段层失效）。 → `occluded=p.occlusion is not None`，并加断言（含遮挡样本必须 occluded=True）。

## P2（条件可关闭 / 需裁定）

- `[P2] .gitignore:12-13` `.gitignore` **不在 Task 允许修改范围**（`doc/tasks/…:35` 只列 experiments/verification/Task-Handoff），handoff:17 却称"全部在允许范围内"。 → 请 Codex 追认该越界，或改由 Task 显式授权后保留。
- `[P2] cli.py:425-439 + 304-306` `summary` 子命令必然 `KeyError: 'synth_count'`（`cmd_summary` 传 `synth_info={}`，`build_summary` 直接下标）。 → 给 `build_summary` 缺省值或让 `cmd_summary` 从盘上重算 synth/dedup 信息；补 CLI 冒烟测试覆盖全部子命令。
- `[P2] cli.py:409-414` `cmd_dedup` 用 `write_manifest(kept)` 回写 `manifest.full.json`，**抹掉 `seed` 与 `lock`（fingerprint/challenge_case_ids）**，破坏"划分一次冻结可复现"。 → 回写时透传原容器 `seed`/`lock`。
- `[P2] splits.py:77-83,93-99` `force=True` 语义失效：跳过校验后仍只处理 `split=="unassigned"` 的样本，故 `cmd_split --seed <新值>` **不会重划**（除 challenge 外全部保持旧 split）。 → force 时先重置非 challenge 样本为 `unassigned` 再分配。
- `[P2] cli.py:345-362` `split_info.fingerprint` 在 **dedup 之前**计算，而 `manifest.full.json` 写的是 dedup 后的样本集；一旦有重复被丢弃，`lock.fingerprint` 与产物不一致（当前 dropped=0 才恰好自洽，handoff 的"重放一致"是脆弱证据）。 → 先 dedup 后 split，或以最终 kept 集重算 fingerprint。
- `[P2] atomicio.py:43-46,96-107 + README:59-61` 存在**第三态**：`os.replace(path,bak)` 之后、`os.replace(tmp,path)` 之前崩溃时主路径**不存在**（旧版在 `.bak`），而 `cleanup_stale_tmp` 只删 `*.tmp`、无任何 bak 恢复路径，`load_manifest` 直接 `ManifestValidationError`；"主路径非旧即新"表述不准。 → `load_manifest` 在 path 缺失时回退 `.bak`（或 `cleanup_stale_tmp` 增加 bak 回退），并修正文档。
- `[P2] README:50-51 + splits.py:6-8` 文档描述的分桶算法（`sha256(seed:group)` 前 8 字节阈值 <0.70/<0.85）与实现 `_ranked_group_split`（**排序后按索引比例切片**，`method=group-hash-rank-v2`）不符，直接影响"可复现口径"的文档可信度。 → 文档改为 rank 切片描述。
- `[P2] report:63-64` val 组成写错："synthetic/poc **22** + vasyanator2/**641253** 9"；实测为 `synthetic/poc 24` + `vasyanator2/701535 7`（641253 是 9 样本组且落 **train**）。该行是裁决④的唯一书面依据，错误会误导集成评估。 → 据 manifest 重写。
- `[P2] report:17 + importers.py:199-206` 报告称"原始 cls/**conf**/harvest 阈值入 provenance"，实测只写 `original_classes`/`harvest_threshold`/`model`/`weights_sha256`，**167 个框的 `conf`/`conf_ge_primary` 被丢弃**（这正是 harvest 0.25 vs primary 0.5 的质量分级依据）。 → 至少保留 `conf` 或 `conf_ge_primary` 统计，或修正报告措辞。
- `[P2] splits.py:86-89 + manifest.full.json:51,381` **challenge 优先级破坏组原子性**：`densho810/vol03` 同组被拆成 challenge 7 + train 8（BJ06 同卷相邻页）。`test_groups_are_atomic…` 用 `if s.split=="challenge": continue` 规避了该检查，challenge 评测分数存在同卷泄漏抬升风险。 → 明文登记"challenge 优先于组原子性"，或把 BJ06 也移出 train（同卷整卷隔离）。
- `[P2] manifest.full.json:1554-1907` **test 集构成近乎无评估价值**：5 个样本全部为 ogkalu pseudo（K01×4 + K02×1，含 1 个空框），与 train 的大量 ogkalu 同源同工序，且无任何人工 GT。 → 在报告中登记，或 T1b 重划 test（引入人工可核验来源）。
- `[P2] synth.py:33-42 + report:46` AC4 明文要求的"毛笔体/艺术字字体"未实现（退化为 meiryo/msgothic 等系统字体），PoC 只声明管线正确性。 → 需 Codex 裁定 AC4 是否按"管线正确性"验收并转 T1b；建议在 Task AC4 勾选说明中显式降级。
- `[P2] cli.py:437（无 `import_info` 语义）` 与 `manifest_summary.json:6` 摘要写入本机绝对路径 `data_root_gitignored`。 → 入库摘要避免本机绝对路径（改相对或省略）。

## P3（建议）

- `[P3] README:10` "27 tests" 与实测 **29**（`grep ^def test_` = 4+6+6+8+5）不符（27 是 red 时数字）。
- `[P3] report:33,35` 测试分项计数错误：AC2 声称 9 tests（实际 8）、AC4 声称 6（实际 5）、AC4 red 声称"3 FAILED+4 ERROR"（`red-run.log:487` 为 **19 failed / 4 passed / 4 errors**，其中 synth 仅 1 FAILED+4 ERROR）。
- `[P3] handoff:17,20` "25 文件"与任务清单 29 不符，且遗漏 `help-run.log`、`selfcheck-run.log`、`tests/__init__.py`、`tests/conftest.py`；"red 三组断言先行"与 red 时已跑 5 文件 27 测试不符。
- `[P3] doc/tasks/M2-SFX-DATA-INFRA.md:5,12,55` frontmatter `status: ready` 与正文"status 保持 in_progress"自相矛盾；`base_commit: 74fa71e9` 与 handoff/Task 正文 `4c12e8af` 不一致；`depends_on` 与"无硬依赖"表述冲突。
- `[P3] schema.json:52-54` `boxes` description 未写"含遮挡推断"，且 JSON Schema 不表达"空框仅 pseudo"约束（仅运行时 dataclass 强制）；`created_at` 无 `minLength`（dataclass 强制非空）——双落地存在轻微语义差。
- `[P3] cli.py:17 / schema.py:9,14 / splits.py:26 / dedup.py:33` 未使用导入与重复常量（`copy`、`field`、`SPLIT_CLASSES` 双定义、`image_sha_by_sample` 参数从未使用）。
- `[P3] cli.py:190-198,240-244 + synth.py:164-214` 每点调用都重算 `anchor_points`/`_rotate_stage`/SVD，重复开销明显；`step_dedup` 的 loader 未 `close()`。
- `[P3] importers.py:25-29,34-37` 素材根与证据 JSON 硬编码本机 worktree 绝对路径（env 仅覆盖素材根），跨机器/CI 不可复现；`discover_fonts` 硬编码 `C:\Windows\Fonts`（非 Windows 直接 RuntimeError）。
- `[P3] 粒度一致性` 同一 manifest 内两种样本粒度：l3/BJ06 一框一样本（4 页被引用 15 次）vs ogkalu 一样本多框；建议在 schema 文档冻结"样本=单实例包络"粒度。
- `[P3] splits.py:114-119` 孤儿 derived 的 fallback `_ranked_group_split([g],seed)` 因 `n<4` **恒返 train**，应在文档中登记为"孤儿派生一律 train"。
- `[P3] test_synth_gt_roundtrip.py:26-43,100-105` 断言 A 用 `np.roll` 做邻域膨胀（有环绕假阳）+ `canvas=(640,640)` 偏移仅在无负坐标时成立；断言 C2 是同义反复（`forward` 根本不读 `occlusion`），不能证明口径语义。
- `[P3] atomicio.py:47-50 + README:60` 声称"读回 json+**schema** 校验"，实现只 `json.loads`（schema 校验缺失，失败类型也与 docstring 不符）。
- `[P3] .gitignore` 冻结的摘要哈希会因后续 `split`/`dedup`/`build-train` 子命令改写 manifest 而 stale（无一致性检查）。

---

# 三、四项重点裁决（独立意见）

**① GT 口径 = 实例包络（含遮挡推断）——同意（附条件）。**
理由链成立：V1 走 4 类检测头（包络与检测目标对齐）、58 个存量资产只有框级证据（若口径=字形像素则全部出局）、合成管线天然 forward 出包络（避免反推误差）、人工标注习惯确实"框全实例"。README 的 4 条理由与 schema docstring 已写清，属可接受的口径决策。**但落地不完整**：`boxes[].occluded` 在合成 8 个遮挡样本上恒为 False（P1-4），JSON Schema 的 `boxes` description 未含"含遮挡推断"，也没有 `gt_scope` 之类字段把口径冻结在机器可读层。因此建议：口径**批准**，但需补 `occluded` 落地 + schema description，否则口径只存在于 README 而非数据。

**② ogkalu 11 个空 detections 以空框 pseudo 入册——入册同意，直接进训练反对。**
作为"证据保全"入册是合理的（43/43 全量对齐 AC5，`provenance.negative=True` 可追溯，schema 已允许 pseudo 空框）。但把"某 crop 在 0.25 灵敏度下无检出"当作负样本送进训练存在**假负样本风险**：这些 crop 本身是从 sfx region 裁出的（crop 内应有字形），空框只说明模型在 crop 内部失效，不说明"此处无 sfx"；叠加 `TrainingSetBuilder` 不过滤状态（P1-2），10 个空框样本会以"无目标"信号进入 train/val。建议：manifest 入册保留，但 builder 默认排除 `provenance.negative` 样本（或单列 `weak_negative` 分组），并让"是否使用弱负样本"成为 T1b 的显式决策；否则请 Codex 明确签署"接受弱负样本"。

**③ dedup 判重 = 同图 + 同框集合——语义同意，实现反对。**
"一页多实例 = 同图不同框 = 合法多样本"是正确的语义，也是首版"同图误杀"修复的正确方向；框哈希含 cls/text/坐标 0.1px 量化，误杀合法相似样本的概率低（漏杀重复标注的概率反而更高，属可接受）。**但"双去重"名不符实**：`box_exact_pairs` 与 `exact_pairs` 在同一分支同时 append（永不独立触发），而 perceptual 分支因 bkey 内嵌 image sha 而**数学上不可达**（P1-1）。所以当前实现只有"图 sha + 框集"单一判重维度；AC3 的"图级感知哈希"需要重写而非调参，并补一条真实触发 perceptual 的测试。

**④ val 组样本级不均（val 31）——反对现状，需决策而非容忍。**
问题不只是"组数 2、样本 31"，而是**成因与后果**：`synthetic/poc` 单组 24 样本整组落 val，造成 val 77% 为域外合成样本、train **零**合成样本，与 report:68"只入 train/val 作辅助监督"直接矛盾。若 val 被用于早停/选型，其信号主要来自合成域，会对 V1 训练有效性产生误导；若仅作辅助监督，则合成样本一个都没进 train，等于没起作用。这不是"批量入册后自然缓解"的问题，而是 split 策略对"单一大合成组"缺少处理。建议 r2 把 `synthetic/poc` 显式钉入 train（或拆成多个合成子组参与切片），val 保留真实来源；在组数≥30 前，报告不得以"辅助监督"描述合成样本的作用。另：`val = synthetic/poc(24) + vasyanator2/701535(7)`，report:63-64 的"22 + 641253(9)"须更正。

---

# 四、Verdict

**changes_requested**

（4 项 P1 需在 r2 修复：perceptual 去重不可达、pseudo/空框样本无过滤进训练、合成样本全落 val 与声明矛盾、遮挡样本 `occluded` 未落地；P2 项可在 r2 一并处理或由 Codex 逐条裁定关闭。无 P0 阻塞级事实错误：7+8+43、82/71/206、fingerprint、BJ06 sha 对账、test/challenge 产物隔离均已静态核实成立。）

---

# 五、执行验证缺口（我无法静态核实，需集成方代跑）

1. **本沙箱 `pwsh` 不可用**（每次均 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），因此**未执行任何命令**，以下全部需代跑：
2. `pytest tests/ -q` → 预期 **29 passed**（当前 `green-run.log` 仅 2 行汇总，无分文件明细，无法交叉核对）。
3. `python -m sfx_data_infra selfcheck` / `--help` → 预期 EXIT=0（仅有既有日志，非我复跑）。
4. `python -m sfx_data_infra pipeline --data-root <tmp> --summary-out <tmp>` → 复现 fingerprint `a02fed3d…`；并请**补跑 `summary` / `dedup` / `split --seed 其它值` 子命令**，验证我指出的三处缺陷（KeyError、lock 丢失、force 失效）。
5. `manifest.full.json` sha256 `095a3c59…`、`manifest.train.json` sha256 `17129854…` 的**实际哈希核对**（我只能读到摘要里声明的值）。
6. 用盘上 manifest 重放 `assign_splits` 比对 fingerprint（当前 `dropped=0` 才自洽，请在有重复样本时再验）。
7. `git diff 4c12e8af..ecb39e67 --stat` 核实"零触碰 `src/**`、`tests/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、`test_assets/**`"，并确认 `.gitignore` 是否唯一越界；以及 `git check-ignore training_data/sfx-v1/manifest.full.json`。
8. 合成渲染"逐像素确定性"、跨机器字体/素材根可用性（当前依赖 `C:\Windows\Fonts` 与本机 worktree 路径）。
9. **建议下一步（基于当前仓库状态）**：把本 r1 结论回传 Codex（Integrator）裁定 `.gitignore` 授权、AC4 字体降级验收、weak-negative 使用策略三项；随后由 Owner（ZCode）按 P1-1~P1-4 出具 r2 补丁与红绿证据，再进入集成验证。
