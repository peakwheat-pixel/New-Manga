# CONTRACT-UNFREEZE-2026-11-02

**任务**：FEA-05-PORT-1（Draft 端口面 + CoreClient registry + Region 契约 UNFREEZE）
**执行**：DSH（Lead / Architect / Integrator）
**日期**：2026-11-02
**依据**：范围冻结 v4（`doc/reviews/FEA-05-PORT-1-scope-r4.md` approved，P0/P1=0）；FEA-05-WIRE-1 W-6 把「端口面 + 不变式」留本卡。

---

## 1. 冻结物 A：`V11R_REGION_WRITE_CONTRACT.md` v1.5 → v1.6

| 项 | 内容 |
|---|---|
| 原状态 | `FROZEN` v1.5（2026-10-30） |
| 变更 | ① 头部状态/版本（v1.5→v1.6）；② §命令清册增加 `DraftsCommandNames`（6 条：`drafts_open`/`drafts_patch`/`drafts_prepare`/`drafts_apply`/`drafts_status`/`drafts_discard`）；③ 不变式由「追加集恰为 `V11RAdditiveCommandNames`（10 写 + 1 读）」改为「追加集 = `RegionWrite ∪ RegionRead ∪ Drafts`（各家族声明集合之并）」；④ §8 验证表同改；⑤ 变更记录 v1.6 |
| 理由 | `RegionWriteCommandTests:107-117` 的两条断言（additive == V11RAdditiveCommandNames 且 additive == RegionWrite ∪ RegionRead）在加入 Drafts 家族后不可同时成立；不能靠不注册规避（`RegistrySurface_IsFullyDeclared` 会失败） |
| 影响 | C078–C083 已在 `V11R_COMMAND_CONTRACT_V1.md` §8.2 登记（PENDING）；CoreClient registry 追加 6 条后 additive = 17 |
| 新 pin | **无**（Region 契约不在 15 份 pin 内；pin 仅 C-07 有） |
| 复核 | 由 FEA-05-PORT-1 实现复核席位独立复核（不参与实现） |

## 2. 冻结物 B：C-07 库存 `FEA-C07_API_INVENTORY.md`

| 项 | 内容 |
|---|---|
| 原状态 | `FROZEN`（2026-11-01）；pin `17c8f701…` |
| 变更 | `IHostController` 47→54（+7 Draft 端口方法：`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync`/`ApplyCandidatesAsync`/`GetDraftAsync`/`ListDraftsAsync`/`DiscardDraftAsync`）；合计 54→61；变更类别 11→18；生成日期/HEAD 更新 |
| 理由 | C-07 要求「新增/删除端口方法时同一 Task 内同步更新清单」（`FEA-C07_API_INVENTORY.md` 用途节） |
| 新 pin | **最终 `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714`**（写入 `FEA-CONTRACT-FROZEN-C07.md` §1；中间值 `5c48083f…` 系成员表首版、后因变更类别文本又改，已废弃） |
| 复核 | 按 `FROZEN-C07:15-17` 需**重新独立复核**；本轮由 FEA-05-PORT-1 实现复核席位执行（独立上下文） |

## 3. 纪律

- 两份冻结物的 UNFREEZE 均由本记录承载；新 pin 已写入 `FEA-CONTRACT-FROZEN-C07.md`；`verify_pins.ps1` 必须 **15/15 PASS**（pin 数量不变）。
- 重新冻结在独立复核通过后由 DSH 执行（本记录 + 复核报告 + pin 更新即冻结依据）。
- 不改本记录未列出的冻结字节；`V11R_REGION_WRITE_CONTRACT.md` 的 C067–C077 既有条目与 C-02/C-03/C-04b/C-08 不动。
