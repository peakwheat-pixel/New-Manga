using System.Collections.ObjectModel;
using System.Windows.Input;
using NewManga.App.Shell.V2;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>Which production surface the preview shows (THEME_STUDIO_SPEC §3.2).</summary>
public enum ThemeStudioPreviewMode
{
    Shelf,
    Workbench,
    Reader,
}

/// <summary>One book tile of the example bookshelf (explicit sample content, never user data).</summary>
public sealed record ThemeStudioSampleBook(string Title, string Meta, NmStatus Status)
{
    public string StatusSymbol => NmStatusInfo.Symbol(Status);

    public string StatusLabel => NmStatusInfo.Label(Status);
}

/// <summary>One page row of the example film strip.</summary>
public sealed record ThemeStudioSamplePage(int Index, string FileName, NmStatus Status)
{
    public string StatusSymbol => NmStatusInfo.Symbol(Status);

    public string StatusLabel => NmStatusInfo.Label(Status);
}

/// <summary>One region box of the example reader page.</summary>
public sealed record ThemeStudioSampleRegion(string Label, string Text, bool IsSelected, NmStatus Status)
{
    public string StatusSymbol => NmStatusInfo.Symbol(Status);
}

/// <summary>One label/value row of the example inspector.</summary>
public sealed record ThemeStudioSampleRow(string Label, string Value, NmStatus? Status = null)
{
    public bool HasStatus => Status is not null;

    public string StatusSymbol => Status is { } status ? NmStatusInfo.Symbol(status) : string.Empty;
}

/// <summary>
/// ② 预览 (THEME_STUDIO_SPEC §3.2): the three production views rendered as real control trees with
/// example content, plus the appearance/density/zoom switches. The palette is scoped to this section, so
/// nothing here touches application resources.
/// </summary>
public sealed class ThemeStudioPreviewViewModel : ThemeStudioSectionViewModel
{
    private readonly List<ThemeStudioOption> _modeOptions = new();
    private readonly List<ThemeStudioOption> _appearanceOptions = new();
    private readonly List<ThemeStudioOption> _densityOptions = new();
    private readonly List<ThemeStudioOption> _zoomOptions = new();
    private ThemeStudioPreviewMode _mode = ThemeStudioPreviewMode.Shelf;
    private AppearanceMode _previewAppearance = AppearanceMode.Dark;
    private bool _highContrast;
    private Density _density = Density.Comfortable;
    private double _zoom = 1.0;
    private ThemeStudioPalette? _palette;

    internal ThemeStudioPreviewViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.Preview)
    {
        AddMode(ThemeStudioPreviewMode.Shelf, "书架", "封面网格 + 筛选条");
        AddMode(ThemeStudioPreviewMode.Workbench, "工作台", "胶片条 + 画布 + 检查器");
        AddMode(ThemeStudioPreviewMode.Reader, "阅读器", "页面 + 译文区域");

        AddAppearance(AppearanceMode.Light, "浅色", "以浅色令牌预览");
        AddAppearance(AppearanceMode.Dark, "深色", "以深色令牌预览");
        AddAppearance(AppearanceMode.System, "系统模拟", "跟随当前系统变体解析");

        AddDensity(Density.Compact, "紧凑", null);
        AddDensity(Density.Comfortable, "舒适", null);
        AddDensity(Density.Spacious, "宽松", null);

        AddZoom(0.5, "50%");
        AddZoom(0.75, "75%");
        AddZoom(1.0, "100%");

        SampleBooks =
        [
            new("雾港来信", "3 章 · 42 页", NmStatus.Done),
            new("星海归途", "5 章 · 118 页", NmStatus.Running),
            new("雨夜便利店", "2 章 · 24 页", NmStatus.Stale),
            new("山猫侦探", "1 章 · 18 页", NmStatus.Failed),
            new("纸月", "6 章 · 203 页", NmStatus.Queued),
            new("雾都列车", "4 章 · 96 页", NmStatus.Skipped),
        ];

        SamplePages =
        [
            new(1, "0001.webp", NmStatus.Done),
            new(2, "0002.webp", NmStatus.Running),
            new(3, "0003.webp", NmStatus.Failed),
            new(4, "0004.webp", NmStatus.Stale),
            new(5, "0005.webp", NmStatus.Queued),
            new(6, "0006.webp", NmStatus.Blocked),
        ];

        SampleRegions =
        [
            new("r1", "这句话是示例译文，用来展示主题在阅读器中的排版与对比度。", true, NmStatus.Done),
            new("r2", "第二处译文：示例内容，不读取用户真实书库。", false, NmStatus.Done),
            new("r3", "第三处译文：过期状态用符号与文字表达，而不是只靠颜色。", false, NmStatus.Stale),
        ];

        // Collections are materialised after every Add* call: an ObservableCollection copy taken
        // before them would stay empty and the toolbar would render no chips.
        ModeOptions = new ObservableCollection<ThemeStudioOption>(_modeOptions);
        AppearanceOptions = new ObservableCollection<ThemeStudioOption>(_appearanceOptions);
        DensityOptions = new ObservableCollection<ThemeStudioOption>(_densityOptions);
        ZoomOptions = new ObservableCollection<ThemeStudioOption>(_zoomOptions);

        SampleRows =
        [
            new("原文", "これはサンプルです。"),
            new("机器译文", "这是示例。"),
            new("人工译文", "这是示例内容。", NmStatus.Done),
            new("Review", "已确认", NmStatus.Done),
            new("四轨", "原图 ● / 文本 ● / 修复 ◐ / 排版 ·"),
        ];
    }

    public ObservableCollection<ThemeStudioOption> ModeOptions { get; }

    public ObservableCollection<ThemeStudioOption> AppearanceOptions { get; }

    public ObservableCollection<ThemeStudioOption> DensityOptions { get; }

    public ObservableCollection<ThemeStudioOption> ZoomOptions { get; }

    public IReadOnlyList<ThemeStudioSampleBook> SampleBooks { get; }

    public IReadOnlyList<ThemeStudioSamplePage> SamplePages { get; }

    public IReadOnlyList<ThemeStudioSampleRegion> SampleRegions { get; }

    public IReadOnlyList<ThemeStudioSampleRow> SampleRows { get; }

    /// <summary>Current preview surface.</summary>
    public ThemeStudioPreviewMode Mode
    {
        get => _mode;
        private set
        {
            if (Set(ref _mode, value))
            {
                OnPropertyChanged(nameof(IsShelf), nameof(IsWorkbench), nameof(IsReader), nameof(ModeLabel));
            }
        }
    }

    public bool IsShelf => Mode == ThemeStudioPreviewMode.Shelf;

    public bool IsWorkbench => Mode == ThemeStudioPreviewMode.Workbench;

    public bool IsReader => Mode == ThemeStudioPreviewMode.Reader;

    public string ModeLabel => Mode switch
    {
        ThemeStudioPreviewMode.Workbench => "工作台",
        ThemeStudioPreviewMode.Reader => "阅读器",
        _ => "书架",
    };

    /// <summary>Appearance simulated for the preview (independent of the applied setting).</summary>
    public AppearanceMode PreviewAppearance
    {
        get => _previewAppearance;
        private set
        {
            if (Set(ref _previewAppearance, value))
            {
                OnPropertyChanged(nameof(PreviewAppearanceLabel));
                RebuildPalette();
            }
        }
    }

    public string PreviewAppearanceLabel => ThemeStudioLabels.Appearance(PreviewAppearance);

    public bool HighContrast
    {
        get => _highContrast;
        set
        {
            if (Set(ref _highContrast, value))
            {
                RebuildPalette();
            }
        }
    }

    public Density Density
    {
        get => _density;
        private set
        {
            if (Set(ref _density, value))
            {
                OnPropertyChanged(nameof(DensityLabel));
                RebuildPalette();
            }
        }
    }

    public string DensityLabel => ThemeStudioLabels.DensityLabel(Density);

    /// <summary>Zoom applied to the preview surface (50/75/100%).</summary>
    public double Zoom
    {
        get => _zoom;
        private set
        {
            if (Set(ref _zoom, value))
            {
                OnPropertyChanged(nameof(ZoomLabel));
            }
        }
    }

    public string ZoomLabel => $"{Zoom * 100:0}%";

    /// <summary>The scoped palette of the previewed theme (bound into the section's PaletteScope).</summary>
    public ThemeStudioPalette? Palette
    {
        get => _palette;
        private set => Set(ref _palette, value);
    }

    /// <summary>Anti-confusion line: applied theme vs session theme (spec §3.2).</summary>
    public string ComparisonLabel
    {
        get
        {
            var applied = Owner.Service.CurrentTheme.Name;
            var draft = Owner.Service.DraftPackage?.Descriptor.Name;
            return draft is null || string.Equals(draft, applied, StringComparison.Ordinal)
                ? $"当前主题 = {applied}（预览与已应用一致）"
                : $"当前主题 = {applied} / 会话主题 = {draft}（未应用）";
        }
    }

    public void SelectMode(ThemeStudioPreviewMode mode)
    {
        Mode = mode;
        foreach (var option in _modeOptions)
        {
            option.IsSelected = string.Equals(option.Key, mode.ToString(), StringComparison.Ordinal);
        }
    }

    public void SelectAppearance(AppearanceMode appearance)
    {
        PreviewAppearance = appearance;
        foreach (var option in _appearanceOptions)
        {
            option.IsSelected = string.Equals(option.Key, appearance.ToString(), StringComparison.Ordinal);
        }
    }

    public void SelectDensity(Density density)
    {
        Density = density;
        foreach (var option in _densityOptions)
        {
            option.IsSelected = string.Equals(option.Key, density.ToString(), StringComparison.Ordinal);
        }
    }

    public void SelectZoom(double zoom)
    {
        Zoom = zoom;
        foreach (var option in _zoomOptions)
        {
            option.IsSelected = Math.Abs(zoom - double.Parse(option.Key, System.Globalization.CultureInfo.InvariantCulture)) < 0.001;
        }
    }

    /// <inheritdoc />
    public override void OnActivated()
    {
        // Start from the applied appearance so the preview opens on what the user currently sees.
        SelectAppearance(Owner.Service.Settings.Appearance);
        SelectDensity(Owner.Service.Settings.Layout.Density);
        RebuildPalette();
        OnPropertyChanged(nameof(ComparisonLabel));
    }

    /// <summary>Recomposes the scoped palette after a draft/settings change.</summary>
    public void RebuildPalette()
    {
        var package = Owner.Service.DraftPackage ?? Owner.Service.AppliedPackage;
        var request = new ThemeStudioPaletteRequest(
            Appearance: PreviewAppearance,
            Contrast: HighContrast ? ContrastMode.High : ContrastMode.Standard,
            Density: Density,
            ReducedMotion: Owner.Service.Settings.ReducedMotion,
            FollowSystemAccent: Owner.Service.Settings.FollowSystemAccent);
        Palette = Owner.Service.ComposePalette(package, request);
        OnPropertyChanged(nameof(ComparisonLabel));
    }

    private void AddMode(ThemeStudioPreviewMode mode, string label, string description)
    {
        var option = new ThemeStudioOption(
            mode.ToString(),
            label,
            description,
            new RelayCommand(() => SelectMode(mode)));
        option.IsSelected = mode == _mode;
        _modeOptions.Add(option);
    }

    private void AddAppearance(AppearanceMode mode, string label, string? description)
    {
        var option = new ThemeStudioOption(
            mode.ToString(),
            label,
            description,
            new RelayCommand(() => SelectAppearance(mode)));
        _appearanceOptions.Add(option);
    }

    private void AddDensity(Density density, string label, string? description)
    {
        var option = new ThemeStudioOption(
            density.ToString(),
            label,
            description,
            new RelayCommand(() => SelectDensity(density)));
        option.IsSelected = density == _density;
        _densityOptions.Add(option);
    }

    private void AddZoom(double zoom, string label)
    {
        var option = new ThemeStudioOption(
            zoom.ToString("0.00", System.Globalization.CultureInfo.InvariantCulture),
            label,
            null,
            new RelayCommand(() => SelectZoom(zoom)));
        option.IsSelected = Math.Abs(zoom - 1.0) < 0.001;
        _zoomOptions.Add(option);
    }
}

/// <summary>
/// ⑤ 外观 (THEME_STUDIO_SPEC §3.5): appearance / contrast / reduced motion / system accent / density apply
/// immediately (they are settings, not theme packages). Layout entries are read-only because V1 only
/// implements <c>TopBand</c> navigation — they are explicitly marked 预留 instead of being fake switches.
/// </summary>
public sealed class ThemeStudioAppearanceViewModel : ThemeStudioSectionViewModel
{
    private readonly List<ThemeStudioOption> _appearanceOptions = new();
    private readonly List<ThemeStudioOption> _densityOptions = new();

    internal ThemeStudioAppearanceViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.Appearance)
    {
        AddAppearance(
            AppearanceMode.Light,
            "浅色",
            "全应用使用浅色令牌；深色主题的浅色变体生效。");
        AddAppearance(
            AppearanceMode.Dark,
            "深色",
            "全应用使用深色令牌；A+C 暗房基线。");
        AddAppearance(
            AppearanceMode.System,
            "系统跟随",
            "跟随 Windows 浅色/深色设置；系统切换时自动替换令牌字典。");

        AddDensity(Density.Compact, "紧凑", "行高 24，面板内边距 8");
        AddDensity(Density.Comfortable, "舒适", "行高 26–28，面板内边距 12");
        AddDensity(Density.Spacious, "宽松", "行高 32，面板内边距 16");

        AppearanceOptions = new ObservableCollection<ThemeStudioOption>(_appearanceOptions);
        DensityOptions = new ObservableCollection<ThemeStudioOption>(_densityOptions);

        LayoutRows = new[]
        {
            new ThemeStudioInfoRow("导航", "TopBand（V1 生效）", "侧栏 / Dock 为预留枚举，不做假开关"),
            new ThemeStudioInfoRow("书架布局", "预留", "网格 / 列表 / 瀑布流随 Library 后续任务生效"),
            new ThemeStudioInfoRow("工作台布局", "预留", "堆叠 / 分栏随 Studio 后续任务生效"),
            new ThemeStudioInfoRow("阅读器布局", "预留", "整页 / 适宽 / 双页 / Webtoon 随阅读器任务生效"),
        };
    }

    public ObservableCollection<ThemeStudioOption> AppearanceOptions { get; }

    public ObservableCollection<ThemeStudioOption> DensityOptions { get; }

    public IReadOnlyList<ThemeStudioInfoRow> LayoutRows { get; }

    public bool HighContrast => Owner.Service.Settings.Contrast == ContrastMode.High;

    public bool ReducedMotion => Owner.Service.Settings.ReducedMotion;

    public bool FollowSystemAccent => Owner.Service.Settings.FollowSystemAccent;

    /// <summary>Two-way wrapper for the high-contrast ToggleSwitch (applies immediately).</summary>
    public bool IsHighContrastOn
    {
        get => HighContrast;
        set
        {
            if (value != HighContrast)
            {
                SetHighContrast(value);
            }

            OnPropertyChanged();
        }
    }

    /// <summary>Two-way wrapper for the reduced-motion ToggleSwitch.</summary>
    public bool IsReducedMotionOn
    {
        get => ReducedMotion;
        set
        {
            if (value != ReducedMotion)
            {
                SetReducedMotion(value);
            }

            OnPropertyChanged();
        }
    }

    /// <summary>Two-way wrapper for the system-accent ToggleSwitch.</summary>
    public bool IsFollowSystemAccentOn
    {
        get => FollowSystemAccent;
        set
        {
            if (value != FollowSystemAccent)
            {
                SetFollowSystemAccent(value);
            }

            OnPropertyChanged();
        }
    }

    public string AppearanceSummary => ThemeStudioLabels.Appearance(Owner.Service.Settings.Appearance);

    public string EffectSummary =>
        $"外观：{AppearanceSummary} · 对比度：{ThemeStudioLabels.Contrast(Owner.Service.Settings.Contrast)} · " +
        $"密度：{ThemeStudioLabels.DensityLabel(Owner.Service.Settings.Layout.Density)}" +
        (Owner.Service.Settings.ReducedMotion ? " · 减少动效" : string.Empty) +
        (Owner.Service.Settings.FollowSystemAccent ? " · 系统强调色基线" : string.Empty);

    public ICommand ToggleHighContrastCommand => _toggleHighContrast ??= new RelayCommand(ToggleHighContrast);

    public ICommand ToggleReducedMotionCommand => _toggleReducedMotion ??= new RelayCommand(ToggleReducedMotion);

    public ICommand ToggleFollowSystemAccentCommand =>
        _toggleFollowAccent ??= new RelayCommand(ToggleFollowSystemAccent);

    private ICommand? _toggleHighContrast;
    private ICommand? _toggleReducedMotion;
    private ICommand? _toggleFollowAccent;

    public void SelectAppearance(AppearanceMode mode)
    {
        foreach (var option in _appearanceOptions)
        {
            option.IsSelected = string.Equals(option.Key, mode.ToString(), StringComparison.Ordinal);
        }

        Run(() => Owner.SetAppearanceAsync(mode));
    }

    public void SelectDensity(Density density)
    {
        foreach (var option in _densityOptions)
        {
            option.IsSelected = string.Equals(option.Key, density.ToString(), StringComparison.Ordinal);
        }

        Run(() => Owner.SetDensityAsync(density));
    }

    public void SetHighContrast(bool enabled) => Run(() => Owner.SetContrastAsync(enabled));

    public void SetReducedMotion(bool enabled) => Run(() => Owner.SetReducedMotionAsync(enabled));

    public void SetFollowSystemAccent(bool enabled) => Run(() => Owner.SetFollowSystemAccentAsync(enabled));

    private void ToggleHighContrast() => SetHighContrast(!HighContrast);

    private void ToggleReducedMotion() => SetReducedMotion(!ReducedMotion);

    private void ToggleFollowSystemAccent() => SetFollowSystemAccent(!FollowSystemAccent);

    /// <inheritdoc />
    public override void OnActivated() => Refresh();

    public void Refresh()
    {
        var settings = Owner.Service.Settings;
        foreach (var option in _appearanceOptions)
        {
            option.IsSelected = string.Equals(option.Key, settings.Appearance.ToString(), StringComparison.Ordinal);
        }

        foreach (var option in _densityOptions)
        {
            option.IsSelected = string.Equals(option.Key, settings.Layout.Density.ToString(), StringComparison.Ordinal);
        }

        OnPropertyChanged(
            nameof(HighContrast),
            nameof(ReducedMotion),
            nameof(FollowSystemAccent),
            nameof(AppearanceSummary),
            nameof(EffectSummary),
            nameof(ToggleHighContrastCommand),
            nameof(ToggleReducedMotionCommand),
            nameof(ToggleFollowSystemAccentCommand));
    }

    private void AddAppearance(AppearanceMode mode, string label, string description)
    {
        _appearanceOptions.Add(new ThemeStudioOption(
            mode.ToString(),
            label,
            description,
            new RelayCommand(() => SelectAppearance(mode))));
    }

    private void AddDensity(Density density, string label, string description)
    {
        _densityOptions.Add(new ThemeStudioOption(
            density.ToString(),
            label,
            description,
            new RelayCommand(() => SelectDensity(density))));
    }
}
