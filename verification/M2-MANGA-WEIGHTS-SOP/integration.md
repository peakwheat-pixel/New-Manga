# M2-MANGA-WEIGHTS-SOP 集成记录（2026-10-01，acting Codex）

## 结论

Task `done` @integration merge `853fc911`（preceded by gitignore guard `d401bed2`；branch `agent/zcode/M2-MANGA-WEIGHTS-SOP`，base `46f079e8`，分支 tip=集成修正 `4723bfb4`）。

## 交付链

`d37ed6f0`(claim) → `1019ed6b`(implement：fetch_manga_weights.py + WEIGHTS-SOP.md) → `8fa23edd`(handoff) → `b0dd843c`(review-fix DSH r1 R-A1..A10) → `4723bfb4`(集成修正：DSH r2 P4-1/P4-2，doc-only)。

## Review 轨迹

- DSH r1 [approved_with_conditions](../../doc/reviews/M2-MANGA-WEIGHTS-SOP-b0dd843c-dsh-r1.md)（3×P2：R-A1 校验时机在 replace 之后+文案相反、R-A2 SOP 场景 B 路径错、R-A3 drift 静默跳过；sha256 `d583c9c5…`）→ Owner review-fix `b0dd843c`（R-A1..A10 全 closed，错 pin 反证 PASS）→ DSH r2 [approved](../../doc/reviews/M2-MANGA-WEIGHTS-SOP-b0dd843c-dsh-r2.md)（P4 残留转集成；sha256 `fc03f720…`）→ 集成修正 `4723bfb4`（P4-1 措辞同步/P4-2 delivery_head）。
- 注：本报告与 T3 共用一轮 DSH 会话（两独立 verdict 节），B 侧结论见同文件 Task B 节。

## 集成方复跑门禁（2026-10-01，@`b0dd843c` 实测）

| 项 | 结果 |
|---|---|
| `--verify-only --dest <C4 快照>` | **EXIT=0**，三 pin 全符（037930a8…/b6d70793…/7e9e2245…） |
| drift 非空目录无 `--force` | **EXIT=2**（消息含 prefer a fresh empty directory） |
| 错 pin 反证（真 revision+0×64 pin，小文件走代理） | **rc=1、target 逐字节原样、.part 零残留**、文案「mismatched bytes were DELETED and nothing was installed … is unchanged」正确 |
| 真实 HF 下载 3/3（含 171,543,900B） | Owner 轮两轮实测（代理 127.0.0.1:7890；pyc 佐证 stub 驱动运行）——集成轮未重跑大文件下载，如实登记 |
| git 层 | `git diff --check 46f079e8..4723bfb4` EXIT=0；4 文件域；porcelain 干净 |

## 集成方动作

- `.gitignore` 权重护栏窄规则（`*.safetensors`/`*.pt`/`*.onnx`）@`d401bed2`（R-A9 转办闭合）。
- DSH r2 P4-1/P4-2 @`4723bfb4`。

## 遗留

- 脚本 pin 与 `detection_manga.py` 手工镜像（re-pin 须同步两处+SOP §0/§5——流程已在 SOP 写死，无自动一致性测试）。
- 真实断网下 `.part` 中断恢复未实测（清理逻辑由反证覆盖）。

Owner branch/worktree 保留于 `4723bfb4`。
