# E8-RESIDUAL-1：E-8 残留项的判定

基线 `e56fa5cd8`。处置 `E8-STUDIO-BINDING-3` 留下的 1 条日志 + `StudioLeaveModal` 的测试缺口。

## 1. `CurrentPage.Image` 的 `'Value is null.'` —— **判定：预期的降级显示，不是缺陷**

### 代码事实（先读后判）

`ReaderOverlay.axaml:53`：

```xml
<Grid IsVisible="{Binding IsPaged}">
  <Image Source="{Binding CurrentPage.Image}"
         Stretch="Uniform"
         IsVisible="{Binding CurrentPageHasImage}" />
  <Border Classes="raised" IsVisible="{Binding !CurrentPageHasImage}">
    <TextBlock Text="页图不可用：Host 资源通道未接入或该页没有图像（不伪造图片）" />
    ...
```

`ReaderOverlayViewModel.cs`：

```csharp
public ReaderPageItem? CurrentPage => PageIndex >= 0 && PageIndex < PageCount ? Pages[PageIndex] : null;
/// <summary>Paged view state: true when the current page image really loaded through the Host channel.</summary>
public bool CurrentPageHasImage => CurrentPage?.HasImage == true;
```

### 判断

无页/无图时：
- `CurrentPageHasImage == false` ⇒ `Image` 被隐藏，**显示"页图不可用"的降级提示**（这是**设计好的**行为，注释明确写着"不伪造图片"）；
- 但 `Image.Source` 的绑定**仍会求值**，得到 `null` ⇒ 写一条 `[Binding]` 日志。

**⇒ 这是预期的降级路径产生的日志，不是缺陷。**

### 为什么不"修"

| 候选修法 | 为什么不做 |
|---|---|
| 给 `Source` 一个占位图 | **违反"不伪造图片"原则** —— 注释与产品语义都明确禁止 |
| 用 `TargetNullValue` 塞占位 | 同上 |
| 用 converter 在 null 时返回空 | 仍会产生一次求值；且引入一层间接，收益仅为消一条日志 |
| 把整块 `Image` 移出可视树 | 需要改布局结构，风险大于收益 |

**结论：保留这条日志。** 它是"该页确实没有图像"的**准确信号**，对排障有用。

## 2. `StudioLeaveModal` 的 3 处修复 —— **仍未测**

`LeaveSaveEnabled` 是**派生只读**属性（源码里只有 `Raise(nameof(LeaveSaveEnabled))`），
要驱动它需模拟完整"离开确认"状态机。本轮未做。

**如实登记（已由独立复核更正）**：这 3 处**不是修复，也没有测试**。

**更正两处**：①此前写"该弹窗 startup 时不构建"**不实** —— `StudioPageWorkspace:83` **无条件** `new StudioLeaveModal`（同一次启动记录到 8 条 HUD 错误即证明 workspace 已挂载）；
②这 3 处本来**就是 no-op** —— modal 继承同一个 Page VM，裸绑定本就可解析；改前 10 条日志里**没有一条** `LeaveBody/LeaveError/LeaveSaveEnabled` 就是反证。

## 3. 本轮结论

- E-8 的 **9/10 条**绑定错误：**已修复 + 单测 + 真实 App 三重证据**。
- 第 10 条：**判定为预期噪音，保留**（给出不修的理由）。
- `StudioLeaveModal` 的 3 处：**仅编译保证**（明确标注）。

**⇒ E-8 可按此口径收口**：核心缺陷（8 个 HUD 按钮永久失效 + inspector 标题不显示）已修并验证；
残留项有明确判定。
