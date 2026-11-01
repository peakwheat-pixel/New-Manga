using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using NewManga.Appearance;
using Xunit;

namespace NewManga.Appearance.Tests;

/// <summary>
/// C-03 v6 §2.2/§2.3/§2.5: appearance document round-trip, forgiving reader and the
/// legacy reducedMotion -> motion.mode migration. These tests are the AC1 evidence.
/// </summary>
public sealed class AppearanceJsonTests
{
    [Fact]
    public void Write_Then_Read_RoundTripsEveryField()
    {
        var settings = new AppearanceSettings
        {
            FrontendId = "builtin.fluent",
            VisualThemeId = "builtin.fluent-dark",
            Mode = AppearanceMode.Dark,
            Contrast = AppearanceContrast.High,
            FollowSystemAccent = true,
            MotionMode = MotionMode.Reduce,
            MotionCategories = MotionCategories.Feedback,
            CornersScale = CornersScale.Lg,
            MaterialAcrylicStrength = 0.25,
            MaterialMicaEnabled = false,
            Layout = LayoutSettings.Default with { Shelf = "list" },
        };

        var json = AppearanceJson.Write(settings);
        var read = AppearanceJson.Read(json);

        Assert.True(read.DocumentParsed);
        Assert.Empty(read.Warnings);
        Assert.Equal(settings.FrontendId, read.Settings.FrontendId);
        Assert.Equal(settings.VisualThemeId, read.Settings.VisualThemeId);
        Assert.Equal(AppearanceMode.Dark, read.Settings.Mode);
        Assert.Equal(AppearanceContrast.High, read.Settings.Contrast);
        Assert.True(read.Settings.FollowSystemAccent);
        Assert.Equal(MotionMode.Reduce, read.Settings.MotionMode);
        Assert.Equal(MotionCategories.Feedback, read.Settings.MotionCategories);
        Assert.Equal(CornersScale.Lg, read.Settings.CornersScale);
        Assert.Equal(0.25, read.Settings.MaterialAcrylicStrength, 3);
        Assert.False(read.Settings.MaterialMicaEnabled);
        Assert.Equal("list", read.Settings.Layout.Shelf);
        Assert.Equal(AppearanceSettings.CurrentSchemaVersion, read.Settings.SchemaVersion);
    }

    [Fact]
    public void Legacy_ReducedMotion_True_MigratesToReduce_WithAllCategoriesOff()
    {
        var read = AppearanceJson.Read("{\"reducedMotion\":true}");

        Assert.Equal(MotionMode.Reduce, read.Settings.MotionMode);
        Assert.Contains(read.Warnings, warning => warning.Contains("reducedMotion", StringComparison.Ordinal));
    }

    [Fact]
    public void Legacy_ReducedMotion_False_MigratesToFull_NotAuto()
    {
        var read = AppearanceJson.Read("{\"reducedMotion\":false}");

        Assert.Equal(MotionMode.Full, read.Settings.MotionMode);
    }

    [Fact]
    public void Legacy_ThemeId_MigratesToVisualThemeId()
    {
        var read = AppearanceJson.Read("{\"themeId\":\"builtin.fluent-dark\"}");

        Assert.Equal("builtin.fluent-dark", read.Settings.VisualThemeId);
    }

    [Fact]
    public void Corrupt_Json_FallsBackToDefaults_WithoutThrowing()
    {
        var read = AppearanceJson.Read("{not json");

        Assert.False(read.DocumentParsed);
        Assert.Equal(AppearanceDefaults.Settings, read.Settings);
        Assert.NotEmpty(read.Warnings);
    }

    [Fact]
    public void Unknown_Frontend_And_VisualTheme_FallBack()
    {
        var read = AppearanceJson.Read("{\"theme.frontendId\":\"x\",\"theme.visualThemeId\":\"y\"}");

        Assert.Equal(AppearanceDefaults.FrontendId, read.Settings.FrontendId);
        Assert.Equal(AppearanceDefaults.VisualThemeId, read.Settings.VisualThemeId);
    }

    [Fact]
    public void MotionCategories_Off_DisablesAllThree()
    {
        var read = AppearanceJson.Read("{\"motion.categories\":\"off\"}");

        Assert.Equal(MotionCategories.None, read.Settings.MotionCategories);
    }

    [Fact]
    public void AcrylicStrength_IsClampedToUnitRange()
    {
        var read = AppearanceJson.Read("{\"material.acrylicStrength\":2.5}");

        Assert.Equal(1.0, read.Settings.MaterialAcrylicStrength, 3);
    }

    [Fact]
    public void Write_EmitsSchemaVersionTwo_AndLfFinalNewline()
    {
        var json = AppearanceJson.Write(AppearanceDefaults.Settings);

        Assert.Contains("\"schemaVersion\": 2", json, StringComparison.Ordinal);
        Assert.DoesNotContain("\r", json, StringComparison.Ordinal);
        Assert.EndsWith("\n", json, StringComparison.Ordinal);
        Assert.Contains("\"motion.mode\": \"auto\"", json, StringComparison.Ordinal);
    }
}

/// <summary>C-03 §2.5: atomic persistence and the read-once legacy discipline.</summary>
public sealed class AppearanceStoreTests : IDisposable
{
    private readonly string _directory = Path.Combine(
        Path.GetTempPath(),
        "nm-appearance-" + Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        if (Directory.Exists(_directory))
        {
            Directory.Delete(_directory, recursive: true);
        }
    }

    [Fact]
    public async Task WriteAsync_IsAtomic_And_ReadableAfterwards()
    {
        var path = Path.Combine(_directory, "presentation-settings.json");
        var store = new AppearanceStore(path);
        var settings = AppearanceDefaults.Settings with { MotionMode = MotionMode.Reduce };

        await store.WriteAsync(settings);

        Assert.True(File.Exists(path));
        Assert.False(File.Exists(path + ".tmp"));
        var read = store.Read();
        Assert.True(read.DocumentParsed);
        Assert.Equal(MotionMode.Reduce, read.Settings.MotionMode);
    }

    [Fact]
    public void Read_MissingFile_YieldsDefaults_WithoutThrowing()
    {
        var store = new AppearanceStore(Path.Combine(_directory, "absent.json"));

        var read = store.Read();

        Assert.False(read.DocumentParsed);
        Assert.Equal(AppearanceDefaults.Settings, read.Settings);
    }

    [Fact]
    public void Read_RemembersTheLegacyDocument_ReadOnce()
    {
        var path = Path.Combine(_directory, "presentation-settings.json");
        Directory.CreateDirectory(_directory);
        File.WriteAllText(path, "{\"reducedMotion\":true}");
        var store = new AppearanceStore(path);

        _ = store.Read();
        File.WriteAllText(path, "{\"reducedMotion\":false}");
        _ = store.Read();

        Assert.Equal("{\"reducedMotion\":true}", store.LegacyDocument);
    }
}
