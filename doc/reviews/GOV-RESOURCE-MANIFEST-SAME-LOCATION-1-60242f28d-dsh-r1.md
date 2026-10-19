---
task_id: GOV-RESOURCE-MANIFEST-SAME-LOCATION-1
reviewer: dsh
reviewed_head: 60242f28d
base_commit: 296a9389d
verdict: APPROVED
---

# Review：GOV-RESOURCE-MANIFEST-SAME-LOCATION-1

Owner 为 Antigravity，本文由 DSH 独立复核（未参与实现）。

## 一、我实际运行了什么

我没有只读 Handoff，而是逐条复跑：

| 验证 | 命令 | 结果 |
|---|---|---|
| 离线套件 | `python tools/governance/tests/run-resource-manifest-cases.py` | **32/32，exit 0** |
| Task 检查 | `check.ps1 -TaskPath ...SAME-LOCATION-1.md` | **PASS (1 warnings)** |
| 全局检查 | `check.ps1` | **PASS (1 warnings)** |
| P19 错误数 | `check.ps1 -TaskPath doc/tasks/P19-UI-FIX-1.md` | **5 errors, 7 warnings** |
| 残留检查 | `git status --porcelain` 查 `ZZ-` | **无残留** |

## 二、逐条 AC 独立判断

| AC | 我的判断 | 依据 |
|---|---|---|
| **AC1** 同源与空值解析 | **达成** | P19 的 5 个 `Same ...` destination 错误全部消失 |
| **AC2** note 可追溯 | **达成** | 实测输出 5 条 WARN，每条含 `resource_type`、原 sentinel 文本、实际使用的 `source_path`（见下） |
| **AC3** 限制匹配范围 | **达成** | 用例 29（`prose destination fails`）与 30（`unknown same destination fails`）均 `expect_manifest_fail=True` 且实测通过 |
| **AC4** 真实缺失路径继续失败 | **达成** | `p19-ui-fix-1-isolation-20261017` 仍是 FAIL，未被豁免 |
| **AC5** 离线回归用例 | **达成** | 19 → **32** 个；既有 19 个预期未变（我核对了 id 1–19 仍全 OK） |
| **AC6** 集成前验证证据 | **达成** | 证据目录留存完整输出与退出码 |
| **AC7** 范围与资源保护 | **达成** | 未改源 JSON、P19 Task/evidence/pins、schema |

### AC2 的实测证据（我亲眼看到的输出）

```
WARN: P19-UI-FIX-1: Resource 'generated-build-artifacts' destination 'Same ignored target/dist locations in this worktree' 解释为同源，使用 source_path 'apps/...'
WARN: P19-UI-FIX-1: Resource 'user-data-source' destination 'Same source location' 解释为同源，使用 source_path '%APPDATA%/com.newmanga...'
WARN: P19-UI-FIX-1: Resource 'sidecar-build-environment' destination 'Same shared build environment' 解释为同源，使用 source_path 'G:/CODEX/New Manga.task-env...'
WARN: P19-UI-FIX-1: Resource 'pyinstaller-cache' destination 'Same local cache location' 解释为同源，使用 source_path 'C:/Users/49745/AppData/Local/pyinstaller...'
WARN: P19-UI-FIX-1: Resource 'read-only-baseline-evidence' destination 'Same main-repository paths' 解释为同源，使用 source_path 'G:/CODEX/New Manga/verification/...'
```

「不得宣称存在一个不同于 source 的 destination」这一条也满足：措辞是「解释为同源，使用 source_path X」，
没有暗示另有一个 destination。

## 三、最关键的一点：负向用例是真的

这个 Task 的风险从来不是「让 `Same ...` 通过」，而是**放宽过度**——一旦解析器开始接受
「随便一段散文」，`Some other place` 就会被当成合法，检查器从此对 destination 完全失去约束。

我逐一核对了 13 个新用例的 `expect_manifest_fail` 值：

| id | 用例 | 期望失败 |
|---|---|---|
| 20–24 | 5 个 sentinel | False |
| 25–27 | 空 / 空白 / `-` | False |
| 28 | 正常存在的 destination | False |
| **29** | **`some other place`** | **True** |
| **30** | **未知 `Same ...` 文本** | **True** |
| **31** | **真实缺失路径** | **True** |
| **32** | **`-` 但 source 也不存在** | **True** |

**用例 32 尤其好**——它堵住了「用 `-` 掩盖源本身也不存在」这条路。这个用例不在我预期的清单里。

## 四、P19 错误数的净变化

| 时点 | 错误数 |
|---|---|
| 本 Task 之前 | 10（5 个 `Same` + 1 个真实缺失 + 4 个历史/环境） |
| 本 Task 之后 | **5**（真实缺失 1 + 历史 2 + 环境性 1 + 未登记文件 1） |

**净减少 5 个**，与 Handoff 声称一致。剩余的 5 个中没有一个是本 Task 造成的，
其中 `verification/P19/import-no-response-r4.md` 的 SHA 差异在**主 checkout 中不存在**，
是 worktree 镜像换行导致的环境性差异。

## 五、发现的问题

**无阻塞项、无严重项。**

一个观察（不构成问题）：`user-data-source` 的 `source_path` 是 `%APPDATA%/...`，
被解释为同源后，路径解析对含 `%VAR%` 的表达式按既有规则跳过校验。这符合 AC1 的
「或明确跳过」，但意味着这一类资源**仍有 note 而非实证校验**。这是真实数据的性质，
不是本 Task 的缺陷；若要覆盖，需要变量展开能力，属另一次范围。

## 六、结论

**APPROVED。** 建议交由 Codex 集成并 closeout。

实现者自行扩展了用例 32（`-` 但 source 缺失仍失败），这是一个我没有要求、但确实堵住
一条真实旁路的补充。这一点值得记录：负向用例不是走形式，而是真的在防「放宽过度」。
