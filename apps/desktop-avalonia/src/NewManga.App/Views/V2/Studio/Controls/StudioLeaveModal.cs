using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;
using Avalonia.Media;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-3: the unsaved-changes modal with the three exits required by SCREEN_SPECS §3
/// (保存 / 放弃 / 取消). The default focus is 取消 (DESIGN_SYSTEM §6.2 <c>Modal</c>), <c>Esc</c> cancels,
/// and 保存 stays disabled with the reason when the pending edit cannot be written (NOT_WIRED).
/// </summary>
public sealed class StudioLeaveModal : Grid
{
    private readonly StudioPageViewModel _viewModel;
    private readonly TextBlock _body;
    private readonly TextBlock _error;
    private readonly Button _saveButton;
    private readonly Button _discardButton;
    private readonly Button _cancelButton;

    public StudioLeaveModal(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;

        var scrim = StudioUi.Box("studio-scrim");
        scrim.HorizontalAlignment = HorizontalAlignment.Stretch;
        scrim.VerticalAlignment = VerticalAlignment.Stretch;
        Children.Add(scrim);

        var card = StudioUi.Box("studio-modal-card");
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;

        var column = StudioUi.Column(12);
        column.Children.Add(StudioUi.Text("离开前保存更改？", "title"));
        _body = new TextBlock { Classes = { "body", "studio-wrap" } };
        _body.Bind(TextBlock.TextProperty, new Avalonia.Data.Binding(nameof(StudioPageViewModel.LeaveBody)));
        column.Children.Add(_body);

        _error = new TextBlock { Classes = { "meta", "studio-wrap" }, Foreground = Brushes.Transparent };
        _error.Bind(TextBlock.TextProperty, new Avalonia.Data.Binding(nameof(StudioPageViewModel.LeaveError)));
        StudioUi.TrackVisible(_error, _viewModel, () => _viewModel.HasLeaveError);
        column.Children.Add(_error);

        var buttons = StudioUi.Row(8);
        buttons.HorizontalAlignment = HorizontalAlignment.Right;
        _saveButton = StudioUi.Button("保存并继续", "sm primary", () => _ = ResolveAsync(StudioLeaveChoice.Save));
        _saveButton.Bind(IsEnabledProperty, new Avalonia.Data.Binding(nameof(StudioPageViewModel.LeaveSaveEnabled)));
        _discardButton = StudioUi.Button("放弃更改", "studio-action danger", () => _ = ResolveAsync(StudioLeaveChoice.Discard));
        _cancelButton = StudioUi.Button("取消", "sm", () => _ = ResolveAsync(StudioLeaveChoice.Cancel));
        buttons.Children.Add(_cancelButton);
        buttons.Children.Add(_discardButton);
        buttons.Children.Add(_saveButton);
        column.Children.Add(buttons);

        card.Child = column;
        Children.Add(card);

        StudioUi.TrackVisible(this, _viewModel, () => _viewModel.IsLeaveModalOpen);
        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.LeaveSaveTooltip) or null)
            {
                StudioUi.SetTooltip(_saveButton, _viewModel.LeaveSaveTooltip);
            }
        };

        StudioUi.SetTooltip(_saveButton, _viewModel.LeaveSaveTooltip);
        IsVisible = _viewModel.IsLeaveModalOpen;
    }

    public Button SaveButton => _saveButton;

    public Button DiscardButton => _discardButton;

    public Button CancelButton => _cancelButton;

    public TextBlock Body => _body;

    public TextBlock ErrorText => _error;

    /// <summary><c>Esc</c> resolves as 取消 (the safe exit), never as 放弃.</summary>
    public Task EscAsync() => ResolveAsync(StudioLeaveChoice.Cancel);

    private async Task ResolveAsync(StudioLeaveChoice choice)
    {
        await _viewModel.ResolveLeaveAsync(choice).ConfigureAwait(true);
    }
}
