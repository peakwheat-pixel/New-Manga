using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Media;

namespace NewManga.App.Controls;

/// <summary>
/// FEA-06-RESIDUAL-4B (4A spec v1.1 S5/AC4): the ONLY failure/empty states the compare panel can
/// show. The three failure reasons are panel-local codes -- they are deliberately NOT members of the
/// frozen <c>DraftErrorMap</c> (19-key closed set, 4A P2-5) and never travel on the wire.
/// </summary>
public enum RegionCompareStatus
{
    /// <summary>Both layers are available (L1 authoritative projection + L2 live working copy).</summary>
    Ready,

    /// <summary>The page really has no regions (<c>regions: []</c> AND a non-null <c>page_size</c>).</summary>
    EmptyPage,

    /// <summary>① Host not ready: the projection was never requested.</summary>
    HostNotReady,

    /// <summary>② The port returned null (IPC failure / read refusal / degraded host).</summary>
    ProjectionUnavailable,

    /// <summary>③ Target region missing from the result, or an unknown page (empty regions + null page_size).</summary>
    TargetNotFound,
}

/// <summary>
/// FEA-06-RESIDUAL-4B (4A P2-5): the panel-local typed reason codes. Kept out of
/// <c>DraftErrorMap</c> on purpose: adding them there would break the FEA-05 §3 19-key closed set.
/// </summary>
public static class RegionCompareReasonCodes
{
    public const string HostNotReady = "HOST_NOT_READY";
    public const string ProjectionUnavailable = "REGION_TEXT_PROJECTION_UNAVAILABLE";
    public const string TargetNotFound = "TARGET_NOT_FOUND";
}

/// <summary>FEA-06-RESIDUAL-4B (4A spec S2): one read-only layer of the compare panel.</summary>
public sealed record RegionCompareLayer(
    string Title,
    string RegionType,
    string SfxPolicy,
    string Origin,
    int RevisionNo,
    string Text,
    string TextSource);

/// <summary>
/// FEA-06-RESIDUAL-4B (4A spec S1/S2/S5): the immutable content of one compare panel. Exactly one of
/// the two shapes is populated: a failure/empty state (<see cref="ReasonCode"/> and/or
/// <see cref="Status"/>, both layers null) or a ready state (both layers present).
/// </summary>
public sealed record RegionTextCompare(
    RegionCompareStatus Status,
    string ReasonCode,
    string ReasonText,
    RegionCompareLayer? BaseLayer,
    RegionCompareLayer? WorkingLayer,
    bool HasRevisionDrift,
    string? DriftNotice);

/// <summary>
/// FEA-06-RESIDUAL-4B (4A spec S4/S6; AC3/AC4/AC5): the read-only「查看对照」panel. Two vertically
/// stacked layers -- L1 committed base text on top, L2 current working copy below -- with a title bar
/// each, wrapping text and NO fixed height. There is deliberately no input control and no
/// "apply/overwrite" action anywhere in the panel (4A S5: compare only, never a one-click overwrite).
/// A failure or empty state renders ONLY its message plus the close button, so an unavailable
/// projection can never fabricate compare content (4A S5 negative invariant).
/// </summary>
public sealed class RegionTextComparePanel : UserControl
{
    public const string PanelTitle = "区域文本对照";
    public const string BaseTitle = "基底文本（只读）";
    public const string WorkingTitle = "当前工作副本（只读）";
    public const string EmptyText = "该页没有区域";
    public const string CloseText = "关闭";

    /// <summary>4A S2 empty-value convention: the real value is empty, nothing is substituted.</summary>
    public const string EmptyValueText = "（空文本）";

    private readonly TextBlock? _workingText;

    public RegionTextComparePanel(RegionTextCompare compare)
    {
        ArgumentNullException.ThrowIfNull(compare);
        Compare = compare;

        CloseButton = FluentUi.Button(CloseText, "fluent-secondary",
            () => CloseRequested?.Invoke(this, EventArgs.Empty), CloseText);

        var layout = FluentUi.Stack("fluent-page-layout");
        layout.Children.Add(FluentUi.Text(PanelTitle, "fluent-status-text"));
        if (compare.DriftNotice is { Length: > 0 } notice)
        {
            layout.Children.Add(FluentUi.Text(notice, "fluent-subtle-text"));
        }

        if (compare.Status == RegionCompareStatus.EmptyPage)
        {
            layout.Children.Add(FluentUi.Text(EmptyText, "fluent-subtle-text"));
        }

        if (compare.ReasonCode.Length > 0)
        {
            // The typed code stays machine-readable on the accessibility name; the visible text is
            // the human reason. Both are panel-local -- nothing here is a wire/DraftErrorMap code.
            var reason = FluentUi.Text(compare.ReasonText, "fluent-status-text");
            AutomationProperties.SetName(reason, compare.ReasonCode);
            layout.Children.Add(reason);
        }

        if (compare.BaseLayer is { } baseLayer)
        {
            layout.Children.Add(BuildLayer(baseLayer, out _));
        }

        if (compare.WorkingLayer is { } workingLayer)
        {
            layout.Children.Add(BuildLayer(workingLayer, out _workingText));
        }

        layout.Children.Add(CloseButton);
        AutomationProperties.SetName(this, PanelTitle);
        Content = FluentUi.Card(layout);
    }

    public RegionTextCompare Compare { get; }

    public RegionCompareStatus Status => Compare.Status;

    public string ReasonCode => Compare.ReasonCode;

    public string ReasonText => Compare.ReasonText;

    public RegionCompareLayer? BaseLayer => Compare.BaseLayer;

    public RegionCompareLayer? WorkingLayer => Compare.WorkingLayer;

    public bool HasRevisionDrift => Compare.HasRevisionDrift;

    public Button CloseButton { get; }

    /// <summary>Raised by the close button and by <c>Esc</c>; the owner decides what "closed" means.</summary>
    public event EventHandler? CloseRequested;

    /// <summary>
    /// 4A S2/S5: the live L2 text. The workbench updates this on every <c>DraftText</c> change so the
    /// panel always shows the CURRENT working copy (never the persisted draft patch, 4A P2-4).
    /// A failure/empty panel has no L2 block, so this is a no-op there -- by design.
    /// </summary>
    public void UpdateWorkingText(string? text)
    {
        if (_workingText is null)
        {
            return;
        }

        var value = DisplayValue(text);
        if (string.Equals(_workingText.Text, value, StringComparison.Ordinal))
        {
            return;
        }

        _workingText.Text = value;
        AutomationProperties.SetName(_workingText, value);
    }

    /// <summary>4A S2: an empty value renders as the "empty" label, never as another layer's value.</summary>
    public static string DisplayValue(string? value) =>
        string.IsNullOrEmpty(value) ? EmptyValueText : value;

    /// <summary>
    /// Keyboard path for <c>Esc</c>. Exposed with the same <c>*ForTest</c> seam name the shell and
    /// surface already use, so the test drives the REAL handler instead of a copy of its logic.
    /// </summary>
    public bool HandleKeyForTest(Key key)
    {
        if (key != Key.Escape)
        {
            return false;
        }

        CloseRequested?.Invoke(this, EventArgs.Empty);
        return true;
    }

    private static Control BuildLayer(RegionCompareLayer layer, out TextBlock textBlock)
    {
        var stack = FluentUi.Stack("fluent-page-layout");
        AutomationProperties.SetName(stack, layer.Title);
        stack.Children.Add(FluentUi.Text(layer.Title, "fluent-status-text"));
        stack.Children.Add(FluentUi.Text($"区域类型：{layer.RegionType}", "fluent-subtle-text"));
        stack.Children.Add(FluentUi.Text($"SFX 策略：{layer.SfxPolicy}", "fluent-subtle-text"));
        stack.Children.Add(FluentUi.Text($"来源：{layer.Origin} · 修订：r{layer.RevisionNo}", "fluent-subtle-text"));
        textBlock = FluentUi.Text(layer.Text, "fluent-status-text");
        textBlock.TextWrapping = TextWrapping.Wrap;
        AutomationProperties.SetName(textBlock, layer.Text);
        stack.Children.Add(textBlock);
        stack.Children.Add(FluentUi.Text($"文本来源：{layer.TextSource}", "fluent-subtle-text"));
        return FluentUi.Card(stack);
    }
}
