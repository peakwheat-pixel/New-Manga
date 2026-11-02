using NewManga.CoreClient;

namespace NewManga.App.ViewModels.V2.Studio;

/// <summary>
/// V11R-B-3: one region as the canvas overlay and the inspector need it. Geometry is kept in both
/// spaces (normalised from the Core read face + page pixels for the current page extent) so the
/// overlay never recomputes coordinates from a stale page size.
/// </summary>
public sealed class StudioRegionItem : StudioObservable
{
    private bool _isSelected;
    private bool _isHovered;
    private bool _isLocked;
    private bool _hasFailed;

    public StudioRegionItem(RegionSummary region, RegionPageSize? pageSize)
    {
        Region = region;
        PageSize = pageSize;
        Normalized = region.Geometry is { } geometry
            ? new StudioRect(geometry.X, geometry.Y, geometry.Width, geometry.Height)
            : StudioRect.Empty;
        PixelRect = StudioCoordinates.NormalizedToPixels(region.Geometry, pageSize);
    }

    public RegionSummary Region { get; private set; }

    public RegionPageSize? PageSize { get; private set; }

    /// <summary>Order of the region inside the page (1-based, list position).</summary>
    public int Order { get; private set; }

    public string RegionId => Region.RegionId;

    public string RegionType => Region.RegionType;

    public string SfxPolicy => Region.SfxPolicy;

    public string Origin => Region.Origin;

    public int RevisionNo => Region.RevisionNo;

    /// <summary>Normalised (0..1) geometry as read from the Core; empty when unavailable.</summary>
    public StudioRect Normalized { get; private set; }

    /// <summary>Page-pixel rectangle for the current page extent.</summary>
    public StudioRect PixelRect { get; private set; }

    public bool HasGeometry => !PixelRect.IsEmpty;

    public string DisplayLabel => $"区 {Order:00} · {RegionType} · rev {RevisionNo}";

    public string ShortLabel => $"区 {Order:00}";

    public string OriginLabel => string.Equals(Origin, "user", StringComparison.OrdinalIgnoreCase) ? "人工" : "机器";

    public bool IsSelected
    {
        get => _isSelected;
        set => Set(ref _isSelected, value);
    }

    public bool IsHovered
    {
        get => _isHovered;
        set => Set(ref _isHovered, value);
    }

    /// <summary>▮ badge. Only settable from a real lock source (NOT_WIRED in this build).</summary>
    public bool IsLocked
    {
        get => _isLocked;
        set => Set(ref _isLocked, value);
    }

    /// <summary>✗ badge. Only settable from a real error source (NOT_WIRED in this build).</summary>
    public bool HasFailed
    {
        get => _hasFailed;
        set => Set(ref _hasFailed, value);
    }

    /// <summary>Review state of the current revision once the history read succeeded.</summary>
    public StudioStateKind? ReviewState { get; private set; }

    /// <summary>Updates the region read row (after a write refresh). Keeps order/flags/selection.</summary>
    public void Update(RegionSummary region, RegionPageSize? pageSize, IReadOnlyList<RegionRevisionSummary>? revisions = null)
    {
        Region = region;
        PageSize = pageSize;
        Normalized = region.Geometry is { } geometry
            ? new StudioRect(geometry.X, geometry.Y, geometry.Width, geometry.Height)
            : StudioRect.Empty;
        PixelRect = StudioCoordinates.NormalizedToPixels(region.Geometry, pageSize);
        if (revisions is not null)
        {
            var current = revisions.FirstOrDefault(item => item.IsCurrent);
            ReviewState = StudioStates.FromReviewState(current?.ReviewState);
        }

        Raise(string.Empty);
    }

    public void SetOrder(int order)
    {
        if (Order == order)
        {
            return;
        }

        Order = order;
        Raise(nameof(Order));
        Raise(nameof(DisplayLabel));
        Raise(nameof(ShortLabel));
    }

    public void SetReviewState(StudioStateKind? state)
    {
        if (ReviewState == state)
        {
            return;
        }

        ReviewState = state;
        Raise(nameof(ReviewState));
    }

    public override string ToString() => DisplayLabel;
}
