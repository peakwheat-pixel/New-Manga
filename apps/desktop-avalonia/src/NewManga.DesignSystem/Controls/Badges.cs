using Avalonia;
using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Controls;
using Avalonia.Controls.Presenters;
using Avalonia.Input;
using Avalonia.Layout;

namespace NewManga.DesignSystem.Controls;

/// <summary>
/// Status badge: tinted surface + symbol + text label. The three-channel encoding of DESIGN_SYSTEM
/// §2.2 is enforced by construction — a badge cannot show a status without its symbol and label.
/// </summary>
public sealed class StatusBadge : Border
{
    /// <summary>The status shown by the badge.</summary>
    public static readonly StyledProperty<StatusKind> StatusProperty =
        AvaloniaProperty.Register<StatusBadge, StatusKind>(nameof(Status));

    private readonly StatusGlyph _glyph = new();
    private readonly TextBlock _label = new();

    public StatusBadge()
    {
        Classes.Add("status-badge");
        _label.Classes.Add("label");
        Child = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Classes = { "nm-status-row" },
            Children = { _glyph, _label },
        };
        Apply();
    }

    /// <summary>Gets or sets the status shown by the badge.</summary>
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
        _glyph.Status = Status;
        _label.Text = StatusCatalog.Label(Status);
        foreach (var kind in Enum.GetValues<StatusKind>())
        {
            Classes.Set(StatusCatalog.ClassName(kind), kind == Status);
        }
    }
}

/// <summary>
/// Filter/count chip (contract §3.2): clickable pill with an optional active state and an optional
/// status hue. Used for filters and `CountChips`, never as a decoration.
/// </summary>
public sealed class Chip : Border
{
    /// <summary>Chip text.</summary>
    public static readonly StyledProperty<string?> TextProperty =
        AvaloniaProperty.Register<Chip, string?>(nameof(Text));

    /// <summary>Whether the chip is currently on (filter selected).</summary>
    public static readonly StyledProperty<bool> IsActiveProperty =
        AvaloniaProperty.Register<Chip, bool>(nameof(IsActive));

    /// <summary>Optional status hue for count chips (symbol/label still comes from the text).</summary>
    public static readonly StyledProperty<StatusKind?> StatusProperty =
        AvaloniaProperty.Register<Chip, StatusKind?>(nameof(Status));

    private readonly TextBlock _label = new();

    public Chip()
    {
        Classes.Add("chip");
        Cursor = new Cursor(StandardCursorType.Hand);
        _label.Classes.Add("label");
        Child = _label;
        PointerPressed += (_, args) =>
        {
            if (args.GetCurrentPoint(this).Properties.IsLeftButtonPressed == false)
            {
                return;
            }

            IsActive = !IsActive;
            Clicked?.Invoke(this, EventArgs.Empty);
            args.Handled = true;
        };
        Apply();
    }

    /// <summary>Raised when the chip is clicked (after the active state toggled).</summary>
    public event EventHandler? Clicked;

    /// <summary>Gets or sets the chip text.</summary>
    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    /// <summary>Gets or sets whether the chip is on.</summary>
    public bool IsActive
    {
        get => GetValue(IsActiveProperty);
        set => SetValue(IsActiveProperty, value);
    }

    /// <summary>Gets or sets an optional status hue.</summary>
    public StatusKind? Status
    {
        get => GetValue(StatusProperty);
        set => SetValue(StatusProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == TextProperty || change.Property == IsActiveProperty || change.Property == StatusProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        _label.Text = Text;
        Classes.Set("active", IsActive);
        foreach (var kind in Enum.GetValues<StatusKind>())
        {
            var isCurrent = Status == kind;
            Classes.Set(StatusCatalog.ClassName(kind), isCurrent);
            _label.Classes.Set("nm-status-" + StatusCatalog.ClassName(kind), isCurrent);
        }
    }
}

/// <summary>Keyboard key cap (contract §3.2 `Kbd`): mono gesture text in a hairline cap.</summary>
/// <remarks>
/// V11R-A11Y-1: a key cap is decorative visually but must publish the gesture as its accessible name;
/// without a peer it would surface a CLR type name (or nothing) to UI Automation.
/// </remarks>
public sealed class Kbd : Border
{
    /// <summary>The key gesture to display, e.g. <c>Ctrl+K</c>.</summary>
    public static readonly StyledProperty<string?> GestureProperty =
        AvaloniaProperty.Register<Kbd, string?>(nameof(Gesture));

    private readonly TextBlock _text = new();

    public Kbd()
    {
        Classes.Add("kbd");
        _text.Classes.Add("data");
        Child = _text;
        Apply();
    }

    /// <summary>Gets or sets the key gesture to display.</summary>
    public string? Gesture
    {
        get => GetValue(GestureProperty);
        set => SetValue(GestureProperty, value);
    }

    /// <summary>The gesture announced to assistive technology.</summary>
    public string AccessibleName => string.IsNullOrWhiteSpace(Gesture) ? "快捷键" : $"快捷键 {Gesture}";

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == GestureProperty)
        {
            Apply();
        }
    }

    protected override AutomationPeer OnCreateAutomationPeer() => new KbdAutomationPeer(this);

    private void Apply()
    {
        _text.Text = Gesture;
        AutomationProperties.SetName(this, AccessibleName);
    }

    private sealed class KbdAutomationPeer : ControlAutomationPeer
    {
        public KbdAutomationPeer(Control owner)
            : base(owner)
        {
        }

        protected override string GetClassNameCore() => "Kbd";

        protected override string GetNameCore() => ((Kbd)Owner).AccessibleName;
    }
}
