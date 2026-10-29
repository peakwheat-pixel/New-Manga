using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace NewManga.App.ViewModels;

/// <summary>
/// One workbench region. READER-WORKBENCH-1 wires this to the real Core <c>list_regions</c> row
/// (region_id / type / origin / revision_no) plus the normalized geometry projected to page pixels;
/// the in-memory constructor keeps the S4 skeleton's model test working without a Host.
/// </summary>
public sealed class RegionItem : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    /// <summary>Core region id (or a local skeleton id when no Host is attached).</summary>
    public string Id { get; init; } = Guid.NewGuid().ToString("N")[..8];

    /// <summary>Page-pixel rectangle of the region on the current page image.</summary>
    public double X { get; set; }

    public double Y { get; set; }

    public double Width { get; set; }

    public double Height { get; set; }

    /// <summary>Core <c>region_type</c> (speech / narration / sfx / …) or the skeleton default.</summary>
    public string Kind { get; set; } = "text";

    /// <summary>Core <c>origin</c> (user / machine) — null on the skeleton path.</summary>
    public string Origin { get; set; } = string.Empty;

    /// <summary>Core current <c>revision_no</c> (0 = unknown/skeleton).</summary>
    public int RevisionNo { get; set; }

    /// <summary>Core <c>sfx_policy</c> (skip / render / …) — null on the skeleton path.</summary>
    public string SfxPolicy { get; set; } = string.Empty;

    /// <summary>Region text (not part of the read face; kept for the skeleton model/tests).</summary>
    public string Text { get; set; } = string.Empty;

    /// <summary>Display label for the region list ("type · origin · rev N").</summary>
    public string Label => RevisionNo > 0
        ? $"{Kind} · {Origin} · rev {RevisionNo}"
        : Kind;

    public void Raise() => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(string.Empty));

    public override string ToString() => Label;
}

public sealed class BubbleItem : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;
    public string Id { get; init; } = Guid.NewGuid().ToString("N")[..8];
    public string Text { get; set; } = string.Empty;
    public string Orientation { get; set; } = "horizontal";
    public double X { get; set; }
    public double Y { get; set; }
    public void Raise() => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(string.Empty));
}

/// <summary>AC1 workbench model: 300/mid/230 columns, 50-200% zoom, tile canvas, regions + bubbles.</summary>
public sealed class WorkbenchViewModel : INotifyPropertyChanged
{
    public const double LeftWidth = 300;
    public const double RightWidth = 230;
    public const double MinZoomPercent = 50;
    public const double MaxZoomPercent = 200;
    public const double ZoomStep = 10;

    private double _zoomPercent = 100;
    private RegionItem? _selectedRegion;
    private BubbleItem? _selectedBubble;

    public event PropertyChangedEventHandler? PropertyChanged;

    public ObservableCollection<RegionItem> Regions { get; } = new();

    public ObservableCollection<BubbleItem> Bubbles { get; } = new();

    public ObservableCollection<string> Thumbnails { get; } = new();

    public bool TileRenderingEnabled { get; set; } = true;

    public bool UsesNoInterpolation => true;

    public double ZoomPercent
    {
        get => _zoomPercent;
        set
        {
            var clamped = Math.Clamp(Math.Round(value / ZoomStep) * ZoomStep, MinZoomPercent, MaxZoomPercent);
            if (Math.Abs(clamped - _zoomPercent) < 0.001)
            {
                return;
            }

            _zoomPercent = clamped;
            Raise(nameof(ZoomPercent));
            Raise(nameof(ZoomLabel));
        }
    }

    public string ZoomLabel => $"{ZoomPercent:0}%";

    /// <summary>Display scale applied to the page image and the region overlay (zoom 50–200%).</summary>
    public double DisplayScale => ZoomPercent / 100.0;

    public RegionItem? SelectedRegion
    {
        get => _selectedRegion;
        set
        {
            if (ReferenceEquals(_selectedRegion, value))
            {
                return;
            }

            _selectedRegion = value;
            Raise(nameof(SelectedRegion));
            Raise(nameof(SelectedRegionLabel));
            Raise(nameof(SelectedRegionText));
            Raise(nameof(SelectedRegionDetail));
        }
    }

    /// <summary>READER-WORKBENCH-1: list-box friendly label of the selected region.</summary>
    public string SelectedRegionLabel => SelectedRegion?.Label ?? string.Empty;

    /// <summary>READER-WORKBENCH-1: "region_id · origin · revision" detail line of the selection.</summary>
    public string SelectedRegionDetail => SelectedRegion is { } region
        ? $"id {ShortId(region.Id)} · {region.Kind} · {region.Origin} · sfx {region.SfxPolicy} · revision {region.RevisionNo}"
        : string.Empty;

    public BubbleItem? SelectedBubble
    {
        get => _selectedBubble;
        set
        {
            _selectedBubble = value;
            Raise(nameof(SelectedBubble));
        }
    }

    public string SelectedRegionText
    {
        get => SelectedRegion?.Text ?? string.Empty;
        set
        {
            if (SelectedRegion is { } region)
            {
                region.Text = value ?? string.Empty;
                region.Raise();
                Raise(nameof(SelectedRegionText));
            }
        }
    }

    public RegionItem AddRegion(double x, double y, double width, double height)
    {
        var region = new RegionItem { X = x, Y = y, Width = width, Height = height };
        Regions.Add(region);
        SelectedRegion = region;
        return region;
    }

    /// <summary>
    /// READER-WORKBENCH-1 AC1: replaces the region list with the Core read-face rows (pixel-projected
    /// geometry already applied). Keeps the previous selection when the same region id survives.
    /// </summary>
    public void ReplaceRegions(IEnumerable<RegionItem> regions)
    {
        var previousId = SelectedRegion?.Id;
        Regions.Clear();
        foreach (var region in regions)
        {
            Regions.Add(region);
        }

        SelectedRegion =
            (previousId is null ? null : Regions.FirstOrDefault(region => string.Equals(region.Id, previousId, StringComparison.Ordinal)))
            ?? Regions.FirstOrDefault();
    }

    /// <summary>Selects one region by Core id (canvas ↔ list synchronization); false when absent.</summary>
    public bool SelectRegionById(string? regionId)
    {
        if (string.IsNullOrEmpty(regionId))
        {
            return false;
        }

        var match = Regions.FirstOrDefault(region => string.Equals(region.Id, regionId, StringComparison.Ordinal));
        if (match is null)
        {
            return false;
        }

        SelectedRegion = match;
        return true;
    }

    public bool DeleteSelectedRegion()
    {
        if (SelectedRegion is not { } region)
        {
            return false;
        }

        Regions.Remove(region);
        SelectedRegion = Regions.LastOrDefault();
        return true;
    }

    public void MoveSelectedRegion(double dx, double dy)
    {
        if (SelectedRegion is not { } region)
        {
            return;
        }

        region.X = Math.Max(0, region.X + dx);
        region.Y = Math.Max(0, region.Y + dy);
        region.Raise();
    }

    public void ResizeSelectedRegion(double dw, double dh)
    {
        if (SelectedRegion is not { } region)
        {
            return;
        }

        region.Width = Math.Max(8, region.Width + dw);
        region.Height = Math.Max(8, region.Height + dh);
        region.Raise();
    }

    public BubbleItem AddBubble(double x, double y)
    {
        var bubble = new BubbleItem { X = x, Y = y, Text = "（新气泡）" };
        Bubbles.Add(bubble);
        SelectedBubble = bubble;
        return bubble;
    }

    public void UpdateBubble(string? text, string? orientation)
    {
        if (SelectedBubble is not { } bubble)
        {
            return;
        }

        bubble.Text = text ?? bubble.Text;
        bubble.Orientation = orientation ?? bubble.Orientation;
        bubble.Raise();
    }

    public void LoadThumbnails(IEnumerable<string> labels)
    {
        Thumbnails.Clear();
        foreach (var label in labels)
        {
            Thumbnails.Add(label);
        }
    }

    private static string ShortId(string id) => id.Length <= 8 ? id : id[..8];

    private void Raise(string? name) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
