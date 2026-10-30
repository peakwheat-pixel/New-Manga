using Avalonia;
using Avalonia.Automation;
using Avalonia.Automation.Peers;
using Avalonia.Controls;
using Avalonia.Layout;

namespace NewManga.App.Views.V2.Shell.Controls;

/// <summary>
/// Local Kbd control until <c>NewManga.DesignSystem.Controls.Kbd</c> is merged (V11R-D-1).
/// Renders one keyboard key hint using the frozen token set (no raw values in consuming XAML).
/// V11R-A11Y-1: exposes the gesture as an automation name (key caps must not fall back to a CLR type).
/// </summary>
public sealed class Kbd : Border
{
    public static readonly StyledProperty<string?> TextProperty =
        AvaloniaProperty.Register<Kbd, string?>(nameof(Text));

    private readonly TextBlock _label = new()
    {
        VerticalAlignment = VerticalAlignment.Center,
        Classes = { "kbd-text" },
    };

    public Kbd()
    {
        Classes.Add("kbd");
        Child = _label;
        _label.Text = Text;
        UpdateAccessibleName();
    }

    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    /// <summary>The gesture shown by this key cap (also its automation name).</summary>
    public string AccessibleName => string.IsNullOrWhiteSpace(Text) ? "快捷键" : $"快捷键 {Text}";

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == TextProperty)
        {
            _label.Text = change.GetNewValue<string?>();
            UpdateAccessibleName();
        }
    }

    protected override AutomationPeer OnCreateAutomationPeer() => new KbdAutomationPeer(this);

    private void UpdateAccessibleName() => AutomationProperties.SetName(this, AccessibleName);

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
