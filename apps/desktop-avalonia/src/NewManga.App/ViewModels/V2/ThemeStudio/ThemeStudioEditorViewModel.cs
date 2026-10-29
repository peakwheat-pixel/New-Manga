using System.Collections.ObjectModel;
using System.Globalization;
using System.Windows.Input;
using Avalonia.Media;
using NewManga.App.Shell.V2;
using NewManga.DesignSystem;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>One editable semantic colour of the editor (35 rows grouped by colour family).</summary>
public sealed class ThemeStudioColorRow : ObservableObject
{
    private readonly ThemeStudioEditorViewModel _owner;
    private string _hexValue;
    private IBrush _swatch = Brushes.Transparent;
    private string _contrastLabel = "—";
    private bool _isInvalid;

    internal ThemeStudioColorRow(ThemeStudioEditorViewModel owner, string tokenKey, string label, string hexValue)
    {
        _owner = owner;
        TokenKey = tokenKey;
        Label = label;
        _hexValue = hexValue;
        UpdateSwatch();
    }

    public string TokenKey { get; }

    /// <summary>Human label ("正文 / 主") — the key itself stays available in the tooltip.</summary>
    public string Label { get; }

    /// <summary>Raw colour value as stored in the theme package.</summary>
    public string HexValue
    {
        get => _hexValue;
        set
        {
            var next = (value ?? string.Empty).Trim();
            if (!Set(ref _hexValue, next))
            {
                return;
            }

            if (!TryParse(next, out var color))
            {
                IsInvalid = true;
                return;
            }

            IsInvalid = false;
            UpdateSwatch(color);
            _owner.ApplyColor(TokenKey, next);
        }
    }

    public IBrush Swatch
    {
        get => _swatch;
        private set => Set(ref _swatch, value);
    }

    /// <summary>Live contrast ratio against the panel surface (text/status rows only otherwise "—").</summary>
    public string ContrastLabel
    {
        get => _contrastLabel;
        internal set => Set(ref _contrastLabel, value);
    }

    public bool IsInvalid
    {
        get => _isInvalid;
        private set => Set(ref _isInvalid, value);
    }

    public string AccessibleLabel => $"{Label}（{TokenKey}）当前值 {HexValue}";

    internal void SetValue(string hexValue, IBrush swatch)
    {
        _hexValue = hexValue;
        _swatch = swatch;
        IsInvalid = false;
        OnPropertyChanged(nameof(HexValue), nameof(Swatch), nameof(IsInvalid), nameof(AccessibleLabel));
    }

    private void UpdateSwatch()
    {
        if (TryParse(_hexValue, out var color))
        {
            UpdateSwatch(color);
        }
    }

    private void UpdateSwatch(Color color)
    {
        Swatch = new SolidColorBrush(color);
        OnPropertyChanged(nameof(AccessibleLabel));
    }

    private static bool TryParse(string raw, out Color color)
    {
        color = default;
        if (string.IsNullOrWhiteSpace(raw))
        {
            return false;
        }

        return Color.TryParse(raw, out color);
    }
}

/// <summary>A semantic colour group of the editor ("配色" section, THEME_STUDIO_SPEC §3.4).</summary>
public sealed class ThemeStudioColorGroup
{
    internal ThemeStudioColorGroup(string key, string title)
    {
        Key = key;
        Title = title;
    }

    public string Key { get; }

    public string Title { get; }

    public ObservableCollection<ThemeStudioColorRow> Rows { get; } = new();
}

/// <summary>
/// ④ 主题编辑 (THEME_STUDIO_SPEC §3.4): six groups — colours (with live WCAG numbers), typography,
/// corners, material, elevation, motion — plus "从当前主题另存为". Every edit goes into the draft package
/// and immediately recomposes the scoped preview palette; nothing is applied until 应用.
/// </summary>
public sealed class ThemeStudioEditorViewModel : ThemeStudioSectionViewModel
{
    private readonly List<ThemeStudioOption> _variantOptions = new();
    private readonly List<ThemeStudioOption> _materialOptions = new();
    private readonly List<ThemeStudioOption> _elevationOptions = new();
    private readonly List<ThemeStudioOption> _motionOptions = new();
    private readonly List<ThemeStudioOption> _lineHeightOptions = new();
    private PaletteVariant _variant = PaletteVariant.Dark;
    private string _scaleLabel = "100%";
    private string _uiFont = string.Empty;
    private string _dataFont = string.Empty;
    private string _displayFont = string.Empty;
    private string _cornerNone = "0";
    private string _cornerSm = "2";
    private string _cornerMd = "3";
    private string _cornerError = string.Empty;
    private string _auditSummary = string.Empty;
    private bool _isRefreshing;

    internal ThemeStudioEditorViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.Editor)
    {
        AddVariant(PaletteVariant.Dark, "深色令牌");
        AddVariant(PaletteVariant.Light, "浅色令牌");

        AddMaterial(ThemeMaterial.Solid, "Solid", "实色面板（V1 默认）");
        AddMaterial(ThemeMaterial.None, "None", "面板透明；V1 不支持 Mica/Acrylic/模糊");

        AddElevation(ThemeElevation.None, "none", "无抬升：仅用明度差 + 1px 描边");
        AddElevation(ThemeElevation.Raised, "raised", "抬升面：仅 1px 描边 + 明度差，无阴影");

        AddMotion("fast", "快速（90 / 140ms）", new ThemeMotion(90, 140, 220));
        AddMotion("normal", "标准（140 / 200ms）", new ThemeMotion(140, 200, 260));
        AddMotion("slow", "慢速（240 / 320ms）", new ThemeMotion(240, 320, 440));

        AddLineHeight(LineHeightPreset.Tight, "紧凑（1.25）");
        AddLineHeight(LineHeightPreset.Normal, "标准（1.45）");
        AddLineHeight(LineHeightPreset.Loose, "宽松（1.6）");

        // Materialise the option collections only after every Add* call (see Preview VM note).
        VariantOptions = new ObservableCollection<ThemeStudioOption>(_variantOptions);
        MaterialOptions = new ObservableCollection<ThemeStudioOption>(_materialOptions);
        ElevationOptions = new ObservableCollection<ThemeStudioOption>(_elevationOptions);
        MotionOptions = new ObservableCollection<ThemeStudioOption>(_motionOptions);
        LineHeightOptions = new ObservableCollection<ThemeStudioOption>(_lineHeightOptions);

        ColorGroups =
        [
            new("bg", "背景（5 级 + 画布）"),
            new("line", "描边（4 级）"),
            new("text", "文本（5 级）"),
            new("accent", "强调（6 级）"),
            new("status", "状态（7 态）"),
            new("statusMuted", "状态底（7 态）"),
        ];

        SaveAsCommand = new RelayCommand(() => Owner.ShowSaveAsDialog());
        RevertDraftCommand = new RelayCommand(() => Run(RevertDraftAsync));
        ResetAuditCommand = new RelayCommand(Refresh);

        FontFamilies = new ObservableCollection<string>(LoadFontFamilies());
        Refresh();
    }

    public ObservableCollection<ThemeStudioOption> VariantOptions { get; }

    public ObservableCollection<ThemeStudioOption> MaterialOptions { get; }

    public ObservableCollection<ThemeStudioOption> ElevationOptions { get; }

    public ObservableCollection<ThemeStudioOption> MotionOptions { get; }

    public ObservableCollection<ThemeStudioOption> LineHeightOptions { get; }

    public IReadOnlyList<ThemeStudioColorGroup> ColorGroups { get; }

    /// <summary>System font families offered by the font pickers (never a bundled font, DESIGN_SYSTEM §3).</summary>
    public ObservableCollection<string> FontFamilies { get; }

    public ObservableCollection<ThemeStudioContrastRow> AuditRows { get; } = new();

    public ObservableCollection<ThemeStudioIssue> Issues { get; } = new();

    public ICommand SaveAsCommand { get; }

    public ICommand RevertDraftCommand { get; }

    public ICommand ResetAuditCommand { get; }

    public ObservableCollection<string> ScaleOptions { get; } =
        new(["80%", "90%", "100%", "110%", "120%", "130%"]);

    /// <summary>Variant whose token set is being edited.</summary>
    public PaletteVariant Variant
    {
        get => _variant;
        private set
        {
            if (Set(ref _variant, value))
            {
                OnPropertyChanged(nameof(VariantLabel));
                Refresh();
            }
        }
    }

    public string VariantLabel => Variant == PaletteVariant.Light ? "浅色令牌" : "深色令牌";

    public string ScaleLabel
    {
        get => _scaleLabel;
        set
        {
            if (!Set(ref _scaleLabel, value ?? "100%"))
            {
                return;
            }

            if (double.TryParse(value?.TrimEnd('%'), NumberStyles.Float, CultureInfo.InvariantCulture, out var percent))
            {
                ApplyTypography(scale: Math.Clamp(percent / 100.0, 0.8, 1.3));
            }
        }
    }

    public string UiFont
    {
        get => _uiFont;
        set
        {
            if (Set(ref _uiFont, value ?? string.Empty) && !_isRefreshing)
            {
                ApplyTypography(ui: value);
            }
        }
    }

    public string DataFont
    {
        get => _dataFont;
        set
        {
            if (Set(ref _dataFont, value ?? string.Empty) && !_isRefreshing)
            {
                ApplyTypography(data: value);
            }
        }
    }

    public string DisplayFont
    {
        get => _displayFont;
        set
        {
            if (Set(ref _displayFont, value ?? string.Empty) && !_isRefreshing)
            {
                ApplyTypography(display: value);
            }
        }
    }

    public string CornerNone
    {
        get => _cornerNone;
        set
        {
            if (Set(ref _cornerNone, value ?? string.Empty))
            {
                ApplyCorners();
            }
        }
    }

    public string CornerSm
    {
        get => _cornerSm;
        set
        {
            if (Set(ref _cornerSm, value ?? string.Empty))
            {
                ApplyCorners();
            }
        }
    }

    public string CornerMd
    {
        get => _cornerMd;
        set
        {
            if (Set(ref _cornerMd, value ?? string.Empty))
            {
                ApplyCorners();
            }
        }
    }

    /// <summary>Corner validation message (hard rule: 0–3px).</summary>
    public string CornerError
    {
        get => _cornerError;
        private set
        {
            if (Set(ref _cornerError, value))
            {
                OnPropertyChanged(nameof(HasCornerError));
            }
        }
    }

    public bool HasCornerError => !string.IsNullOrEmpty(CornerError);

    public string AuditSummary
    {
        get => _auditSummary;
        private set => Set(ref _auditSummary, value);
    }

    public bool HasIssues => Issues.Count > 0;

    /// <summary>True when a draft exists (editor has unsaved changes).</summary>
    public bool HasDraft => Owner.Service.HasDraft;

    public string DraftBadge => HasDraft ? "未保存草稿" : "与已应用主题一致";

    /// <summary>Group-level save-as hint (the applied draft is persisted as a user theme on 应用).</summary>
    public string SaveHint => "应用会把修改保存为自定义主题（内置主题不可覆盖）";

    /// <summary>Selects the variant to edit; defaults to the applied appearance.</summary>
    public void SelectVariant(PaletteVariant variant)
    {
        Variant = variant;
        foreach (var option in _variantOptions)
        {
            option.IsSelected = string.Equals(option.Key, variant.ToString(), StringComparison.Ordinal);
        }
    }

    public void SelectMaterial(ThemeMaterial material)
    {
        foreach (var option in _materialOptions)
        {
            option.IsSelected = string.Equals(option.Key, material.ToString(), StringComparison.Ordinal);
        }

        MutateEachTokens(tokens => tokens with { Material = material });
    }

    public void SelectElevation(ThemeElevation elevation)
    {
        foreach (var option in _elevationOptions)
        {
            option.IsSelected = string.Equals(option.Key, elevation.ToString(), StringComparison.Ordinal);
        }

        MutateEachTokens(tokens => tokens with { Elevation = elevation });
    }

    public void SelectMotionPreset(string key)
    {
        var motion = key switch
        {
            "fast" => new ThemeMotion(90, 140, 220),
            "slow" => new ThemeMotion(240, 320, 440),
            _ => new ThemeMotion(140, 200, 260),
        };

        foreach (var option in _motionOptions)
        {
            option.IsSelected = string.Equals(option.Key, key, StringComparison.Ordinal);
        }

        MutateEachTokens(tokens => tokens with { Motion = motion });
    }

    public void SelectLineHeight(LineHeightPreset preset)
    {
        foreach (var option in _lineHeightOptions)
        {
            option.IsSelected = string.Equals(option.Key, preset.ToString(), StringComparison.Ordinal);
        }

        MutateEachTokens(tokens => tokens with
        {
            Typography = tokens.Typography with { LineHeight = preset },
        });
    }

    /// <summary>Called by a colour row after a valid hex edit.</summary>
    public void ApplyColor(string tokenKey, string hexValue)
    {
        if (_isRefreshing)
        {
            return;
        }

        Mutate(package =>
        {
            var tokens = Variant == PaletteVariant.Light ? package.Light : package.Dark;
            var colors = new Dictionary<string, string>(tokens.Colors, StringComparer.Ordinal)
            {
                [tokenKey] = hexValue,
            };
            var updated = tokens with { Colors = colors };
            return Variant == PaletteVariant.Light
                ? package with { Light = updated }
                : package with { Dark = updated };
        });

        RefreshAudit();
    }

    /// <inheritdoc />
    public override void OnActivated()
    {
        var resolved = ResolveAppliedVariant();
        SelectVariant(resolved);
    }

    /// <summary>Rebuilds every editor row from the current draft (or the applied package).</summary>
    public void Refresh()
    {
        if (_isRefreshing)
        {
            return;
        }

        _isRefreshing = true;
        try
        {
            var package = Owner.Service.DraftPackage ?? Owner.Service.AppliedPackage;
            var tokens = Variant == PaletteVariant.Light ? package.Light : package.Dark;

            foreach (var group in ColorGroups)
            {
                group.Rows.Clear();
                foreach (var key in KeysOf(group.Key))
                {
                    if (!tokens.Colors.TryGetValue(key, out var value))
                    {
                        continue;
                    }

                    var row = new ThemeStudioColorRow(this, key, ThemeStudioColorLabels.For(key), value);
                    group.Rows.Add(row);
                }
            }

            _uiFont = ResolveFontChoice(tokens.Typography.Ui);
            _dataFont = ResolveFontChoice(tokens.Typography.Data);
            _displayFont = ResolveFontChoice(tokens.Typography.Display);
            _scaleLabel = $"{tokens.Typography.Scale * 100:0}%";
            _cornerNone = tokens.Corners.None.ToString("0.##", CultureInfo.InvariantCulture);
            _cornerSm = tokens.Corners.Sm.ToString("0.##", CultureInfo.InvariantCulture);
            _cornerMd = tokens.Corners.Md.ToString("0.##", CultureInfo.InvariantCulture);

            foreach (var option in _materialOptions)
            {
                option.IsSelected = string.Equals(option.Key, tokens.Material.ToString(), StringComparison.Ordinal);
            }

            foreach (var option in _elevationOptions)
            {
                option.IsSelected = string.Equals(option.Key, tokens.Elevation.ToString(), StringComparison.Ordinal);
            }

            foreach (var option in _motionOptions)
            {
                option.IsSelected = MatchesMotion(option.Key, tokens.Motion);
            }

            foreach (var option in _lineHeightOptions)
            {
                option.IsSelected = string.Equals(option.Key, tokens.Typography.LineHeight.ToString(), StringComparison.Ordinal);
            }

            OnPropertyChanged(
                nameof(UiFont),
                nameof(DataFont),
                nameof(DisplayFont),
                nameof(ScaleLabel),
                nameof(CornerNone),
                nameof(CornerSm),
                nameof(CornerMd),
                nameof(HasDraft),
                nameof(DraftBadge));

            RefreshAudit();
        }
        finally
        {
            _isRefreshing = false;
        }
    }

    private bool MatchesMotion(string key, ThemeMotion motion) => key switch
    {
        "fast" => motion.FastMs == 90,
        "slow" => motion.FastMs == 240,
        _ => motion.FastMs == 140,
    };

    /// <summary>Audits the draft (current variant) and refreshes the inline ratio column.</summary>
    public void RefreshAudit()
    {
        var package = Owner.Service.DraftPackage ?? Owner.Service.AppliedPackage;
        var report = Owner.Service.Audit(package, Variant);
        AuditRows.Clear();
        foreach (var row in report.Rows)
        {
            AuditRows.Add(row);
        }

        AuditSummary = report.Summary;

        var tokens = Variant == PaletteVariant.Light ? package.Light : package.Dark;
        foreach (var group in ColorGroups)
        {
            foreach (var row in group.Rows)
            {
                row.ContrastLabel = ContrastOf(tokens, row.TokenKey);
            }
        }

        RecomputeIssues(package);
        OnPropertyChanged(nameof(HasDraft), nameof(DraftBadge), nameof(HasIssues));
    }

    private void RecomputeIssues(ThemePackage package)
    {
        Issues.Clear();
        foreach (var issue in Owner.Service.ValidatePackage(package).Issues)
        {
            Issues.Add(issue);
        }

        OnPropertyChanged(nameof(HasIssues));
    }

    private static string ContrastOf(ThemeTokenSet tokens, string tokenKey)
    {
        if (!tokenKey.StartsWith("Nm.Color.Text.", StringComparison.Ordinal) &&
            !tokenKey.StartsWith("Nm.Color.Status.", StringComparison.Ordinal) &&
            tokenKey != NmKeys.Color.Accent.Base)
        {
            return "—";
        }

        if (!tokens.Colors.TryGetValue(tokenKey, out var foreground) ||
            !tokens.Colors.TryGetValue(NmKeys.Color.Bg.Panel, out var background))
        {
            return "—";
        }

        try
        {
            return $"{ThemeContrast.Ratio(foreground, background):0.00}:1";
        }
        catch (FormatException)
        {
            return "—";
        }
    }

    private void ApplyTypography(double? scale = null, string? ui = null, string? data = null, string? display = null)
    {
        if (_isRefreshing)
        {
            return;
        }

        Mutate(package =>
        {
            var tokens = Variant == PaletteVariant.Light ? package.Light : package.Dark;
            var typography = tokens.Typography with
            {
                Scale = scale ?? tokens.Typography.Scale,
                Ui = string.IsNullOrWhiteSpace(ui) ? tokens.Typography.Ui : ui,
                Data = string.IsNullOrWhiteSpace(data) ? tokens.Typography.Data : data,
                Display = string.IsNullOrWhiteSpace(display) ? tokens.Typography.Display : display,
            };
            var updated = tokens with { Typography = typography };
            return Variant == PaletteVariant.Light
                ? package with { Light = updated }
                : package with { Dark = updated };
        });

        RefreshAudit();
    }

    private void ApplyCorners()
    {
        if (_isRefreshing)
        {
            return;
        }

        if (!TryParseCorner(_cornerNone, out var none) ||
            !TryParseCorner(_cornerSm, out var sm) ||
            !TryParseCorner(_cornerMd, out var md))
        {
            CornerError = "圆角只能是 0–3 之间的数字（DESIGN_SYSTEM §1 规则 4）";
            return;
        }

        CornerError = string.Empty;
        Mutate(package =>
        {
            var tokens = Variant == PaletteVariant.Light ? package.Light : package.Dark;
            var updated = tokens with { Corners = new ThemeCorners(none, sm, md) };
            return Variant == PaletteVariant.Light
                ? package with { Light = updated }
                : package with { Dark = updated };
        });

        RefreshAudit();
    }

    private static bool TryParseCorner(string raw, out double value)
    {
        if (!double.TryParse(raw?.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out value))
        {
            return false;
        }

        return value is >= 0 and <= ThemeCorners.MaxRadius;
    }

    private void MutateEachTokens(Func<ThemeTokenSet, ThemeTokenSet> mutate)
    {
        if (_isRefreshing)
        {
            return;
        }

        Mutate(package => package with
        {
            Light = mutate(package.Light),
            Dark = mutate(package.Dark),
        });
        RefreshAudit();
    }

    private void Mutate(Func<ThemePackage, ThemePackage> mutate)
    {
        var current = Owner.Service.DraftPackage ?? Owner.Service.AppliedPackage;
        var next = mutate(current);
        Owner.ApplyDraftPackage(next);
    }

    private async Task RevertDraftAsync()
    {
        await Owner.Service.CancelPreviewAsync().ConfigureAwait(true);
        Owner.NotifyDraftChanged();
        Refresh();
        Owner.ReportStatus("已放弃草稿，恢复到已应用主题。");
    }

    private PaletteVariant ResolveAppliedVariant() =>
        Owner.Service.Settings.Appearance == AppearanceMode.Light ? PaletteVariant.Light : PaletteVariant.Dark;

    private static IEnumerable<string> KeysOf(string groupKey) => groupKey switch
    {
        "bg" => new[]
        {
            NmKeys.Color.Bg.App, NmKeys.Color.Bg.Canvas, NmKeys.Color.Bg.Panel,
            NmKeys.Color.Bg.Raised, NmKeys.Color.Bg.Overlay, NmKeys.Color.Bg.Sunken,
        },
        "line" => new[]
        {
            NmKeys.Color.Line.Subtle, NmKeys.Color.Line.Default, NmKeys.Color.Line.Strong, NmKeys.Color.Line.Grid,
        },
        "text" => new[]
        {
            NmKeys.Color.Text.Primary, NmKeys.Color.Text.Secondary, NmKeys.Color.Text.Tertiary,
            NmKeys.Color.Text.Disabled, NmKeys.Color.Text.Inverse,
        },
        "accent" => new[]
        {
            NmKeys.Color.Accent.Base, NmKeys.Color.Accent.Hover, NmKeys.Color.Accent.Active,
            NmKeys.Color.Accent.Muted, NmKeys.Color.Accent.On, NmKeys.Color.Accent.Ring,
        },
        "status" => new[]
        {
            NmKeys.Color.Status.Queued, NmKeys.Color.Status.Running, NmKeys.Color.Status.Done,
            NmKeys.Color.Status.Failed, NmKeys.Color.Status.Blocked, NmKeys.Color.Status.Stale,
            NmKeys.Color.Status.Skipped,
        },
        _ => new[]
        {
            NmKeys.Color.StatusMuted.Queued, NmKeys.Color.StatusMuted.Running, NmKeys.Color.StatusMuted.Done,
            NmKeys.Color.StatusMuted.Failed, NmKeys.Color.StatusMuted.Blocked, NmKeys.Color.StatusMuted.Stale,
            NmKeys.Color.StatusMuted.Skipped,
        },
    };

    private void AddVariant(PaletteVariant variant, string label)
    {
        var option = new ThemeStudioOption(
            variant.ToString(),
            label,
            null,
            new RelayCommand(() => SelectVariant(variant)));
        option.IsSelected = variant == _variant;
        _variantOptions.Add(option);
    }

    private void AddMaterial(ThemeMaterial material, string label, string description)
    {
        _materialOptions.Add(new ThemeStudioOption(
            material.ToString(),
            label,
            description,
            new RelayCommand(() => SelectMaterial(material))));
    }

    private void AddElevation(ThemeElevation elevation, string label, string description)
    {
        _elevationOptions.Add(new ThemeStudioOption(
            elevation.ToString(),
            label,
            description,
            new RelayCommand(() => SelectElevation(elevation))));
    }

    private void AddMotion(string key, string label, ThemeMotion motion)
    {
        _motionOptions.Add(new ThemeStudioOption(
            key,
            label,
            $"{motion.FastMs} / {motion.NormalMs} ms",
            new RelayCommand(() => SelectMotionPreset(key))));
    }

    private void AddLineHeight(LineHeightPreset preset, string label)
    {
        _lineHeightOptions.Add(new ThemeStudioOption(
            preset.ToString(),
            label,
            null,
            new RelayCommand(() => SelectLineHeight(preset))));
    }

    /// <summary>
    /// Projects a theme font stack ("family-first, fallback, …") onto the family the picker can show and
    /// adds it to the picker list when the theme came from somewhere else.
    /// </summary>
    private string ResolveFontChoice(string stack)
    {
        if (string.IsNullOrWhiteSpace(stack))
        {
            return string.Empty;
        }

        var first = stack.Split(',', 2, StringSplitOptions.TrimEntries)[0].Trim('"', '\'', ' ');
        if (first.Length == 0)
        {
            return string.Empty;
        }

        if (!FontFamilies.Contains(first, StringComparer.OrdinalIgnoreCase))
        {
            FontFamilies.Insert(0, first);
        }

        return first;
    }

    private static IReadOnlyList<string> LoadFontFamilies()
    {
        var families = new SortedSet<string>(StringComparer.OrdinalIgnoreCase);
        try
        {
            foreach (var family in FontManager.Current.SystemFonts)
            {
                var name = family.Name;
                if (!string.IsNullOrWhiteSpace(name))
                {
                    families.Add(name);
                }
            }
        }
        catch (Exception exception) when (exception is InvalidOperationException or NotSupportedException or ArgumentException)
        {
            // Font enumeration is best-effort; the shipped fallback stack is always offered below.
        }

        foreach (var fallback in new[] { "Segoe UI Variable Text", "Microsoft YaHei UI", "Noto Sans SC", "Cascadia Mono", "Georgia" })
        {
            families.Add(fallback);
        }

        return families.Take(64).ToArray();
    }
}

/// <summary>Human labels of the 35 semantic colour keys (single copy table).</summary>
public static class ThemeStudioColorLabels
{
    private static readonly Dictionary<string, string> Labels = new(StringComparer.Ordinal)
    {
        [NmKeys.Color.Bg.App] = "应用底",
        [NmKeys.Color.Bg.Canvas] = "画布",
        [NmKeys.Color.Bg.Panel] = "面板",
        [NmKeys.Color.Bg.Raised] = "抬升面",
        [NmKeys.Color.Bg.Overlay] = "浮层",
        [NmKeys.Color.Bg.Sunken] = "下沉面",
        [NmKeys.Color.Line.Subtle] = "描边 / 极弱",
        [NmKeys.Color.Line.Default] = "描边 / 默认",
        [NmKeys.Color.Line.Strong] = "描边 / 强",
        [NmKeys.Color.Line.Grid] = "描边 / 网格",
        [NmKeys.Color.Text.Primary] = "文本 / 主",
        [NmKeys.Color.Text.Secondary] = "文本 / 次",
        [NmKeys.Color.Text.Tertiary] = "文本 / 三级",
        [NmKeys.Color.Text.Disabled] = "文本 / 禁用",
        [NmKeys.Color.Text.Inverse] = "文本 / 反色",
        [NmKeys.Color.Accent.Base] = "强调 / 基色",
        [NmKeys.Color.Accent.Hover] = "强调 / 悬停",
        [NmKeys.Color.Accent.Active] = "强调 / 激活",
        [NmKeys.Color.Accent.Muted] = "强调 / 弱底",
        [NmKeys.Color.Accent.On] = "强调 / 前景",
        [NmKeys.Color.Accent.Ring] = "强调 / 焦点环",
        [NmKeys.Color.Status.Queued] = "状态 · 排队",
        [NmKeys.Color.Status.Running] = "状态 ◐ 进行",
        [NmKeys.Color.Status.Done] = "状态 ● 完成",
        [NmKeys.Color.Status.Failed] = "状态 ✗ 失败",
        [NmKeys.Color.Status.Blocked] = "状态 ▲ 阻塞",
        [NmKeys.Color.Status.Stale] = "状态 ▨ 过期",
        [NmKeys.Color.Status.Skipped] = "状态 – 跳过",
        [NmKeys.Color.StatusMuted.Queued] = "状态底 · 排队",
        [NmKeys.Color.StatusMuted.Running] = "状态底 ◐ 进行",
        [NmKeys.Color.StatusMuted.Done] = "状态底 ● 完成",
        [NmKeys.Color.StatusMuted.Failed] = "状态底 ✗ 失败",
        [NmKeys.Color.StatusMuted.Blocked] = "状态底 ▲ 阻塞",
        [NmKeys.Color.StatusMuted.Stale] = "状态底 ▨ 过期",
        [NmKeys.Color.StatusMuted.Skipped] = "状态底 – 跳过",
    };

    /// <summary>Label of a token key, falling back to the key itself.</summary>
    public static string For(string tokenKey) =>
        Labels.TryGetValue(tokenKey, out var label) ? label : tokenKey;
}
