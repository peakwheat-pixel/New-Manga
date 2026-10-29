using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Shell;

/// <summary>TopBand space tab: label + Ctrl+1/2/3 hint + active accent state.</summary>
public sealed class SpaceTabItem : ObservableObject
{
    private bool _isActive;

    public SpaceTabItem(SpaceId space, string label, string shortcut, Action onActivate)
    {
        Space = space;
        Label = label;
        Shortcut = shortcut;
        ActivateCommand = new RelayCommand(onActivate);
    }

    public SpaceId Space { get; }

    public string Label { get; }

    public string Shortcut { get; }

    public RelayCommand ActivateCommand { get; }

    public bool IsActive
    {
        get => _isActive;
        private set => Set(ref _isActive, value);
    }

    public void SetActive(bool active) => IsActive = active;
}

/// <summary>Breadcrumb level: space › book › chapter › page. Every non-last level is clickable.</summary>
public sealed record BreadcrumbItem(int Level, string Label, bool IsCurrent)
{
    public bool IsClickable => !IsCurrent;

    public bool ShowSeparator => Level > 0;
}

/// <summary>Attention aggregate (待确认 / 失败 / 阻塞 / 过期). Counts stay "—" until Run data is wired.</summary>
public sealed class AttentionItem
{
    public AttentionItem(
        string id,
        string label,
        string countText,
        NmStatus status,
        bool isWired,
        Action<AttentionItem> onActivate)
    {
        Id = id;
        Label = label;
        CountText = countText;
        Status = status;
        IsWired = isWired;
        ActivateCommand = new RelayCommand(() => onActivate(this));
    }

    public string Id { get; }

    public string Label { get; }

    public string CountText { get; }

    public NmStatus Status { get; }

    public bool IsWired { get; }

    public RelayCommand ActivateCommand { get; }

    public string Symbol => NmStatusInfo.Symbol(Status);

    public string Tooltip => IsWired ? $"{Label} {CountText}" : "能力待接入：Run 投影未合入（V11R-A-2 / V11R-B-4）";
}

/// <summary>One command-palette row: title + 「空间 · 模式 · 作用域」 + key hint + availability.</summary>
public sealed class CommandPaletteEntry
{
    public CommandPaletteEntry(ShellCommandDefinition definition, bool isContextual, Action<CommandPaletteEntry> onExecute)
    {
        Id = definition.Id;
        Title = definition.Title;
        Annotation = definition.ScopeLabel;
        GestureText = definition.GestureText;
        IsAvailable = definition.IsAvailable;
        UnavailableReason = definition.UnavailableReason;
        IsContextual = isContextual;
        ExecuteCommand = new RelayCommand(() => onExecute(this));
    }

    public string Id { get; }

    public string Title { get; }

    public string Annotation { get; }

    public string GestureText { get; }

    public bool IsAvailable { get; }

    public string? UnavailableReason { get; }

    public bool IsContextual { get; }

    public RelayCommand ExecuteCommand { get; }

    public string AvailabilityText => IsAvailable ? string.Empty : "能力待接入";
}

/// <summary>One Ctrl+P jump target (book / chapter / page).</summary>
public sealed class JumpEntry
{
    public JumpEntry(
        string kindLabel,
        string title,
        string subtitle,
        string? bookId,
        string? chapterId,
        int? pageIndex,
        string? pageId,
        Action<JumpEntry> onJump)
    {
        KindLabel = kindLabel;
        Title = title;
        Subtitle = subtitle;
        BookId = bookId;
        ChapterId = chapterId;
        PageIndex = pageIndex;
        PageId = pageId;
        JumpCommand = new RelayCommand(() => onJump(this));
    }

    public string KindLabel { get; }

    public string Title { get; }

    public string Subtitle { get; }

    public string? BookId { get; }

    public string? ChapterId { get; }

    public int? PageIndex { get; }

    public string? PageId { get; }

    public RelayCommand JumpCommand { get; }
}

/// <summary>F1 shortcut sheet group.</summary>
public sealed class HelpGroup
{
    public HelpGroup(string title, IReadOnlyList<HelpEntry> entries)
    {
        Title = title;
        Entries = entries;
    }

    public string Title { get; }

    public IReadOnlyList<HelpEntry> Entries { get; }
}

public sealed class HelpEntry
{
    public HelpEntry(string title, string gestureText, bool isAvailable)
    {
        Title = title;
        GestureText = gestureText;
        IsAvailable = isAvailable;
    }

    public string Title { get; }

    public string GestureText { get; }

    public bool IsAvailable { get; }

    public string AvailabilityText => IsAvailable ? string.Empty : "能力待接入";
}
