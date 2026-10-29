using System.Collections.ObjectModel;
using NewManga.App.Services;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.Library;

/// <summary>
/// V11R-B-1: the Library import dock (screen spec §2). Files are imported one by one through the
/// existing <see cref="IHostController.ImportFilesAsync"/> seam so every row carries a REAL per-file
/// outcome (imported / duplicate-skipped / failed) instead of a fabricated aggregate. A folder is a
/// single Host call, so its row honestly reports the aggregate result.
/// The "no chapter yet" entry closes audit F011: it is present but reports 能力待接入 until
/// <c>CreateChapterAsync</c> (V11R-A-1, core-bridge) is merged — it never pretends to succeed.
/// </summary>
public sealed class ImportDockViewModel : ObservableObject
{
    private readonly IHostController _controller;
    private readonly IFilePickerGateway? _picker;
    private readonly Action<string, NmStatus> _notify;
    private readonly Func<string?> _chapterId;
    private readonly Func<string?> _chapterTitle;
    private readonly Func<Task> _afterImport;
    private readonly Action _requestCreateChapter;
    private bool _isOpen;
    private bool _isRunning;
    private string _summary = string.Empty;

    public ImportDockViewModel(
        IHostController controller,
        IFilePickerGateway? picker,
        Action<string, NmStatus> notify,
        Func<string?> chapterId,
        Func<string?> chapterTitle,
        Func<Task> afterImport,
        Action requestCreateChapter)
    {
        _controller = controller;
        _picker = picker;
        _notify = notify;
        _chapterId = chapterId;
        _chapterTitle = chapterTitle;
        _afterImport = afterImport;
        _requestCreateChapter = requestCreateChapter;
        Rows = new ObservableCollection<ImportRowViewModel>();
        StartCommand = new RelayCommand(() => _ = StartAsync());
        RetryFailedCommand = new RelayCommand(RetryFailed);
        SkipFailedCommand = new RelayCommand(SkipFailed);
        CloseCommand = new RelayCommand(Close);
        RequestCreateChapterCommand = new RelayCommand(RequestCreateChapter);
    }

    public ObservableCollection<ImportRowViewModel> Rows { get; }

    public RelayCommand StartCommand { get; }

    public RelayCommand RetryFailedCommand { get; }

    public RelayCommand SkipFailedCommand { get; }

    public RelayCommand CloseCommand { get; }

    public RelayCommand RequestCreateChapterCommand { get; }

    public bool IsOpen
    {
        get => _isOpen;
        private set
        {
            if (Set(ref _isOpen, value))
            {
                RaiseDerived();
            }
        }
    }

    public bool IsRunning
    {
        get => _isRunning;
        private set
        {
            if (Set(ref _isRunning, value))
            {
                RaiseDerived();
            }
        }
    }

    public string Summary
    {
        get => _summary;
        private set => Set(ref _summary, value);
    }

    public bool HasRows => Rows.Count > 0;

    public bool HasFailures => Rows.Any(row => row.State == ImportRowState.Failed);

    public bool HasPending => Rows.Any(row => row.State == ImportRowState.Pending);

    public bool HasTargetChapter => !string.IsNullOrEmpty(_chapterId());

    public bool ShowCreateChapterEntry => !HasTargetChapter;

    public string Title => HasTargetChapter
        ? $"导入到「{_chapterTitle()}」"
        : "导入：尚未选择章节";

    /// <summary>Honest degradation notice: chapter creation is a real Core write (V11R-A-1).</summary>
    public string CapabilityText =>
        "当前没有章节：先在右侧就地「新建章节」（走 Core CreateChapter，V11R-A-1），创建成功后即可导入；" +
        "不会伪造章节或伪造导入成功。";

    public string TargetChapterText => HasTargetChapter
        ? $"目标章节：{_chapterTitle()}"
        : "先选择作品与章节，再导入文件。";

    public bool CanStart => IsOpen && !IsRunning && HasPending && HasTargetChapter;

    public async Task OpenWithFilesAsync(IReadOnlyList<string> paths)
    {
        if (paths.Count == 0)
        {
            return;
        }

        IsOpen = true;
        foreach (var path in paths)
        {
            Rows.Add(new ImportRowViewModel(path, isFolder: false));
        }

        UpdateSummary();
        if (HasTargetChapter)
        {
            await StartAsync().ConfigureAwait(true);
        }
        else
        {
            _notify("导入已就绪：请先选择章节（无章节时「新建章节」为能力待接入）", NmStatus.Blocked);
        }
    }

    public async Task OpenWithFolderAsync(string folderPath)
    {
        if (string.IsNullOrWhiteSpace(folderPath))
        {
            return;
        }

        IsOpen = true;
        Rows.Add(new ImportRowViewModel(folderPath, isFolder: true));
        UpdateSummary();
        if (HasTargetChapter)
        {
            await StartAsync().ConfigureAwait(true);
        }
        else
        {
            _notify("导入已就绪：请先选择章节（无章节时「新建章节」为能力待接入）", NmStatus.Blocked);
        }
    }

    /// <summary>Opens the picker and imports the chosen files; used by the Library import buttons.</summary>
    public async Task PickFilesAsync()
    {
        if (_picker is null)
        {
            _notify("文件选择器不可用（Host/窗口未就绪）", NmStatus.Blocked);
            return;
        }

        var paths = await _picker.PickFilesAsync().ConfigureAwait(true);
        if (paths.Count == 0)
        {
            return;
        }

        await OpenWithFilesAsync(paths).ConfigureAwait(true);
    }

    public async Task PickFolderAsync()
    {
        if (_picker is null)
        {
            _notify("文件夹选择器不可用（Host/窗口未就绪）", NmStatus.Blocked);
            return;
        }

        var folder = await _picker.PickFolderAsync().ConfigureAwait(true);
        if (string.IsNullOrWhiteSpace(folder))
        {
            return;
        }

        await OpenWithFolderAsync(folder).ConfigureAwait(true);
    }

    public async Task StartAsync()
    {
        if (!IsOpen)
        {
            return;
        }

        if (!HasTargetChapter)
        {
            _notify("导入被拒绝：尚未选择章节（不会伪造章节或导入结果）", NmStatus.Blocked);
            return;
        }

        if (IsRunning)
        {
            return;
        }

        var chapterId = _chapterId();
        if (string.IsNullOrWhiteSpace(chapterId))
        {
            return;
        }

        IsRunning = true;
        try
        {
            foreach (var row in Rows.Where(item => item.State == ImportRowState.Pending).ToList())
            {
                row.State = ImportRowState.Importing;
                row.Message = "导入中…";
                await ImportOneAsync(chapterId, row).ConfigureAwait(true);
            }
        }
        finally
        {
            IsRunning = false;
            UpdateSummary();
        }

        await _afterImport().ConfigureAwait(true);

        if (HasFailures)
        {
            _notify($"导入部分失败：{Rows.Count(row => row.State == ImportRowState.Failed)} 个文件失败，可重试或跳过", NmStatus.Failed);
        }
        else if (Rows.Any(row => row.State == ImportRowState.Imported))
        {
            _notify(Summary, NmStatus.Done);
        }
    }

    public void RetryFailed()
    {
        if (IsRunning)
        {
            return;
        }

        var failed = Rows.Where(row => row.State == ImportRowState.Failed).ToList();
        if (failed.Count == 0)
        {
            return;
        }

        foreach (var row in failed)
        {
            row.ResetForRetry();
        }

        UpdateSummary();
        _ = StartAsync();
    }

    public void SkipFailed()
    {
        if (IsRunning)
        {
            return;
        }

        foreach (var row in Rows.Where(item => item.State == ImportRowState.Failed))
        {
            row.State = ImportRowState.SkippedByUser;
            row.Message = "已跳过（用户选择）";
        }

        UpdateSummary();
    }

    public void Close()
    {
        if (IsRunning)
        {
            _notify("导入进行中：完成后再关闭导入面板", NmStatus.Running);
            return;
        }

        IsOpen = false;
        Rows.Clear();
        Summary = string.Empty;
        RaiseDerived();
    }

    public void RequestCreateChapter()
    {
        _requestCreateChapter();
        NotifyChapterContextChanged();
    }

    /// <summary>Raised when the Library selection changes so the dock header follows the target.</summary>
    public void NotifyChapterContextChanged()
    {
        OnPropertyChanged(nameof(HasTargetChapter), nameof(ShowCreateChapterEntry), nameof(Title), nameof(TargetChapterText), nameof(CanStart));
    }

    private async Task ImportOneAsync(string chapterId, ImportRowViewModel row)
    {
        try
        {
            var outcome = row.IsFolder
                ? await _controller.ImportFolderAsync(chapterId, row.Path).ConfigureAwait(true)
                : await _controller.ImportFilesAsync(chapterId, new[] { row.Path }).ConfigureAwait(true);

            if (!outcome.Ok)
            {
                row.State = ImportRowState.Failed;
                row.Message = outcome.ErrorCode is { Length: > 0 }
                    ? $"{outcome.Message}（{outcome.ErrorCode}）"
                    : outcome.Message;
                return;
            }

            if (row.IsFolder)
            {
                row.State = outcome.ImportedFiles > 0 ? ImportRowState.Imported : ImportRowState.Skipped;
                row.Message = outcome.Message;
                return;
            }

            if (outcome.ImportedFiles > 0)
            {
                row.State = ImportRowState.Imported;
                row.Message = "已导入";
            }
            else if (outcome.SkippedFiles > 0)
            {
                row.State = ImportRowState.Skipped;
                row.Message = "跳过（重复）";
            }
            else
            {
                row.State = ImportRowState.Skipped;
                row.Message = "没有新内容";
            }
        }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
        {
            row.State = ImportRowState.Failed;
            row.Message = "导入异常：" + ex.Message;
        }
    }

    private void UpdateSummary()
    {
        if (Rows.Count == 0)
        {
            Summary = string.Empty;
        }
        else
        {
            var imported = Rows.Count(row => row.State == ImportRowState.Imported);
            var skipped = Rows.Count(row => row.State is ImportRowState.Skipped or ImportRowState.SkippedByUser);
            var failed = Rows.Count(row => row.State == ImportRowState.Failed);
            var pending = Rows.Count(row => row.State is ImportRowState.Pending or ImportRowState.Importing);
            Summary = $"已导入 {imported} · 跳过 {skipped} · 失败 {failed} · 待处理 {pending}";
        }

        RaiseDerived();
    }

    private void RaiseDerived() => OnPropertyChanged(
        nameof(HasRows),
        nameof(HasFailures),
        nameof(HasPending),
        nameof(CanStart),
        nameof(ShowCreateChapterEntry),
        nameof(HasTargetChapter),
        nameof(Title),
        nameof(TargetChapterText));
}
