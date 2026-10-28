using Avalonia.Controls;
using Avalonia.Platform.Storage;

namespace NewManga.App.Services;

/// <summary>
/// IMPORT-EXPORT-UI-1: the system picker seam. Pages never touch Avalonia storage APIs directly, so
/// headless tests can drive the exact same flow with recorded selections.
/// </summary>
public interface IFilePickerGateway
{
    /// <summary>系统「打开文件」选择器；取消返回空列表。</summary>
    Task<IReadOnlyList<string>> PickFilesAsync(CancellationToken cancellationToken = default);

    /// <summary>系统「选择文件夹」选择器；取消返回 null。</summary>
    Task<string?> PickFolderAsync(CancellationToken cancellationToken = default);

    /// <summary>导出目标的系统「另存为」选择器；取消返回 null。</summary>
    Task<string?> PickExportTargetAsync(
        string suggestedFileName,
        string suggestedDirectory,
        CancellationToken cancellationToken = default);
}

/// <summary>Production gateway backed by the Avalonia 11 StorageProvider of the owning TopLevel.</summary>
public sealed class AvaloniaFilePickerGateway : IFilePickerGateway
{
    private static readonly FilePickerFileType ImageFiles = new("图片")
    {
        Patterns = new[] { "*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.gif", "*.tif", "*.tiff" },
        MimeTypes = new[] { "image/*" },
    };

    private readonly Func<Control?, TopLevel?> _topLevel;

    public AvaloniaFilePickerGateway(Func<Control?, TopLevel?> topLevel) => _topLevel = topLevel;

    public async Task<IReadOnlyList<string>> PickFilesAsync(CancellationToken cancellationToken = default)
    {
        var storage = TryGetStorage();
        if (storage is null)
        {
            return Array.Empty<string>();
        }

        var files = await storage.OpenFilePickerAsync(new FilePickerOpenOptions
        {
            Title = "导入文件到当前章节",
            AllowMultiple = true,
            FileTypeFilter = new[] { ImageFiles, FilePickerFileTypes.All },
        });

        var paths = new List<string>();
        foreach (var file in files)
        {
            var path = file.TryGetLocalPath();
            if (!string.IsNullOrWhiteSpace(path))
            {
                paths.Add(path);
            }
        }

        return paths;
    }

    public async Task<string?> PickFolderAsync(CancellationToken cancellationToken = default)
    {
        var storage = TryGetStorage();
        if (storage is null)
        {
            return null;
        }

        var folders = await storage.OpenFolderPickerAsync(new FolderPickerOpenOptions
        {
            Title = "导入文件夹（按文件名顺序导入）",
            AllowMultiple = false,
        });
        return folders.Count == 0 ? null : folders[0].TryGetLocalPath();
    }

    public async Task<string?> PickExportTargetAsync(
        string suggestedFileName,
        string suggestedDirectory,
        CancellationToken cancellationToken = default)
    {
        var storage = TryGetStorage();
        if (storage is null)
        {
            return null;
        }

        IStorageFolder? start = null;
        if (!string.IsNullOrWhiteSpace(suggestedDirectory) && Directory.Exists(suggestedDirectory))
        {
            start = await storage.TryGetFolderFromPathAsync(suggestedDirectory);
        }

        var file = await storage.SaveFilePickerAsync(new FilePickerSaveOptions
        {
            Title = "导出当前书（ZIP 图片包）",
            SuggestedFileName = suggestedFileName,
            DefaultExtension = "zip",
            SuggestedStartLocation = start,
            FileTypeChoices = new[]
            {
                new FilePickerFileType("ZIP 图片包") { Patterns = new[] { "*.zip" } },
            },
            ShowOverwritePrompt = true,
        });
        return file?.TryGetLocalPath();
    }

    private IStorageProvider? TryGetStorage()
    {
        var topLevel = _topLevel(null);
        return topLevel?.StorageProvider is { CanOpen: true } storageProvider ? storageProvider : null;
    }
}
