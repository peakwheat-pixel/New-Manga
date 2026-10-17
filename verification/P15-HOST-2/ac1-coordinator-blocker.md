# P15-HOST-2 AC1：Coordinator 裁决请求

## 当前恢复点

- Task：`P15-HOST-2`
- Branch：`codex/P15-HOST-2`
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/P15-HOST-2`
- 检查时 HEAD：`fb232344de986de3cb8d6f25d1988970a596861a`
- 检查前工作树：clean
- 结果：AC1 `BLOCKED`；未开始实现、未运行产品测试。

## 不能唯一确定的契约事实

1. [P15_SETTINGS_IPC_CONTRACT.md](../../doc/contracts/P15_SETTINGS_IPC_CONTRACT.md) §2 L20–L27 声明“新增 WebView→Tauri 命令名固定如下”，表头为 `Tauri command`，G22 行逐字列出 `credential_put` / `credential_clear`；该行没有请求参数或响应形状。
2. 同一契约 §4.1 L107–L117 标题为“WebView 与 Host wire”，L109 写“WebView 只能调用以下无 Secret 的 production-only Host 命令”，随后给出的标识符却是 `PutCredential` / `ClearCredential`，并定义参数和响应：

   ```text
   PutCredential { target: CredentialTarget, intent: create | replace }
                 -> { state: configured, masked_hint?: string }
   ClearCredential { target: CredentialTarget } -> { state: missing }
   ```

3. §4.1 L119 又称 `PutCredential` 由 Tauri Host 提供“WebView 外的 Host 所有安全输入面”，没有说明该输入面的启动方式，也没有说明 `PutCredential` 是 WebView→Tauri invoke 名、内部 Host operation，还是外置 UI 流程名。
4. §4.2 L125–L135 对受信 Host→Core wire 则是明确的：`BindProfileCredential { target, credential_ref }` 与 `ClearProfileCredential { target }`，并明确它们只允许 Host 经受信路由调用，不注册为 WebView command。此 Host-only 边界没有歧义，也不应改动。

## 尚存的实现解释

1. **snake_case Tauri commands + Host 外置输入**：WebView invoke `credential_put` / `credential_clear`（§2 表格的字面名称），Put 的安全输入由 Host 在 WebView 外呈现；参数/返回使用 §4.1 的 `target`、`intent` 和状态投影。
2. **§4.1 操作作为 WebView invoke**：WebView invoke `PutCredential` / `ClearCredential`（§4.1 的字面名称）并只传 `target` / `intent`；调用后由 Host 打开其所有的 WebView 外安全输入面。此解释与 §2 的固定 Tauri 名称表冲突，且 L119 未明确输入面由该 invoke 启动。

此外，若 L119 意味着凭据输入必须完全由 Host 侧原生 UI 启动、WebView 不可调用 Put 操作，则这又与 L109 的“WebView 只能调用以下命令”及任务 AC2 要求的 WebView 可达入口冲突。现有文字无法排除该读法。

## 请 Coordinator 明确裁决

请对下列事项给出书面、可执行的唯一 wire 定案；若要修订冻结契约，请另行授权/派发契约修订，不由本 Task 擅改：

1. WebView 可 invoke 的 Tauri command 名究竟是 `credential_put` / `credential_clear`，还是 `PutCredential` / `ClearCredential`？请逐项列出 invoke 名、参数键及响应键。
2. `PutCredential` 的安全输入面由什么动作启动：WebView 调用无 Secret 命令后由 Host 打开原生输入，还是 Host 独立启动输入且 WebView 不调用 Put？`ClearCredential` 的 WebView 调用方式是否仍存在？
3. 明确 Host 内部唯一允许调用 Core 的 wire 为 §4.2 的 `BindProfileCredential` / `ClearProfileCredential`，并确认仍不得加入任何 WebView allowlist。

在裁决到达前，不实现 WebView command、Host 输入 UI、Credential Manager 写入/绑定，也不改四处 surface；不猜测名称、不改变 payload、不伪造成功。待续后再按裁决完成安全反例测试、surface-sync 与基线验证。

## 依据及交叉核对

- 当前 Task 的 AC1 已要求遇歧义停下上报；见 [P15-HOST-2.md](../../doc/tasks/P15-HOST-2.md#L37)。
- P15-HOST-1 记录了相同的 `credential_put` / `credential_clear` 未实现范围冲突；见 [P15-HOST-1.md](../../doc/tasks/P15-HOST-1.md#L71)。
- P15-C1-FU2 closeout 称命名/版本歧义已消除（[P15-C1-FU2.md](../../doc/tasks/P15-C1-FU2.md#L73)），但其契约改动只修订 §4.2 minor 2.6→2.7，没有更改 §2 或 §4.1 命令名称/输入面语义（同文件 L71）。因此该 closeout 不能消解本报告所列的命名歧义。
- 由于 AC1 是实现硬门，Rust source、packaged、Core pytest、frontend、host-only 复扫及 surface-sync 复核均 `NOT_RUN`；这不是测试通过声明。
