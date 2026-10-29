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
public partial class StudioWorkspaceView : UserControl
{
    private readonly StudioWorkspaceViewModel _viewModel;
    private readonly StudioPageWorkspace _pageWorkspace;
    private readonly Grid _root;
    private readonly Button _pageModeButton;
    private readonly Button _batchModeButton;
    private readonly TextBlock _breadcrumb;
    private readonly TextBlock _scopeText;
    private readonly TextBlock _modeText;
    private readonly Control _batchPlaceholder;
    private TextBlock _batchNote = null!;

    /// <summary>Design-time / XAML-loading constructor: no Host, so the view renders its empty state.</summary>
    public StudioWorkspaceView()
        : this(new StudioWorkspaceViewModel(NullHostController.Instance))
    {
    }

    public StudioWorkspaceView(StudioWorkspaceViewModel viewModel)
    {
        InitializeComponent();

        // Temporary Nm.* token shim (dies automatically when NewManga.DesignSystem merges).
        StudioFallbackTokens.EnsureMerged();

        _viewModel = viewModel;
        DataContext = viewModel;
        _root = this.FindControl<Grid>("RootGrid")!;

        // ---------------------------------------------------------------- area head (36px)
        var head = StudioUi.Box("studio-head");
        head.Height = 36;
        var headRow = StudioUi.Row(12);

        (_pageModeButton, _batchModeButton) = BuildModeSwitch(headRow);
        _breadcrumb = new TextBlock { Classes = { "nm-label", "nm-secondary" } };
        _breadcrumb.Bind(TextBlock.TextProperty, new Binding(nameof(StudioWorkspaceViewModel.TitleLine)));
        headRow.Children.Add(_breadcrumb);

        var scopeChip = StudioUi.Box("studio-chip");
        _scopeText = new TextBlock { Classes = { "nm-meta" } };
        _scopeText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioSelection.SelectionSummary))
        {
            Source = _viewModel.Selection,
        });
        scopeChip.Child = _scopeText;
        ToolTip.SetTip(scopeChip, "作用域：所有批量动作都带该后缀（FUSION_SPEC §2.3）");
        headRow.Children.Add(scopeChip);

        _modeText = new TextBlock { Classes = { "nm-meta", "nm-muted" } };
        _modeText.Bind(TextBlock.TextProperty, new Binding(nameof(StudioWorkspaceViewModel.HeaderModeText)));
        headRow.Children.Add(_modeText);

        head.Child = headRow;

        // ---------------------------------------------------------------- content
        _pageWorkspace = new StudioPageWorkspace(viewModel.Page);
        _batchPlaceholder = BuildBatchPlaceholder();
        var content = new Grid();
        content.Children.Add(_pageWorkspace);
        content.Children.Add(_batchPlaceholder);

        Grid.SetRow(head, 0);
        Grid.SetRow(content, 1);
        _root.Children.Add(head);
        _root.Children.Add(content);

        _viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioWorkspaceViewModel.Mode) or nameof(StudioWorkspaceViewModel.IsPageMode) or null)
            {
                ApplyMode();
            }
        };
        _pageWorkspace.Canvas.Focusable = true;
        ApplyMode();
    }

    // ---------------------------------------------------------------- exposed tree (tests + integration)

    public StudioWorkspaceViewModel ViewModel => _viewModel;

    public StudioPageWorkspace PageWorkspace => _pageWorkspace;

    public Control BatchPlaceholder => _batchPlaceholder;

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
        var segmented = StudioUi.Box("studio-segmented");
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

    private Control BuildBatchPlaceholder()
    {
        var host = StudioUi.Box("studio-canvas");
        var card = StudioUi.Box("studio-banner");
        card.Width = 560;
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;

        var column = StudioUi.Column(12);
        column.Children.Add(StudioUi.Text("Studio · Batch", "nm-title"));
        var notWired = StudioUi.Box(StudioUi.Text("NOT_WIRED", "nm-meta"), "studio-chip");
        notWired.HorizontalAlignment = HorizontalAlignment.Left;
        column.Children.Add(notWired);
        _batchNote = new TextBlock { Classes = { "nm-body", "nm-wrap" }, Text = _viewModel.BatchNotWiredNote };
        column.Children.Add(_batchNote);
        var detail = new TextBlock { Classes = { "nm-meta", "nm-wrap" }, Text = _viewModel.BatchNotWiredDetail };
        column.Children.Add(detail);

        var actions = StudioUi.Row(8);
        var start = StudioUi.Button("开始处理", "studio-action primary");
        start.IsEnabled = false;
        ToolTip.SetTip(start, StudioCapabilityGate.NotWiredTooltip);
        var back = StudioUi.Button("返回 Page 模式", "studio-action", () => _viewModel.RequestMode(StudioWorkspaceMode.Page));
        actions.Children.Add(start);
        actions.Children.Add(back);
        column.Children.Add(actions);

        card.Child = column;
        host.Child = card;
        return host;
    }

    private void ApplyMode()
    {
        _pageModeButton.Classes.Set("active", _viewModel.IsPageMode);
        _batchModeButton.Classes.Set("active", _viewModel.IsBatchMode);
        _pageWorkspace.IsVisible = _viewModel.IsPageMode;
        _batchPlaceholder.IsVisible = _viewModel.IsBatchMode;
        _modeText.Text = _viewModel.HeaderModeText;
    }
}
