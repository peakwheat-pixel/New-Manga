using System.IO;
using NewManga.ThemeEngine;

namespace NewManga.ThemeEngine.Tests;

/// <summary>In-memory <see cref="IThemeLayerSink"/> used to prove the service never depends on Avalonia.</summary>
internal sealed class FakeThemeLayerSink : IThemeLayerSink
{
    public event EventHandler? PlatformThemeChanged;

    public bool IsPlatformLight { get; set; }

    public int PlatformThemeChangeCount { get; private set; }

    public void RaisePlatformThemeChanged()
    {
        PlatformThemeChangeCount++;
        PlatformThemeChanged?.Invoke(this, EventArgs.Empty);
    }

    public bool ApplyThemeLayerResult { get; set; } = true;

    public bool RevertResult { get; set; } = true;

    public bool SetAppearanceResult { get; set; } = true;

    public bool SetContrastResult { get; set; } = true;

    public bool SetReducedMotionResult { get; set; } = true;

    public string? LastError { get; private set; }

    public int ApplyCount { get; private set; }

    public int RevertCount { get; private set; }

    public int AppearanceCount { get; private set; }

    public int ContrastCount { get; private set; }

    public int MotionCount { get; private set; }

    public string? LastAppliedThemeId { get; private set; }

    public IReadOnlyDictionary<string, object?>? LastLayer { get; private set; }

    public List<(string ThemeId, IReadOnlyDictionary<string, object?> Layer)> Applied { get; } = [];

    public AppearanceMode Appearance { get; private set; } = AppearanceMode.System;

    public ContrastMode Contrast { get; private set; } = ContrastMode.Standard;

    public bool ReducedMotion { get; private set; }

    public bool ApplyThemeLayer(IReadOnlyDictionary<string, object?> layer, string themeId)
    {
        ApplyCount++;
        if (!ApplyThemeLayerResult)
        {
            LastError = $"fake sink rejected theme layer '{themeId}'";
            return false;
        }

        LastError = null;
        LastAppliedThemeId = themeId;
        LastLayer = layer;
        Applied.Add((themeId, layer));
        return true;
    }

    public bool RevertToBuiltInLayer()
    {
        RevertCount++;
        if (!RevertResult)
        {
            LastError = "fake sink rejected the built-in layer";
            return false;
        }

        LastError = null;
        LastAppliedThemeId = "<builtin>";
        LastLayer = null;
        return true;
    }

    public bool SetAppearance(AppearanceMode mode)
    {
        AppearanceCount++;
        if (!SetAppearanceResult)
        {
            LastError = "fake sink rejected the appearance change";
            return false;
        }

        LastError = null;
        Appearance = mode;
        return true;
    }

    public bool SetContrast(ContrastMode mode)
    {
        ContrastCount++;
        if (!SetContrastResult)
        {
            LastError = "fake sink rejected the contrast change";
            return false;
        }

        LastError = null;
        Contrast = mode;
        return true;
    }

    public bool SetReducedMotion(bool enabled)
    {
        MotionCount++;
        if (!SetReducedMotionResult)
        {
            LastError = "fake sink rejected the reduced-motion change";
            return false;
        }

        LastError = null;
        ReducedMotion = enabled;
        return true;
    }
}

/// <summary>Deterministic <see cref="IThemeRegistry"/> double for load/validation failure branches.</summary>
internal sealed class StubThemeRegistry : IThemeRegistry
{
    private readonly Dictionary<string, ThemeDescriptor> _descriptors = new(StringComparer.Ordinal);
    private readonly Dictionary<string, ThemePackage> _packages = new(StringComparer.Ordinal);

    public Func<string, ThemePackage>? LoadOverride { get; set; }

    public List<string> LoadRequests { get; } = [];

    public StubThemeRegistry Add(ThemePackage package)
    {
        _descriptors[package.Descriptor.Id] = package.Descriptor;
        _packages[package.Descriptor.Id] = package;
        return this;
    }

    public IReadOnlyList<ThemeDescriptor> All =>
        _descriptors.Values.OrderBy(descriptor => descriptor.Id, StringComparer.Ordinal).ToArray();

    public ThemeDescriptor? Find(string id) =>
        _descriptors.TryGetValue(id, out var descriptor) ? descriptor : null;

    public ThemePackage Load(string id)
    {
        LoadRequests.Add(id);
        if (LoadOverride is not null)
        {
            return LoadOverride(id);
        }

        return _packages.TryGetValue(id, out var package)
            ? package
            : throw new ThemePackageException(
                $"theme '{id}' is not installed",
                [ThemeValidationIssue.Error(ThemeIssueCodes.ThemeNotFound, $"theme '{id}' is not installed", id)]);
    }

    public Task RefreshAsync(CancellationToken ct = default) => Task.CompletedTask;

    public Task<ThemeValidationResult> InstallAsync(Stream packageJson, CancellationToken ct = default) =>
        Task.FromResult(ThemeValidationResult.Ok);

    public Task<bool> UninstallAsync(string id) => Task.FromResult(false);

    public Task<string> ExportAsync(string id) => Task.FromResult(ThemePackageJson.Write(Load(id)));
}

/// <summary>Persistence double whose save always fails (proves save failure never loses the applied theme).</summary>
internal sealed class FailingSavePersistence : IThemePersistence
{
    public ThemeSettings LoadResult { get; set; } = ThemeDefaults.Settings;

    public int LoadCount { get; private set; }

    public int SaveCount { get; private set; }

    public ThemeSettings Load()
    {
        LoadCount++;
        return LoadResult;
    }

    public Task SaveAsync(ThemeSettings settings)
    {
        SaveCount++;
        return Task.FromException(new IOException("simulated disk failure"));
    }
}

/// <summary>Persistence double that records saves in memory.</summary>
internal sealed class RecordingPersistence : IThemePersistence
{
    public ThemeSettings LoadResult { get; set; } = ThemeDefaults.Settings;

    public ThemeSettings? LastSaved { get; private set; }

    public int SaveCount { get; private set; }

    public ThemeSettings Load() => LoadResult;

    public Task SaveAsync(ThemeSettings settings)
    {
        SaveCount++;
        LastSaved = settings;
        return Task.CompletedTask;
    }
}
