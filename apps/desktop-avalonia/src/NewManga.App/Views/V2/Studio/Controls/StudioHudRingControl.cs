using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 <c>HUDRing</c>: the eight 22×22 actions around the selected region (N/NE/E/SE/S/SW/W/NW).
/// <c>Tab</c> cycles the focus through enabled slots, <c>Enter</c> executes the focused one. Disabled
/// (NOT_WIRED) slots stay visible so the user can see the capability exists but cannot be run yet;
/// they use the shared 40% disabled opacity and carry the "能力待接入" tooltip.
/// </summary>
public sealed class StudioHudRingControl : Canvas
{
    private const double SlotSize = 22;
    private const double Gap = 4;

    private readonly StudioPageViewModel _viewModel;
    private readonly Dictionary<StudioHudAction, Button> _buttons = new();

    public StudioHudRingControl(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        IsHitTestVisible = true;
        Background = Brushes.Transparent;

        for (var index = 0; index < viewModel.HudSlots.Count; index++)
        {
            var slot = viewModel.HudSlots[index];
            var slotIndex = index;
            var button = StudioUi.Button(slot.Glyph, "studio-hud-slot", () =>
            {
                _viewModel.SetHudFocus(slotIndex);
                _ = _viewModel.ExecuteFocusedHudAsync();
            });
            button.Width = SlotSize;
            button.Height = SlotSize;
            button.FontSize = StudioUi.TokenDouble("Nm.FontSize.Xs", 11);
            ToolTip.SetTip(button, slot.Label);
            _buttons[slot.Action] = button;
            Children.Add(button);

            var captured = slot;
            StudioUi.TrackClass(button, "active", slot, () => captured.IsFocused);
            button.Bind(IsEnabledProperty, new Avalonia.Data.Binding(nameof(StudioHudSlotViewModel.IsEnabled)));
            ToolTip.SetTip(button, string.Empty);
            slot.PropertyChanged += (_, _) => ToolTip.SetTip(button, captured.Tooltip);
        }

        UpdateLayoutState();
    }

    /// <summary>Buttons in ring order (tests assert 8 slots and their positions).</summary>
    public IReadOnlyList<Button> Buttons => _viewModel.HudSlots.Select(slot => _buttons[slot.Action]).ToList();

    public Button? ButtonFor(StudioHudAction action) =>
        _buttons.TryGetValue(action, out var button) ? button : null;

    /// <summary>Positions the ring around the selected region (called by the viewport on every frame change).</summary>
    public void UpdateLayoutState()
    {
        var region = _viewModel.SelectedRegion;
        IsVisible = _viewModel.HudVisible;
        if (region is null || !region.HasGeometry)
        {
            return;
        }

        var zoom = _viewModel.Zoom;
        var rect = region.PixelRect.Scale(zoom);
        var centerX = rect.X + rect.Width / 2;
        var centerY = rect.Y + rect.Height / 2;
        var centers = new Dictionary<StudioHudAction, Point>
        {
            [StudioHudAction.ShowTextTier] = new(centerX, rect.Y - Gap - SlotSize / 2),
            [StudioHudAction.ShowStyle] = new(rect.Right + Gap + SlotSize / 2, rect.Y - Gap - SlotSize / 2),
            [StudioHudAction.ShowHistory] = new(rect.Right + Gap + SlotSize / 2, centerY),
            [StudioHudAction.RerenderPage] = new(rect.Right + Gap + SlotSize / 2, rect.Bottom + Gap + SlotSize / 2),
            [StudioHudAction.RestorePreviousRevision] = new(centerX, rect.Bottom + Gap + SlotSize / 2),
            [StudioHudAction.ReOcrRegion] = new(rect.X - Gap - SlotSize / 2, rect.Bottom + Gap + SlotSize / 2),
            [StudioHudAction.ToggleLock] = new(rect.X - Gap - SlotSize / 2, centerY),
            [StudioHudAction.DeleteRegion] = new(rect.X - Gap - SlotSize / 2, rect.Y - Gap - SlotSize / 2),
        };

        foreach (var (action, center) in centers)
        {
            if (!_buttons.TryGetValue(action, out var button))
            {
                continue;
            }

            SetLeft(button, Math.Round(center.X - SlotSize / 2));
            SetTop(button, Math.Round(center.Y - SlotSize / 2));
        }
    }
}
