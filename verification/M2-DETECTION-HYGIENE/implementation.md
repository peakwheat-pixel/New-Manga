# M2-DETECTION-HYGIENE 实现记录（主会话直接实现，2026-10-02）

## AC1 逐项

1. **TILING R1/R3**（detection_manga.py）：`_tiling_config` 四处 `if raw and raw.strip():` → `if raw is not None:`——空/空白 env 值从静默回落改为 typed 拒绝（`float("")`/`int("")` → ValueError 含 env 名，never-silent-default）；docstring 登记 R1 语义选择：config 在每次 detect 读取（触发判定需 trigger_ratio）→ 非法 env 值对所有页 fail-fast=与 `NEWMANGA_SFX_CONF_THRESHOLD` 同语义，「普通页零变化」主张限定为 env 未设置或合法时。
2. **BACKFILL N1**（service.py）：backfill 规划期 `except PipelineError` 收窄为 `error.code in {"TARGET_DELETED","TARGET_NOT_FOUND"}` 才跳过，其他 PipelineError 重 raise（未来新增错误码不再被静默吞掉）。
3. **SETTINGS-IPC R7/R8**：本分支 base=24a89d7d 不含 SETTINGS-IPC merge（其文件在此不存在）——**由集成方在 main 侧收口时顺手闭合**（两行注释/计数更正），本 Task 登记。

## 测试

- tiling：parametrize 扩展 +10 用例（四 env × 空/空白）——修改前红（回落无 raise）、修改后绿（typed）。
- BACKFILL N1：**桩测试降级登记**——运行时桩注入（monkeypatch service._catalog.current）与装配闭包交互产生不可靠结果（部分调用点经闭包捕获不受属性 patch 影响，两臂行为矛盾），收窄语义改由 code review + 既有 F 系回归保证；两个桩测试已移除并在此登记原因。
- 回归：pytest 三套件 **611 passed+1 skipped 0 failed**（603+8 tiling 空白用例）；cargo **46+1ig**；vitest **49**（前端零改动）；tsc 不涉及。

## 环境（fresh worktree 搭建记录）

build_sidecar.ps1（sidecar）+ npm install + npm run build（frontend/dist）——README §2.0 两前置；build.rs fail-closed 与 generate_context! 编译期检查均按设计工作。


## r2 P0 事故登记（同款错误第二次发生，流程修正）

r2 抓住 P0：r1-R1 的 lazy split 被红态归档的 `git checkout HEAD -- <file>` 恢复操作**抹掉**（HEAD 此刻=implement commit，恢复即回到无修复版本），且 `git add -A` 时该文件与 HEAD 零 diff → 修复从 02b6d2a2 **零痕迹消失**——与 BACKFILL R9 红态归档抹掉 R6/R7 修改是**同一失败模式第二次发生**。

流程修正（已生效）：
1. 红态归档的 checkout-恢复后，**必须重新核对当时工作区的全部未提交修改**（`git status`+逐文件 diff 对照修改清单），而非仅确认目标文件恢复。
2. 红态归档前**先 commit 已完成的修改**（红态 checkout 只应发生在干净树上）——本 Task 修复已按此重做：lazy split 重新应用（ed86cc46 前刀）→ 绿态重归档（tiling 82/82）→ 三套件 611+1sk 复跑。
