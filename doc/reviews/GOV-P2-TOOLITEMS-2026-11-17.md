# 两条 P2 工具项处置（2026-11-17，DSH）

来源：用户 2026-11-17 交接清单「C. 2 条 P2 工具项」：
1. `EVIDENCE-MANIFEST` 的 panic 路径评估；
2. 历史 `ALREADY_ABSENT` 统一为 `PRESERVE_UNKNOWN`（该值不在允许枚举内）。

---

## 1. `ALREADY_ABSENT` —— **已迁移完毕（无需再改）**

**实测方法**：解析 `doc/tasks/*.md` 全部卡片 `## Resource Manifest` 段落，逐行取第 3 列（disposition）。

| 项 | 实测 |
|---|---|
| 扫描行数 | **1,106** Resource Manifest 行 |
| disposition 仍为 `ALREADY_ABSENT` 的行 | **0** |
| 文本中出现 `ALREADY_ABSENT` 的卡片 | 15（**全部是历史说明文字**，例如「原 `ALREADY_ABSENT` 改为 `PRESERVE_UNKNOWN`」） |

**结论**：此前批次（`GOV-EVIDENCE-PIN-REPAIR-1` AC4 batch 5/6）已把 disposition 统一为 `PRESERVE_UNKNOWN`；
剩下的 15 处是**解释性散文**，属于历史记录，**不得改写**。
本项**关闭，无需动作**。若将来新卡误用 `ALREADY_ABSENT`，`check.ps1` 的表格路径会报 `Resource disposition 无效`（fail-closed），
这正是当前允许枚举（`DELETE_SAFE/MIGRATE/ARCHIVE/PRESERVE_REFERENCED/PRESERVE_USER_DATA/PRESERVE_UNKNOWN/NOT_APPLICABLE`）的预期行为 ——
**不得**为了让旧卡通过而往允许枚举里加 `ALREADY_ABSENT`（那是放宽检查）。

> 备注（口径不一致，已登记不改）：`check.ps1` 的**外部 JSON manifest 路径**（`Test-ExternalResourceManifest`）允许枚举里含 `ALREADY_ABSENT`，
> 表格路径不含。两者语义不同（JSON 路径要求同时提供 `absent_evidence` 且目标确实不存在），当前没有卡片因此失败；
> 统一两侧枚举属**放宽或收紧检查**，需单独裁定，本轮不动。

## 2. `EVIDENCE-MANIFEST` panic 路径 —— **评估完成，补 2 条 fail-closed 测试**

**代码现状（`tools/governance/check.ps1:1337-1420`）**：
- 解析包在 `try/catch` 内，失败即 `EVIDENCE_MANIFEST_INVALID`（`$manifest = $null`）；
- 仅 `kind: research` 可用；
- 每个条目校验：绝对路径 / `..` 逃逸 / 通配符 / 64 位小写十六进制 / 路径重复；
- 门禁**自己重新枚举目录并重算哈希**，manifest 永不作为真值；文件集必须**精确相等**；
- manifest 自身必须被 Canonical Evidence 行登记；
- 目录内符号链接在枚举时被跳过（`$file.LinkType → continue`），且清单若列出该路径会因「列出的文件不存在」报错（fail-closed）。

**评估结论**：现实输入下**没有未捕获的 panic 路径**；残余风险只有资源耗尽类（超大 manifest 整文件读入内存、超大目录递归哈希），
属仓库内自控输入，**不加固**（加固会引入新依赖/新失败面，收益不成比例）。

**本次补的判别力测试**（`tools/governance/tests/test_bulk_evidence_manifest.py`，8 → **10** 条）：

| 测试 | 断言 |
|---|---|
| `test_malformed_json_fails_closed_without_crash` | 非法 JSON ⇒ 输出含 `EVIDENCE_MANIFEST_INVALID` 且 `Governance check: FAIL`（不是崩溃、不是 PASS） |
| `test_files_not_a_list_fails_closed` | `files` 为标量 ⇒ **不得** `Governance check: PASS` |

**实测**：`python -B -m unittest tools.governance.tests.test_bulk_evidence_manifest` → **Ran 10 tests … OK**。

## 3. 边界

- 本轮**未修改** `check.ps1` 的任何判定语义（只加测试），**未放宽**任何检查。
- 未改任何历史卡片的 `Resource Manifest` 行、未改 `verification/**` 字节。
