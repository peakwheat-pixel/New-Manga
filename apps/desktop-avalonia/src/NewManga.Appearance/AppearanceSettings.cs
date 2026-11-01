using System;
using System.Collections.Generic;

namespace NewManga.Appearance;

/// <summary>
/// C-03 v6 §2.2: the persisted appearance document (schemaVersion 2). Field names
/// follow the frozen JSON keys; the C# names drop only the namespace prefix.
/// </summary>
public sealed record AppearanceSettings
{
    /// <summary>Current schema version written to disk.</summary>
    public const int CurrentSchemaVersion = 2;

    /// <summary><c>theme.frontendId</c>: builtin.current-v2 | builtin.fluent.</summary>
    public string FrontendId { get; init; } = AppearanceDefaults.FrontendId;

    /// <summary><c>theme.visualThemeId</c>: newmanga-default | builtin.fluent-dark.</summary>
    public string VisualThemeId { get; init; } = AppearanceDefaults.VisualThemeId;

    /// <summary><c>appearance.mode</c>: system | light | dark.</summary>
    public AppearanceMode Mode { get; init; } = AppearanceMode.System;

    /// <summary><c>appearance.contrast</c>: standard | high.</summary>
    public AppearanceContrast Contrast { get; init; } = AppearanceContrast.Standard;

    /// <summary><c>appearance.followSystemAccent</c>.</summary>
    public bool FollowSystemAccent { get; init; }

    /// <summary><c>motion.mode</c>: auto | full | reduce (there is no "off" state).</summary>
    public MotionMode MotionMode { get; init; } = MotionMode.Auto;

    /// <summary><c>motion.categories</c>: the three independently switchable usage classes.</summary>
    public MotionCategories MotionCategories { get; init; } = MotionCategories.All;

    /// <summary><c>corners.scale</c>: sm | md | lg (Fluent only).</summary>
    public CornersScale CornersScale { get; init; } = CornersScale.Md;

    /// <summary><c>material.acrylicStrength</c> in [0,1] (Fluent only).</summary>
    public double MaterialAcrylicStrength { get; init; } = AppearanceDefaults.AcrylicStrength;

    /// <summary><c>material.micaEnabled</c> (Fluent only).</summary>
    public bool MaterialMicaEnabled { get; init; } = true;

    /// <summary><c>layout.*</c> (structure unchanged from C-03).</summary>
    public LayoutSettings Layout { get; init; } = LayoutSettings.Default;

    /// <summary><c>schemaVersion</c>: written as 2; anything else triggers migration.</summary>
    public int SchemaVersion { get; init; } = CurrentSchemaVersion;
}

/// <summary>C-03 §2.1: the appearance mode enum.</summary>
public enum AppearanceMode
{
    System,
    Light,
    Dark,
}

/// <summary>C-03 §2.1: the contrast enum.</summary>
public enum AppearanceContrast
{
    Standard,
    High,
}

/// <summary>C-03 §2.3: three-state motion preference (no "off" state).</summary>
public enum MotionMode
{
    /// <summary>Follow the platform accessibility setting through <see cref="IMotionPreferenceSource"/>.</summary>
    Auto,
    Full,
    Reduce,
}

/// <summary>C-03 §2.3: the three independently switchable motion usage classes.</summary>
[Flags]
public enum MotionCategories
{
    None = 0,
    Navigation = 1,
    Feedback = 2,
    Decorative = 4,
    All = Navigation | Feedback | Decorative,
}

/// <summary>C-03 §2.2: the Fluent corner scale.</summary>
public enum CornersScale
{
    Sm,
    Md,
    Lg,
}

/// <summary>C-03 §2.2: <c>layout.*</c> (structure unchanged).</summary>
public sealed record LayoutSettings
{
    public string Id { get; init; } = "default";

    public string Navigation { get; init; } = "expanded";

    public string Shelf { get; init; } = "grid";

    public string Density { get; init; } = "comfortable";

    public string Workbench { get; init; } = "split";

    public string Reader { get; init; } = "fit";

    public static LayoutSettings Default { get; } = new();
}

/// <summary>C-03 §2.2 defaults and the frozen id vocabularies.</summary>
public static class AppearanceDefaults
{
    public const string FrontendId = "builtin.current-v2";

    public const string VisualThemeId = "newmanga-default";

    public const double AcrylicStrength = 0.5;

    public static AppearanceSettings Settings { get; } = new();
}

/// <summary>
/// C-03 §2.2/§2.3: the platform motion preference SPI. Avalonia 11.3.22 exposes no
/// animation switch, so <see cref="Auto"/> reads this source; a failure degrades to
/// <see cref="MotionMode.Full"/> with a warning (never blocks startup).
/// </summary>
public interface IMotionPreferenceSource
{
    /// <summary>Returns the platform preference; <c>null</c> means unavailable.</summary>
    MotionMode? Read();
}

/// <summary>Fallback source used when no platform implementation is registered.</summary>
public sealed class NullMotionPreferenceSource : IMotionPreferenceSource
{
    public static NullMotionPreferenceSource Instance { get; } = new();

    public MotionMode? Read() => null;
}
