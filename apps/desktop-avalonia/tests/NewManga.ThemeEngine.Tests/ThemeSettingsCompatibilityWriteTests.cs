using NewManga.ThemeEngine;
using Xunit;

namespace NewManga.ThemeEngine.Tests;

/// <summary>
/// FEA-06-PREREQ-2 P5 / AC5 (W-9/Q-32): the one-release compatibility write. The store keeps writing the
/// legacy <c>theme-settings.json</c> and mirrors the same settings into the canonical appearance document
/// through the app-provided <see cref="IThemeSettingsSink"/>; the two-parameter constructor stays intact and
/// the sink failure is surfaced (never silently swallowed).
/// </summary>
public sealed class ThemeSettingsCompatibilityWriteTests
{
    private sealed class RecordingSink : IThemeSettingsSink
    {
        public List<ThemeSettings> Writes { get; } = [];

        public Task WriteAsync(ThemeSettings settings, CancellationToken cancellationToken = default)
        {
            Writes.Add(settings);
            return Task.CompletedTask;
        }
    }

    private sealed class ThrowingSink : IThemeSettingsSink
    {
        public Task WriteAsync(ThemeSettings settings, CancellationToken cancellationToken = default) =>
            throw new IOException("presentation-settings.json is not writable");
    }

    private static ThemeSettings SettingsFor(ThemeSettings? source = null) => source ?? new ThemeSettings(
        ThemeDefaults.DefaultThemeId,
        AppearanceMode.Dark,
        ContrastMode.High,
        LayoutProfile.Default with { Shelf = ShelfLayout.List, Density = Density.Compact },
        ReducedMotion: true,
        FollowSystemAccent: true);

    [Fact]
    public async Task CompatibilityWrite_WritesTheLegacyDocument_AndMirrorsThroughTheSink()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        var sink = new RecordingSink();
        var store = new ThemeSettingsStore(path, registry: null, presentationSink: sink);
        var settings = SettingsFor();

#pragma warning disable CS0618 // FEA-06-PREREQ-2 P5: the compatibility write is the subject under test.
        await store.SaveAsync(settings);
#pragma warning restore CS0618

        Assert.True(File.Exists(path), "the legacy document must keep being written during the compatibility window");
        Assert.Equal(settings, Assert.Single(sink.Writes));
        Assert.Equal(settings, store.Load());
    }

    [Fact]
    public async Task CompatibilityWrite_WithoutASink_OnlyWritesTheLegacyDocument()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        var store = new ThemeSettingsStore(path);

#pragma warning disable CS0618 // FEA-06-PREREQ-2 P5: the compatibility write is the subject under test.
        await store.SaveAsync(SettingsFor());
#pragma warning restore CS0618

        Assert.True(File.Exists(path));
        Assert.Equal(SettingsFor(), store.Load());
    }

    [Fact]
    public async Task CompatibilityWrite_SurfacesSinkFailures_AfterTheLegacyWrite()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        var store = new ThemeSettingsStore(path, registry: null, presentationSink: new ThrowingSink());

#pragma warning disable CS0618 // FEA-06-PREREQ-2 P5: the compatibility write is the subject under test.
        await Assert.ThrowsAsync<IOException>(() => store.SaveAsync(SettingsFor()));
#pragma warning restore CS0618

        // Order discipline: the legacy document is written first; a canonical-document failure must not
        // silently disappear (ThemeService.TrySave records it as a warning).
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void ExistingTwoParameterConstructor_IsKeptUnchanged()
    {
        using var temp = new TempDirectory();
        var path = temp.File("theme-settings.json");
        IThemePersistence persistence = new ThemeSettingsStore(path, registry: null);

        Assert.Equal(Path.GetFullPath(path), ((ThemeSettingsStore)persistence).SettingsFilePath);
        Assert.NotNull(new ThemeSettingsStore());
    }
}
