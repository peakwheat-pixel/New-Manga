# M2-PROD-DETECT-2 集成记录（2026-09-30，acting Codex=编排会话 ZCode 代行）

## 结论

Task `done` @integration merge `9e44fb214dddfe0ca3e89eee817b70da34651f59`（parents `1d876ef7`+`3bef8a15`，无冲突，61 文件 +25,705/-77 全允许路径）。集成后 main 三套件 **401 passed + 1 既有环境性失败**（复现一致）。

## 交付链（branch `agent/zcode/M2-PROD-DETECT-2`，base `f79203eb`，15 commit）

| commit | 内容 |
|---|---|
| `44e70f66` | claim |
| `1cf731ca` | implement（首轮交付：ML 栈进闭包/权重随包/装配回退/GATE 25/25/探针 5/5） |
| `80f7a0cb`→`e0e367c1` | handoff + hygiene + sync（delivery_head=1cf731ca） |
| `dbad2027` | review-fix R1-R12（**含前任 Owner 熔断遗留半成品完成**，message 注明） |
| `6b066a9e` | r1 返修证据重跑（绑定 dbad2027；warn 四文件+分类、PYZ 清单、GATE/探针/pytest） |
| `716997be`→`1c0bc399` | delivery_head 记录 + hygiene（delivery_head=6b066a9e） |
| `a48dbfbd` | **集成修正**（acting Codex 方向）：DSH r2 N1-N6 闭合 + 全量重建绑定 |
| `f8a1ee8f`→`3bef8a15` | 集成轮证据 + hygiene + handoff sync（分支 tip=3bef8a15） |

## Review 轨迹（Owner≠Reviewer≠Integrator 保持）

- **DSH r1** `changes_requested`（2×P1 + 5×P2 + 其余 P3/P4；无 P0 无伪造）：R1 warn 证据载体错位（PyInstaller 四入口共用 warn 文件，留存的是无 ML 的末次 Analysis）、R2 AC5 判 PASS 口径高于证据强度（frozen 无 detect RPC，端到端不可达）→ **acting Codex 裁决**：AC5=PARTIAL；装配期 fail-fast 降级（stderr 警告+detect 期统一 typed fail-closed，与 doctr 对称）；hiddenimports 双保险。报告原字节入库：[doc/reviews/M2-PROD-DETECT-2-dbad2027-dsh-r1.md](../../doc/reviews/M2-PROD-DETECT-2-dbad2027-dsh-r1.md)（sha256 `ee010f9b…`）。
- **Owner review-fix**：R1-R12 全 closed（含前任熔断半成品完成交接——前任遗留 2 个未提交文件经核实方向一致后补完并入新 Owner commit，披露于 commit message）。中途 Owner 子 agent 二次熔断，新子 agent 续接完成。
- **DSH r2** `approved`（可集成；N1-N6 非阻塞）：R1-R12 全实质闭合（四份 warn 归档内容互异证伪「末次覆盖」、构建期断言时机正确、装配新语义与裁决一致、raw-r1 归档内容忠实）；零回潮。报告原字节入库：[doc/reviews/M2-PROD-DETECT-2-dbad2027-dsh-r2.md](../../doc/reviews/M2-PROD-DETECT-2-dbad2027-dsh-r2.md)（sha256 `f213bde6…`）。
- **集成修正 `a48dbfbd`**：N1（警告文本 join bug 修复+整行布局断言）、N3（closure 断言补 `transformers.models.rt_detr_v2` 三名钉）、N2/N4/N5（文档同步）、N6（安装态权重 hash dump 入库）——**全量重建+复跑绑定**（裁决：exe≡集成 commit，不留 src/exe 漂移）。

## 集成终态证据（绑定 `a48dbfbd`，日志在 verification/M2-PROD-DETECT-2/raw/）

| 项 | 结果 |
|---|---|
| onedir | 1,116,381,309 B / 5,550 文件（PyInstaller 330s） |
| NSIS | 460,181,312 B（438.86 MiB）/ sha256 `07d7daa19ac9e3e9e72fbc4b8f2bea708be46805816d9b26f01092a7db1b7b81`（GATE CS-E2 绑定） |
| 构建期闭包断言 | `core_service PYZ carries transformers, transformers.models.rt_detr, transformers.models.rt_detr_v2 (8572 pure modules)` |
| warn 分类 | 958 missing / 12 桶 / 0 unclassified；detect 链硬依赖（torch/torchvision/transformers+rt_detr+rt_detr_v2/safetensors/tokenizers/numpy/cv2/PIL/doctr/h5py/shapely/scipy）**零 missing** |
| GATE | **25/25 PASS**（新 NSIS；M2-AC5 raw 6 文件+gen/schemas 14 文件已还原，专项 diff 空） |
| 探针 | **6/6 PASS**：L1 frozen ping / L2 移权重→stderr 警告+装配 ready（干净单行）→还原消失 / L3 真实推理 EXIT=0 候选=2 稳态 273ms/页（冷启动 6,124ms）/ L4 doctr 启动正常+detect typed PROVIDER_NOT_CONFIGURED |
| 安装态权重 sha256 | 三值=pin（raw/installed-weights-sha256.txt） |
| pytest | providers 289+1 既有环境性失败（test_registry_readiness，base 同败）/ m2_acceptance 35 / core 77；merge 后 main **401+1**（@9e44fb21 复跑） |
| git 层 | 15 commit 链完整；`git diff --check f79203eb..HEAD` EXIT=0；禁改面（tauri.conf.json/run_clean_start_e2e.py/ports/**/两 provider/requirements.txt/experiments/**）专项 diff **空**；权重零 tracked；porcelain 干净 |
| cargo/vitest | 本轮零触碰（r1 轮 44+1ig / 31 留痕，沿用） |

## AC 终判

AC1 构建 ✅ / AC2 权重随包 ✅ / AC3 包内回退解析 ✅（失败语义统一 detect 期+装配期 stderr 警告，两 backend 对称）/ AC4 GATE ✅ 25/25 / **AC5 = PARTIAL**（frozen 进程内 ML import/detect 为 NOT_RUN——frozen 命令面 core.ping/ListBooks/core.shutdown 无 detect RPC，结构性不可达；「发布形态 detect 端到端可用」未验证；已验证=运行时+权重随包就绪+闭包外等价推理）/ AC6 回归 ✅ / AC7 ✅。

## 遗留与后续 slice 候选（登记不释放）

1. **M2-IPC1 命令面扩展 + frozen 进程内 detect 验证**（AC5 PARTIAL 闭合条件，须 Codex 立契约）。
2. docTR 权重发布形态不可用（裁决 3，fail-closed NOT_CONFIGURED+指引；源码 venv 形态不受影响）。
3. 权重更新走 data root 覆盖（运维放置即生效），无 UI 权重管理。
4. `test_registry_readiness` 环境断言遗留（M2-PROD-DETECT-1 已登记）。

Owner branch/worktree 保留于 `3bef8a15`。
