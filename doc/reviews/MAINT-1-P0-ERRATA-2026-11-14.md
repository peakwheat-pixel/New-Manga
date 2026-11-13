# MAINT-1 P0 治理一致性 errata（2026-11-14）

范围：只读审计发现 → 一致性修复。不改产品代码、不改任何历史证据/Review/verification 字节。
基线：`main` @ `fb220a8e9`，工作区 clean。执行人：DSH（MAINT-1 owner）。

## E-1 PLAN 未登记表外节点（已修）

**现象**：`pwsh -File tools/governance/check.ps1 -TaskPath doc/tasks/<card>.md` 对 4 张非终态卡返回 `FAIL: 当前 DAG 未登记非终态 Task`：
`GIT-CLEAN-PUBLICATION-DIAG-1`、`GIT-CLEAN-PUBLICATION-1`、`GIT-CLEAN-RUST-ISOLATION-1`、`GIT-CLEAN-RUST-CAPACITY-DESIGN-1`（后者另报 `READY Task 未出现在 Plan 的 READY 节点`）。
另：`MAINT-1` 的 `depends_on: [PUBLISH-FIX-1]`，而 `PUBLISH-FIX-1`、`REL-GATE-1`、`SEC-01/02/03`、`CORE-01`、`AUDIT-07/09/12/14`、`FEA-08`、`FEA-09` 均无 DAG 行。

**约束**：`check.ps1:663` 对 PLAN 的预算是 7000 B / 64 行；当时 6891 B / 64 行，**行数余量 0**。放宽预算等于降低门禁，故只能在同预算内提高信息密度。

**修复**：状态加粗归一化（`**done**`→`done`，纯格式、零信息损失）+ 去尾重复管道 + 合并空行，在「当前活动程序」段新增一行表外节点声明与 READY 声明。

**验证**：默认 `check.ps1` PASS；上述 4 张卡与 `MAINT-1` 的分卡检查全部 PASS。PLAN 6954 B / 64 行（预算内）。

## E-2 TASK_LEDGER 算术不可自洽 + 账本陈旧（已修）

**现象**：`doc/TASK_LEDGER.md` 记 `task files 599 = terminal 588 + non-terminal 10`，相加少 1；且 `By status` 非终态各行相加为 11。

**根因**：`tools/governance/task_ledger.py:114-119` 有意把无 `status:` 字段的文件 `(none)` 视为草稿并从 `non-terminal` 排除（与 `check.ps1` 口径一致），生成文档却没有复述这条规则；同时账本自 `259301fdd` 登记 MAINT-1 后未重生成，`named in the plan` 仍为 0、`outside the plan` 仍为 10。

**修复**：生成器补 "Arithmetic note"（说明 `task files = terminal + non-terminal + (none)`）；`task_ledger.py --write` 重生成 → `named in the plan` 0→1、`outside the plan` 10→9。计数值本身未改（原值正确）。

## E-3 STATUS 时效（已修）

**现象**：`doc/STATUS.md:6` 写「**FEA 线 ACTIVE（S5）**」，而 `doc/REBASELINE_PLAN.md:58` 写「ACTIVE：MAINT-1」，S0–S5 节点已全终态。

**修复**：改为「**FEA 线已收口（S0–S5 全终态；9 节点带 limitation）**」，并把「刚收口」一行改为「收口尾项」。STATUS 3147 B / 32 行（预算 3200 B / 45 行，PASS）。

## E-4 REL-GATE-1 AC2 理由与源码不符（只登记，不改历史字节）

**现象**：`doc/tasks/REL-GATE-1.md` AC2 写「App 无隔离数据根入口，启动会写真实 %APPDATA% 根（本 Task 禁止）」，据此把 GUI 冒烟记 BLOCKED。

**反证**（源码优先）：
- `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs:97` 的开关白名单含 `data-root`；
- `:216` 为其解析分支；
- `:343-351` 把 `DataRoot` 写入 `HostOptions.DataRoot`，**未提供时才回落** `%APPDATA%\com.newmanga.desktop`。

**处置**：仅登记 errata，不改 `REL-GATE-1` 任何字节；AC2 仍为 `<<PARTIAL>>`，本记录不构成冒烟已执行、不改变 BLOCKED 结论。后续由 P2 可见 UI 冒烟卡据此实测隔离启动；若 `--data-root` 不足以隔离主题/日志等其他根，须在该卡登记**具体缺口**，不得回退成"无入口"。

## 未修改清单

`REL-GATE-1` 与其他 Task 卡历史字节、所有 Review、`verification/**`、产品源码、契约、依赖、真实用户数据、远端。

## 门禁

`check.ps1` PASS（3 warnings：10 张非终态卡的固定提示 + 两份文档 80% 预算提示）；`verify_pins.ps1` 18/18 PASS。
