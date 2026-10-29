using System.Collections.ObjectModel;
using System.Windows.Input;
using NewManga.App.Shell.V2;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// ⑥ 导入导出 (THEME_STUDIO_SPEC §3.6): drag-in / paste / pick a <c>.nmtheme</c> or <c>.json</c>, show every
/// validation finding (level + path + message + suggestion), block import on errors and export the
/// canonical package JSON. Round-trip equivalence is verified by the service tests (export → validate →
/// import produces the same document).
/// </summary>
public sealed class ThemeStudioImportExportViewModel : ThemeStudioSectionViewModel
{
    private string _inputJson = string.Empty;
    private string _sourceName = "粘贴的主题包";
    private ThemeStudioValidationReport? _report;
    private string _statusMessage = "拖入 .nmtheme / .json 文件，或粘贴主题包 JSON 后点击“校验”。";
    private bool _isValidating;
    private bool _isDropActive;
    private string? _lastExportJson;
    private string? _selectedExportThemeId;

    internal ThemeStudioImportExportViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.ImportExport)
    {
        ValidateCommand = new RelayCommand(() => Run(ValidateAsync));
        ImportCommand = new RelayCommand(() => Run(ImportAsync), () => CanImport);
        ClearCommand = new RelayCommand(Clear);
        PickFileCommand = new RelayCommand(() => Run(PickFileAsync));
        ExportCommand = new RelayCommand(() => Run(ExportAsync), () => SelectedExportThemeId is not null);
        UseSampleCommand = new RelayCommand(LoadExportableSample);
    }

    public ObservableCollection<ThemeStudioIssue> Issues { get; } = new();

    public ObservableCollection<ThemeStudioOption> ExportThemeOptions { get; } = new();

    public ICommand ValidateCommand { get; }

    public ICommand ImportCommand { get; }

    public ICommand ClearCommand { get; }

    public ICommand PickFileCommand { get; }

    public ICommand ExportCommand { get; }

    public ICommand UseSampleCommand { get; }

    /// <summary>Raw package JSON (pasted or read from a dropped file).</summary>
    public string InputJson
    {
        get => _inputJson;
        set
        {
            if (!Set(ref _inputJson, value ?? string.Empty))
            {
                return;
            }

            Report = null;
            Issues.Clear();
            OnPropertyChanged(nameof(HasInput), nameof(IsEmpty), nameof(CanImport));
        }
    }

    /// <summary>Where the JSON came from (file name), shown in the result header.</summary>
    public string SourceName
    {
        get => _sourceName;
        private set => Set(ref _sourceName, value);
    }

    /// <summary>Validation outcome of the current input (null = not validated yet).</summary>
    public ThemeStudioValidationReport? Report
    {
        get => _report;
        private set
        {
            if (Set(ref _report, value))
            {
                OnPropertyChanged(
                    nameof(HasReport),
                    nameof(CanImport),
                    nameof(IsValid),
                    nameof(IsInvalid),
                    nameof(ReportSummary),
                    nameof(IsEmpty));
            }
        }
    }

    public bool HasReport => Report is not null;

    public bool IsValid => Report is { IsValid: true };

    public bool IsInvalid => Report is { IsValid: false };

    public string ReportSummary => Report switch
    {
        null => "尚未校验",
        { IsValid: true } report when report.WarningCount == 0 => "校验通过：无问题",
        { IsValid: true } report => $"校验通过：{report.WarningCount} 条警告",
        _ => $"校验未通过：{Report!.ErrorCount} 个错误 / {Report.WarningCount} 条警告",
    };

    public bool HasInput => !string.IsNullOrWhiteSpace(InputJson);

    public bool IsEmpty => !HasInput && !HasReport;

    /// <summary>True while the background validation runs (the primary button shows a busy label).</summary>
    public bool IsValidating
    {
        get => _isValidating;
        private set => Set(ref _isValidating, value);
    }

    /// <summary>The drop zone highlight (bound to the DragOver state).</summary>
    public bool IsDropActive
    {
        get => _isDropActive;
        set => Set(ref _isDropActive, value);
    }

    public string StatusMessage
    {
        get => _statusMessage;
        private set => Set(ref _statusMessage, value);
    }

    /// <summary>Errors block the import button (THEME_STUDIO_SPEC §3.6).</summary>
    public bool CanImport => Report is { IsValid: true } && HasInput && !IsBusy;

    /// <summary>JSON produced by the last successful export (also asserted by the round-trip tests).</summary>
    public string? LastExportJson
    {
        get => _lastExportJson;
        private set => Set(ref _lastExportJson, value);
    }

    public string? SelectedExportThemeId
    {
        get => _selectedExportThemeId;
        set
        {
            if (Set(ref _selectedExportThemeId, value))
            {
                OnPropertyChanged(nameof(CanExport));
            }
        }
    }

    public bool CanExport => SelectedExportThemeId is not null;

    /// <summary>Compatibility note required by the spec (§3.6).</summary>
    public string CompatibilityNote => "该主题包适用于 New Manga Theme Engine v1（schema newmanga.theme/1）";

    /// <summary>File picker honesty: when no gateway is wired the UI must say so.</summary>
    public bool IsPickerAvailable => Owner.FileGateway.IsAvailable;

    public string PickerHint => Owner.FileGateway.IsAvailable
        ? "选择 .nmtheme / .json 文件"
        : "文件选择器未接线（NOT_WIRED）：可拖入文件或粘贴 JSON";

    /// <summary>
    /// Validates the current input and publishes the per-item findings. Parsing/validating a theme package
    /// is CPU-only and bounded (≤1 MiB document), so it runs inline: hopping to the thread pool here would
    /// make the surface's UI-thread callers wait on a continuation that needs the same thread.
    /// </summary>
    public Task ValidateAsync()
    {
        if (!HasInput)
        {
            StatusMessage = "没有可校验的内容：请拖入文件或粘贴主题包 JSON。";
            return Task.CompletedTask;
        }

        IsValidating = true;
        try
        {
            var report = Service.ValidateJson(InputJson, SourceName);
            Report = report;
            Issues.Clear();
            foreach (var issue in report.Issues)
            {
                Issues.Add(issue);
            }

            StatusMessage = report.IsValid
                ? "校验通过：可以导入。"
                : "校验未通过：错误项会阻止导入，请按建议修正。";
        }
        finally
        {
            IsValidating = false;
            OnPropertyChanged(nameof(CanImport), nameof(IsValidating));
        }

        return Task.CompletedTask;
    }

    /// <summary>Imports the validated input; an id clash escalates to the overwrite dialog.</summary>
    public async Task ImportAsync()
    {
        if (!HasInput)
        {
            StatusMessage = "没有可导入的内容。";
            return;
        }

        if (Report is null)
        {
            await ValidateAsync().ConfigureAwait(true);
        }

        if (Report is not { IsValid: true })
        {
            StatusMessage = "导入被阻止：请先修正校验错误。";
            return;
        }

        var result = await Service.ImportAsync(InputJson, SourceName).ConfigureAwait(true);
        if (!result.Success && result.Issues.Any(issue => issue.Code == "registry.duplicate-id"))
        {
            Owner.ShowOverwriteThemeDialog(
                result.Message,
                () => Run(() => ImportOverwriteAsync()));
            return;
        }

        StatusMessage = result.Message;
        if (result.Success)
        {
            Refresh();
            Owner.Refresh();
            Report = ThemeStudioValidationReport.From(result.Issues);
        }
        else
        {
            Issues.Clear();
            foreach (var issue in result.Issues)
            {
                Issues.Add(issue);
            }
        }
    }

    private async Task ImportOverwriteAsync()
    {
        var result = await Service.ImportAsync(InputJson, SourceName, overwrite: true).ConfigureAwait(true);
        StatusMessage = result.Message;
        if (result.Success)
        {
            Refresh();
            Owner.Refresh();
        }
        else
        {
            Issues.Clear();
            foreach (var issue in result.Issues)
            {
                Issues.Add(issue);
            }
        }
    }

    /// <summary>Reads a dropped/selected file and validates it immediately.</summary>
    public async Task ImportFileAsync(string path)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        try
        {
            var text = await File.ReadAllTextAsync(path).ConfigureAwait(true);
            InputJson = text;
            SourceName = Path.GetFileName(path);
            await ValidateAsync().ConfigureAwait(true);
            StatusMessage = "已读取文件：确认校验结果后点击“导入”。";
        }
        catch (Exception exception) when (exception is IOException or UnauthorizedAccessException or NotSupportedException)
        {
            StatusMessage = $"文件无法读取：{exception.Message}";
        }
    }

    private async Task PickFileAsync()
    {
        if (!Owner.FileGateway.IsAvailable)
        {
            StatusMessage = PickerHint;
            return;
        }

        var path = await Owner.FileGateway.PickPackagePathAsync().ConfigureAwait(true);
        if (path is not null)
        {
            await ImportFileAsync(path).ConfigureAwait(true);
        }
    }

    /// <summary>Exports the selected theme through the file gateway; keeps the JSON for evidence.</summary>
    public async Task ExportAsync()
    {
        if (SelectedExportThemeId is null)
        {
            StatusMessage = "请选择要导出的主题。";
            return;
        }

        var json = await Service.ExportAsync(SelectedExportThemeId).ConfigureAwait(true);
        if (json is null)
        {
            StatusMessage = "导出失败：主题不存在或不可读。";
            return;
        }

        LastExportJson = json;
        if (!Owner.FileGateway.IsAvailable)
        {
            StatusMessage = $"已生成 .nmtheme 内容（{json.Length} 字节）；文件选择器未接线（NOT_WIRED），可在接入后保存。";
            return;
        }

        var path = await Owner.FileGateway.PickExportPathAsync(SelectedExportThemeId + ".nmtheme").ConfigureAwait(true);
        if (path is null)
        {
            StatusMessage = "已取消导出。";
            return;
        }

        var written = await Owner.FileGateway.WriteTextAsync(path, json).ConfigureAwait(true);
        StatusMessage = written ? $"已导出到 {Path.GetFileName(path)}" : "写入目标文件失败。";
    }

    /// <summary>Accepts JSON produced by the my-themes export flow (kept for evidence + round-trip).</summary>
    internal void PublishExport(string json)
    {
        LastExportJson = json;
        StatusMessage = $"已生成 .nmtheme 内容（{json.Length} 字节）。";
    }

    private void LoadExportableSample()
    {
        var package = Service.AppliedPackage;
        InputJson = NewManga.ThemeEngine.ThemePackageJson.Write(package);
        SourceName = package.Descriptor.Id + ".nmtheme";
        StatusMessage = $"已载入当前主题「{package.Descriptor.Name}」作为往返校验样本。";
    }

    private void Clear()
    {
        InputJson = string.Empty;
        SourceName = "粘贴的主题包";
        StatusMessage = "已清空。";
    }

    /// <inheritdoc />
    public override void OnActivated() => Refresh();

    /// <summary>Refreshes the export selector from the catalog.</summary>
    public void Refresh()
    {
        ExportThemeOptions.Clear();
        foreach (var package in Service.Themes)
        {
            var option = new ThemeStudioOption(
                package.Descriptor.Id,
                package.Descriptor.Name,
                $"v{package.Descriptor.Version} · {ThemeStudioLabels.ThemeKindLabel(package.Descriptor.Kind)}",
                new RelayCommand(() => SelectedExportThemeId = package.Descriptor.Id));
            ExportThemeOptions.Add(option);
        }

        SelectedExportThemeId ??= Service.AppliedPackage.Descriptor.Id;
        foreach (var option in ExportThemeOptions)
        {
            option.IsSelected = string.Equals(option.Key, SelectedExportThemeId, StringComparison.Ordinal);
        }

        OnPropertyChanged(nameof(CanExport), nameof(CanImport), nameof(IsPickerAvailable), nameof(PickerHint));
    }
}

/// <summary>
/// ⑦ 恢复默认 (THEME_STUDIO_SPEC §3.7): double confirmation, never deletes user theme files unless the
/// user explicitly ticks "同时清除我的主题" and confirms again with the file list on screen.
/// </summary>
public sealed class ThemeStudioResetViewModel : ThemeStudioSectionViewModel
{
    private bool _clearUserThemes;
    private string _statusMessage = "恢复默认不会删除你的自定义主题文件，只会重置当前选择。";

    internal ThemeStudioResetViewModel(ThemeStudioViewModel owner)
        : base(owner, ThemeStudioSection.Reset)
    {
        ConfirmCommand = new RelayCommand(() => Owner.ShowResetDialog(this));
        RefreshCommand = new RelayCommand(Refresh);
    }

    public ObservableCollection<string> UserThemeNames { get; } = new();

    public ObservableCollection<ThemeStudioInfoRow> ImpactRows { get; } = new();

    public ICommand ConfirmCommand { get; }

    public ICommand RefreshCommand { get; }

    /// <summary>Second confirmation gate: delete user theme files as well (destructive).</summary>
    public bool ClearUserThemes
    {
        get => _clearUserThemes;
        set => Set(ref _clearUserThemes, value);
    }

    public string StatusMessage
    {
        get => _statusMessage;
        private set => Set(ref _statusMessage, value);
    }

    public bool HasUserThemes => UserThemeNames.Count > 0;

    public string ClearThemesLabel => $"同时清除我的主题（{UserThemeNames.Count} 个文件）";

    /// <summary>Performs the reset after the dialogs confirmed it (called by the surface).</summary>
    public async Task PerformResetAsync()
    {
        var result = await Service.ResetToDefaultAsync(ClearUserThemes).ConfigureAwait(true);
        StatusMessage = result.Message;
        ClearUserThemes = false;
        Refresh();
        Owner.Refresh();
    }

    /// <inheritdoc />
    public override void OnActivated() => Refresh();

    /// <summary>Rebuilds the impact list and the user-theme file list.</summary>
    public void Refresh()
    {
        var settings = Service.Settings;
        ImpactRows.Clear();
        ImpactRows.Add(new ThemeStudioInfoRow("主题", Service.CurrentTheme.Name, $"→ {NewManga.ThemeEngine.ThemeDefaults.DefaultThemeId}"));
        ImpactRows.Add(new ThemeStudioInfoRow("外观", ThemeStudioLabels.Appearance(settings.Appearance), "→ 系统跟随"));
        ImpactRows.Add(new ThemeStudioInfoRow("对比度", ThemeStudioLabels.Contrast(settings.Contrast), "→ 标准"));
        ImpactRows.Add(new ThemeStudioInfoRow("密度", ThemeStudioLabels.DensityLabel(settings.Layout.Density), "→ 舒适"));
        ImpactRows.Add(new ThemeStudioInfoRow("布局", ThemeStudioLabels.Navigation(settings.Layout.Navigation), "→ TopBand"));
        ImpactRows.Add(new ThemeStudioInfoRow("减少动效", settings.ReducedMotion ? "开" : "关", "→ 关"));

        UserThemeNames.Clear();
        foreach (var package in Service.Themes.Where(package =>
                     package.Descriptor.Kind == NewManga.ThemeEngine.ThemeKind.User))
        {
            UserThemeNames.Add($"{package.Descriptor.Name}（{package.Descriptor.Id}）");
        }

        OnPropertyChanged(nameof(HasUserThemes), nameof(ClearThemesLabel));
    }
}
