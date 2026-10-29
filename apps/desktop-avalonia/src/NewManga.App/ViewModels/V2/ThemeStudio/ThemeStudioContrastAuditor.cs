using NewManga.DesignSystem;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// Live WCAG 2.1 audit of one theme variant (THEME_STUDIO_SPEC §5: "编辑器实时计算并显示数值").
///
/// <para>
/// The ratios come from the Theme Engine's own <see cref="ThemeContrast.Ratio(string, string)"/> — the
/// same implementation the import validator uses — so the number the editor shows and the number that
/// blocks an import can never diverge. Floors are the frozen R-09 table (DESIGN_SYSTEM §2.3 + the
/// Lead ruling recorded in the Theme Engine README §5).
/// </para>
/// </summary>
public static class ThemeStudioContrastAuditor
{
    /// <summary>Body text floor (DESIGN_SYSTEM §2.3: 正文 ≥ 7:1).</summary>
    public const double BodyFloor = 7.0;

    /// <summary>Secondary text and status floor (DESIGN_SYSTEM §2.3: ≥ 4.5:1).</summary>
    public const double SecondaryFloor = 4.5;

    /// <summary>Focus-ring / non-text UI floor (DESIGN_SYSTEM §2.3: 焦点环 ≥ 3:1).</summary>
    public const double NonTextFloor = 3.0;

    /// <summary>Audits the given variant of a package.</summary>
    public static ThemeStudioContrastReport Evaluate(ThemePackage package, PaletteVariant variant)
    {
        ArgumentNullException.ThrowIfNull(package);
        var tokens = variant == PaletteVariant.Light ? package.Light : package.Dark;
        return Evaluate(tokens, variant);
    }

    /// <summary>Audits one token set.</summary>
    public static ThemeStudioContrastReport Evaluate(ThemeTokenSet tokens, PaletteVariant variant)
    {
        ArgumentNullException.ThrowIfNull(tokens);

        var rows = new List<ThemeStudioContrastRow>(16);

        Add(rows, tokens, "正文 / 面板", NmKeys.Color.Text.Primary, NmKeys.Color.Bg.Panel, BodyFloor);
        Add(rows, tokens, "正文 / 画布", NmKeys.Color.Text.Primary, NmKeys.Color.Bg.Canvas, BodyFloor);
        Add(rows, tokens, "次要 / 面板", NmKeys.Color.Text.Secondary, NmKeys.Color.Bg.Panel, SecondaryFloor);
        Add(rows, tokens, "次要 / 画布", NmKeys.Color.Text.Secondary, NmKeys.Color.Bg.Canvas, SecondaryFloor);

        foreach (var key in StatusKeys)
        {
            Add(rows, tokens, $"状态 {StatusLabel(key)} / 面板", key, NmKeys.Color.Bg.Panel, SecondaryFloor);
        }

        Add(rows, tokens, "主按钮文字 / 强调", NmKeys.Color.Accent.On, NmKeys.Color.Accent.Base, SecondaryFloor);
        Add(rows, tokens, "焦点环 / 面板", NmKeys.Color.Accent.Base, NmKeys.Color.Bg.Panel, NonTextFloor);

        return new ThemeStudioContrastReport(variant, rows);
    }

    /// <summary>True when the package passes every floor on both variants (used by the catalog filter).</summary>
    public static bool IsHighContrastFriendly(ThemePackage package)
    {
        ArgumentNullException.ThrowIfNull(package);
        return Evaluate(package, PaletteVariant.Light).IsPassing &&
               Evaluate(package, PaletteVariant.Dark).IsPassing;
    }

    private static void Add(
        ICollection<ThemeStudioContrastRow> rows,
        ThemeTokenSet tokens,
        string label,
        string foregroundKey,
        string backgroundKey,
        double floor)
    {
        rows.Add(new ThemeStudioContrastRow(label, foregroundKey, backgroundKey, Ratio(tokens, foregroundKey, backgroundKey), floor, IsRequired: true));
    }

    private static double Ratio(ThemeTokenSet tokens, string foregroundKey, string backgroundKey)
    {
        if (!tokens.Colors.TryGetValue(foregroundKey, out var foreground) ||
            !tokens.Colors.TryGetValue(backgroundKey, out var background))
        {
            return 1.0;
        }

        try
        {
            return ThemeContrast.Ratio(foreground, background);
        }
        catch (FormatException)
        {
            return 1.0;
        }
    }

    private static string StatusLabel(string key) => key switch
    {
        NmKeys.Color.Status.Queued => "排队 ·",
        NmKeys.Color.Status.Running => "进行 ◐",
        NmKeys.Color.Status.Done => "完成 ●",
        NmKeys.Color.Status.Failed => "失败 ✗",
        NmKeys.Color.Status.Blocked => "阻塞 ▲",
        NmKeys.Color.Status.Stale => "过期 ▨",
        _ => "跳过 –",
    };

    private static readonly string[] StatusKeys =
    [
        NmKeys.Color.Status.Queued,
        NmKeys.Color.Status.Running,
        NmKeys.Color.Status.Done,
        NmKeys.Color.Status.Failed,
        NmKeys.Color.Status.Blocked,
        NmKeys.Color.Status.Stale,
        NmKeys.Color.Status.Skipped,
    ];
}
