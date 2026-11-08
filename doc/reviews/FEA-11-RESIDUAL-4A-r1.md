# FEA-11-RESIDUAL-4A Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `5c2ac5eeb`（base `89ef7a868`） |
| 结论 | **changes_requested**（P0=0 / **P1=1** / P2=3 / P3=9） |

## 判定
AC-R3-1（AC11-7 投影，operation 作用域）**MET**；AC-R3-2（AC11-9 Host 级全链）**MET（带 D-5 limitation）**；AC-R3-3（AC11-6 四类用例）**MET**；AC-R3-4（L-M4 不实现 + re-home）**MET**；AC-R3-5 回填 **MET**；AC-R3-6 证据/治理 = **DSH closeout 待办**。

## P1
- **P1-1**：`HostRuntime.cs:1191-1200` `RecordSourceOperationFailure` 仍向已打开 payload 写嵌套 object（D-1c，与 D-1a/D-1b 同类）⇒ `source_record_operation_failure` 经生产 dispatcher 抛 `InvalidOperationException`，无测试。

## P2/P3
P2-1 FEA-11 done 卡 EV pin 失效/未登记文件/Resource Manifest 缺（DSH closeout）；P2-2 D-1 before 证据归因误标 + 缺修复后全链证据；P2-3 AC-R3-2 的 D-5 limitation（seed 旧绑定无 grant 映射）；P3-1…P3-9（行文矛盾、journal 分支断言、旁路用例、AC 未勾选、指针陈旧、re-home 卡未建、EOF 空行、数字口径）。

## 变异实测
M1（folder 拒绝）/M2（gate 放行）/M3（投影过滤）/M4a（dispatcher 嵌套）/M5（ping 未闭合）均 RED → 逐字节复原 sha256 MATCH → 复绿。
