using Avalonia.Controls;
using Avalonia.Interactivity;
using NewManga.App.ViewModels.V2.Shell;

namespace NewManga.App.Views.V2.Shell;

public partial class Breadcrumb : UserControl
{
    public Breadcrumb() => InitializeComponent();

    private void OnBreadcrumbClick(object? sender, RoutedEventArgs e)
    {
        if (sender is not Control { DataContext: BreadcrumbItem item } ||
            DataContext is not AppShellViewModel shell)
        {
            return;
        }

        shell.ActivateBreadcrumb(item);
    }
}
