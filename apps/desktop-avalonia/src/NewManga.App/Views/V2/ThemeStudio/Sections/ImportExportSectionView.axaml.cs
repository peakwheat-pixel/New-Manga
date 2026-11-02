using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Platform.Storage;
using NewManga.App.ViewModels.V2.ThemeStudio;

namespace NewManga.App.Views.V2.ThemeStudio.Sections;

/// <summary>
/// ⑥ 导入导出 view. Owns the file drop target: the view passes the dropped path to the ViewModel, which
/// delegates reading to the service (the UI itself never opens arbitrary paths).
/// </summary>
public partial class ImportExportSectionView : UserControl
{
    public ImportExportSectionView()
    {
        InitializeComponent();
        DragDrop.SetAllowDrop(DropZone, true);
        DropZone.AddHandler(DragDrop.DragEnterEvent, OnDragOver);
        DropZone.AddHandler(DragDrop.DragOverEvent, OnDragOver);
        DropZone.AddHandler(DragDrop.DragLeaveEvent, OnDragLeave);
        DropZone.AddHandler(DragDrop.DropEvent, OnDrop);
    }

    private ThemeStudioImportExportViewModel? ViewModel => DataContext as ThemeStudioImportExportViewModel;

    private void OnDragOver(object? sender, DragEventArgs e)
    {
        var hasFiles = e.DataTransfer.Contains(DataFormat.File);
        if (ViewModel is { } viewModel)
        {
            viewModel.IsDropActive = hasFiles;
        }

        e.DragEffects = hasFiles ? DragDropEffects.Copy : DragDropEffects.None;
        e.Handled = true;
    }

    private void OnDragLeave(object? sender, DragEventArgs e)
    {
        if (ViewModel is { } viewModel)
        {
            viewModel.IsDropActive = false;
        }
    }

    private void OnDrop(object? sender, DragEventArgs e)
    {
        if (ViewModel is not { } viewModel)
        {
            return;
        }

        viewModel.IsDropActive = false;
        e.Handled = true;

        var path = FirstLocalPath(e.DataTransfer);
        if (path is not null)
        {
            _ = viewModel.ImportFileAsync(path);
        }
    }

    private static string? FirstLocalPath(IDataTransfer transfer)
    {
        var files = transfer.TryGetFiles();
        if (files is null)
        {
            return null;
        }

        foreach (IStorageItem file in files)
        {
            if (file.Path is { IsFile: true } uri)
            {
                return uri.LocalPath;
            }
        }

        return null;
    }
}
