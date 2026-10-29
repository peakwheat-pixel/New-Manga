using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace NewManga.App.Views.V2.Shell.Controls;

/// <summary>
/// Local Kbd control until <c>NewManga.DesignSystem.Controls.Kbd</c> is merged (V11R-D-1).
/// Renders one keyboard key hint using the frozen token set (no raw values in consuming XAML).
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
    }

    public string? Text
    {
        get => GetValue(TextProperty);
        set => SetValue(TextProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == TextProperty)
        {
            _label.Text = change.GetNewValue<string?>();
        }
    }
}
