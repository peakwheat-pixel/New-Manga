# FEA-07-IMMERSIVE-F11-1 Review r4（独立子代理）

- reviewer：DSH fresh 子代理 r4（未参与实现/返修，只读；未写仓库文件）
- reviewed_head：`57d7d9eaa`；base `9d4b4c8ea`；范围 `61e324e1d` + `404a68e3d` + `57d7d9eaa`
- decision：**approved**（P0=0 / P1=0 / P2=0 / P3=4；AC5 仍 PARTIAL，不写 PASS）

## 结论
r3 的 9 条 findings（N-010…N-018）全部实质关闭：`apps/**` 自 base 起零改动；关账材料事实准确性（更正落地、Esc 后状态持久化、证据表哈希、ledger、allowed_paths、Closeout Record）经独立复核成立。新增 4 条 P3 仅记录精度补正。

## 实跑结果
- HEAD `57d7d9eaa`，`git status` 干净；`9d4b4c8ea..HEAD` 3 commit、11 文件全在 `doc/**`/`verification/**`；`git diff 9d4b4c8ea..HEAD -- apps/` 为空。
- `dotnet test --filter F11HotkeyTests` → 9/9，EXIT 0；`--filter "ReaderLibraryTests|ReaderChapterSelectorTests"` → 20/20，EXIT 0。
- `check.ps1` 与 `-TaskPath` → PASS（3 warnings，既有）。
- `task_ledger.py` → 558/558/0、terminal 542、non-terminal 15，与提交 ledger 逐项一致。
- 证据表 14 行 × 6 列、14/14 SHA 匹配；3 张截图 SHA 与 JSON 匹配，PNG 2560×1440、内容 bbox 1920×1080。

## N-010…N-018 关闭
| ID | 判定 | 依据 |
|---|---|---|
| N-010 | CLOSED | DEFECTS `diff` = 8 增 0 删（纯 append，原 `-32000` 保留）；ADJ 改为「追加更正」措辞；三条几何断言经 JSON 核实 |
| N-011 | CLOSED | 卡「原生复测」改为 legacy 成功 + 历史旧归因废弃；AC5 PARTIAL |
| N-012 | CLOSED（主项） | JSON 含 `afterEsc`/`build`/`displaysNow`，工具已持久化；截图哈希匹配 |
| N-013 | CLOSED | moved-evidence = 7 产物 + MANIFEST，12 副本已删；7/7 SHA 匹配 |
| N-014 | CLOSED | ledger 558/0/15 与现算一致 |
| N-015 | CLOSED | reviewer 字段更新；r1/r2/r3 报告入库 |
| N-016 | CLOSED | V2 卡入 allowed_paths；depends_on 仅 FEA-07 |
| N-017 | CLOSED | 证据表 6 列 14 行无碎行；日志含 shell/CWD/完整 CMD/EXIT |
| N-018 | CLOSED | Closeout Record 存在且要素齐全 |

## 新增 P3（非阻断）
| ID | 摘要 | 建议 |
|---|---|---|
| N-019 | `coversPrimary` 仍按硬编码 2560×1440 计算，1920×1080 会话中恒 false，易误读 | 改为按 probe 显示器矩形计算或改名并注明 |
| N-020 | `moved-evidence/MANIFEST.md` 末段称 12 副本为 `displays-final-*` tracked 副本，但仓库从未 track 该前缀 | 列出实际 12 文件名或标注「清单未保留」 |
| N-021 | 卡「背景」:44/「证据」:65 仍以未标注方式复述已被否定的 v2 采样 | 加交叉引用「见 DEFECTS §D-AC5-2 更正；已 superseded」 |
| N-022 | 截图含用户其他应用且被遮挡；JSON 未记前台窗口；无法目视证明内容/前台 | 记录 `GetForegroundWindow`；Closeout 注明可见性结论依据 Win32 采样；AC5 维持 PARTIAL |

## 未核实
`build.exeSha256` 因 review 复跑重建而不可复核（作者无责）；r2 为忠实摘要；未重跑原生脚本（仅 PostMessage，非物理键盘）；未复核 superseded 采样全字段；未审 `doc/handoffs/`、`doc/STATUS.md`。
