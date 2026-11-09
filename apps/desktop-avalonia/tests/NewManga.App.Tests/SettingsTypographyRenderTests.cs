using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Media;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.DesignSystem.Controls;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-SET-1 (AC1/AC3/AC8): the 字体 group must RENDER its projection rows and must
/// not mutate global resources or styles. Runs under the Avalonia headless harness so the
/// view (not just the view model) is exercised.
/// </summary>
public sealed class SettingsTypographyRenderTests
{
    private sealed class FakeSource : ITypographySource
    {
        private readonly TypographySnapshot _snapshot;

        public FakeSource(TypographySnapshot snapshot) => _snapshot = snapshot;

        public TypographySnapshot Read() => _snapshot;
    }

    private static TypographySnapshot Snapshot() => new(
        [
            TypographyResolver.Resolve(
                "Nm.FontFamily.Ui", "Missing A, Installed B", family => family == "Installed B",
                scale: 14, lineHeight: 1.6),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Data", "Installed B", _ => true, scale: 14, lineHeight: 1.5),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Display", "Installed B", _ => true, scale: 24, lineHeight: 1.4),
        ],
        Available: true,
        UnavailableReason: null);

    private static SettingsViewModel NewViewModel(TypographySnapshot snapshot) =>
        new SettingsViewModel(null, null, null, new FakeSource(snapshot));

    [AvaloniaFact]
    public void TheTypographyGroupRendersItsProjectionRows()
    {
        var viewModel = NewViewModel(Snapshot());
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view, Width = 960, Height = 720 };
        window.Show();

        var texts = window.GetVisualDescendants()
            .OfType<TextBlock>()
            .Select(block => block.Text ?? string.Empty)
            .ToList();

        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Ui"));
        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Data"));
        Assert.Contains(texts, text => text.Contains("Nm.FontFamily.Display"));
        // The resolved family and the missing segment are explained in the row text.
        Assert.Contains(texts, text => text.Contains("Installed B"));
        Assert.Contains(texts, text => text.Contains("Missing A"));
        // The panel states that family selection belongs to the visual theme.
        Assert.Contains(texts, text => text.Contains("视觉主题"));
    }

    [AvaloniaFact]
    public void RenderingTheTypographyGroupDoesNotMutateGlobalResourcesOrStyles()
    {
        var application = Application.Current;
        Assert.NotNull(application);
        var resourcesBefore = application!.Resources.Count;
        var styleKeysBefore = application.Styles
            .Select(style => style.GetHashCode())
            .ToList();

        var viewModel = NewViewModel(Snapshot());
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view };
        window.Show();
        window.Measure(new Size(960, 720));

        Assert.Same(application, Application.Current);
        Assert.Equal(resourcesBefore, application.Resources.Count);
        Assert.Equal(styleKeysBefore, application.Styles.Select(style => style.GetHashCode()).ToList());
    }

    [AvaloniaFact]
    public void SearchingForTheTopicStillShowsTheProjectionRows()
    {
        var viewModel = NewViewModel(Snapshot());
        viewModel.Search = "字体";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);
        viewModel.SelectedGroup = SettingsGroupId.Typography;
        var view = new SettingsPageView(viewModel);
        var window = new Window { Content = view };
        window.Show();

        var visibleRows = window.GetVisualDescendants()
            .OfType<SettingsField>()
            .Where(field => field.IsVisible)
            .Count();
        // R-008: the group-level match must not hide every row inside the group.
        Assert.True(visibleRows > 0, "the typography rows must stay visible after a group match");
    }
}
