using Avalonia.Controls;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.DesignSystem.Controls;

namespace NewManga.DesignSystem.Tests;

/// <summary>FEA-06 visual component classes expose the same open/closed and selected states headlessly.</summary>
public sealed class FluentComponentsTests
{
    [AvaloniaFact]
    public void Fluent_components_expose_canonical_identity_and_overlay_states()
    {
        var dialog = new FluentDialog { IsOpen = false };
        var drawer = new Drawer { IsOpen = false, Header = "Inspector" };
        var bookCard = new BookCard { Content = "Book" };
        var bookRow = new BookRow { Content = "Book" };
        var pageStrip = new PageThumbStrip();
        var regionBox = new RegionBox();
        var batchMatrix = new BatchMatrix();
        var runBar = new RunProjectionBar();
        var readerPage = new NewManga.DesignSystem.Controls.ReaderPage();
        var progress = new ReaderProgressBar();
        var settingsGroup = new SettingsGroup();
        var settingsField = new SettingsField();
        var tabStrip = new TabStrip();
        var search = new SearchField { Placeholder = "Search" };
        var segmented = new SegmentedControl { Items = new[] { "Page", "Batch" } };
        var window = new Window
        {
            Width = 520,
            Height = 360,
            Content = new StackPanel
            {
                Children =
                {
                    dialog, drawer, bookCard, bookRow, pageStrip, regionBox, batchMatrix,
                    runBar, readerPage, progress, settingsGroup, settingsField, tabStrip, search, segmented,
                },
            },
        };
        window.Show();
        Dispatcher.UIThread.RunJobs();

        Assert.False(dialog.IsVisible);
        Assert.False(drawer.IsVisible);
        dialog.IsOpen = true;
        drawer.IsOpen = true;
        Dispatcher.UIThread.RunJobs();
        Assert.True(dialog.IsVisible);
        Assert.True(drawer.IsVisible);
        Assert.All(new Control[] { bookCard, bookRow, pageStrip, regionBox, batchMatrix, runBar, readerPage,
            progress, settingsGroup, settingsField, tabStrip, search, segmented },
            control => Assert.NotEmpty(control.Classes));
        Assert.Equal("Search", search.Placeholder);
        Assert.Equal(2, segmented.GetVisualDescendants().OfType<Button>().Count());

        window.Close();
    }
}
