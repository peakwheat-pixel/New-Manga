# AC1–AC3 — 为 hash-pinned 证据固定 LF 行尾

**Task**: GOV-EOL-PIN-1 · **性质**: 单文件属性改动

## AC1 — 追加的规则

```gitattributes

# GOV-EOL-PIN-1: canonical evidence and handoff files are SHA-256 pinned.
# Keep LF on checkout so pins remain reproducible when core.autocrlf=true.
verification/GOV-UNTRACKED-BACKLOG-1/** text eol=lf
doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md text eol=lf
```

追加于文件末尾，独立成组并带注释。**既有四条规则未改动**：
`SEC-FIX-PATH-ECHO-1-c52ce46.md`、`tools/governance/check.ps1`、
`verification/P19-UI-MANIFEST-VIEW-1/**`、以及 M2 相关的 `-text` / `-whitespace` 组。

## 属性生效对照

| 时点 | `git check-attr text eol` |
|---|---|
| 追加前 | `text: unspecified`、`eol: unspecified` |
| 追加后 | `text: set`、`eol: lf` |

## AC2 — renormalize 结果

`git add --renormalize` 后 `git status --porcelain` **只显示 `.gitattributes` 被修改**，
6 份证据与 Handoff **无字节变化**——这正是预期结果：它们本来就是 LF，
`text eol=lf` 只固定未来的检出行为，不改现有内容。

`git ls-files --eol` 全部为：

```
i/lf    w/lf    attr/text eol=lf      	doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-inventory.json
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac2-anomalous-entries.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac3-references.json
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac4-worktree-mirror-guide.md
```

## AC3 — worktree 复现验证

在提交 `76e4a1544` 后新建一次性 linked worktree 实测：

| 项 | 结果 |
|---|---|
| worktree 内 `ls-files --eol` | `i/lf w/lf attr/text eol=lf` |
| worktree 内 `ac1-ac3-composition-and-references.md` SHA-256 | `A86B42336085345E0D27EDF5664061AAC53D4337CAF98E0B23A80CA62D883E6A` |
| 主 checkout 同一文件 SHA-256 | **同上，完全一致** |

**修复前的预期**：无该规则时，`core.autocrlf=true` 下 worktree 检出为 CRLF，
hash 与 pin 失配。
**修复后实测**：worktree 与主 checkout 字节相同，pin 可复现。

探针 worktree 已 `git worktree remove --force` 并 `prune`，确认路径已不存在。

## 明确未做

- 未改任何证据文件内容（renormalize 无字节变化）。
- 未改 `tools/governance/`、其它 Task、Plan/STATUS 的节点状态。
- 未改既有 `.gitattributes` 规则。
- 未删除、未移动任何文件。
