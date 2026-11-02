using System.Windows.Input;
using Avalonia;
using Avalonia.Controls;

namespace NewManga.App.Views.V2.Shell.Controls;

/// <summary>
/// Local EmptyState stand-in until <c>NewManga.DesignSystem.Controls.EmptyState</c> is merged
/// (V11R-D-1): one sentence + one action, never a spinner-as-empty.
/// </summary>
public partial class EmptyState : UserControl
{
    public static readonly StyledProperty<string> TitleProperty =
        AvaloniaProperty.Register<EmptyState, string>(nameof(Title), "空");

    public static readonly StyledProperty<string> HintProperty =
        AvaloniaProperty.Register<EmptyState, string>(nameof(Hint), string.Empty);

    public static readonly StyledProperty<string?> ActionTextProperty =
        AvaloniaProperty.Register<EmptyState, string?>(nameof(ActionText));

    public static readonly StyledProperty<ICommand?> ActionCommandProperty =
        AvaloniaProperty.Register<EmptyState, ICommand?>(nameof(ActionCommand));

    public EmptyState()
    {
        InitializeComponent();
        ActionButton.Click += (_, _) => ActionCommand?.Execute(null);
        Apply();
    }

    public string Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    public string Hint
    {
        get => GetValue(HintProperty);
        set => SetValue(HintProperty, value);
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
        if (change.Property == TitleProperty ||
            change.Property == HintProperty ||
            change.Property == ActionTextProperty ||
            change.Property == ActionCommandProperty)
        {
            Apply();
        }
    }

    private void Apply()
    {
        if (TitleText is null || HintText is null || ActionButton is null)
        {
            return;
        }

        TitleText.Text = Title;
        HintText.Text = Hint;
        HintText.IsVisible = !string.IsNullOrWhiteSpace(Hint);
        var hasAction = !string.IsNullOrWhiteSpace(ActionText) && ActionCommand is not null;
        ActionButton.IsVisible = hasAction;
        ActionButton.Content = ActionText;
    }
}
