using System.ComponentModel;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Library;

namespace NewManga.App.Views.V2.Library;

/// <summary>
/// FEA-12-UI: recycle-bin host. The disclosure panel is an inline confirm step, so it owns the
/// keyboard contract for that step: default focus lands on 取消 and Esc closes the panel without
/// deleting anything. Enter never confirms by itself — the delete needs the explicit understood
/// checkbox plus a deliberate button activation (AC4/AC5).
/// </summary>
public partial class RecycleBinView : UserControl
{
    private LibraryViewModel? _viewModel;
    private TrashViewModel? _trash;

    public RecycleBinView()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => AttachViewModel();
    }

    private void AttachViewModel()
    {
        if (_trash is not null)
        {
            _trash.PropertyChanged -= OnTrashPropertyChanged;
        }

        _viewModel = DataContext as LibraryViewModel;
        _trash = _viewModel?.Trash;
        if (_trash is not null)
        {
            _trash.PropertyChanged += OnTrashPropertyChanged;
        }
    }

    private void OnTrashPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (e.PropertyName == nameof(TrashViewModel.IsPreviewOpen) && _trash is { IsPreviewOpen: true })
        {
            // DESIGN_SYSTEM §6.2: the destructive modal starts on 取消, never on the dangerous action.
            Dispatcher.UIThread.Post(() => PreviewCancelButton?.Focus());
        }
    }

    protected override void OnKeyDown(KeyEventArgs e)
    {
        if (HandleKey(e.Key))
        {
            e.Handled = true;
            return;
        }

        base.OnKeyDown(e);
    }

    /// <summary>Test seam mirroring the shell's HandleKeyForTest: Esc closes the disclosure step.</summary>
    internal bool HandleKeyForTest(Key key) => HandleKey(key);

    private bool HandleKey(Key key)
    {
        if (key == Key.Escape && _trash is { IsPreviewOpen: true })
        {
            _trash.CancelPreview();
            return true;
        }

        return false;
    }
}
