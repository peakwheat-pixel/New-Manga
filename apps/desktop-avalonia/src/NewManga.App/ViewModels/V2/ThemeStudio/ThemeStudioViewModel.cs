using System.Collections.ObjectModel;
using System.Windows.Input;
using Avalonia.Input;
using NewManga.App.Shell.V2;
using NewManga.ThemeEngine;

namespace NewManga.App.ViewModels.V2.ThemeStudio;

/// <summary>
/// The Theme Studio surface view model (THEME_STUDIO_SPEC §2/§4). It is the single state source of the
/// surface: current section, applied vs draft theme, dialog state, right-rail summary and the palette
/// scopes. Sections read and mutate it; they never keep a second copy of the draft.
///
/// <para>
/// Integration surface for V11R-INT-1: <see cref="OpenAsync"/>, <see cref="Close"/>, and the
/// <see cref="RequestClose"/> event. The shell pushes <c>ShellSurface.ThemeStudio</c> and hosts
/// <c>ThemeStudioView</c>; everything else is internal to this assembly.
/// </para>
/// </summary>
public sealed class ThemeStudioViewModel : ObservableObject, IDisposable
{
    private readonly IThemeStudioService _service;
    private readonly IThemeStudioFileGateway _fileGateway;
    private readonly List<ThemeStudioSectionItem> _sectionItems = new();
    private ThemeStudioSection _currentSection = ThemeStudioSection.Library;
    private ThemeStudioSectionItem? _selectedSection;
    private ThemeStudioPalette? _appliedPalette;
    private ThemeStudioPalette? _draftPalette;
    private ThemeStudioValidationReport? _startupIssues;
    private IReadOnlyList<ThemeStudioMigrationNotice> _migrationNotices = [];
    private string _statusMessage = "就绪";
    private string _applyStateLabel = "已同步";
    private bool _isBusy;
    private bool _isRefreshing;
    private bool _disposed;
    private ThemeStudioSectionViewModel _currentSectionView = null!;

    /// <summary>Creates the surface view model over a service facade.</summary>
    /// <param name="service">Theme Studio service (engine-backed in production, sandbox in tests).</param>
    /// <param name="fileGateway">Optional picker seam; null keeps drag-and-drop/paste only.</param>
    public ThemeStudioViewModel(IThemeStudioService service, IThemeStudioFileGateway? fileGateway = null)
    {
        _service = service ?? throw new ArgumentNullException(nameof(service));
        _fileGateway = fileGateway ?? NullThemeStudioFileGateway.Instance;

        Library = new ThemeStudioLibraryViewModel(this);
        Preview = new ThemeStudioPreviewViewModel(this);
        MyThemes = new ThemeStudioMyThemesViewModel(this);
        Editor = new ThemeStudioEditorViewModel(this);
        Appearance = new ThemeStudioAppearanceViewModel(this);
        ImportExport = new ThemeStudioImportExportViewModel(this);
        Reset = new ThemeStudioResetViewModel(this);

        Sections = new ObservableCollection<ThemeStudioSectionItem>(_sectionItems);
        foreach (var section in ThemeStudioLabels.AllSections)
        {
            var item = new ThemeStudioSectionItem(section, new RelayCommand(() => SelectSection(section)));
            _sectionItems.Add(item);
            Sections.Add(item);
        }

        ApplyCommand = new RelayCommand(() => _ = ApplyDraftAsync(), () => !IsBusy);
        CancelCommand = new RelayCommand(() => _ = CancelAsync(), () => !IsBusy);
        BackCommand = new RelayCommand(Close);
        ToggleHighContrastCommand = new RelayCommand(() => Appearance.SetHighContrast(!Appearance.HighContrast));
        ToggleReducedMotionCommand = new RelayCommand(() => Appearance.SetReducedMotion(!Appearance.ReducedMotion));
        ToggleFollowSystemAccentCommand = new RelayCommand(() => Appearance.SetFollowSystemAccent(!Appearance.FollowSystemAccent));
        RetryInitializationCommand = new RelayCommand(() => _ = EnsureInitializedAsync());

        Dialog.CancelCommand = new RelayCommand(CancelDialog);

        _service.Changed += OnServiceChanged;
        _currentSectionView = Library;
        _selectedSection = _sectionItems[0];
        _selectedSection.IsSelected = true;
        Refresh();
    }

    /// <summary>Raised when the surface should close (shell pops <c>ShellSurface.ThemeStudio</c>).</summary>
    public event EventHandler? RequestClose;

    /// <summary>Raised when the surface wants the theme-library search box focused (Ctrl+F).</summary>
    public event EventHandler? FocusSearchRequested;

    /// <summary>The service facade (sections use it; the view binds a few summary values from it).</summary>
    public IThemeStudioService Service => _service;

    /// <summary>The file-picker seam (import/export section).</summary>
    internal IThemeStudioFileGateway FileGateway => _fileGateway;

    // ------------------------------------------------------------------ sections

    /// <summary>Left-rail items, in the frozen order.</summary>
    public ObservableCollection<ThemeStudioSectionItem> Sections { get; }

    public ThemeStudioSection CurrentSection => _currentSection;

    /// <summary>The active section view model (the main area data context).</summary>
    public ThemeStudioSectionViewModel CurrentSectionView => _currentSectionView;

    public ThemeStudioLibraryViewModel Library { get; }

    public ThemeStudioPreviewViewModel Preview { get; }

    public ThemeStudioMyThemesViewModel MyThemes { get; }

    public ThemeStudioEditorViewModel Editor { get; }

    public ThemeStudioAppearanceViewModel Appearance { get; }

    public ThemeStudioImportExportViewModel ImportExport { get; }

    public ThemeStudioResetViewModel Reset { get; }

    /// <summary>True for the section currently hosted in the main area (bound as IsVisible).</summary>
    public bool ShowLibrary => CurrentSection == ThemeStudioSection.Library;

    public bool ShowPreview => CurrentSection == ThemeStudioSection.Preview;

    public bool ShowMyThemes => CurrentSection == ThemeStudioSection.MyThemes;

    public bool ShowEditor => CurrentSection == ThemeStudioSection.Editor;

    public bool ShowAppearance => CurrentSection == ThemeStudioSection.Appearance;

    public bool ShowImportExport => CurrentSection == ThemeStudioSection.ImportExport;

    public bool ShowReset => CurrentSection == ThemeStudioSection.Reset;

    /// <summary>Header title of the main area.</summary>
    public string SectionTitle => ThemeStudioLabels.Section(CurrentSection);

    /// <summary>Header subtitle of the main area (or the dirty hint when a draft exists).</summary>
    public string SectionSubtitle => HasDraft
        ? $"{ThemeStudioLabels.SectionSubtitle(CurrentSection)} · 未提交改动（实时预览中）"
        : ThemeStudioLabels.SectionSubtitle(CurrentSection);

    // ------------------------------------------------------------------ right rail

    /// <summary>Applied theme summary shown in the right rail.</summary>
    public ThemeDescriptor CurrentTheme => _service.CurrentTheme;

    public string CurrentThemeName => CurrentTheme.Name;

    public string CurrentThemeAuthor => string.IsNullOrWhiteSpace(CurrentTheme.Author) ? "未知作者" : CurrentTheme.Author;

    public string CurrentThemeVersion => $"v{CurrentTheme.Version}";

    public string CurrentThemeSupport => ThemeStudioLabels.AppearanceSupport(
        CurrentTheme.SupportsLight,
        CurrentTheme.SupportsDark);

    public string CurrentThemeTags => CurrentTheme.Tags.Count == 0 ? "无标签" : string.Join(" · ", CurrentTheme.Tags);

    public string CurrentThemeKind => ThemeStudioLabels.ThemeKindLabel(CurrentTheme.Kind);

    /// <summary>"当前主题 = X / 会话主题 = Y" anti-confusion line (spec §3.2).</summary>
    public string SessionThemeLabel
    {
        get
        {
            var applied = _service.CurrentTheme.Name;
            var draft = _service.DraftPackage?.Descriptor.Name;
            return draft is null || string.Equals(draft, applied, StringComparison.Ordinal)
                ? $"会话主题 = {applied}"
                : $"会话主题 = {draft}（未应用）";
        }
    }

    /// <summary>True when there is an unapplied change (THEME_STUDIO_SPEC §4 HasDraft).</summary>
    public bool HasDraft => _service.HasDraft;

    public string DirtyLabel => HasDraft ? "未提交改动" : "无未提交改动";

    public string ApplyButtonLabel => HasDraft ? "应用修改" : "应用";

    public string ApplyStateLabel
    {
        get => _applyStateLabel;
        private set => Set(ref _applyStateLabel, value);
    }

    /// <summary>Rail headline status (never fakes a durable apply).</summary>
    public string StatusMessage
    {
        get => _statusMessage;
        private set => Set(ref _statusMessage, value);
    }

    public bool IsBusy
    {
        get => _isBusy;
        private set
        {
            if (Set(ref _isBusy, value))
            {
                OnPropertyChanged(nameof(ApplyButtonLabel));
            }
        }
    }

    /// <summary>Scoped palette of the applied theme (installed on the surface root).</summary>
    public ThemeStudioPalette? AppliedPalette
    {
        get => _appliedPalette;
        private set => Set(ref _appliedPalette, value);
    }

    /// <summary>
    /// Scoped palette of an <em>unsaved</em> editor draft (mounted on the surface root). Null while the
    /// engine's own preview session already renders the selected installed theme application-wide.
    /// </summary>
    public ThemeStudioPalette? DraftPalette
    {
        get => _draftPalette;
        private set => Set(ref _draftPalette, value);
    }

    /// <summary>Palette request used by the library/my-themes card mini-views.</summary>
    public ThemeStudioPaletteRequest CardPaletteRequest =>
        ThemeStudioPaletteRequest.FromSettings(_service.Settings);

    /// <summary>Compact WCAG rows of the right rail (body/secondary/focus/worst status).</summary>
    public ObservableCollection<ThemeStudioContrastRow> RailAuditRows { get; } = new();

    public string RailAuditSummary { get; private set; } = string.Empty;

    public bool RailAuditPassing { get; private set; } = true;

    /// <summary>Migration decisions disclosed by the engine at load time (retirement plan §2.1).</summary>
    public ObservableCollection<ThemeStudioMigrationNotice> MigrationNotices { get; } = new();

    public bool HasMigrationNotices => MigrationNotices.Count > 0;

    /// <summary>Catalog-level problems (quarantined theme files, broken built-ins).</summary>
    public string StartupIssueSummary { get; private set; } = string.Empty;

    public bool HasStartupIssues { get; private set; }

    // ------------------------------------------------------------------ capabilities (honesty)

    public ThemeStudioCapabilities Capabilities => _service.Capabilities;

    public string SourceLabel => Capabilities.SourceLabel;

    public bool IsSandbox => Capabilities.IsSandbox;

    public string CapabilityNote => Capabilities.Note ?? (IsSandbox
        ? "预览（未持久化）：当前为 STUB 沙箱，应用不会写入磁盘。"
        : "已连接 Theme Engine：应用会持久化到 theme-settings.json");

    public bool HasCapabilityNote => !string.IsNullOrEmpty(Capabilities.Note);

    /// <summary>True only when "应用" really is durable app-wide (otherwise the rail says 预览/未持久化).</summary>
    public bool ShowsDurableApply => Capabilities.ShowsDurableApplyLabel;

    public string PersistenceLabel => ShowsDurableApply ? "持久化：开" : "持久化：关（预览）";

    // ------------------------------------------------------------------ dialog & commands

    /// <summary>The modal dialog currently shown (unsaved changes / reset / save-as / delete …).</summary>
    public ThemeStudioDialogViewModel Dialog { get; } = new();

    public ICommand ApplyCommand { get; }

    public ICommand CancelCommand { get; }

    public ICommand BackCommand { get; }

    public ICommand ToggleHighContrastCommand { get; }

    public ICommand ToggleReducedMotionCommand { get; }

    public ICommand ToggleFollowSystemAccentCommand { get; }

    public ICommand RetryInitializationCommand { get; }

    // ------------------------------------------------------------------ lifecycle / navigation

    /// <summary>Loads the service state once and opens the requested section (shell entry point).</summary>
    public async Task OpenAsync(ThemeStudioSection section = ThemeStudioSection.Library, CancellationToken ct = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        await EnsureInitializedAsync(ct).ConfigureAwait(true);
        _service.BeginPreview();
        SelectSection(section);
    }

    /// <summary>Initialises the service (idempotent) and refreshes the surface.</summary>
    public async Task EnsureInitializedAsync(CancellationToken ct = default)
    {
        if (_initialized)
        {
            return;
        }

        await _service.InitializeAsync(ct).ConfigureAwait(true);
        _initialized = true;
        Refresh();
    }

    /// <summary>Switches the main area to one of the seven sections (draft survives the switch).</summary>
    public void SelectSection(ThemeStudioSection section)
    {
        if (_disposed || (CurrentSection == section && _currentSectionView.Section == section && _initialized))
        {
            CurrentSectionView.OnActivated();
            return;
        }

        _currentSectionView.OnDeactivated();
        _currentSection = section;
        _currentSectionView = section switch
        {
            ThemeStudioSection.Library => Library,
            ThemeStudioSection.Preview => Preview,
            ThemeStudioSection.MyThemes => MyThemes,
            ThemeStudioSection.Editor => Editor,
            ThemeStudioSection.Appearance => Appearance,
            ThemeStudioSection.ImportExport => ImportExport,
            _ => Reset,
        };

        foreach (var item in _sectionItems)
        {
            item.IsSelected = item.Section == section;
        }

        _selectedSection = _sectionItems.FirstOrDefault(item => item.Section == section);
        _currentSectionView.OnActivated();
        OnPropertyChanged(
            nameof(CurrentSection),
            nameof(CurrentSectionView),
            nameof(SectionTitle),
            nameof(SectionSubtitle),
            nameof(ShowLibrary),
            nameof(ShowPreview),
            nameof(ShowMyThemes),
            nameof(ShowEditor),
            nameof(ShowAppearance),
            nameof(ShowImportExport),
            nameof(ShowReset));
        UpdateDirtyMarkers();
    }

    /// <summary>Arrow-key section navigation (rail items call this through the key router).</summary>
    public void SelectNextSection(int delta)
    {
        var index = (int)CurrentSection;
        var next = Math.Clamp(index + delta, 0, ThemeStudioLabels.AllSections.Count - 1);
        SelectSection(ThemeStudioLabels.AllSections[next]);
    }

    /// <summary>Ctrl+F: focus the theme-library search field.</summary>
    public void FocusSearch()
    {
        if (CurrentSection != ThemeStudioSection.Library)
        {
            SelectSection(ThemeStudioSection.Library);
        }

        FocusSearchRequested?.Invoke(this, EventArgs.Empty);
    }

    /// <summary>Esc ladder (THEME_STUDIO_SPEC §5): dialog → unsaved-changes modal → leave surface.</summary>
    public bool HandleEscape()
    {
        if (Dialog.IsOpen)
        {
            CancelDialog();
            return true;
        }

        if (HasDraft)
        {
            ShowUnsavedChangesDialog();
            return true;
        }

        RaiseClose();
        return true;
    }

    /// <summary>
    /// Surface-level key router. Returns true when the key was consumed, so the shell's key map never
    /// double-handles it (the shell owns the global registration; this owns the surface-local ladder).
    /// </summary>
    public bool HandleKey(Key key, KeyModifiers modifiers)
    {
        var control = modifiers.HasFlag(KeyModifiers.Control);
        if (control && key == Key.Enter)
        {
            _ = ApplyDraftAsync();
            return true;
        }

        if (control && key == Key.F)
        {
            FocusSearch();
            return true;
        }

        if (key == Key.Escape && modifiers == KeyModifiers.None)
        {
            return HandleEscape();
        }

        if (modifiers == KeyModifiers.None)
        {
            switch (key)
            {
                case Key.Up:
                case Key.Left:
                    SelectNextSection(-1);
                    return true;
                case Key.Down:
                case Key.Right:
                    SelectNextSection(1);
                    return true;
            }
        }

        return false;
    }

    /// <summary>Closes the surface; a dirty draft first goes through the three-exit dialog.</summary>
    public void Close()
    {
        if (Dialog.IsOpen)
        {
            CancelDialog();
            return;
        }

        if (HasDraft)
        {
            ShowUnsavedChangesDialog();
            return;
        }

        RaiseClose();
    }

    // ------------------------------------------------------------------ draft mutation (used by sections)

    /// <summary>Puts an edited package into the live preview session.</summary>
    public void ApplyDraftPackage(ThemePackage package)
    {
        ArgumentNullException.ThrowIfNull(package);
        _service.PreviewDocument(package);
        NotifyDraftChanged();
    }

    /// <summary>Recomputes the rail + palette scopes after a draft/settings change (no list rebuild).</summary>
    public void NotifyDraftChanged()
    {
        RefreshPalettes();
        UpdateRail();
        UpdateDirtyMarkers();
        OnPropertyChanged(nameof(SectionSubtitle));
        Preview.RebuildPalette();
    }

    /// <summary>Previews an installed theme (library card click / Enter / double click).</summary>
    public void PreviewThemeById(string themeId)
    {
        if (string.IsNullOrWhiteSpace(themeId))
        {
            return;
        }

        _service.BeginPreview();
        _service.PreviewTheme(themeId);
        NotifyDraftChanged();
        StatusMessage = $"正在预览「{_service.DraftPackage?.Descriptor.Name ?? themeId}」（未应用）";
    }

    /// <summary>Applies a theme id directly (card "应用" / double click apply).</summary>
    public async Task<ThemeStudioApplyResult> ApplyThemeAsync(string themeId, bool commitPreview = true)
    {
        IsBusy = true;
        try
        {
            _service.BeginPreview();
            _service.PreviewTheme(themeId);
            var result = await _service.ApplyAsync().ConfigureAwait(true);
            ApplyStateLabel = result.StatusLabel;
            StatusMessage = result.Success
                ? $"{result.StatusLabel}：{result.AppliedThemeId}"
                : "应用失败：已保留当前主题，请重试或取消。";
            if (!result.Success)
            {
                foreach (var issue in result.Issues)
                {
                    StatusMessage += $" · {issue.Message}";
                }
            }

            Refresh();
            return result;
        }
        finally
        {
            IsBusy = false;
            OnPropertyChanged(nameof(ApplyButtonLabel));
        }
    }

    /// <summary>The right-rail "应用" action: commits the draft (engine commit + persistence).</summary>
    public async Task ApplyDraftAsync()
    {
        if (IsBusy)
        {
            return;
        }

        IsBusy = true;
        try
        {
            var result = await _service.ApplyAsync().ConfigureAwait(true);
            ApplyStateLabel = result.StatusLabel;
            StatusMessage = result.Success
                ? $"{result.StatusLabel}：{result.AppliedThemeId}"
                : "应用失败：草稿与预览会话已保留，可重试或取消。";
            if (!result.Success)
            {
                foreach (var issue in result.Issues)
                {
                    StatusMessage += $" · {issue.Message}";
                }
            }

            Refresh();
        }
        finally
        {
            IsBusy = false;
            OnPropertyChanged(nameof(ApplyButtonLabel));
        }
    }

    /// <summary>The right-rail "取消" action: full rollback to the applied state.</summary>
    public async Task CancelAsync()
    {
        IsBusy = true;
        try
        {
            await _service.CancelPreviewAsync().ConfigureAwait(true);
            _service.BeginPreview();
            ApplyStateLabel = "已取消（回滚到已应用主题）";
            StatusMessage = "已取消：主题、外观、密度与布局回到进入前的状态。";
            Refresh();
        }
        finally
        {
            IsBusy = false;
            OnPropertyChanged(nameof(ApplyButtonLabel));
        }
    }

    /// <summary>Settings setters (appearance section + rail toggles).</summary>
    public Task SetAppearanceAsync(AppearanceMode mode) => RunServiceAsync(() => _service.SetAppearanceAsync(mode));

    public Task SetContrastAsync(bool highContrast) =>
        RunServiceAsync(() => _service.SetContrastAsync(highContrast ? ContrastMode.High : ContrastMode.Standard));

    public Task SetDensityAsync(Density density) => RunServiceAsync(() => _service.SetDensityAsync(density));

    public Task SetReducedMotionAsync(bool enabled) => RunServiceAsync(() => _service.SetReducedMotionAsync(enabled));

    public Task SetFollowSystemAccentAsync(bool enabled) =>
        RunServiceAsync(() => _service.SetFollowSystemAccentAsync(enabled));

    /// <summary>Favorites (library cards + my themes).</summary>
    public async Task ToggleFavoriteAsync(ThemeStudioCardViewModel card)
    {
        ArgumentNullException.ThrowIfNull(card);
        await ToggleFavoriteByIdAsync(card.Id).ConfigureAwait(true);
        card.IsFavorite = _service.IsFavorite(card.Id);
    }

    public async Task ToggleFavoriteByIdAsync(string themeId)
    {
        var result = await _service.ToggleFavoriteAsync(themeId).ConfigureAwait(true);
        ReportStatus(result.Message);
        Refresh();
    }

    /// <summary>Exports a theme through the file gateway (or reports NOT_WIRED and keeps the JSON).</summary>
    public async Task ExportThemeAsync(string themeId)
    {
        var json = await _service.ExportAsync(themeId).ConfigureAwait(true);
        if (json is null)
        {
            ReportError("导出失败：主题不可读。");
            return;
        }

        ImportExport.PublishExport(json);
        if (!_fileGateway.IsAvailable)
        {
            ReportStatus($"已生成 .nmtheme 内容（{json.Length} 字节）；文件选择器未接线（NOT_WIRED）。");
            return;
        }

        var path = await _fileGateway.PickExportPathAsync(themeId + ThemeDefaults.ThemeFileExtension).ConfigureAwait(true);
        if (path is null)
        {
            ReportStatus("已取消导出。");
            return;
        }

        var written = await _fileGateway.WriteTextAsync(path, json).ConfigureAwait(true);
        ReportStatus(written ? $"已导出「{themeId}」" : "写入目标文件失败。");
    }

    /// <summary>Status line helper (sections report through here).</summary>
    public void ReportStatus(string? message)
    {
        if (!string.IsNullOrWhiteSpace(message))
        {
            StatusMessage = message;
        }
    }

    /// <summary>Error line helper (never throws at the UI).</summary>
    public void ReportError(string message)
    {
        StatusMessage = string.IsNullOrWhiteSpace(message) ? "操作失败" : message;
    }

    // ------------------------------------------------------------------ dialogs

    /// <summary>Three-exit modal when leaving with an unapplied draft (spec §3.4).</summary>
    public void ShowUnsavedChangesDialog()
    {
        var continueEditing = new ThemeStudioDialogAction(
            "继续编辑",
            IsPrimary: true,
            IsDanger: false,
            new RelayCommand(CancelDialog));
        var discard = new ThemeStudioDialogAction(
            "放弃改动并退出",
            IsPrimary: false,
            IsDanger: true,
            new RelayCommand(() =>
            {
                CloseDialog();
                _ = DiscardAndCloseAsync();
            }));
        var apply = new ThemeStudioDialogAction(
            "应用并退出",
            IsPrimary: false,
            IsDanger: false,
            new RelayCommand(() =>
            {
                CloseDialog();
                _ = ApplyAndCloseAsync();
            }));

        OpenDialog(
            ThemeStudioDialogKind.UnsavedChanges,
            "有未提交的改动",
            "当前主题/外观的改动仍在实时预览中，尚未应用。选择如何处理这些改动：",
            "应用会写入设置并全局生效；放弃会完整回滚到进入前的主题。",
            [continueEditing, discard, apply]);
    }

    /// <summary>Delete confirmation for a user theme (built-ins are rejected before this point).</summary>
    public void ShowDeleteThemeDialog(ThemeStudioCardViewModel card, Func<Task> confirm)
    {
        ArgumentNullException.ThrowIfNull(card);
        OpenDialog(
            ThemeStudioDialogKind.DeleteTheme,
            "删除自定义主题",
            $"将删除主题文件「{card.Name}」（{card.Id}）。此操作不可撤销。",
            "内置主题不受影响；删除当前正在使用的主题会自动回退到默认主题。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("删除", IsPrimary: false, IsDanger: true, new RelayCommand(() =>
                {
                    CloseDialog();
                    _ = RunConfirmedAsync(confirm);
                })),
            ]);
    }

    /// <summary>Duplicate dialog (name input; the copy always gets a fresh user id).</summary>
    public void ShowDuplicateThemeDialog(ThemeStudioCardViewModel card, Func<string, Task> confirm)
    {
        ArgumentNullException.ThrowIfNull(card);
        OpenDialog(
            ThemeStudioDialogKind.SaveAsTheme,
            "复制为主题",
            "复制当前主题为一个新的用户主题（颜色/字体/圆角/材质/阴影/动效全部保留）。",
            "内置主题不可覆盖，复制会生成新的用户主题文件。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("复制", IsPrimary: false, IsDanger: false, new RelayCommand(() =>
                {
                    var name = Dialog.NameInput;
                    CloseDialog();
                    _ = RunConfirmedAsync(() => confirm(string.IsNullOrWhiteSpace(name) ? card.Name + " 副本" : name));
                })),
            ],
            name: card.Name + " 副本",
            author: card.Package.Descriptor.Author,
            tags: string.Join(", ", card.Package.Descriptor.Tags));
    }

    /// <summary>"从当前主题另存为" dialog (name/author/tags → user theme file).</summary>
    public void ShowSaveAsDialog()
    {
        var descriptor = _service.DraftPackage?.Descriptor ?? _service.AppliedPackage.Descriptor;
        OpenDialog(
            ThemeStudioDialogKind.SaveAsTheme,
            "从当前主题另存为",
            "把当前编辑中的草稿保存为一个用户主题文件（%APPDATA%/NewManga/themes）。",
            "保存不会自动应用；应用仍需要在右栏点击“应用”。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("保存", IsPrimary: false, IsDanger: false, new RelayCommand(() =>
                {
                    var name = Dialog.NameInput;
                    var author = Dialog.AuthorInput;
                    var tags = Dialog.TagsInput;
                    CloseDialog();
                    _ = RunConfirmedAsync(() => SaveDraftAsThemeAsync(name, author, tags));
                })),
            ],
            name: descriptor.Name,
            author: descriptor.Author,
            tags: string.Join(", ", descriptor.Tags));
    }

    /// <summary>Import overwrite confirmation (id clash, spec §3.6).</summary>
    public void ShowOverwriteThemeDialog(string message, Action confirm)
    {
        OpenDialog(
            ThemeStudioDialogKind.OverwriteTheme,
            "主题 ID 已存在",
            message,
            "覆盖会替换该用户的主题文件；取消可改名后重新导入。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("覆盖导入", IsPrimary: false, IsDanger: true, new RelayCommand(() =>
                {
                    CloseDialog();
                    confirm();
                })),
            ]);
    }

    /// <summary>Reset flow: step 1 always, step 2 only when the user opted into deleting theme files.</summary>
    public void ShowResetDialog(ThemeStudioResetViewModel reset)
    {
        ArgumentNullException.ThrowIfNull(reset);
        var clearThemes = reset.ClearUserThemes;
        OpenDialog(
            ThemeStudioDialogKind.ResetConfirm,
            "恢复出厂默认",
            "将把主题、外观、对比度、密度和布局重置为出厂默认。" +
            (clearThemes
                ? $"同时会删除 {reset.UserThemeNames.Count} 个用户主题文件（不可撤销）。"
                : "不会删除任何用户主题文件，只重置当前选择。"),
            clearThemes
                ? "第二步还会要求确认删除文件清单。"
                : "恢复后应用会重新读取默认主题；用户主题包仍保留在磁盘上。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("恢复默认", IsPrimary: false, IsDanger: clearThemes, new RelayCommand(() =>
                {
                    CloseDialog();
                    if (clearThemes)
                    {
                        ShowResetClearThemesDialog(reset);
                    }
                    else
                    {
                        _ = RunConfirmedAsync(reset.PerformResetAsync);
                    }
                })),
            ]);
    }

    private void ShowResetClearThemesDialog(ThemeStudioResetViewModel reset)
    {
        var files = reset.UserThemeNames.Count == 0 ? "（没有用户主题文件）" : string.Join("、", reset.UserThemeNames);
        OpenDialog(
            ThemeStudioDialogKind.ResetClearThemesConfirm,
            "确认删除用户主题文件",
            $"即将删除以下 {reset.UserThemeNames.Count} 个文件：{files}",
            "这一步不可撤销。若只想重置选择而不删除文件，请取消并关闭“同时清除我的主题”。",
            [
                new ThemeStudioDialogAction("取消", IsPrimary: true, IsDanger: false, new RelayCommand(CancelDialog)),
                new ThemeStudioDialogAction("确认删除并恢复", IsPrimary: false, IsDanger: true, new RelayCommand(() =>
                {
                    CloseDialog();
                    _ = RunConfirmedAsync(reset.PerformResetAsync);
                })),
            ]);
    }

    // ------------------------------------------------------------------ refresh

    private bool _initialized;

    /// <summary>Rebuilds every derived value from the service (catalog, applied state, rail, dirty flags).</summary>
    public void Refresh()
    {
        if (_disposed)
        {
            return;
        }

        if (_isRefreshing)
        {
            return;
        }

        _isRefreshing = true;
        try
        {
            RefreshPalettes();
            UpdateRail();

            Library.Refresh();
            MyThemes.Refresh();
            Editor.Refresh();
            Appearance.Refresh();
            ImportExport.Refresh();
            Reset.Refresh();
            if (CurrentSection == ThemeStudioSection.Preview)
            {
                Preview.RebuildPalette();
            }

            UpdateDirtyMarkers();
            OnPropertyChanged(
                nameof(CurrentTheme),
                nameof(CurrentThemeName),
                nameof(CurrentThemeAuthor),
                nameof(CurrentThemeVersion),
                nameof(CurrentThemeSupport),
                nameof(CurrentThemeTags),
                nameof(CurrentThemeKind),
                nameof(Capabilities),
                nameof(SourceLabel),
                nameof(IsSandbox),
                nameof(CapabilityNote),
                nameof(HasCapabilityNote),
                nameof(ShowsDurableApply),
                nameof(PersistenceLabel),
                nameof(SectionTitle),
                nameof(SectionSubtitle));
        }
        finally
        {
            _isRefreshing = false;
        }
    }

    private void RefreshPalettes()
    {
        AppliedPalette = _service.GetAppliedPalette();
        DraftPalette = _service.GetDraftPalette();
        OnPropertyChanged(nameof(CardPaletteRequest), nameof(SessionThemeLabel));
    }

    private void UpdateRail()
    {
        OnPropertyChanged(
            nameof(CurrentTheme),
            nameof(CurrentThemeName),
            nameof(CurrentThemeAuthor),
            nameof(CurrentThemeVersion),
            nameof(CurrentThemeSupport),
            nameof(CurrentThemeTags),
            nameof(CurrentThemeKind),
            nameof(SessionThemeLabel),
            nameof(Capabilities),
            nameof(SourceLabel),
            nameof(IsSandbox),
            nameof(CapabilityNote),
            nameof(HasCapabilityNote),
            nameof(ShowsDurableApply),
            nameof(PersistenceLabel));

        _startupIssues = _service.StartupIssues;
        HasStartupIssues = _startupIssues.ErrorCount > 0 || _startupIssues.WarningCount > 0;
        StartupIssueSummary = HasStartupIssues
            ? $"主题目录诊断：{_startupIssues.ErrorCount} 个错误 / {_startupIssues.WarningCount} 条警告（非法主题包已隔离，未影响启动）"
            : string.Empty;

        _migrationNotices = _service.MigrationNotices;
        MigrationNotices.Clear();
        foreach (var notice in _migrationNotices)
        {
            MigrationNotices.Add(notice);
        }

        var package = _service.DraftPackage ?? _service.AppliedPackage;
        var variant = ResolveVariant();
        var report = _service.Audit(package, variant);
        RailAuditRows.Clear();
        foreach (var row in PickRailRows(report))
        {
            RailAuditRows.Add(row);
        }

        RailAuditSummary = report.Summary;
        RailAuditPassing = report.IsPassing;
        OnPropertyChanged(
            nameof(RailAuditSummary),
            nameof(RailAuditPassing),
            nameof(HasMigrationNotices),
            nameof(HasStartupIssues),
            nameof(StartupIssueSummary),
            nameof(HasDraft),
            nameof(DirtyLabel),
            nameof(ApplyButtonLabel));
    }

    private PaletteVariant ResolveVariant() => _service.Settings.Appearance switch
    {
        AppearanceMode.Light => PaletteVariant.Light,
        AppearanceMode.Dark => PaletteVariant.Dark,
        _ => PaletteVariant.Dark,
    };

    private static IEnumerable<ThemeStudioContrastRow> PickRailRows(ThemeStudioContrastReport report)
    {
        var wanted = new List<ThemeStudioContrastRow>();
        foreach (var row in report.Rows)
        {
            if (row.ForegroundKey == NewManga.DesignSystem.NmKeys.Color.Text.Primary &&
                row.BackgroundKey == NewManga.DesignSystem.NmKeys.Color.Bg.Panel)
            {
                wanted.Add(row);
            }
            else if (row.ForegroundKey == NewManga.DesignSystem.NmKeys.Color.Text.Secondary &&
                     row.BackgroundKey == NewManga.DesignSystem.NmKeys.Color.Bg.Panel)
            {
                wanted.Add(row);
            }
            else if (row.ForegroundKey == NewManga.DesignSystem.NmKeys.Color.Accent.Base)
            {
                wanted.Add(row);
            }
        }

        var worstStatus = report.Rows
            .Where(row => row.ForegroundKey.StartsWith("Nm.Color.Status.", StringComparison.Ordinal))
            .OrderBy(row => row.Ratio)
            .FirstOrDefault();
        if (worstStatus is not null)
        {
            wanted.Add(worstStatus);
        }

        return wanted;
    }

    private void UpdateDirtyMarkers()
    {
        var dirty = HasDraft;
        foreach (var item in _sectionItems)
        {
            item.IsDirty = item.Section switch
            {
                ThemeStudioSection.Editor => dirty,
                ThemeStudioSection.Preview => dirty,
                ThemeStudioSection.Library =>
                    _service.DraftPackage is { } draft &&
                    !string.Equals(draft.Descriptor.Id, _service.CurrentTheme.Id, StringComparison.Ordinal),
                _ => false,
            };
        }

        OnPropertyChanged(nameof(HasDraft), nameof(DirtyLabel), nameof(ApplyButtonLabel));
    }

    // ------------------------------------------------------------------ helpers

    private async Task RunServiceAsync(Func<Task> action)
    {
        IsBusy = true;
        try
        {
            await action().ConfigureAwait(true);
            Refresh();
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            ReportError(exception.Message);
        }
        finally
        {
            IsBusy = false;
            OnPropertyChanged(nameof(ApplyButtonLabel));
        }
    }

    private async Task SaveDraftAsThemeAsync(string name, string author, string tags)
    {
        var tagList = tags.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
        var result = await _service.SaveDraftAsUserThemeAsync(name, author, tagList).ConfigureAwait(true);
        ReportStatus(result.Message);
        Refresh();
        SelectSection(ThemeStudioSection.MyThemes);
    }

    private async Task DiscardAndCloseAsync()
    {
        await _service.CancelPreviewAsync().ConfigureAwait(true);
        Refresh();
        RaiseClose();
    }

    private async Task ApplyAndCloseAsync()
    {
        await ApplyDraftAsync().ConfigureAwait(true);
        if (!HasDraft)
        {
            RaiseClose();
        }
    }

    private async Task RunConfirmedAsync(Func<Task> confirm)
    {
        try
        {
            await confirm().ConfigureAwait(true);
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            ReportError(exception.Message);
        }
        finally
        {
            Refresh();
        }
    }

    private void OpenDialog(
        ThemeStudioDialogKind kind,
        string title,
        string message,
        string? footnote,
        IReadOnlyList<ThemeStudioDialogAction> actions,
        string? name = null,
        string? author = null,
        string? tags = null,
        string? checkboxLabel = null)
    {
        Dialog.Configure(kind, title, message, footnote, actions, name, author, tags, checkboxLabel);
        OnPropertyChanged(nameof(Dialog));
    }

    private void CancelDialog() => CloseDialog();

    private void CloseDialog()
    {
        Dialog.Close();
        OnPropertyChanged(nameof(Dialog));
    }

    private void RaiseClose()
    {
        if (Dialog.IsOpen)
        {
            CloseDialog();
        }

        RequestClose?.Invoke(this, EventArgs.Empty);
    }

    private void OnServiceChanged(object? sender, EventArgs e)
    {
        if (_disposed)
        {
            return;
        }

        Refresh();
    }

    /// <inheritdoc />
    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        _service.Changed -= OnServiceChanged;
        _service.Dispose();
    }
}
