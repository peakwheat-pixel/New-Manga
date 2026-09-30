# M2-PROD-DETECT-1 集成记录（2026-09-30，acting Codex=编排会话 ZCode 代行）

## 结论

Task `done` @integration merge `056617e4488513ae6336a27a3ba44f0c42dfca12`（parents `2fee7d6e`+`320d7955`，无冲突，11 文件 +1693/-33 全允许路径）。

## 交付链（branch `agent/zcode/M2-PROD-DETECT-1`，base `2fee7d6e`）

| commit | 内容 |
|---|---|
| `2e1d3deb` | claim（ready→in_progress） |
| `d7faea39` | implement：detection_manga.py 418 行 + 装配 backend 选择 + requirements 授权 + 3 测试文件 |
| `0b0c9bc7` | AC6/AC7 证据 + Handoff（status in_review） |
| `40d4ab64` | delivery_head 记录 |
| `a016d38c` | review-fix：DSH r1 R1-R10 处置（**delivery_head**，最后实质 commit） |
| `efd134c2` | delivery_head 记录 a016d38c（2 文件 4 行：Task frontmatter + Handoff 锚点注） |
| `320d7955` | 集成修正（acting Codex）：DSH r2 N1-N4 闭合（doc/注释-only，行为零变化） |

## Review 轨迹（Owner≠Reviewer≠Integrator 保持）

- **DSH r1** `approved_with_conditions`（0×P0/P1、2×P2、8×P3/P4）：契约零修订、fail-closed 四纪律同款、C4 推理序列一致、装配 backend 语义、范围纪律、Owner 自报两项（registry_readiness 既有失败 / M2-AC5 raw 还原）全部 PASS。R1-R10 → Owner review-fix `a016d38c` 全 closed。报告原字节入库：[doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r1.md](../../doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r1.md)（sha256 见下表）。
- **DSH r2** `approved`（可集成）：R1-R10 逐条复核全 closed、禁改路径零回潮、计数算术自洽（28/275+35=310=309+1）；新 N1（P3 release note 死链，集成修正必改）+ N2-N4（P4 可选）。报告原字节入库：[doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r2.md](../../doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r2.md)。

## 集成方复跑证据（DSH NOT_VERIFIED 清单处置）

| 项 | 结果 |
|---|---|
| manga 单测+real（@efd134c2） | **28+2 passed，0 skipped**（R8 numpy/字体 skip 守卫未触发，环境在位） |
| providers 全套 | **275 passed + 1 failed**（`test_registry_readiness::test_no_model_runtime_is_installed_in_this_environment` 既有环境性失败，base 同 venv 复现一致） |
| m2_acceptance / core | **35 passed** / **77 passed**（基数保持） |
| merge 后 main 三套件 | **387 passed + 1 既有失败**（275+35+77 算术自洽，@056617e4） |
| 三权重 SHA-256 复算 | model.safetensors `037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d`（171,543,900 B）/ config.json `b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072`（2,320 B）/ preprocessor_config.json `7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca`（470 B）——**逐字一致** |
| git 层 | commit 链 7 节点完整；`git show --stat` 归属拆分（a016d38c=8 文件 review-fix 体 / efd134c2=2 文件记录）与声称一致；`git diff --check 2fee7d6e..320d7955` EXIT=0；禁改路径专项 diff（ports/**、detection_doctr.py、experiments/**、apps/**、packaging/**）为 **0 文件** |
| sidecar GATE 25/25 | 沿用 Owner 轮证据（cleanstart-gate.json @d7faea39）：review-fix 后源码变化仅缺目录错误消息追加指引与 NaN 校验（不在 GATE 场景路径、闭包面 +0 文件不变），**未重建复跑，如实登记为推定** |
| C4 GPU 76.1ms / CPU 315.6ms | 已冻结量级参考（口径注已补入 envelope），不复测 |

## DSH 报告原字节 SHA-256（集成实值）

| 文件 | sha256 | 字节数 |
|---|---|---|
| doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r1.md | `796a6985ab3e84731b41322c03a7cb3a9137e277665029b3e9ba71bbf28f41ae` | 12,713 |
| doc/reviews/M2-PROD-DETECT-1-a016d38c-dsh-r2.md | `250342e3cbe771e66164f9eaf50c810f511be6b28652bb953968760f4632e469` | 12,712 |

## 集成修正 `320d7955` 明细（DSH r2 §回潮）

- **N1（P3，必改）**：Handoff 锚点表 release note 死链 `doc/tasks/M2-PROD-DETECT-1/release-c8eefb4b.md` → `verification/M2-PROD-DETECT-1/release-c8eefb4b.md`。
- **N2（P4）**：Handoff frontmatter `delivery_head` 加消歧注（实现时点值，≠ Task frontmatter 与锚点表语义）。
- **N3（P4）**：Handoff AC1/AC4 行数与计数同步（418→review-fix 后 436 行；27→28 项）。
- **N4（P4）**：`detection_manga.py` docstring「non-finite geometry」收紧为「NaN geometry（±inf 归 clip 既有语义）」。

## 遗留与后续 slice 候选（登记不释放）

1. **发布形态检测器运行时/权重分发**（DSH r1 R1）：发布包内默认 manga backend 的 detect 报 `PROVIDER_DEPENDENCY_MISSING`（docTR 在 base 同样如此）；本 Task 仅源码 venv 形态可用 + PyInstaller 闭包纪律。
2. **manga 权重 fetch/verify 脚本与部署 SOP**（DSH r1 R6）：对照 docTR `fetch_doctr_weights.py` 的 sanctioned 获取+校验路径。
3. **`test_registry_readiness` 环境断言遗留**：断言 venv 无 torch 与 T1.1.1 后事实冲突，修复（条件化/挪舱）另立 slice。
4. 默认 backend=manga 为代理裁决（可撤销）；用户终审披露项：无（本 Task 无用户判定依赖）。

Owner branch/worktree 保留于 `320d7955`。
