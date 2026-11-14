# ADJ-B-RESTART-HINT-1 证据

卡面：`doc/tasks/ADJ-B-RESTART-HINT-1.md`。基线 `eb8b5c82a`。

## 1. 裁决 B 的前提核实（本卡存在的理由）

裁决 B 要求「**保留并清楚展示**『修改模型配置后重启应用生效』」，并留下待核前提：
「**现有重启提示覆盖相关配置入口**……若提示不可见，应单独按实际故障开卡」。

**核实结果：提示没有覆盖配置入口。**

`RestartHint` 在全仓只有三处引用（已用 `Select-String` 全量确认）：

```
TranslateErrorText.cs:16: public const string RestartHint = "修改模型配置后需重启应用生效。";
TranslateErrorText.cs:20: "……修改模型配置后需重启应用生效。"（PROVIDER_NOT_CONFIGURED 文案）
TranslateErrorText.cs:41: public const string RestartHintShort = RestartHint;
```

- `RestartHintShort` **定义后从未被引用**；
- **没有任何 XAML/VM 绑定**这个常量；
- Provider 配置段（`ConsoleView.axaml` "② Provider 与凭据"）只有安全约束 banner、标题、四个按钮、列表，
  **没有重启提示**。

⇒ 用户改了模型配置后，只有**等翻译失败**才可能读到"需重启"。**裁定：缺陷成立（P2），按裁决 B 开卡修复。**

## 2. 修复

- `ConsoleViewModel`：`public string RestartHintText => TranslateErrorText.RestartHint;`（复用常量，不复制文案）
- `ConsoleView.axaml`：Provider 段安全 banner 下加 `<TextBlock Classes="meta" Text="{Binding RestartHintText}" />`

**一次编译失败已登记**：最初用 `<ctrl:AlertBanner Severity="Info" …>`，报
`AVLN3000: Unable to find suitable setter or adder for property Severity`（`Severity` 是受限枚举 `NmStatus`）。
改用 `TextBlock` 后编译通过。

## 3. 测试与判别力

新增 `apps/desktop-avalonia/tests/NewManga.App.Tests/RestartHintVisibilityTests.cs`（2 个）：

1. `ViewModel_ExposesTheSameSentenceAsTheErrorMapper` —— 断言 VM 的 `RestartHintText`
   **与 `TranslateErrorText.RestartHint` 逐字符相等**（防止文案分叉出第二份）。
2. `ProviderSection_PaintsTheRestartHint` —— 进入 Console → `SelectSectionById(ConsoleSectionId.Providers)`
   → 在**真实视图树**里找 `IsVisible` 的 `TextBlock`，断言其中**确实画出了那句提示**。

| 实验 | 结果 |
|---|---|
| 正常 | **2 passed / 0 skipped** |
| **删掉 XAML 里的 `TextBlock`** | **`ProviderSection_PaintsTheRestartHint` 变红**（已还原） |
| 无夹具 App.Tests 全量 | **953 / 0 / 11 / 964**（新增 2 个测试；skip 仍 11，未新增） |

## 4. 未做（如实登记）

- **「重启后确能使用新配置」未验证**：需要真实模型权重（`yolo11s-seg.onnx` 全工作区不存在）与真实
  Provider 凭据，属用户不可替代的实物。**标 `NOT_RUN`**。
  不能因为"提示已经显示了"就说裁决 B 的两个前提都满足了 —— **只满足了提示可见这一半**。
