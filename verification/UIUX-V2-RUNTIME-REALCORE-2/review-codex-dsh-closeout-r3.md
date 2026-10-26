verdict: acceptable

task_id: UIUX-V2-RUNTIME-REALCORE-2
reviewer: Codex
author: DSH
base_commit: 0718482e5
reviewed_head: a045d4f14fe4e7ff38b5bc421faa6b73ad5da66d
decision: approved
scope: 仅复核 apps/desktop/frontend/e2e/uiux-v2/run.mjs 相对 0718482e5 的变更及 S8 控制流；未修改实现、未 commit、未重跑 E2E。

# Review：DSH closeout r3

## 结论

r2 指出的降级缺陷已修复。`cdpInjectionUnavailable` 在 S8 初始化为 `false`，只有 `pngInput.inputNodeId` 不大于 0、进入“无 input[type=file]”分支时才置为 `true`。进入白名单转换循环前，该标志已完成置位；只有 `FAIL`、标志为真、且标签命中四项白名单时才转为 `HUMAN_VERIFY`。

## 必答问题

1. **置位点对应注入前置不可用：是。** 唯一置位位于首次 `findImportFileInput(cdp)` 的 `else`，即 `inputNodeId` 不大于 0 的分支；不是通用异常处理，也不由后续断言结果触发。若查找本身抛错，会进入 catch，标志保持 `false`，因此不会误降级。
2. **注入成功时四条白名单 FAIL 不会降级：是。** `inputNodeId > 0` 走注入分支，不会置位；即使真实 PNG 或不支持格式的 `setImportFileInput` 成功后，错误码断言失败，循环条件中的 `cdpInjectionUnavailable` 为 false，状态仍为 `FAIL`。标签命中本身不足以降级。
3. **无顺序、作用域或 S8 分支漏洞：未发现。** 标志在 S8 块内声明，置位在后续降级循环之前。无书籍、查找/其他步骤异常等绕过探测的分支保持 false，倾向保留 FAIL；未见其他置位路径。diff 中无可见语义问题；else 分支新增一行缩进不齐，仅格式瑕疵。
4. **run-i36 证据：** canonical `run-i36/report.json` 的 S8 记录 `inputNodeId=0`，4 条白名单项均为 `HUMAN_VERIFY`，其他四条断言 PASS，统计为 4 PASS / 0 FAIL / 5 HUMAN_VERIFY。它与不可用路径相符，但没有实际覆盖“inputNodeId>0 且错误码校验失败”的反向场景；此项由静态控制流确认，不把声称的 10/10 当作该反向场景的动态证明。

## 审查覆盖与限制

- 执行只读 diff 检查：`git diff 0718482e5 HEAD -- apps/desktop/frontend/e2e/uiux-v2/run.mjs`，并追踪 S8 标志初始化、唯一写入点、白名单和转换循环。
- 未重跑 run-i36 或其他测试；未覆盖人工原生选择器流程。
- 复审仅确认本次 r2 P1 的修复，不重新批准 S8 导入端到端人工验证项。

