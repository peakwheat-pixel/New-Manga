using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// Deterministic Theme Studio sandbox for headless tests and screenshot evidence.
///
/// <para>
/// It is <b>not</b> a second service implementation: it builds the real engine chain
/// (<see cref="ThemeRegistry"/> + <see cref="ThemeSettingsStore"/> + <see cref="ThemeService"/>) over a
/// throw-away directory and a <see cref="NullThemeLayerSink"/> so nothing leaks into the live application
/// or <c>%APPDATA%</c>. The shipped UI never uses this factory — it uses
/// <see cref="ThemeEngineThemeStudioService.CreateProduction"/>.
/// </para>
///
/// <para>
/// The seeded fixture packages are derived from the shipped default package by changing
/// typography/corners/motion (never colours), so they stay validator-clean and cannot be mistaken for a
/// product theme; they exist so the 4/3/2-column library grid and 我的主题 have content.
/// </para>
/// </summary>
public static class StubThemeStudioService
{
    /// <summary>Default sandbox root (temporary; never the real <c>%APPDATA%</c>).</summary>
    public static string DefaultSandboxDirectory { get; } =
        Path.Combine(Path.GetTempPath(), "newmanga-theme-studio-sandbox");

    /// <summary>Fixture built for the screenshot/grid evidence (STUB only).</summary>
    public static IReadOnlyList<ThemePackage> FixturePackages { get; } = BuildFixtures();

    /// <summary>Creates the sandbox service, seeding fixtures into the sandbox theme directory.</summary>
    public static ThemeEngineThemeStudioService Create(
        string? sandboxDirectory = null,
        bool seedFixtures = true,
        bool persistsToDisk = true)
    {
        var root = string.IsNullOrWhiteSpace(sandboxDirectory)
            ? DefaultSandboxDirectory
            : Path.GetFullPath(sandboxDirectory);
        var themeDirectory = Path.Combine(root, "themes");
        Directory.CreateDirectory(themeDirectory);

        if (seedFixtures)
        {
            foreach (var fixture in FixturePackages)
            {
                var path = Path.Combine(themeDirectory, fixture.Descriptor.Id + ThemeDefaults.ThemeFileExtension);
                if (!File.Exists(path))
                {
                    File.WriteAllText(path, ThemePackageJson.Write(fixture), new System.Text.UTF8Encoding(false));
                }
            }
        }

        var registry = new ThemeRegistry(themeDirectory);
        var settingsStore = new ThemeSettingsStore(Path.Combine(root, "theme-settings.json"), registry);
        var service = new ThemeService(registry, settingsStore, new NullThemeLayerSink(platformIsLight: false));
        return new ThemeEngineThemeStudioService(
            service,
            registry,
            settingsStore,
            new ThemeStudioFavoritesStore(Path.Combine(root, "theme-studio-favorites.json")),
            palettes: null,
            isSandbox: true,
            persistsToDisk: persistsToDisk);
    }

    /// <summary>Creates and initializes the sandbox (async form for tests).</summary>
    public static async Task<ThemeEngineThemeStudioService> CreateAsync(
        string? sandboxDirectory = null,
        bool seedFixtures = true,
        bool persistsToDisk = true,
        CancellationToken ct = default)
    {
        var service = Create(sandboxDirectory, seedFixtures, persistsToDisk);
        await service.InitializeAsync(ct).ConfigureAwait(false);
        return service;
    }

    /// <summary>
    /// A package the validator rejects (6px corner radius): proves the "非法主题包 → issue + 回退默认，不崩溃"
    /// path with a document produced by the engine's own writer.
    /// </summary>
    public static ThemePackage CreateIllegalFixture() => Fixture(
        BuiltInThemes.Default,
        "stub-illegal",
        "STUB 非法主题",
        "Sandbox fixture: declares a 6px corner radius (must be rejected).",
        ["stub", "illegal"],
        typographyScale: 1.0,
        lineHeight: LineHeightPreset.Normal,
        corners: new ThemeCorners(0, 2, 6),
        motion: new ThemeMotion(90, 140, 220));

    private static IReadOnlyList<ThemePackage> BuildFixtures()
    {
        var baseline = BuiltInThemes.Default;
        return
        [
            Fixture(
                baseline,
                "stub-fixture-compact",
                "STUB 紧凑网格",
                "Sandbox fixture: tighter corners and smaller type scale.",
                ["stub", "fixture"],
                typographyScale: 0.9,
                lineHeight: LineHeightPreset.Tight,
                corners: new ThemeCorners(0, 1, 2),
                motion: new ThemeMotion(60, 100, 160)),
            Fixture(
                baseline,
                "stub-fixture-spacious",
                "STUB 宽松排版",
                "Sandbox fixture: larger type scale and loose line height.",
                ["stub", "fixture"],
                typographyScale: 1.15,
                lineHeight: LineHeightPreset.Loose,
                corners: baseline.Dark.Corners,
                motion: new ThemeMotion(120, 200, 280)),
            Fixture(
                baseline,
                "stub-fixture-raised",
                "STUB 抬升面板",
                "Sandbox fixture: raised elevation declaration with default type.",
                ["stub", "fixture"],
                typographyScale: 1.0,
                lineHeight: LineHeightPreset.Normal,
                corners: baseline.Dark.Corners,
                motion: baseline.Dark.Motion,
                elevation: ThemeElevation.Raised),
        ];
    }

    private static ThemePackage Fixture(
        ThemePackage baseline,
        string id,
        string name,
        string description,
        IReadOnlyList<string> tags,
        double typographyScale,
        LineHeightPreset lineHeight,
        ThemeCorners corners,
        ThemeMotion motion,
        ThemeElevation elevation = ThemeElevation.None)
    {
        var descriptor = baseline.Descriptor with
        {
            Id = id,
            Name = name,
            Version = "1.0.0",
            Author = "New Manga Theme Studio (STUB)",
            Description = description,
            Kind = ThemeKind.User,
            Tags = tags,
        };

        ThemeTokenSet Adjust(ThemeTokenSet tokens) => tokens with
        {
            Typography = tokens.Typography with { Scale = typographyScale, LineHeight = lineHeight },
            Corners = corners,
            Motion = motion,
            Elevation = elevation,
            Material = ThemeMaterial.Solid,
        };

        return baseline with
        {
            Descriptor = descriptor,
            Light = Adjust(baseline.Light),
            Dark = Adjust(baseline.Dark),
            Metadata = baseline.Metadata with { Generator = "newmanga-theme-studio-stub/1" },
        };
    }
}

/// <summary>
/// Sandbox <see cref="IThemeLayerSink"/>: records what the service would have applied instead of touching
/// Avalonia resources. Used only by <see cref="StubThemeStudioService"/> so headless logic tests can run
/// without an <see cref="Avalonia.Application"/>; it asserts the layer shape the real sink receives.
/// </summary>
public sealed class NullThemeLayerSink : IThemeLayerSink
{
    private string? _lastError;

    /// <summary>Creates the sink with a fixed platform variant.</summary>
    public NullThemeLayerSink(bool platformIsLight = false) => IsPlatformLight = platformIsLight;

    /// <summary>The last layer the service asked to apply (evidence/assertions).</summary>
    public IReadOnlyDictionary<string, object?>? LastLayer { get; private set; }

    /// <summary>Theme id of <see cref="LastLayer"/>.</summary>
    public string? LastThemeId { get; private set; }

    /// <summary>Number of applied layers (preview + apply).</summary>
    public int ApplyCount { get; private set; }

    /// <summary>True when the last operation restored the shipped built-in layer.</summary>
    public bool Reverted { get; private set; }

    /// <inheritdoc />
    public bool IsPlatformLight { get; }

    /// <inheritdoc />
    public string? LastError => _lastError;

    /// <inheritdoc />
    public event EventHandler? PlatformThemeChanged;

    /// <inheritdoc />
    public bool ApplyThemeLayer(IReadOnlyDictionary<string, object?> layer, string themeId)
    {
        LastLayer = layer;
        LastThemeId = themeId;
        ApplyCount++;
        Reverted = false;
        _lastError = null;
        return true;
    }

    /// <inheritdoc />
    public bool RevertToBuiltInLayer()
    {
        LastLayer = null;
        LastThemeId = null;
        Reverted = true;
        return true;
    }

    /// <inheritdoc />
    public bool SetAppearance(AppearanceMode mode)
    {
        if (mode == AppearanceMode.System && IsPlatformLight)
        {
            PlatformThemeChanged?.Invoke(this, EventArgs.Empty);
        }

        return true;
    }

    /// <inheritdoc />
    public bool SetContrast(ContrastMode mode) => true;

    /// <inheritdoc />
    public bool SetReducedMotion(bool enabled) => true;
}
