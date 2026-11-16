# GOV-EOL-PIN-1 延伸（`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` 固定 LF）— Codex 书面裁定与 DSH 采纳

- **裁定者**：Codex（`codex exec`，model `gpt-6-luna`，reasoning `xhigh`，只读沙箱，cwd = 仓库根）
- **派发者**：DSH（Lead / Architect / Integrator）
- **裁定时间**：2026-11-16
- **被裁 head**：`d2707dcee`（裁定前最后 push）
- **裁定结论**：`APPROVED_WITH_CONDITIONS`
- **裁定原文**：`G:\CODEX\New Manga.workspace\tmp-dsh\r3\codex-eol-ruling.md`（3,062 B）
- **裁定者自述限制（如实保留）**：其本机命令执行未能启动（Windows `CreateProcessAsUserW failed: 740`），
  因此**没有独立复核**仓库 pin 路径清单；要求 DSH 入库前按条件 3、4 自行生成路径与数量清单。

## 裁定原文（逐字）

```
verdict: APPROVED_WITH_CONDITIONS
Q1: A — 仅为 `doc/REBASELINE_PLAN.md` 和 `doc/STATUS.md` 固定 `eol=lf`，解决签出换行导致的预算波动。
Q2: C — 保留原 pin，并为 WORKTREE 口径增加一个经验证的 LF 对照摘要；只接受这两个预先记录的精确摘要。

条件（逐条编号，必须可机械核验）:
1. `.gitattributes` 只新增上述两条精确路径规则；不得扩大为 `doc/*.md`。验收时对两路径执行 `git check-attr eol`，结果必须为 `lf`。
2. 新签出验收按实际字节运行预算门禁：`REBASELINE_PLAN.md` 为 6939 B、`STATUS.md` 为 3156 B，且现有预算检查通过。不得通过提高预算替代 EOL 固定；提高预算会放宽内容长度门禁。
3. 对 Q1 的 pin 影响按路径精确枚举所有已入库 SHA-256 pin，并将记录摘要与 LF、CRLF 两种签出字节的摘要比较。按已给出的当前字节事实，这两份文件从当前工作树到 `eol=lf` 签出的字节差为 0，预期失效数为 **0**。若枚举发现记录的是 CRLF 摘要、而新签出只产生 LF 摘要，则逐条保留旧摘要并记录 LF 对照摘要后再启用规则；不得静默重算覆盖旧值。
4. Q2 保留原 `pin.channel` 与原摘要作为历史事实。对 13 条明确标为 `WORKTREE` 的记录，以及 `LEGACY-SHELL-ARCHIVE-1` 的 worktree 口径 archive 证据行，记录对应 LF 字节的 SHA-256；迁移前须证明原字节仅经 CRLF→LF 转换即可与该 LF 字节逐字节相等。按给定明细，这是 **14 条 worktree 口径记录**；2 条 `BLOB` 口径记录保持原样。
5. 校验只允许与该 pin 绑定的原 WORKTREE 摘要或其已登记的 LF 对照摘要精确匹配，并在告警中写明命中的摘要口径。不得运行时宽泛规范化空白、内容或元数据后再比较。

负例要求:
1. 在换行不变的情况下，对任一受 pin 文件增加、删除或替换一个内容字节，校验必须以 `SOURCE_DRIFT` 失败。
2. 混合换行或其他非登记字节表示不得因"归一化后相似"而通过；摘要候选必须按文件路径和 pin 记录绑定，跨文件摘要不得通过。
3. 对照摘要生成时，若 CRLF→LF 后不等于对应 Git blob（或 archive 证据的 LF 对照字节），迁移必须失败并交由历史证据裁定，不得自动补录为有效候选。

风险与遗留:
- 只加两条规则能固定这两份预算门禁；扩为 `doc/*.md` 会扩大签出字节变化面，增加非必要的 pin 迁移风险。提高预算则会放松门禁，且仍保留换行敏感性。
- 单独采用 Q2-A、对现有单一摘要做"worktree SHA 或 blob SHA"比较，并不能让 CRLF 摘要自动匹配 LF 签出；必须先把对应的第二个精确摘要登记为允许值。
- 本次本机命令执行未能启动，Windows 返回 `CreateProcessAsUserW failed: 740`，因此没有独立复核仓库 pin 路径清单。DSH 入库前应按条件 3、4 生成路径与数量清单；若 Q1 发现非零失效项，先完成逐项 pin 迁移。
```

## DSH 采纳（Lead 名义）

采纳结论：**按 Q1=A、Q2=C 实施**，条件 1–5 与负例 1–3 全部落实；裁定者未独立复核的部分由 DSH 以实测补齐并记录。

### 对条件 3 的实测（pin 枚举）

`doc/REBASELINE_PLAN.md` / `doc/STATUS.md` 被 3 条已入库 Canonical Evidence 行引用：

| 卡片 | evidence_id | 路径 | commit | 记录摘要（前 12 位） |
|---|---|---|---|---|
| AUDIT14-V1-MANIFEST-1 | AUDIT14-STATUS-1 | `doc/STATUS.md` | `90301427380e67ec72cd253a721fe53214e43333` | `7c418a73d0ce` |
| FEA-DOC-RECONCILE-1 | EV-RECON-STATUS | `doc/STATUS.md` | `-` | `59e7bb9f6dde` |
| FEA-DOC-RECONCILE-1 | EV-RECON-PLAN | `doc/REBASELINE_PLAN.md` | `-` | `a2d9c7fda96e` |

- 这 3 条都 pin 在**各自 commit**（或历史字节）上，与当前工作树字节无关；`eol=lf` 只影响**未来签出**。
  当前工作树两份文件已是 LF（`sha_lf = ecd5d129…` / `0a0fc119…`），所以签出规则生效后字节**不变** ⇒ **失效数 0**，与裁定预期一致。
- 未对任何历史 pin 重算或覆盖旧值。

### 对条件 4 的实测（14 条 worktree 口径的对照摘要）

14 条 WORKTREE 口径记录（13 条 `pinned_defect_retentions` 的 `WORKTREE` 通道 + `LEGACY-SHELL-ARCHIVE-1` 的 archive 证据行）逐条：

- 记录摘要 = 当前签出字节的 SHA-256（迁移前实测一致，未改动 `sha256` 字段）；
- 对照摘要 `sha256_alt` = 同字节仅做 `CRLF↔LF` 转换后的 SHA-256，`alt_kind` 记录方向：
  - 9 条为纯 LF 记录 → `alt_kind=CRLF`（对照为 CRLF 形态）；
  - 5 条为 CRLF 记录（`FEA-11-RENDITION-1`×2、`FEA-11-RUN-GRANT-2`×2、`legacy-shell/README.md`）→ `alt_kind=LF`；
- **迁移前提已逐条证明**：其 LF 形态与 `git cat-file blob HEAD:<path>` **逐字节相等**（否则迁移脚本报错、拒绝写入）。
  2 条 `BLOB` 口径记录保持原样（schema 亦不允许它们带 `sha256_alt`/`alt_kind`，由 `exact` 键集强制）。

### 对条件 5 的实现

`clean_workspace.py` 的保留态校验改为：对**实时字节**取一次 SHA-256，与 `sha256`（命中记 `pin_basis=ORIGINAL`）
或 `sha256_alt`（命中记 `pin_basis=ALT_LF`/`ALT_CRLF`）**精确比对**；两者都不命中 ⇒ `SOURCE_DRIFT` 致命失败。
运行期不做任何空白/内容/元数据规范化。

### 对负例 1–3 的落实

`tools/governance/tests/test_historical_binding_policy.py` 新增/改写 3 项：
- `test_worktree_alt_digest_is_a_pure_line_ending_transform`：对照摘要必须等于「仅换行转换」的字节摘要，且 LF 形态 == 提交 blob；BLOB 记录不得携带对照摘要。
- `test_retention_rejects_content_change_and_mixed_eol`：改 1 个内容字节（换行不变）⇒ 两个登记摘要都不命中；混合换行 ⇒ 都不命中；**跨文件摘要不得解锁本记录**。
- `test_pinned_retention_pins_still_verify`：实时字节必须命中两个登记摘要之一。

### 未采纳项（如有）

无。裁定未提出与本项目硬约束（禁止绿洗、不碰历史证据字节）冲突的要求。
