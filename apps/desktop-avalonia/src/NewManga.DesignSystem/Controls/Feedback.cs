using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace NewManga.DesignSystem.Controls;

/// <summary>
/// EmptyState (contract §3.2): one sentence + one primary action + an optional fact line. No
/// illustrations (DESIGN_SYSTEM §6.5).
/// </summary>
public sealed class EmptyState : StackPanel
{
    /// <summary>Headline sentence.</summary>
    public static readonly StyledProperty<string?> TitleProperty =
        AvaloniaProperty.Register<EmptyState, string?>(nameof(Title), "暂无内容");

    /// <summary>Optional supporting fact line.</summary>
    public static readonly StyledProperty<string?> HintProperty =
        AvaloniaProperty.Register<EmptyState, string?>(nameof(Hint));

    /// <summary>Optional primary action label; the action button is hidden when empty.</summary>
    public static readonly StyledProperty<string?> ActionTextProperty =
        AvaloniaProperty.Register<EmptyState, string?>(nameof(ActionText));

    private readonly TextBlock _title = new() { Classes = { "title" } };
    private readonly TextBlock _hint = new() { Classes = { "meta" } };
    private readonly Button _action = new() { Classes = { "primary" } };

    public EmptyState()
    {
        Classes.Add("empty-state");
        Orientation = Orientation.Vertical;
        HorizontalAlignment = HorizontalAlignment.Center;
        VerticalAlignment = VerticalAlignment.Center;
        Children.Add(_title);
        Children.Add(_hint);
        Children.Add(_action);
        _action.Click += (_, _) => ActionInvoked?.Invoke(this, EventArgs.Empty);
        Apply();
    }

    /// <summary>Raised when the primary action is activated.</summary>
    public event EventHandler? ActionInvoked;

    /// <summary>Gets or sets the headline sentence.</summary>
    public string? Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    /// <summary>Gets or sets the optional fact line.</summary>
    public string? Hint
    {
        get => GetValue(HintProperty);
        set => SetValue(HintProperty, value);
    }

    /// <summary>Gets or sets the primary action label.</summary>
    public string? ActionText
    {
        get => GetValue(ActionTextProperty);
        set => SetValue(ActionTextProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == TitleProperty || change.Property == HintProperty || change.Property == ActionTextProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        _title.Text = Title;
        _hint.Text = Hint;
        _hint.IsVisible = !string.IsNullOrWhiteSpace(Hint);
        _action.Content = ActionText;
        _action.IsVisible = !string.IsNullOrWhiteSpace(ActionText);
    }
}

/// <summary>
/// AlertBanner (contract §3.2): blocked/stale/interrupted/partial-import banner with a status glyph,
/// one consequence sentence and an optional action. Always three-channel encoded.
/// </summary>
public sealed class AlertBanner : Border
{
    /// <summary>Severity/status hue of the banner.</summary>
    public static readonly StyledProperty<StatusKind> SeverityProperty =
        AvaloniaProperty.Register<AlertBanner, StatusKind>(nameof(Severity), StatusKind.Blocked);

    /// <summary>Short title.</summary>
    public static readonly StyledProperty<string?> TitleProperty =
        AvaloniaProperty.Register<AlertBanner, string?>(nameof(Title));

    /// <summary>One-sentence consequence.</summary>
    public static readonly StyledProperty<string?> MessageProperty =
        AvaloniaProperty.Register<AlertBanner, string?>(nameof(Message));

    /// <summary>Optional action label.</summary>
    public static readonly StyledProperty<string?> ActionTextProperty =
        AvaloniaProperty.Register<AlertBanner, string?>(nameof(ActionText));

    private readonly StatusGlyph _glyph = new() { VerticalAlignment = Avalonia.Layout.VerticalAlignment.Top };
    private readonly TextBlock _title = new() { Classes = { "label" } };
    private readonly TextBlock _message = new() { Classes = { "body" } };
    private readonly Button _action = new() { Classes = { "sm" } };

    public AlertBanner()
    {
        Classes.Add("alert-banner");
        _message.Classes.Add("muted");
        var actionColumn = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("*,Auto"),
            Children = { _title, _action },
        };
        Grid.SetColumn(_action, 1);
        var textStack = new StackPanel
        {
            Classes = { "nm-alert-text" },
            Orientation = Orientation.Vertical,
            Children = { actionColumn, _message },
        };
        var row = new Grid
        {
            ColumnDefinitions = new ColumnDefinitions("Auto,*"),
            Classes = { "nm-alert-row" },
            Children = { _glyph, textStack },
        };
        Grid.SetColumn(textStack, 1);
        Child = row;
        _action.Click += (_, _) => ActionInvoked?.Invoke(this, EventArgs.Empty);
        Apply();
    }

    /// <summary>Raised when the action is activated.</summary>
    public event EventHandler? ActionInvoked;

    /// <summary>Gets or sets the severity/status hue.</summary>
    public StatusKind Severity
    {
        get => GetValue(SeverityProperty);
        set => SetValue(SeverityProperty, value);
    }

    /// <summary>Gets or sets the title.</summary>
    public string? Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    /// <summary>Gets or sets the consequence sentence.</summary>
    public string? Message
    {
        get => GetValue(MessageProperty);
        set => SetValue(MessageProperty, value);
    }

    /// <summary>Gets or sets the optional action label.</summary>
    public string? ActionText
    {
        get => GetValue(ActionTextProperty);
        set => SetValue(ActionTextProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == SeverityProperty || change.Property == TitleProperty ||
            change.Property == MessageProperty || change.Property == ActionTextProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        _glyph.Status = Severity;
        _title.Text = Title;
        _message.Text = Message;
        _message.IsVisible = !string.IsNullOrWhiteSpace(Message);
        _action.Content = ActionText;
        _action.IsVisible = !string.IsNullOrWhiteSpace(ActionText);
        foreach (var kind in Enum.GetValues<StatusKind>())
        {
            Classes.Set(StatusCatalog.ClassName(kind), kind == Severity);
        }
    }
}

/// <summary>One overview counter: label, count and optional status hue (contract §3.2 `CountChips`).</summary>
public sealed record CountChipItem(string Label, int Count, StatusKind? Status = null);

/// <summary>
/// CountChips (contract §3.2): overview counters (total/done/failed/stale/pending/blocked) rendered as
/// clickable chips; clicking one is the filter shortcut for that count.
/// </summary>
public sealed class CountChips : StackPanel
{
    /// <summary>The counters to show.</summary>
    public static readonly StyledProperty<IReadOnlyList<CountChipItem>?> CountsProperty =
        AvaloniaProperty.Register<CountChips, IReadOnlyList<CountChipItem>?>(nameof(Counts));

    public CountChips()
    {
        Classes.Add("count-chips");
        Orientation = Orientation.Horizontal;
    }

    /// <summary>Raised with the clicked counter.</summary>
    public event EventHandler<CountChipItem>? ChipClicked;

    /// <summary>Gets or sets the counters to show.</summary>
    public IReadOnlyList<CountChipItem>? Counts
    {
        get => GetValue(CountsProperty);
        set => SetValue(CountsProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == CountsProperty)
        {
            Rebuild();
        }
    }

    private void Rebuild()
    {
        Children.Clear();
        if (Counts is null)
        {
            return;
        }

        foreach (var item in Counts)
        {
            var chip = new Chip
            {
                Text = $"{item.Label} {item.Count}",
                Status = item.Status,
            };
            var captured = item;
            chip.Clicked += (_, _) => ChipClicked?.Invoke(this, captured);
            Children.Add(chip);
        }
    }
}

