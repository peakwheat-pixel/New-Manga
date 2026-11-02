using NewManga.App.Services;
using NewManga.Appearance;

namespace NewManga.App.ViewModels.Fluent;

/// <summary>
/// FEA-06-RESIDUAL-1 I-5: the frozen motion parameters from `doc/design/fluent-v1/02-motion.md` §2,
/// expressed as one table so every consumer resolves the same numbers. `auto` never reaches this type:
/// <see cref="MotionResolver"/> resolves it against the platform preference first. A disabled category
/// resolves to 0ms (design `motion.categories[x]=关`), and `reduce` keeps feedback's colour change while
/// zeroing its motion (design §2.2/§3 判据③).
/// </summary>
public static class MotionTimings
{
    /// <summary>一级页面切换（书架↔工作台↔阅读器↔设置）: 240ms ease-out (0.2,0,0,1).</summary>
    public const double NavigationPageMilliseconds = 240d;

    /// <summary>Tab 切换（工作台 页面/批量/控制台）: 180ms ease-out (0.2,0,0,1).</summary>
    public const double NavigationTabMilliseconds = 180d;

    /// <summary>浮层进入: 200ms ease-out (0.2,0,0,1)。</summary>
    public const double NavigationOverlayInMilliseconds = 200d;

    /// <summary>浮层退出: 160ms ease-in (0.4,0,1,1)。</summary>
    public const double NavigationOverlayOutMilliseconds = 160d;

    /// <summary>按钮 hover 背景: 120ms ease (0.4,0,0.2,1)；reduce 下保留颜色变化、无位移/无缩放。</summary>
    public const double FeedbackHoverMilliseconds = 120d;

    /// <summary>按钮 pressed 形变: 缩放 0.98，90ms。</summary>
    public const double FeedbackPressedMilliseconds = 90d;

    /// <summary>状态点/徽标出现: 淡入 150ms + 缩放 0.9→1。</summary>
    public const double FeedbackBadgeMilliseconds = 150d;

    /// <summary>书架背景渐变缓动: 8s 循环（02-motion §2.3 decorative）。</summary>
    public const double DecorativeShelfGradientMilliseconds = 8000d;

    /// <summary>阅读器翻页装饰粒子: 400ms，翻页触发一次（02-motion §2.3 decorative）。</summary>
    public const double DecorativePageTurnMilliseconds = 400d;

    /// <summary>
    /// Resolves the effective timing profile for a resolved motion setting. `navigation`/`decorative`
    /// disabled by category or by reduce become 0ms; feedback keeps its colour transition at 0ms under
    /// reduce (design §2.2 and 判据③), so its duration is reported as 0 while <see cref="MotionTimingProfile.FeedbackColourOnly"/>
    /// stays true.
    /// </summary>
    public static MotionTimingProfile Resolve(MotionSettings settings)
    {
        ArgumentNullException.ThrowIfNull(settings);

        var navigation = settings.IsEnabled(MotionCategories.Navigation);
        var feedback = settings.Feedback;
        var decorative = settings.IsEnabled(MotionCategories.Decorative);
        var reduce = settings.EffectiveMode == MotionMode.Reduce;

        return new MotionTimingProfile(
            NavigationPageMilliseconds: navigation ? NavigationPageMilliseconds : 0d,
            NavigationTabMilliseconds: navigation ? NavigationTabMilliseconds : 0d,
            NavigationOverlayInMilliseconds: navigation ? NavigationOverlayInMilliseconds : 0d,
            NavigationOverlayOutMilliseconds: navigation ? NavigationOverlayOutMilliseconds : 0d,
            FeedbackHoverMilliseconds: feedback && !reduce ? FeedbackHoverMilliseconds : 0d,
            FeedbackPressedMilliseconds: feedback && !reduce ? FeedbackPressedMilliseconds : 0d,
            FeedbackBadgeMilliseconds: feedback && !reduce ? FeedbackBadgeMilliseconds : 0d,
            FeedbackColourOnly: feedback && reduce,
            DecorativeShelfGradientMilliseconds: decorative ? DecorativeShelfGradientMilliseconds : 0d,
            DecorativePageTurnMilliseconds: decorative ? DecorativePageTurnMilliseconds : 0d,
            DecorativeEnabled: decorative,
            Reduced: reduce);
    }
}

/// <summary>Resolved timing profile (0ms = no animation). See <see cref="MotionTimings"/>.</summary>
public sealed record MotionTimingProfile(
    double NavigationPageMilliseconds,
    double NavigationTabMilliseconds,
    double NavigationOverlayInMilliseconds,
    double NavigationOverlayOutMilliseconds,
    double FeedbackHoverMilliseconds,
    double FeedbackPressedMilliseconds,
    double FeedbackBadgeMilliseconds,
    bool FeedbackColourOnly,
    double DecorativeShelfGradientMilliseconds,
    double DecorativePageTurnMilliseconds,
    bool DecorativeEnabled,
    bool Reduced)
{
    /// <summary>True when a finite navigation/feedback transition may run. Decorative loops are reported by DecorativeEnabled.</summary>
    public bool HasMotion =>
        NavigationPageMilliseconds > 0 ||
        NavigationTabMilliseconds > 0 ||
        NavigationOverlayInMilliseconds > 0 ||
        NavigationOverlayOutMilliseconds > 0 ||
        FeedbackHoverMilliseconds > 0 ||
        FeedbackPressedMilliseconds > 0 ||
        FeedbackBadgeMilliseconds > 0;
}
