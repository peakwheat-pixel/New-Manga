using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using NewManga.App.Shell.V2;

namespace NewManga.App.Views.V2.Shell.Controls;

/// <summary>
/// Local StatusGlyph/StatusBadge stand-in until <c>NewManga.DesignSystem.Controls.StatusGlyph</c> is
/// merged (V11R-D-1). Always renders the frozen three-channel state language: symbol + label + the
/// status colour class (st-*), never colour alone (DESIGN_SYSTEM §2.2).
/// </summary>
public sealed class StatusBadge : Border
{
    public static readonly StyledProperty<NmStatus> StatusProperty =
        AvaloniaProperty.Register<StatusBadge, NmStatus>(nameof(Status));

    public static readonly StyledProperty<bool> ShowLabelProperty =
        AvaloniaProperty.Register<StatusBadge, bool>(nameof(ShowLabel), defaultValue: true);

    private readonly TextBlock _symbol = new()
    {
        VerticalAlignment = VerticalAlignment.Center,
        Classes = { "symbol" },
    };

    private readonly TextBlock _label = new()
    {
        VerticalAlignment = VerticalAlignment.Center,
        Classes = { "label" },
    };

    public StatusBadge()
    {
        Classes.Add("statusbadge");
        var panel = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            Spacing = 4,
            VerticalAlignment = VerticalAlignment.Center,
        };
        panel.Children.Add(_symbol);
        panel.Children.Add(_label);
        Child = panel;
        ApplyStatus();
    }

    public NmStatus Status
    {
        get => GetValue(StatusProperty);
        set => SetValue(StatusProperty, value);
    }

    public bool ShowLabel
    {
        get => GetValue(ShowLabelProperty);
        set => SetValue(ShowLabelProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == StatusProperty || change.Property == ShowLabelProperty)
        {
            ApplyStatus();
        }
    }

    private void ApplyStatus()
    {
        var status = Status;
        _symbol.Text = NmStatusInfo.Symbol(status);
        _label.Text = NmStatusInfo.Label(status);
        _label.IsVisible = ShowLabel;

        foreach (var candidate in Enum.GetValues<NmStatus>())
        {
            Classes.Set(NmStatusInfo.ClassName(candidate), candidate == status);
        }
    }
}
