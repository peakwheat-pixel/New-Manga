# P02-NEW-TIME-X6-AC1-AC7 I2 运行调查与结果报告

- **RunId**：`p02-newtime-ac-20261014-i2`
- **执行角色**：Codex（本轮临时承担 Owner）
- **产品源码基线**：`49d2a2f9c56462f5602b00ad4b824c5381abb1ab`
- **固定 EXE**：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-X6-BUILD-CARGO/apps/desktop/src-tauri/target/release/m2rc1-desktop.exe`，9,367,040 bytes，SHA-256 `92AC7B8EFB646FE77DF8245B13C9AF9314BEF415B2F0E007B1CDCEA729BC13FD`
- **隔离执行根**：`G:/CODEX/New Manga.workspace/task-envs/P02-NEW-TIME-X6-AC1-AC7/run-i2/`；创建时为新空目录。AC6 与 safety-check 的所有运行时写入均留在此 Task-local 根。
- **证据根**：`verification/P02-NEW-TIME-X6-AC1-AC7/runs/p02-newtime-ac-20261014-i2/`

## I2 结果

I2 只针对 DSH r3 的 R3-01、R3-04、R3-02、R3-06。AC1–AC5 未重跑，引用 I1 证据；I1 的有效场景退出码为 0。此限定仅描述 I1 的有效场景，不覆盖下表保留的失败尝试，也不覆盖 I2 AC6 失败尝试。

AC6 采集器已改为对表单控件读取 `value` / `placeholder`，且逐行记录是否实际执行 alpha 合成。I2 共有四次 AC6 启动尝试，均以 `node_exit_code=1` / `status=FAIL` / `verdict=ERROR` 结束，未产生新的 `ac6-contrast.json` 对比表。因此 AC6=`BLOCKED`；不得沿用 I1 的数字冒充本轮测量。

| I2 尝试 | 场景 / 端口 | 结果 | 证据 |
|---|---|---|---|
| a1 | `ac6-contrast` / 9334 | `FAIL / ERROR / node_exit_code=1`；等待 45 秒后 `CDP endpoint never appeared: TypeError: fetch failed` | `attempts/ac6-contrast-a1-failed/` |
| a2 | `ac6-contrast-a2` / 9335 | `FAIL / ERROR / node_exit_code=1`；同样未建立 CDP | `attempts/ac6-contrast-a2-failed/` |
| a3 | `ac6-contrast-a3` / 9336 | `FAIL / ERROR / node_exit_code=1`；进程快照确认对应 WebView2 命令行没有 `--remote-debugging-port`，端口无 listener | `attempts/ac6-contrast-a3-failed/` |
| a4 recovery | `ac6-contrast` / 9333 | `FAIL / ERROR / node_exit_code=1`；启动前 9333 空闲，仍在 45 秒后报 `CDP endpoint never appeared: TypeError: fetch failed`；失败后 9333 仍无 listener | `attempts/ac6-contrast-a4-failed/` |

Coordinator 已清除占用 9333 的两个 DSH 探测进程；本次按正确端口 9333 重跑前后该端口均空闲，但 CDP 端点仍未出现。当前证据不能把本次失败归因于端口占用，也不足以断言固定 EXE 不支持 CDP。因采集器未连接，`[data-testid="page-id-input"]` 在 I2 **没有样本行**，故无实际 `contrast_result`、`contrast_ratio` 或采样器 `reason` 可报告；运行器错误为 `CDP endpoint never appeared: TypeError: fetch failed`。**Alpha 合成分支本轮未触发**（采样器未连接，不能据此证明合成算法行为）。

## AC6 与 P-04

I1 的 `[data-testid="page-id-input"]` 因采样器只查 `textContent` 而被标为 `present:false`；该路径对 input 内容判断不成立。I2 修正路径使用 `value` / `placeholder`，但运行阻塞使输入框颜色、背景、contrast ratio 和 PASS/FAIL 均未实测。Review 已核实固定源码基线中的输入框采用不透明 `#101418`；这项源码事实不能替代 I2 的真实 WebView 样本。

**P-04（Harness observation，R3-01）**：I1 的 NOT_VERIFIABLE 来自表单控件文本过滤遗漏，不能归因于“半透明背景”“祖先链缺少不透明容器”或“alpha 合成保护”。本轮正确采样与对比度结果尚未取得；P-04 / R3-01=`BLOCKED`。本轮没有声称 alpha 合成已被证明。

## AC 状态与历史失败尝试

| AC | 本轮状态 | 证据 / 说明 |
|---|---|---|
| AC1–AC5 | I1 有效证据沿用；I2 未重跑 | `runs/p02-newtime-ac-20261014-i1/` |
| AC6 | **BLOCKED** | 四次 CDP 启动失败；a4 在已空闲的 9333 端口仍未连通；见 I2 `attempts/` |
| AC7 | **Owner scope 完成；DSH Review 与 Codex Gate 仍 pending** | 本报告、汇总及 Handoff 已写；不代表 Review 或 Gate 通过 |

I1 文档中“所有有效场景退出码为 0”的表述现限定为“**I1 有效场景**退出码为 0”。以下四个已保留失败尝试仍为 `status=FAIL / verdict=ERROR / node_exit_code=null`，未计入有效场景：

| 场景 | 原因 |
|---|---|
| `ac3-debounce-a2` | observer wrapper 未进入 `ACTIVE` |
| `ac4-write-refresh` | 未找到 `[data-testid="region-frame-syn-region-ac4-001"]` |
| `ac4-write-refresh-a2` | 未找到 `[data-testid="region-frame-syn-region-ac4-001"]` |
| `ac5-keyboard` | 未找到 `[data-testid="inspector-revision-history"]` |

I2 四个 AC6 启动失败保存在上表目录，实际 `node_exit_code=1`。a4 的 `node.stderr.log`、runner、metadata 与端口快照见 `attempts/ac6-contrast-a4-failed/`。复现核验读取 `runner-execution.json` 的字段是 `node_exit_code`。

## Safety-check 与静态检查

- `node --check`：`apps/desktop/frontend/e2e/p02-new-time/**/*.mjs` 共 11 个模块；聚合 exit 0。
- 命令：`node apps/desktop/frontend/e2e/p02-new-time/lib/safety-check.mjs`；exit 0；stdout 仅 1 个 JSON 块：

```json
{
  "status": "PASS",
  "failClosed": true,
  "errorCode": "EEXIST",
  "preexistingPreserved": true,
  "verifiedPath": "G:\\CODEX\\New Manga.workspace\\task-envs\\P02-NEW-TIME-X6-AC1-AC7\\run-i2\\tmp\\no-overwrite-check\\target.txt"
}
```

实际 stdout 与失败关闭证据保存在 `safety-check-output.json`。`safety-check.mjs` 现仅在 `import.meta.url === pathToFileURL(process.argv[1]).href` 时执行自检。

## R3 disposition

- **R3-01 — 未闭合（BLOCKED）**：表单控件读取已修正；必须的真实 AC6 JSON 未能采得，alpha 分支未触发。
- **R3-04 — 已闭合**：精确 CLI 守卫与上述 `COPYFILE_EXCL → EEXIST → 原字节保留` 自检通过。
- **R3-02 — 已闭合**：退出码文字限定为 I1 有效场景，并列出四个失败尝试及各自原因；核验字段为 `node_exit_code`。
- **R3-06 — 已闭合**：Task / rollup 的 AC7 已标记 Owner scope 完成，DSH Review 和 Codex Gate pending，不标 `PASS`。

Task 保持 `blocked`，不得标 `approved` / `done`。I2 是最后一轮；不再追加实现轮次。
