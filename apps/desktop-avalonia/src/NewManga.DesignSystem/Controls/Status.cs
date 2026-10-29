using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;

namespace NewManga.DesignSystem.Controls;

/// <summary>
/// The nine status states of the frozen design system: the seven pipeline states plus not-started and
/// locked (DESIGN_SYSTEM §2.2). Every status is encoded with hue + symbol + text label.
/// </summary>
public enum StatusKind
{
    Queued,
    Running,
    Done,
    Failed,
    Blocked,
    Stale,
    Skipped,
    NotStarted,
    Locked,
}

/// <summary>
/// The single source of the status language: symbol (<see cref="NmStatusSymbols"/>), resource-key class
/// and human label. UI code must not invent status symbols or colors itself (contract §2.3).
/// </summary>
public static class StatusCatalog
{
    /// <summary>Style class used to tint a control with the status hue (e.g. <c>StatusGlyph.failed</c>).</summary>
    public static string ClassName(StatusKind kind) => kind switch
    {
        StatusKind.Queued => "queued",
        StatusKind.Running => "running",
        StatusKind.Done => "done",
        StatusKind.Failed => "failed",
        StatusKind.Blocked => "blocked",
        StatusKind.Stale => "stale",
        StatusKind.Skipped => "skipped",
        StatusKind.NotStarted => "notstarted",
        StatusKind.Locked => "locked",
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, null),
    };

    /// <summary>The frozen symbol channel for this status.</summary>
    public static string Symbol(StatusKind kind) => kind switch
    {
        StatusKind.Queued => NmStatusSymbols.Queued,
        StatusKind.Running => NmStatusSymbols.Running,
        StatusKind.Done => NmStatusSymbols.Done,
        StatusKind.Failed => NmStatusSymbols.Failed,
        StatusKind.Blocked => NmStatusSymbols.Blocked,
        StatusKind.Stale => NmStatusSymbols.Stale,
        StatusKind.Skipped => NmStatusSymbols.Skipped,
        StatusKind.NotStarted => NmStatusSymbols.NotStarted,
        StatusKind.Locked => NmStatusSymbols.Locked,
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, null),
    };

    /// <summary>The visible text label that completes the three-channel encoding.</summary>
    public static string Label(StatusKind kind) => kind switch
    {
        StatusKind.Queued => "排队",
        StatusKind.Running => "进行中",
        StatusKind.Done => "完成",
        StatusKind.Failed => "失败",
        StatusKind.Blocked => "阻塞",
        StatusKind.Stale => "过期",
        StatusKind.Skipped => "跳过",
        StatusKind.NotStarted => "未开始",
        StatusKind.Locked => "锁定",
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, null),
    };

    /// <summary>The <c>Nm.Color.Status.*</c>/<c>Nm.Color.Text.Disabled</c> key carrying this status hue.</summary>
    public static string ColorKey(StatusKind kind) => kind switch
    {
        StatusKind.Queued => NmKeys.Color.Status.Queued,
        StatusKind.Running => NmKeys.Color.Status.Running,
        StatusKind.Done => NmKeys.Color.Status.Done,
        StatusKind.Failed => NmKeys.Color.Status.Failed,
        StatusKind.Blocked => NmKeys.Color.Status.Blocked,
        StatusKind.Stale => NmKeys.Color.Status.Stale,
        StatusKind.Skipped => NmKeys.Color.Status.Skipped,
        StatusKind.NotStarted => NmKeys.Color.Text.Disabled,
        StatusKind.Locked => NmKeys.Color.Status.Blocked,
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, null),
    };

    /// <summary>The <c>Nm.Color.StatusMuted.*</c> key used as a status-tinted surface, when one exists.</summary>
    public static string? MutedColorKey(StatusKind kind) => kind switch
    {
        StatusKind.Queued => NmKeys.Color.StatusMuted.Queued,
        StatusKind.Running => NmKeys.Color.StatusMuted.Running,
        StatusKind.Done => NmKeys.Color.StatusMuted.Done,
        StatusKind.Failed => NmKeys.Color.StatusMuted.Failed,
        StatusKind.Blocked or StatusKind.Locked => NmKeys.Color.StatusMuted.Blocked,
        StatusKind.Stale => NmKeys.Color.StatusMuted.Stale,
        StatusKind.Skipped => NmKeys.Color.StatusMuted.Skipped,
        _ => null,
    };
}

/// <summary>
/// Symbol-only status channel: renders the frozen symbol and applies the status hue class. It is a
/// <see cref="TextBlock"/> so it inherits the typography stack and can be inline with text.
/// </summary>
public sealed class StatusGlyph : TextBlock
{
    /// <summary>The status whose symbol/hue is displayed.</summary>
    public static readonly StyledProperty<StatusKind> StatusProperty =
        AvaloniaProperty.Register<StatusGlyph, StatusKind>(nameof(Status));

    public StatusGlyph()
    {
        Classes.Add("status-glyph");
        Apply();
    }

    /// <summary>Gets or sets the status whose symbol/hue is displayed.</summary>
    public StatusKind Status
    {
        get => GetValue(StatusProperty);
        set => SetValue(StatusProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == StatusProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        Text = StatusCatalog.Symbol(Status);
        foreach (var kind in Enum.GetValues<StatusKind>())
        {
            Classes.Set(StatusCatalog.ClassName(kind), kind == Status);
        }
    }
}
