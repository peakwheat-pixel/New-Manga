using NewManga.App.Shell.V2;
using Avalonia.Controls;
using Avalonia.Data;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Markup.Xaml;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.ViewModels.V2.Studio;
using NewManga.App.Views.V2.Studio.Controls;

namespace NewManga.App.Shell.V2.Studio;

/// <summary>
/// V11R-B-3: the Studio workspace entry point the V2 shell will host (integration wiring is the Lead's
/// V11R-INT-1 step). It exposes a <see cref="Controls.Control"/>-shaped content and a small adapter
/// surface (<see cref="LoadAndRenderAsync"/>, <see cref="Activate"/>, <see cref="Deactivate"/>) instead
/// of implementing <c>IWorkspaceView</c>, because that interface is owned by the shell task and is not
/// in this branch yet. The view model instance is created once per view and never rebuilt, so Page ⇄
/// Batch keeps selection, zoom/pan, filters and inspector tab (AC2).
/// </summary>
public partial class StudioWorkspaceView : UserControl, IWorkspaceView
{
    private readonly StudioWorkspaceViewModel _viewModel;
    private readonly StudioPageWorkspace _pageWorkspace;
    private readonly Grid _root;
    private readonly Button _pageModeButton;
    private readonly Button _batchModeButton;
    private readonly TextBlock _breadcrumb;
    private readonly TextBlock _scopeText;
    private readonly TextBlock _modeText;
    private readonly StudioBatchWorkspace _batchWorkspace;
    private readonly StudioToolsOverlay _tools;


    /// <summary>Design-time / XAML-loading constructor: no Host, so the view renders its empty state.</summary>
    public StudioWorkspaceView()
        : this(new StudioWorkspaceViewModel(NullHostController.Instance))
    {
    }

    public StudioWorkspaceView(StudioWorkspaceViewModel viewModel)
    {
        InitializeComponent();

        // Temporary Nm.* token shim (dies automatically when NewManga.DesignSystem merges).
        

        _viewModel = viewModel;
        _tools = new StudioToolsOverlay(viewModel);
        DataContext = viewModel;
        _root = this.FindControl<Grid>("RootGrid")!;

        // ---------------------------------------------------------------- area head (36px)
        var head = StudioUi.Box("studio-head");
        head.Height = 36;
        var headRow = StudioUi.Row(12);

        (_pageModeButton, _batchModeButton) = BuildModeSwitch(headRow);
        _breadcrumb = new TextBlock { Classes = { "label", "muted" } };
        _breadcrumb.Bind(TextBlock.TextProperty, new Binding("Page.BreadcrumbText"));
        headRow.Children.Add(_breadcrumb);

        var scopeChip = StudioUi.Box("studio-chip");
        _scopeText = new TextBlock { Classes = { "meta" } };
        _scopeText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioSelection.SelectionSummary))
        {
            Source = _viewModel.Selection,
        });
        scopeChip.Child = _scopeText;
        ToolTip.SetTip(scopeChip, "作用域：所有批量动作都带该后缀（FUSION_SPEC §2.3）");
        headRow.Children.Add(scopeChip);

        _modeText = new TextBlock { Classes = { "meta", "muted" } };
        _modeText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioWorkspaceViewModel.HeaderModeText)));
        headRow.Children.Add(_modeText);
        var exportButton = StudioUi.Button("导出", "ghost sm", () => _ = _tools.OpenAsync(StudioToolsTab.Preflight));
        var termsButton = StudioUi.Button("术语", "ghost sm", () => _ = _tools.OpenAsync(StudioToolsTab.Terms));
        headRow.Children.Add(exportButton);
        headRow.Children.Add(termsButton);

        head.Child = headRow;

        // ---------------------------------------------------------------- content
        _pageWorkspace = new StudioPageWorkspace(viewModel.Page);
        _batchWorkspace = new StudioBatchWorkspace(viewModel.Batch);
        var content = new Grid();
        content.Children.Add(_pageWorkspace);
        content.Children.Add(_batchWorkspace);

        Grid.SetRow(head, 0);
        Grid.SetRow(content, 1);
        _root.Children.Add(head);
        _root.Children.Add(content);
        Grid.SetRow(_tools, 0);
        Grid.SetRowSpan(_tools, 2);
        _root.Children.Add(_tools);

        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioWorkspaceViewModel.Mode) or nameof(StudioWorkspaceViewModel.IsPageMode) or null)
            {
                ApplyMode();
            }
        };
        _pageWorkspace.Canvas.Focusable = true;
        WireBatchDrillDown();
        ApplyMode();
    }

    // ---------------------------------------------------------------- exposed tree (tests + integration)

    public StudioWorkspaceViewModel ViewModel => _viewModel;

    public StudioPageWorkspace PageWorkspace => _pageWorkspace;

    public Control BatchPlaceholder => _batchWorkspace;

    public StudioBatchWorkspace BatchWorkspace => _batchWorkspace;

    public StudioToolsOverlay Tools => _tools;

    public TextBlock BreadcrumbText => _breadcrumb;

    public TextBlock ScopeText => _scopeText;

    public Button PageModeButton => _pageModeButton;

    public Button BatchModeButton => _batchModeButton;

    /// <summary>
    /// AC1: real load chain into the Page mode. Called by the shell on activation and by the headless
    /// screenshot tests; the ids come from the shell selection (null bootstraps from the reader projection).
    /// </summary>
    public async Task<bool> LoadAndRenderAsync(
        string? bookId = null,
        string? chapterId = null,
        CancellationToken cancellationToken = default)
    {
        var loaded = await _viewModel.LoadAsync(bookId, chapterId, cancellationToken).ConfigureAwait(true);
        Dispatcher.UIThread.RunJobs();
        return loaded;
    }

    /// <summary>IWorkspaceView adapter (bridge): restore the persisted selection/zoom when the space activates.</summary>
    public void Activate() => _viewModel.Page.SetViewportSize(_pageWorkspace.Canvas.Bounds.Width, _pageWorkspace.Canvas.Bounds.Height);

    /// <summary>IWorkspaceView adapter (bridge): the selection object already holds zoom/pan/tabs.</summary>
    public void Deactivate() => _viewModel.Page.SetViewportSize(0, 0);

    /// <summary>Overview mode switch from the shell command palette / <c>Tab</c>.</summary>
    public bool SwitchMode(StudioWorkspaceMode mode) => _viewModel.RequestMode(mode);

    // ---------------------------------------------------------------- keyboard

    protected override void OnKeyDown(KeyEventArgs args)
    {
        if (args.Handled)
        {
            base.OnKeyDown(args);
            return;
        }

        if (StudioKeyboard.Handle(_viewModel.Page, this, args))
        {
            base.OnKeyDown(args);
            return;
        }

        if (args.Key == Key.Tab)
        {
            // Tab = Studio mode switch (§6.3). While a region is selected the HUD owns Tab (handled above).
            _viewModel.ToggleMode();
            args.Handled = true;
        }

        base.OnKeyDown(args);
    }

    // ---------------------------------------------------------------- composition details

    private (Button Page, Button Batch) BuildModeSwitch(StackPanel host)
    {
        var segmented = StudioUi.Box("raised");
        var row = StudioUi.Row(0);
        var page = StudioUi.Button("页面", "studio-segment", () => _viewModel.RequestMode(StudioWorkspaceMode.Page));
        var batch = StudioUi.Button("矩阵", "studio-segment", () => _viewModel.RequestMode(StudioWorkspaceMode.Batch));
        ToolTip.SetTip(page, "Studio · Page 模式（默认）");
        ToolTip.SetTip(batch, "Studio · Batch 模式（V11R-B-4 交付）");
        row.Children.Add(page);
        row.Children.Add(batch);
        segmented.Child = row;
        host.Children.Add(segmented);

        _viewModel.PropertyChanged += (_, _) =>
        {
            page.Classes.Set("active", _viewModel.IsPageMode);
            batch.Classes.Set("active", _viewModel.IsBatchMode);
        };
        page.Classes.Set("active", _viewModel.IsPageMode);
        batch.Classes.Set("active", _viewModel.IsBatchMode);
        return (page, batch);
    }

    private async Task SyncBatchAsync()
    {
        await _viewModel.Batch.RefreshAsync().ConfigureAwait(true);
        _viewModel.Page.ApplyRunProjection(_viewModel.Batch.Projection);
    }

    private async Task DrillToPageAsync(string pageId, string? stageType)
    {
        await _viewModel.Page.SelectPageAsync(pageId).ConfigureAwait(true);
        _viewModel.Page.HighlightPipelineStage(stageType);
        _viewModel.RequestMode(StudioWorkspaceMode.Page);
    }

    private void WireBatchDrillDown()
    {
        _viewModel.Batch.DrillToPageRequested += (_, target) => _ = DrillToPageAsync(target.PageId, target.StageType);
        _viewModel.Page.PipelineStageActivated += (_, stageType) =>
        {
            _viewModel.Batch.HighlightStage(stageType, _viewModel.Page.CurrentPageId);
            _ = SyncBatchAsync();
            _viewModel.RequestMode(StudioWorkspaceMode.Batch);
        };
    }

    private void ApplyMode()
    {
        if (_viewModel.IsBatchMode)
        {
            _batchWorkspace.Activate();
        }
        else
        {
            _batchWorkspace.Deactivate();
        }
        _pageModeButton.Classes.Set("active", _viewModel.IsPageMode);
        _batchModeButton.Classes.Set("active", _viewModel.IsBatchMode);
        _pageWorkspace.IsVisible = _viewModel.IsPageMode;
        _batchWorkspace.IsVisible = _viewModel.IsBatchMode;
        if (_viewModel.IsBatchMode)
        {
            _ = SyncBatchAsync();
        }
        _modeText.Text = _viewModel.HeaderModeText;
    }
    // ---------------------------------------------------------------- IWorkspaceView (P1-2)

    public SpaceId Space => SpaceId.Studio;

    public Control CreateContent() => this;

    /// <summary>
    /// On entry the shell hands over its authoritative <see cref="ShellState"/>: the selection is already
    /// the same instance through <c>StudioSelection</c>, so activation only restores the Batch poll and the
    /// retained zoom/offset/inspector tab (kept on the shared selection object, never rebuilt).
    /// </summary>
    public void OnActivated(ShellState state)
    {
        if (_viewModel.IsBatchMode)
        {
            _batchWorkspace.Activate();
        }
    }

    /// <summary>On exit the Batch poll stops; selection was written back to <see cref="ShellState"/> live.</summary>
    public void OnDeactivated(ShellState state)
    {
        _batchWorkspace.Deactivate();
    }

    /// <summary>
    /// R-17: Studio first refusal on its own keys. Page mode: HUD Tab/Enter, Esc stepwise, J/K, [ ],
    /// +/-, 0 (the shell keeps everything else). Batch mode: arrows/J/K move the matrix selection,
    /// Enter drills into Page, Esc closes gate/stop/drawer.
    /// </summary>
    public bool TryHandleKey(KeyEventArgs e, ShellState state) =>
        _viewModel.IsBatchMode
            ? StudioBatchKeyboard.Handle(_viewModel.Batch, e)
            : StudioKeyboard.Handle(_viewModel.Page, this, e);
}