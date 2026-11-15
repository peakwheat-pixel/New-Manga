# doc/tasks 控制字符修复 — 证据

Task：`DOC-CONTROL-CHAR-REPAIR-1`（Owner：DSH）
基线：HEAD `3fd3316ed`

## 1. 问题

`doc/tasks/**` 中 **65 个文件 / 113 处**含 C 风格转义泄漏——`\v`→`0x0B`、`\a`→`0x07`、`\b`→`0x08`、
`\f`→`0x0C`、`\e`→`0x1B`、`\0`→`0x00`。后果：`verification` 被写成 `erification`、
`apps/` 写成 `pps/`、`frozen` 写成 `rozen`，**这些词在卡面不可 grep**。

## 2. 方法与判定

1. **全量清点**：`scan.py` 输出每处的 文件/行/字节列/hex/上下文（`scan.md`，113 行表格 + 逐行原文）。
2. **映射候选**：按 C 转义 `0x0B→v`、`0x07→a`、`0x08→b`、`0x0C→f`、`0x1B→e`、`0x00→e`。
3. **验证驱动**：把候选替入后取该位置的 ASCII token，检查是否存在于
   （a）仓库文本 token 集合（782,253 条），或（b）`git cat-file -t` 可解析的 commit hash。
   **86 处自动通过**。
4. **逐条人工判定 27 处**（自动验证不通过者）：
   - **21 处**：token 是路径/文件名/9 位短 commit（词表未收录，但上下文唯一可判）→ 填单字母；
   - **2 处**（`GOV-EVIDENCE-DIR-SWEEP-1.md:48/:56`）：原文是**两字节 `\a`**
     （`G:\CODEX\New Manga.workspace\archive\...` 的路径分隔符被转义）→ 替换为 `\a`（文件 +1 字节）；
   - **4 处**：候选字母会造成非法 token（如 `完成。` + `e752fbad` 若填 `e` 得 `ee752fbad`；
     `为准；` + `base_commit` 若填 `b` 得 `bbase_commit`）→ 判定为**多余字符，删除**。

**无法唯一判定：0 处**（113/113 均有明确依据，明细见 `verify.log`）。

## 3. 结果

| 指标 | 值 |
|---|---|
| 修复处数 | **113 / 113** |
| 涉及文件 | **65** |
| 残留控制符 | **0**（`doc/tasks/**` 全扫） |
| 无法判定 | 0 |

**差异最小化**（`git diff --numstat`，65 个卡文件）：
`1/1` ×43、`2/2` ×14、`3/3` ×2、`4/4` ×1、`5/5` ×2 —— **每个文件的增/删行数相等**，
即每行只改控制符所在字节。另有 3 个文件（`D-14-STATUS-COLOR-FIX`、`GPU-ORT-PROBE-1`、
`LEGACY-SHELL-REMOVAL-1`）因 HEAD blob 含控制符被 git 视为 binary（`-/-`），
但 `git diff --text --stat` 显示 `Bin 6197 -> 6197`（**大小不变**）等，确认无整文件重写。

**可 grep 性**（修复后 `doc/tasks/*.md` 命中文件数）：
`verification` 631｜`apps/` 365｜`frozen` 155｜`vitest` 93｜`existing` 49。

## 4. 不回归

```
check.ps1                    → PASS (3 warnings)
verify_pins.ps1              → PASS (all 18)
generate_api_inventory.py    → OK (1/80/6=87)
verify_locators.py（AC 注释）→ 418/418 行内命中，0 偏差
```

AC 注释里的 418 个 `test:`/`grep:` 定位符全部不受影响（控制符均在非 AC 行）。

## 5. 已知限制（不淡化）

1. **3 个文件在 git 中仍显示为 binary**：`D-14-STATUS-COLOR-FIX.md`、`GPU-ORT-PROBE-1.md`、
   `LEGACY-SHELL-REMOVAL-1.md` —— 其 HEAD blob 含控制符，git 按 binary 处理 diff。
   修复后工作区已是合法 UTF-8（stric 校验通过）且无控制符；提交后新 blob 不再含控制符。
2. **2 处替换使文件 +1 字节**（`\a` 两字节复原），这是**还原**而非膨胀。
3. 本修复**只动控制符所在字节**；卡面其它既有的格式/内容问题（如台账行号引用）不在范围内。
4. `doc/tasks/**` 之外（如 `doc/reviews/**`、`verification/**`）是否也有同类损坏**未排查**——
   本次范围按 `AC-CHECKBOX-AUTHORITY-1` §7.8 的登记，仅 `doc/tasks`。

## 6. 复现

```powershell
cd "G:\CODEX\New Manga"
# 清点（只读）
python "G:\CODEX\New Manga.workspace\tasks\DOC-CONTROL-CHAR-REPAIR-1\scan.py"
# 判定（dry-run，不改文件）
python "G:\CODEX\New Manga.workspace\tasks\DOC-CONTROL-CHAR-REPAIR-1\repair.py" --dry-run
```
