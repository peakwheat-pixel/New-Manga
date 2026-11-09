# FEA-07-IMMERSIVE-F11-1 Review r3（独立子代理）

- reviewer：DSH fresh 子代理（未参与实现/返修，只读；变异在 `%TEMP%` 复制完成并已删除）
- reviewed_head：`9d4b4c8ea`；base `a4b59f860`；范围 `b4f801e2f` + `9d4b4c8ea`
- decision：**changes_requested**（P0=0 / P1=0 / P2=3 / P3=6）

## 结论
r2 的 P1（N-001 壳错误）与 P2（N-002/N-003）**实质关闭**；代码/测试主路径可接受（9/9、20/20；删除 `IsVisible` 守卫变异后 1 failed/8 passed，判别力成立）。未通过集中在关账材料事实准确性：
1. ADJ §7.20/commit message 声称的 D-AC5-2 更正**不存在**（N-010）；
2. 卡片 §原生复测仍保留「键盘未进入应用」旧归因（N-011）；
3. AC5「Esc 关闭、主窗恢复」无持久化证据（JSON 仅 Esc 前，N-012）。

## 实跑
- `git status` 干净；HEAD=`9d4b4c8ea`。
- `dotnet test --filter F11HotkeyTests` → 9/9；`ReaderLibraryTests|ReaderChapterSelectorTests` → 20/20。
- `task_ledger.py`：558 文件、tracked 558/untracked 0、terminal 542、non-terminal 15；已提交 ledger 仍写 557/1/14（N-014）。
- `check.ps1` / `-TaskPath`：PASS；证据表 13/13 SHA 匹配。
- 变异：删除 `IsVisible` 守卫 → 1 failed（`Assert.False()` Actual True）⇒ N-003 判别力成立。
- 范围：`b4f801e2f` 4 文件全在 allowed_paths；`9d4b4c8ea` 的 `doc/tasks/FEA-07-V2-F11-1.md` 不在 allowed_paths（N-016）。
- 当前仅 1 屏 1920×1080；moved-evidence 19 文件 = 7 新产物 + 12 个 tracked 副本（N-013）。

## N-001…N-009 关闭确认（摘要）
- N-001 CLOSED：legacy JSON 记录 exe/args/shell/sidecar/dataRoot/logDir；导航为 legacy 四项；卡 :59 与 ADJ §7.20 已改；但卡 §原生复测仍旧（N-011）。
- N-002 CLOSED（壳/args）；残余：无显示器枚举、`coversPrimary` 硬编码 2560×1440、主窗为 Esc 前采样。
- N-003 CLOSED：静默不可见用例存在；变异有判别力；残余：该分支未前置 Minimized（恢复语义由异常分支覆盖）。
- N-004 CLOSED：150101/150419 同 pid（52436），superseded 措辞一致。
- N-005 CLOSED：13 行无表内空行；残余：末行与下一标题缺空行（N-017）。
- N-006 CLOSED：`Assert.False(window.TryOpenImmersiveReader())` 存在，变异命中。
- N-007 CLOSED：approval 去重；残余：`reviewer` 仍写「r2 待审」（N-015）。
- N-008 CLOSED：失败提示只在 `RefreshStatusText()`；注：`StartHostAsync` catch 另写文案，理论可覆盖（P3 注）。
- N-009 部分关闭：7 个产物已移出仓库、Manifest 如实；但目录含 12 个 tracked 副本、manifest 列填的是 legacy JSON（N-013）。

## 新 findings
| ID | 级别 | 摘要 |
|---|---|---|
| N-010 | **P2** | ADJ/commit 声称的 DEFECTS 更正不存在（实际被 `git checkout` 回滚）；应 append-only 更正并保留原字节 |
| N-011 | **P2** | 卡 §原生复测仍写「键盘未进入应用」，与 legacy 成功结论矛盾 |
| N-012 | **P2** | JSON 未持久化 Esc 后状态/截图，无 build 绑定与显示器枚举；`coversPrimary` 易误读 |
| N-013 | P3 | moved-evidence 含 12 个 tracked 副本；manifest 列非真实清单 |
| N-014 | P3 | 提交的 ledger 过期（557/1/14 → 558/0/15） |
| N-015 | P3 | reviewer 字段过期；r2 review 未入库 |
| N-016 | P3 | `FEA-07-V2-F11-1.md` 不在本卡 allowed_paths；depends_on 指向终态卡 |
| N-017 | P3 | 证据表末行缺空行；运行日志命令不完整、无 shell 头 |
| N-018 | P3 | 终态卡缺 Closeout Record |

## 未核实
未重跑原生脚本、未查看截图内容；15:32 拓扑与 build 绑定仅依据 JSON 与源码；未复跑全量 .NET；未看 r2 原文（现已入库）。
