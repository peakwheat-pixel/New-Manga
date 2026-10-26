using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace NewManga.App.ViewModels;

public sealed class RegionItem : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;
    public string Id { get; init; } = Guid.NewGuid().ToString("N")[..8];
    public double X { get; set; }
    public double Y { get; set; }
    public double Width { get; set; }
    public double Height { get; set; }
    public string Kind { get; set; } = "text";
    public string Text { get; set; } = string.Empty;

    public void Raise() => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(string.Empty));
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

    public RegionItem? SelectedRegion
    {
        get => _selectedRegion;
        set
        {
            _selectedRegion = value;
            Raise(nameof(SelectedRegion));
        }
    }

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

    private void Raise(string? name) => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
