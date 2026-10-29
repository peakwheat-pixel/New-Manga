using Avalonia;
using Avalonia.Controls;

namespace NewManga.App.Views.V2.Shell;

/// <summary>
/// V11R-INT-0: placeholder shown when a space's <c>IWorkspaceView</c> is not registered. Copy is
/// supplied by the shell (never a fake workspace); this control only renders it.
/// </summary>
public partial class WorkspacePlaceholderView : UserControl
{
    public static readonly StyledProperty<string> TitleProperty =
        AvaloniaProperty.Register<WorkspacePlaceholderView, string>(nameof(Title), "工作区");

    public static readonly StyledProperty<string> DetailProperty =
        AvaloniaProperty.Register<WorkspacePlaceholderView, string>(nameof(Detail), string.Empty);

    public WorkspacePlaceholderView() => InitializeComponent();

    public string Title
    {
        get => GetValue(TitleProperty);
        set => SetValue(TitleProperty, value);
    }

    public string Detail
    {
        get => GetValue(DetailProperty);
        set => SetValue(DetailProperty, value);
    }
}
