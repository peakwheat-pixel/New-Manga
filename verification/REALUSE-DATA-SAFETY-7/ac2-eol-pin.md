# AC2（R-002）：证据 pin 行尾基准规范化

日期：2026-11-01。Owner：DSH。基线：`main@29d06c462`。

> **2026-11-01 修订（REALUSE-DATA-SAFETY-8 AC1 / SAFETY-7 Review F-001）**：初版本文档把 SAFETY-6 的
> pin 记成「11 条、2 条更新、9 条不变」，与实际不符。SAFETY-6 卡实际有 **12 条** Canonical Evidence
> （4 条代码 + 8 条证据），实际值变化 **5 条**（3 代码 + 2 证据），未变 7 条；初版对照表漏列 4 条
> 代码 pin。本修订补齐全部 12 条对照并更正计数。

## 根因

SAFETY-6 的 Canonical Evidence pin 记录的是 **工作树字节** 的 sha256。仓库 `core.autocrlf=true`，
而证据文件在 git 中的 blob 是 LF、检出到工作树是 CRLF：

```
git ls-files --eol verification/REALUSE-DATA-SAFETY-6/
  i/lf  w/crlf  attr/   verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md   （修前）
```

于是同一文件在「CRLF checkout」与「LF checkout」下得到不同 sha256 —— pin 换环境后失效
（SAFETY-6 Review R-002 实测 worktree 一致 10/11、blob 一致 6/11）。

## 修复

1. `.gitattributes` 追加规则（只作用于 SAFETY-6 证据目录，不触碰其他历史证据）：

```
verification/REALUSE-DATA-SAFETY-6/** text eol=lf
```

2. 强制重新检出该目录（删除工作树副本后 `git checkout --`），使 `w/crlf` → `w/lf`，与 blob 一致。
3. 所有 pin 统一改为 **commit blob（LF）基准**。检查器 `check.ps1` 的核对顺序是「先比工作树字节，
   不匹配再回退到 pin 所指 commit 的 blob 字节」（`tools/governance/check.ps1:691-714`），因此 blob
   基准在后续 Task 修改工作树文件后仍然稳定。
4. 按 LF 基准重算，并更新到 `doc/tasks/REALUSE-DATA-SAFETY-6.md`。

## 完整对照表（12 条，2026-11-01 实测）

### 代码证据（4 条，commit `fb5065013`）

| evidence_id | 旧 pin（工作树 CRLF 或旧基准） | 新 pin（blob/LF） | 变化 |
|---|---|---|---|
| `E-AC1-READER-VM` | `603ed15e600aefaf91fa04984fb4844e2daa32b459e88dca616ab586151fe865` | `db99f3ebcaa07805b3d195048dabf3ab7eee00e17bd3805d5f0951b782b642ef` | **已更新** |
| `E-AC1-LIBRARY-VM` | `2b6f2525f1724cecaf0e0a5de6cf18560ceb28ef6d71784cdb7ba8c2c53066f6` | `bc651c5657d05fc041754d25b00d503ee68ce734fa005a6469d8afb21e2d66e7` | **已更新** |
| `E-AC1-TEST` | `135de02c1856c5989269a70f8544925d03c4a7e3127642b0b75e88f3cff260a2` | `135de02c1856c5989269a70f8544925d03c4a7e3127642b0b75e88f3cff260a2` | 不变 |
| `E-AC1-TEST-FAKE` | `6c63c2c5fc933eea8fab51ba792246d6131e997ce31bccb248eb32d2affe4a11` | `c0c4822bc7ffb7ae0eabf6fcc6832c1100f31b729844235b2b23031fee716533` | **已更新** |

### 证据文件（8 条）

| evidence_id | 旧 pin | 新 pin（LF） | 变化 |
|---|---|---|---|
| `E-AC1-LOG` | `2eab80965115b0d2feb5ca9fb9a4903682311e63b78a3ac1be9e1a517cc0a63c` | `1bb0ac36aa1866230b38385c189edfcf97bf63bc87a43e2d307048477723466c` | **已更新** |
| `E-AC1-DOC` | `e913e2dd01d8e8f8af6cc54b7d1126eb5993b64d0b0976f0bf2f0d44669866e8` | 同左 | 不变 |
| `E-AC2-DOC` | `1edb35f14a3676cecaad7c8d2b78ed75af2ca3ae43b43c20967bb85e73c77c47` | 同左 | 不变 |
| `E-AC2-DATA` | `22f9793f071de4173aed7bad4017d54edf8261692a14242694a4a17bd2da0ddc` | `e21061547e8adb405490d0119efd93b24fcdfd0b79966dffefc219963d3c5dea` | **已更新** |
| `E-AC3-DOC` | `9c27d477301e090e79cb48a3fafa892b86ddfce80e41723826cd2acfef5c950b` | 同左 | 不变 |
| `E-EVIDENCE-INDEX` | `d199f4843dea5c3c6b25ee293f1b54b93ce58bdb82fa9960c4eb6676041ca3ff` | 同左 | 不变 |
| `E-GOV-CHECK`（commit `b94dc3d86`） | `bc97d7a78e4db6e84899c415bc82a27e45b8874c16b31e71baf571c69e7b592e` | 同左 | 不变 |
| `E-RESOURCE-MANIFEST`（commit `82e86e97b`） | `133943d78481e43c0bb4d4766cf7691ca00fe7358506c249c50130b629befd99` | 同左 | 不变 |

**计数**：12 条 pin；**5 条值变化**（3 代码 + 2 证据）；7 条不变。

## 复核方式

```powershell
# 逐条用 commit blob 原始字节复核（不受工作树行尾影响）
$blob = git rev-parse "fb5065013:<repo-relative-path>"
git cat-file blob $blob > tmp.bin
(Get-FileHash tmp.bin -Algorithm SHA256).Hash.ToLower()
```

SAFETY-7 与 SAFETY-8 的独立 Review 均按此方式复核并全部一致（SAFETY-6 12/12、SAFETY-7 10/10）。

## 边界

- 只改 SAFETY-6 证据目录的行尾规则与 5 条 pin 值；**不改证据内容**（LF/CRLF 是同一文本）。
- 不改 SAFETY-6 的 AC 判定、Closeout 记录或历史 Review 字节。
- 其他历史 verification 目录保持原状（未批量 renormalize，避免大面积 diff）。
