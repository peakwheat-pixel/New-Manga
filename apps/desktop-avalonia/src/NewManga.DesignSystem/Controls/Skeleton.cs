using Avalonia;
using Avalonia.Controls;

namespace NewManga.DesignSystem.Controls;

/// <summary>The three skeleton shapes required by DESIGN_SYSTEM §7: book card, list row and panel block.</summary>
public enum SkeletonVariant
{
    BookCard,
    Row,
    Panel,
}

/// <summary>
/// Loading placeholder (DESIGN_SYSTEM §7): a neutral raised-surface block in one of the three canonical
/// shapes. Skeleton blocks are static by design — no pulse/shimmer animation — so reduced-motion users
/// and animation-free screenshots see the same stable placeholder. The size comes from tokens; callers
/// may still set Width for the horizontal footprint.
/// </summary>
public sealed class Skeleton : Border
{
    /// <summary>Which placeholder shape to render.</summary>
    public static readonly StyledProperty<SkeletonVariant> VariantProperty =
        AvaloniaProperty.Register<Skeleton, SkeletonVariant>(nameof(Variant));

    public Skeleton()
    {
        Classes.Add("skeleton");
        ApplyVariant();
    }

    /// <summary>Gets or sets the placeholder shape.</summary>
    public SkeletonVariant Variant
    {
        get => GetValue(VariantProperty);
        set => SetValue(VariantProperty, value);
    }

    protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
    {
        base.OnPropertyChanged(change);
        if (change.Property == VariantProperty)
        {
            ApplyVariant();
        }
    }

    private void ApplyVariant()
    {
        Classes.Remove("book-card");
        Classes.Remove("row");
        Classes.Remove("panel");
        Classes.Add(Variant switch
        {
            SkeletonVariant.BookCard => "book-card",
            SkeletonVariant.Row => "row",
            _ => "panel",
        });
    }
}
