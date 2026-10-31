# AC2（R-002）：证据 pin 行尾基准规范化

日期：2026-11-01。Owner：DSH。基线：`main@29d06c462`。

## 根因

SAFETY-6 的 Canonical Evidence pin 记录的是 **工作树字节** 的 sha256。仓库 `core.autocrlf=true`，
而证据文件在 git 中的 blob 是 LF、检出到工作树是 CRLF：

```
git ls-files --eol verification/REALUSE-DATA-SAFETY-6/
  i/lf  w/crlf  attr/   verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md   （修前）
```

于是同一文件在"CRLF  checkout"与"LF checkout"下得到不同 sha256 —— pin 在换环境后失效
（SAFETY-6 Review R-002 实测 worktree 一致 10/11、blob 一致 6/11）。

## 修复

1. `.gitattributes` 追加规则（只作用于 SAFETY-6 证据目录，不触碰其他历史证据）：

```
verification/REALUSE-DATA-SAFETY-6/** text eol=lf
```

2. 强制重新检出该目录（删除工作树副本后 `git checkout --`），使 `w/crlf` → `w/lf`，与 blob 一致。
3. 按 LF 字节重算 11 条 pin 对照；仅 2 条与旧 pin 不同（其余 9 条原本就是 LF 基准），已更新到
   `doc/tasks/REALUSE-DATA-SAFETY-6.md` 的 Canonical Evidence 表。

## 对照表（LF 基准，2026-11-01 实测）

| 证据文件 | 旧 pin（CRLF 或旧基准） | 新 pin（LF） | 变化 |
|---|---|---|---|
| `ac1-progress-refresh-test-log.txt` | `2eab8096…` | `1bb0ac36aa1866230b38385c189edfcf97bf63bc87a43e2d307048477723466c` | **已更新** |
| `ac1-progress-refresh.md` | `e913e2dd…` | `e913e2dd01d8e8f8af6cc54b7d1126eb5993b64d0b0976f0bf2f0d44669866e8` | 不变 |
| `ac2-derived-conclusion.md` | `1edb35f1…` | `1edb35f14a3676cecaad7c8d2b78ed75af2ca3ae43b43c20967bb85e73c77c47` | 不变 |
| `ac2-derived-realdata.json` | `22f9793f…` | `e21061547e8adb405490d0119efd93b24fcdfd0b79966dffefc219963d3c5dea` | **已更新** |
| `ac3-options.md` | `9c27d477…` | `9c27d477301e090e79cb48a3fafa892b86ddfce80e41723826cd2acfef5c950b` | 不变 |
| `governance-check.txt` | `bc97d7a7…` | `bc97d7a78e4db6e84899c415bc82a27e45b8874c16b31e71baf571c69e7b592e` | 不变 |
| `README.md` | `d199f484…` | `d199f4843dea5c3c6b25ee293f1b54b93ce58bdb82fa9960c4eb6676041ca3ff` | 不变 |
| `resource-manifest.json` | `133943d7…` | `133943d78481e43c0bb4d4766cf7691ca00fe7358506c249c50130b629befd99` | 不变 |

（`ac1-progress-refresh.md` 等 6 条在 SAFETY-6 卡中原本记录的就是 LF hash，故不变。）

## 边界

- 只改 SAFETY-6 证据目录的行尾规则与 2 条 pin；**不改证据内容**（LF/CRLF 是同一文本）。
- 不改 SAFETY-6 的 AC 判定、Closeout 记录或历史 Review 字节。
- 其他历史 verification 目录保持原状（未批量 renormalize，避免大面积 diff）。
