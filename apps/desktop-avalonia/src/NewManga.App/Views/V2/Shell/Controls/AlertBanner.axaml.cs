using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;
using NewManga.App.Shell.V2;

namespace NewManga.App.Views.V2.Shell.Controls;

/// <summary>
/// Local AlertBanner stand-in until <c>NewManga.DesignSystem.Controls.AlertBanner</c> is merged
/// (V11R-D-1). Used for 能力待接入 / partial failure / stale states — always with symbol + text.
/// </summary>
public partial class AlertBanner : UserControl
{
    public static readonly StyledProperty<NmStatus> SeverityProperty =
        AvaloniaProperty.Register<AlertBanner, NmStatus>(nameof(Severity), NmStatus.Blocked);

    public static readonly StyledProperty<string> MessageProperty =
        AvaloniaProperty.Register<AlertBanner, string>(nameof(Message), string.Empty);

    public static readonly StyledProperty<string?> ActionTextProperty =
        AvaloniaProperty.Register<AlertBanner, string?>(nameof(ActionText));

    public static readonly StyledProperty<ICommand?> ActionCommandProperty =
        AvaloniaProperty.Register<AlertBanner, ICommand?>(nameof(ActionCommand));

    public AlertBanner()
    {
        InitializeComponent();
        ActionButton.Click += (_, _) => ActionCommand?.Execute(null);
        Apply();
    }

    public NmStatus Severity
    {
        get => GetValue(SeverityProperty);
        set => SetValue(SeverityProperty, value);
    }

    public string Message
    {
        get => GetValue(MessageProperty);
        set => SetValue(MessageProperty, value);
    }

    public string? ActionText
    {
        get => GetValue(ActionTextProperty);
        set => SetValue(ActionTextProperty, value);
    }

    public ICommand? ActionCommand
    {
        get => GetValue(ActionCommandProperty);
        set => SetValue(ActionCommandProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == SeverityProperty ||
            change.Property == MessageProperty ||
            change.Property == ActionTextProperty ||
            change.Property == ActionCommandProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        if (SymbolText is null || MessageText is null || ActionButton is null || Root is null)
        {
            return;
        }

        SymbolText.Text = NmStatusInfo.Symbol(Severity);
        MessageText.Text = Message;
        foreach (var candidate in Enum.GetValues<NmStatus>())
        {
            Classes.Set(NmStatusInfo.ClassName(candidate), candidate == Severity);
        }

        var hasAction = !string.IsNullOrWhiteSpace(ActionText) && ActionCommand is not null;
        ActionButton.IsVisible = hasAction;
        ActionButton.Content = ActionText;
    }
}
