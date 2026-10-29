using Avalonia.Controls;
using Avalonia.Input;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3 AC5: Studio keyboard map. <c>Tab</c> cycles the HUD ring while a region is selected,
/// <c>Enter</c> executes the focused slot, <c>J/K</c> walk regions, <c>[ ]</c> walk pages, <c>+/-</c>
/// zoom, <c>0</c> fit, <c>Esc</c> closes step by step (modal → inspector → selection). Letter
/// shortcuts yield while a text input owns the focus (IME safety, DESIGN_SYSTEM §8).
/// </summary>
public static class StudioKeyboard
{
    /// <summary>Returns true when the key was consumed by the Studio.</summary>
    public static bool Handle(StudioPageViewModel viewModel, Control scope, KeyEventArgs args)
    {
        if (args.Handled || IsTextInputFocused(scope))
        {
            return false;
        }

        var shift = (args.KeyModifiers & KeyModifiers.Shift) != 0;
        switch (args.Key)
        {
            case Key.Tab when viewModel.HudVisible:
                viewModel.CycleHud(shift ? -1 : 1);
                args.Handled = true;
                return true;

            case Key.Enter when viewModel.HudVisible:
                _ = viewModel.ExecuteFocusedHudAsync();
                args.Handled = true;
                return true;

            case Key.J:
                viewModel.MoveRegionSelection(1);
                args.Handled = true;
                return true;

            case Key.K:
                viewModel.MoveRegionSelection(-1);
                args.Handled = true;
                return true;

            case Key.OemOpenBrackets:
                _ = viewModel.MovePageAsync(-1);
                args.Handled = true;
                return true;

            case Key.OemCloseBrackets:
                _ = viewModel.MovePageAsync(1);
                args.Handled = true;
                return true;

            case Key.OemPlus or Key.Add:
                viewModel.ZoomIn();
                args.Handled = true;
                return true;

            case Key.OemMinus or Key.Subtract:
                viewModel.ZoomOut();
                args.Handled = true;
                return true;

            case Key.D0 or Key.NumPad0:
                viewModel.FitWindow();
                args.Handled = true;
                return true;

            case Key.Escape:
                return HandleEscape(viewModel);

            default:
                return false;
        }
    }

    private static bool HandleEscape(StudioPageViewModel viewModel)
    {
        if (viewModel.IsLeaveModalOpen)
        {
            _ = viewModel.ResolveLeaveAsync(StudioLeaveChoice.Cancel);
            return true;
        }

        if (viewModel.InspectorExpanded)
        {
            viewModel.InspectorExpanded = false;
            return true;
        }

        if (viewModel.HudVisible)
        {
            viewModel.SelectRegion(null);
            return true;
        }

        return false;
    }

    /// <summary>
    /// IME safety: while a text input owns focus the letter shortcuts must not fire. The Studio has no
    /// free-text field in this build (人工译文输入框 is NOT_WIRED), so this guard mainly serves the
    /// F0-1 merge and the shell's palette field.
    /// </summary>
    private static bool IsTextInputFocused(Control scope)
    {
        var focused = TopLevel.GetTopLevel(scope)?.FocusManager?.GetFocusedElement();
        return focused is TextBox;
    }
}
/// <summary>I3: Batch-mode keys (arrows / J,K / Enter / Esc). Returns true when the Batch consumed it.</summary>
public static class StudioBatchKeyboard
{
    public static bool Handle(StudioBatchViewModel batch, KeyEventArgs args)
    {
        if (args.Handled)
        {
            return false;
        }

        var row = batch.SelectingAnchor?.RowIndex ?? 0;
        switch (args.Key)
        {
            case Key.Escape:
                if (batch.IsGateConfirmOpen)
                {
                    batch.CancelGate();
                    args.Handled = true;
                    return true;
                }

                if (batch.StopArmed)
                {
                    batch.CancelStop();
                    args.Handled = true;
                    return true;
                }

                if (batch.IsDrawerOpen)
                {
                    batch.CloseDrawer();
                    args.Handled = true;
                    return true;
                }

                return false;
            case Key.Enter:
                if (batch.Rows.Count > 0)
                {
                    batch.RequestDrillToPage(Math.Clamp(row, 0, batch.Rows.Count - 1));
                    args.Handled = true;
                    return true;
                }

                return false;
            case Key.Down or Key.J:
                Move(batch, row + 1);
                args.Handled = true;
                return true;
            case Key.Up or Key.K:
                Move(batch, row - 1);
                args.Handled = true;
                return true;
            case Key.Right or Key.OemCloseBrackets:
                MoveColumn(batch, 1);
                args.Handled = true;
                return true;
            case Key.Left or Key.OemOpenBrackets:
                MoveColumn(batch, -1);
                args.Handled = true;
                return true;
            default:
                return false;
        }
    }

    private static void Move(StudioBatchViewModel batch, int row)
    {
        if (batch.Rows.Count == 0)
        {
            return;
        }

        batch.SelectRow(Math.Clamp(row, 0, batch.Rows.Count - 1));
    }

    private static void MoveColumn(StudioBatchViewModel batch, int delta)
    {
        if (batch.Rows.Count == 0 || batch.StageColumnCount == 0)
        {
            return;
        }

        var row = Math.Clamp(batch.SelectingAnchor?.RowIndex ?? 0, 0, batch.Rows.Count - 1);
        var current = batch.StageColumns.ToList().FindIndex(stage =>
            string.Equals(stage.CoreStepType, batch.SelectingAnchor?.StageType, StringComparison.OrdinalIgnoreCase));
        var next = Math.Clamp((current < 0 ? 0 : current) + delta, 0, batch.StageColumnCount - 1);
        batch.SelectCell(row, batch.StageColumns[next].CoreStepType);
    }
}