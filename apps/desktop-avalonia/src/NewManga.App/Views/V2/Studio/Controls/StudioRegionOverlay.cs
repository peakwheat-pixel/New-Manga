using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// One absolute-positioned region rectangle (DESIGN_SYSTEM §6.4 <c>RegionBox</c>): accent outline when
/// selected, half-bright accent on hover, ▮ badge when locked, ✗ badge when failed. Badges only appear
/// when a real source reported the flag — the read face for them is NOT_WIRED in this build.
/// </summary>
public sealed class StudioRegionBox : Border
{
    private readonly StudioRegionItem _item;
    private readonly Border _lockBadge;
    private readonly Border _failBadge;
    private readonly Border _labelChip;

    public StudioRegionBox(
        StudioRegionItem item,
        Action<StudioRegionItem> onSelect,
        Action<StudioRegionItem?> onHover)
    {
        _item = item;
        Classes.Add("studio-region");
        Background = Brushes.Transparent;
        ClipToBounds = false;

        _labelChip = StudioUi.Box("studio-region-label");
        _labelChip.Child = StudioUi.Text(item.ShortLabel, "nm-data");
        _labelChip.HorizontalAlignment = HorizontalAlignment.Left;
        _labelChip.VerticalAlignment = VerticalAlignment.Top;
        _labelChip.Margin = new Thickness(2);

        _failBadge = StudioUi.Box("studio-region-badge");
        _failBadge.Child = StudioUi.Text("✗", "studio-region-badge-failed", "nm-num");
        _failBadge.HorizontalAlignment = HorizontalAlignment.Right;
        _failBadge.VerticalAlignment = VerticalAlignment.Top;
        _failBadge.Margin = new Thickness(2);

        _lockBadge = StudioUi.Box("studio-region-badge");
        _lockBadge.Child = StudioUi.Text("▮", "studio-region-badge-locked", "nm-num");
        _lockBadge.HorizontalAlignment = HorizontalAlignment.Right;
        _lockBadge.VerticalAlignment = VerticalAlignment.Bottom;
        _lockBadge.Margin = new Thickness(2);

        var layer = new Canvas { IsHitTestVisible = false };
        Canvas.SetLeft(_labelChip, 0);
        Canvas.SetTop(_labelChip, 0);
        layer.Children.Add(_labelChip);
        layer.Children.Add(_failBadge);
        layer.Children.Add(_lockBadge);
        Child = layer;

        PointerEntered += (_, _) => onHover(item);
        PointerExited += (_, _) => onHover(null);
        PointerPressed += (_, args) =>
        {
            onSelect(item);
            args.Handled = true;
        };

        item.PropertyChanged += (_, _) => ApplyState();
        ApplyState();
    }

    public StudioRegionItem Item => _item;

    public Border LabelChip => _labelChip;

    public Border LockBadge => _lockBadge;

    public Border FailBadge => _failBadge;

    /// <summary>Re-applies the class set from the item (selection/hover/lock/failure/geometry).</summary>
    public void ApplyState()
    {
        Classes.Set("selected", _item.IsSelected);
        Classes.Set("hovered", _item.IsHovered);
        Classes.Set("locked", _item.IsLocked);
        Classes.Set("nogeometry", !_item.HasGeometry);
        _lockBadge.IsVisible = _item.IsLocked;
        _failBadge.IsVisible = _item.HasFailed;
        ToolTip.SetTip(this, _item.DisplayLabel);
    }
}

/// <summary>
/// V11R-B-3: the region overlay layer. Percent-based Core geometry is projected to page pixels and
/// multiplied by the current zoom; the layer never intercepts page dragging (it is hit-testable only
/// on the region boxes themselves).
/// </summary>
public sealed class StudioRegionOverlay : Canvas
{
    private readonly StudioPageViewModel _viewModel;
    private readonly Dictionary<string, StudioRegionBox> _boxes = new(StringComparer.Ordinal);

    public StudioRegionOverlay(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        Background = Brushes.Transparent;
        IsHitTestVisible = false;
        viewModel.Regions.CollectionChanged += (_, _) => Rebuild();
        Rebuild();
    }

    /// <summary>Boxes in region order (asserted by the headless control-tree tests).</summary>
    public IReadOnlyList<StudioRegionBox> Boxes => _boxes.Values.ToList();

    public StudioRegionBox? BoxFor(string regionId) =>
        _boxes.TryGetValue(regionId, out var box) ? box : null;

    public void Rebuild()
    {
        foreach (var stale in _boxes.Values.Where(box => !_viewModel.Regions.Contains(box.Item)).ToList())
        {
            Children.Remove(stale);
            _boxes.Remove(stale.Item.RegionId);
        }

        foreach (var item in _viewModel.Regions)
        {
            if (_boxes.ContainsKey(item.RegionId))
            {
                continue;
            }

            var box = new StudioRegionBox(
                item,
                selected => _viewModel.SelectRegion(selected),
                hovered => _viewModel.HoverRegion(hovered));
            _boxes[item.RegionId] = box;
            Children.Add(box);
        }

        Relayout();
    }

    /// <summary>Repositions every box for the current zoom/offset (invoked by the viewport).</summary>
    public void Relayout()
    {
        var zoom = _viewModel.Zoom;
        foreach (var (regionId, box) in _boxes)
        {
            var item = _viewModel.Regions.FirstOrDefault(region =>
                string.Equals(region.RegionId, regionId, StringComparison.Ordinal));
            if (item is null || !item.HasGeometry)
            {
                box.IsVisible = false;
                continue;
            }

            var rect = item.PixelRect.Scale(zoom);
            box.IsVisible = true;
            box.Width = Math.Max(6, rect.Width);
            box.Height = Math.Max(6, rect.Height);
            SetLeft(box, rect.X);
            SetTop(box, rect.Y);
            box.ApplyState();
        }
    }
}
