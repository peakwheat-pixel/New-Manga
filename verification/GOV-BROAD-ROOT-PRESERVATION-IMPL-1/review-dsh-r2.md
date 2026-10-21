# DeepSeek R2：实现批准及非阻断建议

session: session-0fa5098c-d90a-465f-b919-9eb52e3b8418；exit0；web_visibility=unverified

## 结论

**approved**（固定 `reviewed_head=71dc9bd592aecd347d038aef5abf326c1a0448f2`，`diff_base=f47c68969dac7d3cec0dddbe3fca4ea2fa7803db`，`source=528940a007ffc53ae7278a3ea007fa80d4a65f6d`）。

- **P0：0；P1：0。**
- 代码自 `528940a` 到 `71dc9bd` 未变（`tools/**` diff 为空）；新增两提交仅中断记录、5 目录保全和 Task/evidence metadata。
- 未发现实现、Spec、数据安全或最小实现层面的阻断问题。批准范围仅本实现与本 Task metadata；**不批准**父 Task done、r212 解除、真实 cleanup/迁移/归档、100/138 资源处置或删除审查探针目录。

## P2（不阻塞 merge，第 1 项建议 done 前修正）

1. **探针目录实际为 6 个，登记为 5 个。** 5 个 `dsh-probe-*` 已逐项登记为空并 `PRESERVE_REFERENCED`；但实际还存在第 6 个空目录 `G:/CODEX/New Manga/.dsh-mode-29c6eed9`（本审查早前 `os.mkdir(0o700)` 权限探针产生），未被 `review-probe-inventory.json` 或 Task Resource Manifest 登记。它不是用户源，内容为空，无删除授权；建议在 done 前补录或明确列为第 6 项范围例外，仍不得删除。
2. **`test-execution.json` 的 `log_sha256` 与 EV 日志 blob 不一致。** 其值为 agent-output 的 CRLF 原日志：`b95ebd0f…`、`7082e2f5…`、`13880f31…`；已提交 EV 的 LF 副本为 `222ae2b7…`（EV-16）、`096a00bf…`（EV-10）、`e37acea…`（EV-13）。逐字节比较仅差 CRLF/LF，内容一致，不影响 18/29/80 结果；但 `test-execution.json` 自身不能直接复核 EV 日志 blob，建议修正或注明“哈希指向 agent-output 原日志”。
3. **原子失败路径的窄竞态。** `_apply_broad_preservation` 在源身份复核时调用的是**原** `index._declared_identity`；若 `resolve_real_target` 在先前 `require(real == root_real_expected)` 与该调用之间发生变化，`_declared_identity` 可能先向原 index 追加 `DECL_ALIAS_REAL_TARGET` warning，再进入 fatal 路径，严格说不是“只添一项 fatal”。未复现，属 P2 加固建议：改用无副作用身份解析或只对 staged 容器调用。
4. **Spec 字面差异（信息未丢失）。** design §收口 3 写“message 包含 role、policy/源文件/locator/root/原 source_keep”；实现的 warning `message` 含 role/policy/root/source_keep，源文件与 locator 放在结构化 `file`/`locator` 字段。审计信息完整，但字面不完全一致，可作为后续文档/实现对齐项。

## 实际只读校验（当前 canonical 数据，22 EV 后实时计数）

- **同数据独立 scan（base 旧模块 vs WT 候选模块）：**
  - base：`24 errors / 2515 declarations / 256 warnings / 1838 protected roots`
  - candidate：`12 / 2527 / 268 / 1843`
  - 移除恰 **12** 条、新增错误 **0**；剩余 12 条按原顺序/完整 identity（含 `file`、`locator`、`message`）相等；移除集合与 policy 六条 `error_pair` 多重集完全相等。
  - `+12 Declaration / +12 warnings / +5 roots`；旧 protected 是 candidate 子集；`scanned` 的 declarations/errors/warnings 与新 index 一致；新增 warnings 全为 `DECL_BROAD_ROOT_PRESERVED`。
  - 旧 24 中其他 12 项保持：`DECL_ENV×4`、`DECL_UNKNOWN_DISPOSITION×2`、`FILE_UNREADABLE×3`、`DECL_RELATIVE_AMBIGUOUS×1`、`DECL_RELATIVE_UNRESOLVED×1`、`DECL_DESTINATION_UNRESOLVED×1`。
- **两旧源与例外表不变：** `SEC-FIX-PATH-ECHO-1.md` SHA `5961e38e…`、`WORKSPACE-CONSOLIDATION-1.md` SHA `e95bdfa8…`，与 policy 的 `origin_raw_sha256` 一致；69 项 non-declaration manifest 未修改（`CE6FF6…`）。
- **22 EV：** 逐项 `raw = blob = pin` 全部成立（EV-1…EV-22，EV-21/22 在 `b656c6acb`）；实际 `parse_markdown_declarations` 得 **EVIDENCE_PIN 22、errors 0**（Task 解析共 36 declarations）。
- **固定 head 与 canonical 检查：** `git diff --check f47c…71dc9bd` exit 0；canonical `tools/governance/check.ps1` **PASS**（2 个既有 warning）。
- **Owner 证据只读核对：** `new-tests-r3.log` 18 OK、`declaration-tests-r2.log` 29 OK、`hardening-tests-r2.log` 80 OK（127、0 skip 内容一致）；两个 incident replay 均为 `15 REJECT / 0 deleted / 0 violations`。
- **CLI 只读行为（前一轮，代码未变）：** candidate/WT 模块对 canonical 数据的 audit/clean/remove 均 **exit 2**、12 个错误拒绝；remove 使用 Task 自有空合成 inventory，仅拒绝探针，不是真实资源清单，未执行任何真实 apply/删除。
- **历史快照区分：** `runtime-proof.json` 的 `2483/1811→2495/1816` 是 `4d5a035` 时点快照；本次实时为 `2515/1838→2527/1843`，差异来自其后 22 EV/5 探针 metadata，不混称。

## 纯内存负例（无 fixture、无文件写入）

以 canonical 正常 parser 得到 24 基线 index（mock 将 `_apply_broad_preservation` 替换为 `_finish_declaration_scan`），再对副本调用 helper，使用 `io.BytesIO`/`mock.patch` 注入：

- **成功对照：** 12 errors、`+12` Declaration、`+12` warnings、`+5` roots。
- **14 个注入负例：** 坏 schema/未知 key/重复 ID/重复 JSON key/缺 pair/第 6 次 `_register_protective` 异常/计数阶段异常 → `POLICY_INVALID`；错误对 message 漂移 → `ERROR_MISMATCH`；source_keep 错/root 绝对 dot-dot → `RECORD_DRIFT`；源字节漂移 → `SOURCE_DRIFT`；untracked → `POLICY_UNTRACKED`；tracked 缺失 → `BROAD_PRESERVATION_POLICY_MISSING`；Git 失败 → `GIT_FAILED`。每例均为 `errors=25（原 24+1）`，`declarations=2515`、`roots=1838`、`warnings=256` 与原容器一致，确认未部分发布。
- **我的断言脚本用 deepcopy 对象身份比较，打印了 FAIL 标签；上述计数说明保留性成立。**
- **REAL_DRIFT：** 我的 mock 用 `str(path)==ws` 比较，而实际传入的是小写 normalized 路径，未命中，故**我未实际触发 REAL_DRIFT**；该项记为 NOT_RUN，仅静态确认代码存在 `REAL_DRIFT` 强制校验，Owner T10 结果不作为我的执行。未把该行成功状态当作代码放行。

## NOT_RUN / 未测

- **Reviewer 完整 18 fixture 复跑：NOT_RUN。** 授权 `reviewer-test-temp` 在沙箱外，创建/写入被拒绝；无 approval channel；未改 ACL/未升级。上一会话被 Codex 终止（exit `4294967295`），没有 final Review，不构成 PASS。本轮按指令未再尝试任何写入/fixture/探针。
- **canonical consolidate 全 100/138 资源盘点：未跑**；不声称实测全盘。
- **产品/构建、真实 apply/cleanup/迁移/归档/GC/prune/push/ACL/Legacy：未执行。**
- **REAL_DRIFT 内存负例：** 如上述 mock 未命中，NOT_RUN。
- 100 heads/138 WT 未重新枚举，未做任何增减；仅确认本审查 6 个空目录的事实状态。

## 5 目录保留例外（及第 6 个）

- 已登记 5 个：`dsh-probe-36zy1stn`、`6lu_0g3w`、`dagqohp7`、`npzn41rw`、`ut0j1y6p`；均空、原位 `PRESERVE_REFERENCED`，不是用户源，不构成清理授权，不得移动/删除。
- 实际第 6 个：`G:/CODEX/New Manga/.dsh-mode-29c6eed9`；同样空、由本审查探针产生，未登记。保留现状；建议 Codex 补录，不删除、不改 ACL。

## 范围与下一步

- 本批准仅覆盖 `71dc9bd` 上的实现（代码实际为 `528940a`）及本 Task metadata/evidence 链；**不批准**父 Task done、r212 解除、真实资源清理或 100/138 处置。
- 建议 Codex 正常 merge 后，在 canonical main 复验：旧 guard 24 → 新正式 12、剩余 12 完整 identity、五根/12 warnings、EV/check/diff；同时补录第 6 个空目录或明确例外，修正 `test-execution.json` 日志哈希说明；done 前保持 5/6 目录原位与 r212 禁令。
