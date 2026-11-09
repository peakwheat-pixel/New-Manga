using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.Appearance;

namespace NewManga.App.Tests;

/// <summary>
/// FEA-14-SET-1 (AC1/AC3/AC4/AC5): the 字体 panel is a READ-ONLY projection.
///
/// The view model is constructed without an Avalonia <c>Application</c> (a fake
/// <see cref="ITypographySource"/> is injected), so the group enumeration/search and the
/// projection rows are testable in isolation. The panel must never write resources,
/// styles or AppData.
/// </summary>
public sealed class SettingsTypographyPanelTests
{
    private sealed class FakeSource : ITypographySource
    {
        private readonly TypographySnapshot _snapshot;

        public FakeSource(TypographySnapshot snapshot) => _snapshot = snapshot;

        public TypographySnapshot Read() => _snapshot;
    }

    private static TypographySnapshot InstalledSnapshot() => new(
        [
            TypographyResolver.Resolve("Nm.FontFamily.Ui", "Installed B, sans-serif", _ => true),
            TypographyResolver.Resolve("Nm.FontFamily.Data", "Installed B, serif", _ => true),
            TypographyResolver.Resolve(
                "Nm.FontFamily.Display", "Missing A, Installed B", family => family == "Installed B"),
        ],
        Available: true,
        UnavailableReason: null);

    private static SettingsViewModel NewViewModel(TypographySnapshot snapshot) =>
        new SettingsViewModel(null, null, null, new FakeSource(snapshot));

    [Fact]
    public void ThePanelProjectsThreeRowsWithoutAnAvaloniaApplication()
    {
        var viewModel = NewViewModel(InstalledSnapshot());

        Assert.True(viewModel.TypographyAvailable);
        Assert.Equal(3, viewModel.TypographyLines.Count);
        Assert.Equal("Nm.FontFamily.Ui", viewModel.TypographyLines[0].TokenKey);
        Assert.Equal("Installed B", viewModel.TypographyLines[0].ResolvedFamily);
        Assert.Contains("视觉主题", viewModel.TypographySourceNotice);
    }

    [Fact]
    public void AnUnavailableThemeShowsAStablePlaceholder()
    {
        var viewModel = NewViewModel(new TypographySnapshot(
            Array.Empty<TypographyLine>(), false, "当前主题未初始化（缺少 Nm.FontFamily.* 资源）。"));

        Assert.False(viewModel.TypographyAvailable);
        Assert.Empty(viewModel.TypographyLines);
        Assert.Contains("未初始化", viewModel.TypographyUnavailableReason);
    }

    [Fact]
    public void TheTypographyGroupIsSearchableByChineseAndToken()
    {
        var viewModel = NewViewModel(InstalledSnapshot());

        viewModel.Search = "字体";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);

        viewModel.Search = "typography.ui";
        Assert.Contains(SettingsGroupId.Typography, viewModel.VisibleGroups);

        viewModel.Search = "zzz-no-match";
        Assert.DoesNotContain(SettingsGroupId.Typography, viewModel.VisibleGroups);
    }

    [Fact]
    public void ReadingTheProjectionDoesNotTouchApplicationResourcesOrStyles()
    {
        // AC3: there is no Application in this test; reading the projection must not
        // create one or mutate global state.
        var beforeApplication = Avalonia.Application.Current;
        var viewModel = NewViewModel(InstalledSnapshot());

        _ = viewModel.TypographyLines;
        _ = viewModel.TypographySourceNotice;

        Assert.Same(beforeApplication, Avalonia.Application.Current);
    }

    [Fact]
    public void ReadingTheProjectionLeavesTheRealAppDataDirectoryUntouched()
    {
        // AC4: the real %APPDATA%\NewManga must not receive writes from a read-only panel.
        var appData = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "NewManga");
        var before = Fingerprint(appData);
        var viewModel = NewViewModel(InstalledSnapshot());
        _ = viewModel.TypographyLines;
        var after = Fingerprint(appData);
        Assert.Equal(before, after);
    }

    private static string Fingerprint(string directory)
    {
        if (!Directory.Exists(directory)) return "<absent>";
        var entries = Directory
            .EnumerateFileSystemEntries(directory, "*", SearchOption.AllDirectories)
            .OrderBy(item => item, StringComparer.Ordinal)
            .Select(item =>
            {
                var info = new FileInfo(item);
                return $"{item}|{(info.Exists ? info.Length : 0)}|{(info.Exists ? info.LastWriteTimeUtc.Ticks : 0)}";
            });
        return string.Join("\n", entries);
    }
}
