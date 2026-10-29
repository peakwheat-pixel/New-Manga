using System.Collections.ObjectModel;
using System.Windows.Input;
using Avalonia.Controls;
using Avalonia.Media;
using NewManga.App.Shell.V2;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// The seven Theme Studio sections (THEME_STUDIO_SPEC §2). Order is the frozen navigation order
/// (1 主题库 … 7 恢复默认) and is also the Tab order of the left rail.
/// </summary>
public enum ThemeStudioSection
{
    Library = 0,
    Preview = 1,
    MyThemes = 2,
    Editor = 3,
    Appearance = 4,
    ImportExport = 5,
    Reset = 6,
}

/// <summary>UI severity of one validation finding (contract §4 keeps severity as an "error"/"warning" string).</summary>
public enum ThemeStudioIssueLevel
{
    Info,
    Warning,
    Error,
}

/// <summary>
/// One validation finding shown to the user: level + path + explanation + suggestion
/// (THEME_STUDIO_SPEC §3.6 "级别/路径/说明/建议").
/// </summary>
public sealed record ThemeStudioIssue(
    string Code,
    ThemeStudioIssueLevel Level,
    string Message,
    string? Path,
    string? Suggestion)
{
    /// <summary>True when this finding must block import/apply.</summary>
    public bool IsError => Level == ThemeStudioIssueLevel.Error;

    /// <summary>Display label of the level ("错误"/"警告"/"提示").</summary>
    public string LevelLabel => Level switch
    {
        ThemeStudioIssueLevel.Error => "错误",
        ThemeStudioIssueLevel.Warning => "警告",
        _ => "提示",
    };

    /// <summary>Path or an em dash, so the column never collapses.</summary>
    public string PathLabel => string.IsNullOrEmpty(Path) ? "—" : Path;

    /// <summary>Suggestion or a neutral fallback.</summary>
    public string SuggestionLabel => string.IsNullOrEmpty(Suggestion) ? ThemeStudioLabels.NoSuggestion : Suggestion;

    /// <summary>Projects an engine finding into the UI shape, deriving a stable suggestion from the code.</summary>
    public static ThemeStudioIssue From(ThemeValidationIssue issue)
    {
        ArgumentNullException.ThrowIfNull(issue);
        var level = issue.IsError ? ThemeStudioIssueLevel.Error : ThemeStudioIssueLevel.Warning;
        return new ThemeStudioIssue(issue.Code, level, issue.Message, issue.Path, ThemeStudioSuggestions.For(issue.Code));
    }
}

/// <summary>Validation outcome with the UI projection of every finding.</summary>
public sealed record ThemeStudioValidationReport(bool IsValid, IReadOnlyList<ThemeStudioIssue> Issues)
{
    /// <summary>Valid with no findings.</summary>
    public static ThemeStudioValidationReport Ok { get; } = new(true, []);

    /// <summary>Every error finding, in order.</summary>
    public IReadOnlyList<ThemeStudioIssue> Errors =>
        Issues.Where(static issue => issue.IsError).ToArray();

    /// <summary>Every non-error finding, in order.</summary>
    public IReadOnlyList<ThemeStudioIssue> Warnings =>
        Issues.Where(static issue => !issue.IsError).ToArray();

    public int ErrorCount => Errors.Count;

    public int WarningCount => Warnings.Count;

    /// <summary>"通过" / "N 个错误" summary used by the surface chrome and the right rail.</summary>
    public string Summary => IsValid
        ? (WarningCount == 0 ? "通过" : $"通过（{WarningCount} 条警告）")
        : $"未通过（{ErrorCount} 个错误）";

    /// <summary>Builds a report from findings; valid only when no finding is an error.</summary>
    public static ThemeStudioValidationReport From(IEnumerable<ThemeStudioIssue> issues)
    {
        ArgumentNullException.ThrowIfNull(issues);
        var list = issues as IReadOnlyList<ThemeStudioIssue> ?? issues.ToArray();
        return new ThemeStudioValidationReport(list.All(static issue => !issue.IsError), list);
    }

    /// <summary>Projects an engine result.</summary>
    public static ThemeStudioValidationReport From(ThemeValidationResult result)
    {
        ArgumentNullException.ThrowIfNull(result);
        return From(result.Issues.Select(ThemeStudioIssue.From));
    }
}

/// <summary>What the packaged service can actually do; drives the honest "STUB / NOT_WIRED" labels.</summary>
/// <param name="EngineConnected">True when a real <see cref="IThemeService"/> seam is wired.</param>
/// <param name="PersistsSettings">True when the applied theme/settings survive a restart.</param>
/// <param name="CanApplyAppWide">True when "应用" changes the whole application (not only this surface).</param>
/// <param name="CanManageUserThemes">True when user theme files can be installed/uninstalled/exported.</param>
/// <param name="SourceLabel">Where the catalog comes from ("Theme Engine v1" / "STUB 临时沙箱").</param>
/// <param name="Note">Optional honesty note rendered in the right rail.</param>
public sealed record ThemeStudioCapabilities(
    bool EngineConnected,
    bool PersistsSettings,
    bool CanApplyAppWide,
    bool CanManageUserThemes,
    bool IsSandbox,
    string SourceLabel,
    string? Note)
{
    /// <summary>False when the surface must not claim a durable "已应用" success.</summary>
    public bool ShowsDurableApplyLabel => PersistsSettings && CanApplyAppWide;
}

/// <summary>One retired-theme-id migration decision surfaced by the engine (retirement plan §2.1).</summary>
public sealed record ThemeStudioMigrationNotice(string LegacyId, string Message)
{
    /// <summary>Short level label for the banner.</summary>
    public string LevelLabel => "已迁移";
}

/// <summary>Outcome of "应用" (THEME_STUDIO_SPEC §4).</summary>
public sealed record ThemeStudioApplyResult(
    bool Success,
    string? AppliedThemeId,
    bool Persisted,
    IReadOnlyList<ThemeStudioIssue> Issues,
    bool Recovered)
{
    /// <summary>Applied and persisted.</summary>
    public static ThemeStudioApplyResult Applied(string themeId, bool persisted) =>
        new(true, themeId, persisted, [], false);

    /// <summary>Applied but a fallback was needed (unknown id resolved to the default theme).</summary>
    public static ThemeStudioApplyResult RecoveredWith(
        string themeId,
        bool persisted,
        IEnumerable<ThemeStudioIssue> issues) =>
        new(true, themeId, persisted, issues as IReadOnlyList<ThemeStudioIssue> ?? issues.ToArray(), true);

    /// <summary>Nothing was applied; the caller keeps the previous state.</summary>
    public static ThemeStudioApplyResult Failed(IEnumerable<ThemeStudioIssue> issues) =>
        new(false, null, false, issues as IReadOnlyList<ThemeStudioIssue> ?? issues.ToArray(), false);

    public string StatusLabel => Success
        ? (Persisted ? "已应用并保存" : "已应用（预览，未持久化）")
        : "应用失败";
}

/// <summary>Outcome of a user-theme management command (import/export/duplicate/delete/save/favorite).</summary>
public sealed record ThemeStudioOperationResult(
    bool Success,
    string Message,
    IReadOnlyList<ThemeStudioIssue> Issues)
{
    /// <summary>Successful operation without findings.</summary>
    public static ThemeStudioOperationResult Ok(string message) => new(true, message, []);

    /// <summary>Failed operation with findings.</summary>
    public static ThemeStudioOperationResult Fail(string message, IEnumerable<ThemeStudioIssue> issues) =>
        new(false, message, issues as IReadOnlyList<ThemeStudioIssue> ?? issues.ToArray());

    /// <summary>Successful operation that still carries warnings.</summary>
    public static ThemeStudioOperationResult OkWith(string message, IEnumerable<ThemeStudioIssue> issues) =>
        new(true, message, issues as IReadOnlyList<ThemeStudioIssue> ?? issues.ToArray());
}

/// <summary>
/// Appearance/contrast/density/motion knobs a palette is composed for. Appearance is resolved against
/// the platform light/dark state (or pinned through <see cref="VariantOverride"/> for the preview section).
/// </summary>
public sealed record ThemeStudioPaletteRequest(
    AppearanceMode Appearance = AppearanceMode.Dark,
    PaletteVariant? VariantOverride = null,
    ContrastMode Contrast = ContrastMode.Standard,
    Density Density = Density.Comfortable,
    bool ReducedMotion = false,
    bool FollowSystemAccent = false)
{
    /// <summary>Request used by the library cards / right rail for the currently applied settings.</summary>
    public static ThemeStudioPaletteRequest FromSettings(ThemeSettings settings, PaletteVariant? variant = null) =>
        new(settings.Appearance, variant, settings.Contrast, settings.Layout.Density, settings.ReducedMotion, settings.FollowSystemAccent);
}

/// <summary>A scoped <c>Nm.*</c> token layer ready to be installed on a subtree (DynamicResource resolves it).</summary>
public sealed record ThemeStudioPalette(string ThemeId, PaletteVariant Variant, IResourceDictionary Tokens)
{
    /// <summary>True when a brush token exists and can be inspected (used by tests and probes).</summary>
    public IBrush? Brush(string key) =>
        Tokens.TryGetResource(key, Avalonia.Styling.ThemeVariant.Default, out var value) ? value as IBrush : null;
}

/// <summary>One row of the live WCAG audit (THEME_STUDIO_SPEC §5 / DESIGN_SYSTEM §2.3).</summary>
public sealed record ThemeStudioContrastRow(
    string Label,
    string ForegroundKey,
    string BackgroundKey,
    double Ratio,
    double Floor,
    bool IsRequired)
{
    public bool Pass => Ratio + 1e-9 >= Floor;

    /// <summary>"7.42:1（≥7:1）" — the numeric value is always visible, never color-only (AC11).</summary>
    public string RatioLabel => $"{Ratio:0.00}:1（≥{Floor:0.##}:1）";

    /// <summary>Status text channel: the pass/fail state is readable without colour.</summary>
    public string StateLabel => Pass ? "通过" : "未通过";
}

/// <summary>The full live audit of one theme variant.</summary>
public sealed record ThemeStudioContrastReport(PaletteVariant Variant, IReadOnlyList<ThemeStudioContrastRow> Rows)
{
    public int PassCount => Rows.Count(static row => row.Pass);

    public IReadOnlyList<ThemeStudioContrastRow> Failures =>
        Rows.Where(static row => !row.Pass).ToArray();

    public bool IsPassing => Failures.Count == 0;

    /// <summary>Compact summary for the right rail ("13 项通过 / 0 项失败").</summary>
    public string Summary => Failures.Count == 0
        ? $"{Rows.Count} 项全部通过"
        : $"{PassCount}/{Rows.Count} 项通过 · {Failures.Count} 项未通过";

    /// <summary>Worst ratio (used to rank / filter "高对比友好" themes).</summary>
    public double WorstRatio => Rows.Count == 0 ? 0 : Rows.Min(static row => row.Ratio);
}

/// <summary>Display state of one dialog opened by the surface (THEME_STUDIO_SPEC §3.4/§3.7).</summary>
public enum ThemeStudioDialogKind
{
    None,
    UnsavedChanges,
    ResetConfirm,
    ResetClearThemesConfirm,
    SaveAsTheme,
    DeleteTheme,
    OverwriteTheme,
    ImportConfirm,
}

/// <summary>One command button inside a dialog.</summary>
public sealed record ThemeStudioDialogAction(
    string Label,
    bool IsPrimary,
    bool IsDanger,
    ICommand Command,
    string? KeyHint = null);

/// <summary>
/// Modal dialog state. The surface renders it as an overlay and routes <c>Esc</c> to
/// <see cref="CancelCommand"/>; every dialog spells out its consequence (DESIGN_SYSTEM §6.2).
/// </summary>
public sealed class ThemeStudioDialogViewModel : ObservableObject
{
    private string _title = string.Empty;
    private string _message = string.Empty;
    private string? _footnote;
    private string _nameInput = string.Empty;
    private string _authorInput = string.Empty;
    private string _tagsInput = string.Empty;
    private bool _isInputVisible;
    private bool _isCheckboxVisible;
    private bool _isChecked;
    private string _checkboxLabel = string.Empty;
    private string _validationMessage = string.Empty;
    private bool _hasValidationError;

    public ThemeStudioDialogKind Kind { get; private set; }

    public string Title
    {
        get => _title;
        private set => Set(ref _title, value);
    }

    public string Message
    {
        get => _message;
        private set => Set(ref _message, value);
    }

    public string? Footnote
    {
        get => _footnote;
        private set => Set(ref _footnote, value);
    }

    public bool HasFootnote => !string.IsNullOrEmpty(Footnote);

    public string NameInput
    {
        get => _nameInput;
        set => Set(ref _nameInput, value);
    }

    public string AuthorInput
    {
        get => _authorInput;
        set => Set(ref _authorInput, value);
    }

    public string TagsInput
    {
        get => _tagsInput;
        set => Set(ref _tagsInput, value);
    }

    public bool IsInputVisible
    {
        get => _isInputVisible;
        private set => Set(ref _isInputVisible, value);
    }

    public bool IsCheckboxVisible
    {
        get => _isCheckboxVisible;
        private set => Set(ref _isCheckboxVisible, value);
    }

    public bool IsChecked
    {
        get => _isChecked;
        set => Set(ref _isChecked, value);
    }

    public string CheckboxLabel
    {
        get => _checkboxLabel;
        private set => Set(ref _checkboxLabel, value);
    }

    public string ValidationMessage
    {
        get => _validationMessage;
        set
        {
            if (Set(ref _validationMessage, value))
            {
                OnPropertyChanged(nameof(HasValidationMessage));
            }
        }
    }

    public bool HasValidationMessage => !string.IsNullOrEmpty(ValidationMessage);

    public bool HasValidationError
    {
        get => _hasValidationError;
        set => Set(ref _hasValidationError, value);
    }

    public ObservableCollection<ThemeStudioDialogAction> Actions { get; } = new();

    public ICommand CancelCommand { get; internal set; } = EmptyCommand.Instance;

    public bool IsOpen => Kind != ThemeStudioDialogKind.None;

    internal void Configure(
        ThemeStudioDialogKind kind,
        string title,
        string message,
        string? footnote,
        IEnumerable<ThemeStudioDialogAction> actions,
        string? name = null,
        string? author = null,
        string? tags = null,
        string? checkboxLabel = null)
    {
        Kind = kind;
        Title = title;
        Message = message;
        Footnote = footnote;
        Actions.Clear();
        foreach (var action in actions)
        {
            Actions.Add(action);
        }

        NameInput = name ?? string.Empty;
        AuthorInput = author ?? string.Empty;
        TagsInput = tags ?? string.Empty;
        IsInputVisible = kind is ThemeStudioDialogKind.SaveAsTheme or ThemeStudioDialogKind.OverwriteTheme;
        IsCheckboxVisible = checkboxLabel is not null;
        CheckboxLabel = checkboxLabel ?? string.Empty;
        IsChecked = false;
        ValidationMessage = string.Empty;
        HasValidationError = false;
        OnPropertyChanged(nameof(IsOpen), nameof(HasFootnote));
    }

    internal void Close()
    {
        Kind = ThemeStudioDialogKind.None;
        Actions.Clear();
        OnPropertyChanged(nameof(IsOpen));
    }
}

/// <summary>No-op command used before the owning view model wires the real one.</summary>
internal sealed class EmptyCommand : ICommand
{
    public static EmptyCommand Instance { get; } = new();

    public event EventHandler? CanExecuteChanged
    {
        add { }
        remove { }
    }

    public bool CanExecute(object? parameter) => false;

    public void Execute(object? parameter)
    {
    }
}

/// <summary>Static display vocabulary of the surface (Chinese copy lives in one place).</summary>
public static class ThemeStudioLabels
{
    public const string NoSuggestion = "按规范修正后重试";

    public const string SampleContent = "示例内容";

    public const string SampleContentHint = "示例内容 · 非真实书库";

    public const string StubBadge = "STUB";

    public const string NotWiredBadge = "NOT_WIRED";

    public static string Section(ThemeStudioSection section) => section switch
    {
        ThemeStudioSection.Library => "主题库",
        ThemeStudioSection.Preview => "预览",
        ThemeStudioSection.MyThemes => "我的主题",
        ThemeStudioSection.Editor => "主题编辑",
        ThemeStudioSection.Appearance => "外观",
        ThemeStudioSection.ImportExport => "导入导出",
        _ => "恢复默认",
    };

    public static string SectionSubtitle(ThemeStudioSection section) => section switch
    {
        ThemeStudioSection.Library => "搜索 / 分类 / 筛选 / 收藏",
        ThemeStudioSection.Preview => "书架 · 工作台 · 阅读器",
        ThemeStudioSection.MyThemes => "已安装 / 收藏 / 自定义",
        ThemeStudioSection.Editor => "配色 / 字体 / 圆角 / 材质 / 阴影 / 动效",
        ThemeStudioSection.Appearance => "浅色 / 深色 / 系统 + 无障碍",
        ThemeStudioSection.ImportExport => ".nmtheme / .json 校验与导出",
        _ => "二次确认后重置",
    };

    public static IReadOnlyList<ThemeStudioSection> AllSections { get; } =
    [
        ThemeStudioSection.Library,
        ThemeStudioSection.Preview,
        ThemeStudioSection.MyThemes,
        ThemeStudioSection.Editor,
        ThemeStudioSection.Appearance,
        ThemeStudioSection.ImportExport,
        ThemeStudioSection.Reset,
    ];

    public static string Appearance(AppearanceMode mode) => mode switch
    {
        AppearanceMode.Light => "浅色",
        AppearanceMode.Dark => "深色",
        _ => "系统跟随",
    };

    public static string Contrast(ContrastMode mode) => mode == ContrastMode.High ? "高对比" : "标准";

    public static string DensityLabel(Density density) => density switch
    {
        Density.Compact => "紧凑",
        Density.Spacious => "宽松",
        _ => "舒适",
    };

    public static string Navigation(LayoutNavigation navigation) => navigation switch
    {
        LayoutNavigation.Sidebar => "侧栏（预留）",
        LayoutNavigation.Dock => "Dock（预留）",
        _ => "TopBand",
    };

    public static string Shelf(ShelfLayout shelf) => shelf switch
    {
        ShelfLayout.List => "列表",
        ShelfLayout.Masonry => "瀑布流",
        _ => "网格",
    };

    public static string Workbench(WorkbenchLayout layout) => layout == WorkbenchLayout.Split ? "分栏" : "堆叠";

    public static string Reader(ReaderLayout layout) => layout switch
    {
        ReaderLayout.FitWidth => "适宽",
        ReaderLayout.DoublePage => "双页",
        ReaderLayout.Webtoon => "Webtoon 纵向",
        _ => "整页",
    };

    public static string ThemeKindLabel(ThemeKind kind) => kind == ThemeKind.BuiltIn ? "内置" : "用户";

    /// <summary>Light/dark support badge text — never colour-only (AC11).</summary>
    public static string AppearanceSupport(bool supportsLight, bool supportsDark) => (supportsLight, supportsDark) switch
    {
        (true, true) => "明暗均支持",
        (true, false) => "仅浅色",
        (false, true) => "仅深色",
        _ => "无外观声明",
    };

    public static string Material(ThemeMaterial material) => material == ThemeMaterial.Solid ? "Solid" : "None";

    public static string Elevation(ThemeElevation elevation) => elevation == ThemeElevation.Raised ? "raised" : "none";

    public static string LineHeight(LineHeightPreset preset) => preset switch
    {
        LineHeightPreset.Tight => "紧凑（1.25）",
        LineHeightPreset.Loose => "宽松（1.6）",
        _ => "标准（1.45）",
    };
}

/// <summary>Stable, code-driven suggestions so every finding has an actionable hint (AC7).</summary>
public static class ThemeStudioSuggestions
{
    public static string? For(string code)
    {
        if (string.IsNullOrEmpty(code))
        {
            return null;
        }

        if (code.StartsWith("colors.missing-key", StringComparison.Ordinal))
        {
            return "补齐该 Nm.Color.* 键（主题包必须定义全部 35 个颜色键）";
        }

        if (code.StartsWith("colors.invalid-value", StringComparison.Ordinal))
        {
            return "使用 #RRGGBB / #AARRGGBB / rgb() / rgba() 中的一种写法";
        }

        if (code.StartsWith("colors.unknown-key", StringComparison.Ordinal))
        {
            return "删除未知颜色键，或使用契约 §2.2 中的键名";
        }

        if (code.StartsWith("corners.", StringComparison.Ordinal))
        {
            return "圆角只能取 0–3px（DESIGN_SYSTEM §1 规则 4）";
        }

        if (code.StartsWith("contrast.", StringComparison.Ordinal))
        {
            return "提高该颜色的明度差，正文 ≥7:1、次要/状态 ≥4.5:1";
        }

        if (code.StartsWith("typography.", StringComparison.Ordinal))
        {
            return "使用系统字体族名（禁止字体文件路径），字号缩放保持在 80–130%";
        }

        if (code.StartsWith("motion.", StringComparison.Ordinal))
        {
            return "动效时长 0–1000ms，且 fast 不应大于 normal";
        }

        if (code.StartsWith("package.schema", StringComparison.Ordinal))
        {
            return "主题包 schema 必须是 newmanga.theme/1";
        }

        if (code.StartsWith("descriptor.", StringComparison.Ordinal))
        {
            return "id 用小写 slug（3–64 字符），并填写名称、版本与至少一种外观";
        }

        if (code.StartsWith("json.", StringComparison.Ordinal) || code.StartsWith("package.", StringComparison.Ordinal))
        {
            return "检查 JSON 语法与字段拼写后重新导入";
        }

        return null;
    }
}
