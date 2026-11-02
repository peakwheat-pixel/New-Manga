using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using Avalonia.Data;
using Avalonia.Input;
using Avalonia.Layout;
using Avalonia.Threading;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>
/// V11R-B-5 tools surface inside Studio: 导出预检 / 导出历史 / 术语与约束, as a modal-style overlay.
/// Every number shown comes from a real Host read (translated ids, run projection, export snapshot,
/// export history) or is rendered "—" with its reason; nothing is simulated.
/// </summary>
public sealed class StudioToolsOverlay : Grid
{
    private readonly StudioWorkspaceViewModel _viewModel;
    private readonly StudioExportPreflightPanel _preflight;
    private readonly StudioExportHistoryPanel _history;
    private readonly StudioTermsPanel _terms;
    private readonly StackPanel _content;
    private readonly List<Button> _tabs = new();
    private readonly Button _closeButton;
    private readonly DispatcherTimer _timer;
    private StudioToolsTab _tab = StudioToolsTab.Preflight;

    public StudioToolsOverlay(StudioWorkspaceViewModel viewModel)
    {
        _viewModel = viewModel;
        _preflight = new StudioExportPreflightPanel(viewModel.Export);
        _history = new StudioExportHistoryPanel(viewModel.Export);
        _terms = new StudioTermsPanel(viewModel.Terms);
        _content = new StackPanel { Orientation = Orientation.Vertical, Spacing = 8 };

        var scrim = StudioUi.Box("studio-scrim");
        scrim.PointerPressed += (_, _) => Close();
        Children.Add(scrim);

        var card = StudioUi.Box("raised");
        card.Width = 900;
        card.Height = 640;
        card.HorizontalAlignment = HorizontalAlignment.Center;
        card.VerticalAlignment = VerticalAlignment.Center;
        card.Padding = new Thickness(16);

        var header = StudioUi.Row(8);
        header.Children.Add(StudioUi.Text("工作室 · 导出与术语", "title"));
        header.Children.Add(new Panel { Width = 12 });
        foreach (var tab in new[] { (StudioToolsTab.Preflight, "导出预检"), (StudioToolsTab.History, "导出历史"), (StudioToolsTab.Terms, "术语与约束") })
        {
            var captured = tab.Item1;
            var button = StudioUi.Button(tab.Item2, "studio-tab", () => SetTab(captured));
            _tabs.Add(button);
            header.Children.Add(button);
        }

        header.Children.Add(new Panel { Width = 1 });
        _closeButton = StudioUi.Button("关闭", "ghost sm", Close);
        header.Children.Add(_closeButton);

        _content.Children.Add(_preflight);
        _content.Children.Add(_history);
        _content.Children.Add(_terms);

        var column = StudioUi.Column(12);
        column.Children.Add(header);
        column.Children.Add(_content);
        card.Child = column;
        Children.Add(card);

        _timer = new DispatcherTimer { Interval = viewModel.Export.PollInterval };
        _timer.Tick += (_, _) => _ = viewModel.Export.TickAsync();
        IsVisible = false;
        KeyDown += (_, args) =>
        {
            if (args.Key == Key.Escape)
            {
                Close();
                args.Handled = true;
            }
        };
        SetTab(StudioToolsTab.Preflight);
    }

    public StudioExportPreflightPanel Preflight => _preflight;

    public StudioExportHistoryPanel ExportHistory => _history;

    public StudioTermsPanel Terms => _terms;

    public Button CloseButton => _closeButton;

    public IReadOnlyList<Button> Tabs => _tabs;

    public StudioToolsTab ActiveTab => _tab;

    public bool IsOpen => IsVisible;

    /// <summary>Opens the overlay and loads the real reads (preflight + history + terms).</summary>
    public async Task OpenAsync(StudioToolsTab tab = StudioToolsTab.Preflight)
    {
        IsVisible = true;
        Focusable = true;
        Focus();
        SetTab(tab);
        await _viewModel.Export.RefreshPreflightAsync().ConfigureAwait(true);
        await _viewModel.Export.LoadHistoryAsync().ConfigureAwait(true);
        await _viewModel.Terms.LoadAsync().ConfigureAwait(true);
        _timer.Start();
    }

    public void Close()
    {
        IsVisible = false;
        _timer.Stop();
    }

    public void SetTab(StudioToolsTab tab)
    {
        _tab = tab;
        _preflight.IsVisible = tab == StudioToolsTab.Preflight;
        _history.IsVisible = tab == StudioToolsTab.History;
        _terms.IsVisible = tab == StudioToolsTab.Terms;
        for (var index = 0; index < _tabs.Count; index++)
        {
            _tabs[index].Classes.Set("active", index == (int)tab);
        }
    }

    /// <summary>Test hook: one export poll tick without waiting for the timer.</summary>
    public Task TickAsync(CancellationToken cancellationToken = default) =>
        _viewModel.Export.TickAsync(cancellationToken);
}

/// <summary>Overlay tabs.</summary>
public enum StudioToolsTab
{
    Preflight = 0,
    History = 1,
    Terms = 2,
}

/// <summary>Export preflight: real counts, scope, format, stale policy (only what the Host supports).</summary>
public sealed class StudioExportPreflightPanel : Border
{
    private readonly StudioExportViewModel _viewModel;
    private readonly TextBlock _translated;
    private readonly TextBlock _exportable;
    private readonly TextBlock _failed;
    private readonly TextBlock _blocked;
    private readonly TextBlock _unconfirmed;
    private readonly TextBlock _stale;
    private readonly TextBlock _phase;
    private readonly TextBlock _target;
    private readonly TextBlock _status;
    private readonly Button _chapterScope;
    private readonly Button _selectionScope;
    private readonly Button _zip;
    private readonly Button _pdf;
    private readonly Button _pdfImageOnly;
    private readonly Button _pdfSearchable;
    private readonly Button _abortPolicy;
    private readonly Button _continuePolicy;
    private readonly Button _start;
    private readonly Button _cancel;
    private readonly Button _reveal;
    private readonly ProgressBar _progress;
    private readonly TextBlock _progressText;
    private readonly TextBlock _output;
    private readonly TextBlock _capability;
    private readonly StackPanel _pdfOptions;

    public StudioExportPreflightPanel(StudioExportViewModel viewModel)
    {
        _viewModel = viewModel;
        Padding = new Thickness(4);

        _translated = new TextBlock { Classes = { "data" } };
        _exportable = new TextBlock { Classes = { "data" } };
        _failed = new TextBlock { Classes = { "data" } };
        _blocked = new TextBlock { Classes = { "data" } };
        _unconfirmed = new TextBlock { Classes = { "data" } };
        _stale = new TextBlock { Classes = { "data" } };
        _phase = new TextBlock { Classes = { "body" } };
        _target = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _status = new TextBlock { Classes = { "meta" } };
        _progressText = new TextBlock { Classes = { "data" } };
        _output = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _capability = new TextBlock { Classes = { "meta", "muted", "studio-wrap" } };

        var counts = StudioUi.Row(16);
        counts.Children.Add(CountBlock("已翻译", _translated, "本章已翻译页数（GetTranslatedPageIds）"));
        counts.Children.Add(CountBlock("可导出", _exportable, "按当前作用域与实际已翻译页取交集"));
        counts.Children.Add(CountBlock("失败", _failed, "来自当前 Run 投影（GetTaskProjection）"));
        counts.Children.Add(CountBlock("阻塞", _blocked, "来自当前 Run 投影（GetTaskProjection）"));
        counts.Children.Add(CountBlock("未确认", _unconfirmed, "读取命令未接入：显示 — 而不是 0"));
        counts.Children.Add(CountBlock("过期", _stale, "Core 在 StartExport 内计算；无预读命令：显示 —"));

        _chapterScope = StudioUi.Button("本章", "studio-scope-chip", () => _viewModel.Scope = StudioExportScope.Chapter);
        _selectionScope = StudioUi.Button("选中页", "studio-scope-chip", () => _viewModel.Scope = StudioExportScope.SelectedPages);
        var scopeRow = StudioUi.Row(6);
        scopeRow.Children.Add(StudioUi.Text("范围", "label"));
        scopeRow.Children.Add(_chapterScope);
        scopeRow.Children.Add(_selectionScope);

        _zip = StudioUi.Button("ZIP", "studio-count-chip", () => _viewModel.Format = StudioExportFormat.Zip);
        _pdf = StudioUi.Button("PDF", "studio-count-chip", () => _viewModel.Format = StudioExportFormat.Pdf);
        var formatRow = StudioUi.Row(6);
        formatRow.Children.Add(StudioUi.Text("格式", "label"));
        formatRow.Children.Add(_zip);
        formatRow.Children.Add(_pdf);

        _pdfImageOnly = StudioUi.Button("仅图像", "studio-scope-chip", () => _viewModel.PdfContent = StudioPdfContentMode.ImageOnly);
        _pdfSearchable = StudioUi.Button("可搜索双图层", "studio-scope-chip", () => _viewModel.PdfContent = StudioPdfContentMode.SearchableDualLayer);
        _pdfOptions = StudioUi.Row(6);
        _pdfOptions.Children.Add(StudioUi.Text("PDF 内容", "label"));
        _pdfOptions.Children.Add(_pdfImageOnly);
        _pdfOptions.Children.Add(_pdfSearchable);

        _abortPolicy = StudioUi.Button("abort", "studio-count-chip", () => _viewModel.TrySelectStalePolicy(StudioStalePolicy.Abort));
        ToolTip.SetTip(_abortPolicy, StudioExportViewModel.AbortDescription);
        ToolTip.SetTip(_abortPolicy, StudioExportViewModel.AbortDescription);
        _continuePolicy = StudioUi.Button("continue_existing", "studio-count-chip", () => _viewModel.TrySelectStalePolicy(StudioStalePolicy.ContinueExisting));
        ToolTip.SetTip(_continuePolicy, StudioExportViewModel.ContinueExistingDescription);
        var policyRow = StudioUi.Row(6);
        policyRow.Children.Add(StudioUi.Text("stale 策略", "label"));
        policyRow.Children.Add(_abortPolicy);
        policyRow.Children.Add(_continuePolicy);

        _start = StudioUi.Button("开始导出", "primary", () => { _ = _viewModel.StartExportAsync(); });
        _cancel = StudioUi.Button("取消导出", "danger sm", () => { _ = _viewModel.CancelAsync(); });
        _reveal = StudioUi.Button("打开导出目录", "ghost sm", () => { _ = _viewModel.RevealAsync(); });
        var actions = StudioUi.Row(8);
        actions.Children.Add(_start);
        actions.Children.Add(_cancel);
        actions.Children.Add(_reveal);

        _progress = new ProgressBar { Minimum = 0, Maximum = 100, Height = 8, IsIndeterminate = false };
        _progress.Bind(ProgressBar.ValueProperty, new Binding(nameof(StudioExportViewModel.SnapshotPercent)) { Source = viewModel });

        var progressHost = StudioUi.Column(6);
        progressHost.Children.Add(_progress);
        progressHost.Children.Add(_progressText);
        progressHost.Children.Add(_output);

        var column = StudioUi.Column(10);
        column.Children.Add(StudioUi.Text("EXPORT PREFLIGHT", "studio-section-title"));
        column.Children.Add(counts);
        column.Children.Add(scopeRow);
        column.Children.Add(formatRow);
        column.Children.Add(_pdfOptions);
        column.Children.Add(policyRow);
        column.Children.Add(StudioUi.Text("目标文件", "studio-section-title"));
        column.Children.Add(_target);
        column.Children.Add(actions);
        column.Children.Add(StudioUi.Text("进度", "studio-section-title"));
        column.Children.Add(progressHost);
        column.Children.Add(_phase);
        column.Children.Add(_status);
        column.Children.Add(_capability);
        Child = column;

        viewModel.PropertyChanged += (_, _) => Refresh();
        Refresh();
    }

    public Button StartButton => _start;

    public Button CancelButton => _cancel;

    public Button RevealButton => _reveal;

    public Button AbortPolicyButton => _abortPolicy;

    public Button ContinueExistingButton => _continuePolicy;

    public Button ZipButton => _zip;

    public Button PdfButton => _pdf;

    public ProgressBar Progress => _progress;

    public TextBlock PhaseText => _phase;

    public TextBlock TranslatedText => _translated;

    public TextBlock ExportableText => _exportable;

    public TextBlock UnconfirmedText => _unconfirmed;

    public TextBlock StaleText => _stale;

    public TextBlock TargetText => _target;

    public TextBlock CapabilityText => _capability;

    private void Refresh()
    {
        _translated.Text = $"{_viewModel.TranslatedPageCount}";
        _exportable.Text = $"{_viewModel.ExportablePageIds.Count}";
        _failed.Text = _viewModel.HasRunProjection ? _viewModel.FailedPageCount.ToString() : "—";
        _blocked.Text = _viewModel.HasRunProjection ? _viewModel.BlockedPageCount.ToString() : "—";
        _unconfirmed.Text = _viewModel.UnconfirmedText;
        _stale.Text = _viewModel.StaleText;
        ToolTip.SetTip(_unconfirmed, _viewModel.UnconfirmedTooltip);
        ToolTip.SetTip(_stale, _viewModel.StaleTooltip);
        ToolTip.SetTip(_failed, _viewModel.HasRunProjection ? "来自任务投影" : "无 Run 投影：显示 —");
        _phase.Text = _viewModel.PhaseText;
        _target.Text = $"{_viewModel.TargetFileName} · {_viewModel.TargetHint}";
        _status.Text = _viewModel.StatusText ?? string.Empty;
        _progressText.Text = _viewModel.ProgressText;
        _output.Text = _viewModel.OutputText;
        _progress.IsVisible = _viewModel.IsRunning || _viewModel.IsTerminal;
        _start.IsEnabled = _viewModel.CanStart;
        _cancel.IsEnabled = _viewModel.CanCancel;
        _reveal.IsEnabled = _viewModel.CanReveal;
        _selectionScope.IsEnabled = _viewModel.HasSelectedPages;
        ToolTip.SetTip(
            _selectionScope,
            _viewModel.HasSelectedPages
                ? $"使用共享选择（{_viewModel.SelectedPageCount} 页，Page/Batch 同一 StudioSelection）"
                : "没有选中页：先在 Batch 矩阵或 FilmStrip 选择页面");
        _pdfOptions.IsVisible = _viewModel.IsPdf;
        StudioUi.TrackClass(_chapterScope, "active", _viewModel, () => _viewModel.Scope == StudioExportScope.Chapter);
        StudioUi.TrackClass(_selectionScope, "active", _viewModel, () => _viewModel.Scope == StudioExportScope.SelectedPages);
        StudioUi.TrackClass(_zip, "active", _viewModel, () => _viewModel.Format == StudioExportFormat.Zip);
        StudioUi.TrackClass(_pdf, "active", _viewModel, () => _viewModel.Format == StudioExportFormat.Pdf);
        StudioUi.TrackClass(_pdfImageOnly, "active", _viewModel, () => _viewModel.PdfContent == StudioPdfContentMode.ImageOnly);
        StudioUi.TrackClass(_pdfSearchable, "active", _viewModel, () => _viewModel.PdfContent == StudioPdfContentMode.SearchableDualLayer);
        StudioUi.TrackClass(_abortPolicy, "active", _viewModel, () => _viewModel.StalePolicy == StudioStalePolicy.Abort);
        StudioUi.TrackClass(_continuePolicy, "active", _viewModel, () => _viewModel.StalePolicy == StudioStalePolicy.ContinueExisting);
        _capability.Text = _viewModel.BuildCapabilityInventory().Count == 0
            ? string.Empty
            : "能力清单：" + string.Join(" · ", _viewModel.BuildCapabilityInventory().Take(2)) + "（详见证据 NOT_WIRED 清单）";
    }

    private static Control CountBlock(string label, TextBlock value, string tip)
    {
        var column = StudioUi.Column(2);
        column.Children.Add(StudioUi.Text(label, "meta", "muted"));
        column.Children.Add(value);
        ToolTip.SetTip(column, tip);
        return column;
    }
}

/// <summary>Export history (real <c>GetExportHistory</c>) with per-row reveal.</summary>
public sealed class StudioExportHistoryPanel : Border
{
    private readonly StudioExportViewModel _viewModel;
    private readonly TextBlock _empty;
    private readonly ItemsControl _list;

    public StudioExportHistoryPanel(StudioExportViewModel viewModel)
    {
        _viewModel = viewModel;
        Padding = new Thickness(4);
        _empty = new TextBlock { Classes = { "meta", "muted" } };
        _list = new ItemsControl
        {
            ItemTemplate = new FuncDataTemplate<StudioExportHistoryItemViewModel>((item, scope) =>
            {
                var glyph = StudioUi.Text(item.StateGlyph, "data");
                glyph.Classes.Add(item.StateClass);
                var row = StudioUi.Row(10);
                row.Children.Add(glyph);
                row.Children.Add(StudioUi.Text(item.Format, "label"));
                row.Children.Add(StudioUi.Text(item.PageCountText, "data"));
                row.Children.Add(StudioUi.Text(item.FileName, "data"));
                row.Children.Add(StudioUi.Text(item.CompletedAt, "meta", "muted"));
                row.Children.Add(StudioUi.Text(item.ShaPrefix, "meta", "muted"));
                var reveal = StudioUi.Button("打开目录", "ghost sm", () => { _ = _viewModel.RevealExportAsync(item.ExportId); });
                row.Children.Add(reveal);
                ToolTip.SetTip(row, item.Tooltip);
                return row;
            }, false),
        };

        var header = StudioUi.Row(8);
        header.Children.Add(StudioUi.Text("EXPORT HISTORY", "studio-section-title"));
        header.Children.Add(StudioUi.Button("刷新", "ghost sm", () => { _ = _viewModel.LoadHistoryAsync(); }));
        var column = StudioUi.Column(8);
        column.Children.Add(header);
        column.Children.Add(_list);
        column.Children.Add(_empty);
        Child = column;
        viewModel.History.CollectionChanged += (_, _) => Refresh();
        Refresh();
    }

    public ItemsControl List => _list;

    public TextBlock EmptyText => _empty;

    private void Refresh()
    {
        _list.ItemsSource = _viewModel.History;
        _empty.Text = _viewModel.HistoryEmptyText;
        _empty.IsVisible = _viewModel.History.Count == 0;
    }
}

/// <summary>Terms &amp; constraints: three sections, NOT_WIRED banner, zero fabricated rows.</summary>
public sealed class StudioTermsPanel : Border
{
    private readonly StudioTermsViewModel _viewModel;
    private readonly TextBlock _title;
    private readonly TextBlock _body;
    private readonly TextBox _search;
    private readonly TextBlock _sectionLabel;
    private readonly TextBlock _empty;
    private readonly TextBlock _status;
    private readonly StackPanel _sectionTabs;
    private readonly ItemsControl _rows;

    public StudioTermsPanel(StudioTermsViewModel viewModel)
    {
        _viewModel = viewModel;
        Padding = new Thickness(4);

        _title = new TextBlock { Classes = { "body" } };
        _body = new TextBlock { Classes = { "meta", "studio-wrap" } };
        var banner = StudioUi.Box("studio-banner-partial");
        var bannerText = StudioUi.Column(2);
        bannerText.Children.Add(_title);
        bannerText.Children.Add(_body);
        banner.Child = bannerText;

        _search = new TextBox { Watermark = "搜索术语 / 原文 / 译文" };
        _sectionLabel = new TextBlock { Classes = { "meta" } };
        _empty = new TextBlock { Classes = { "meta", "muted" } };
        _status = new TextBlock { Classes = { "meta", "studio-wrap" } };
        _sectionTabs = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 6 };
        _rows = new ItemsControl
        {
            ItemTemplate = new FuncDataTemplate<StudioTermRow>((row, scope) =>
            {
                var line = StudioUi.Row(8);
                line.Children.Add(StudioUi.Text(row.SourceText, "data"));
                line.Children.Add(StudioUi.Text("→", "meta", "muted"));
                line.Children.Add(StudioUi.Text(row.TargetText, "data"));
                line.Children.Add(StudioUi.Text(row.Scope, "meta", "muted"));
                return line;
            }, false),
        };

        var column = StudioUi.Column(8);
        column.Children.Add(banner);
        column.Children.Add(_search);
        column.Children.Add(_sectionTabs);
        column.Children.Add(_sectionLabel);
        column.Children.Add(_rows);
        column.Children.Add(_empty);
        column.Children.Add(_status);
        Child = column;

        _search.IsEnabled = viewModel.IsSearchEnabled;
        viewModel.PropertyChanged += (_, _) => Refresh();
        Refresh();
    }

    public TextBox SearchBox => _search;

    public ItemsControl RowsList => _rows;

    public TextBlock EmptyText => _empty;

    public TextBlock BannerBody => _body;

    public IReadOnlyList<Button> SectionButtons => _sectionTabs.Children.OfType<Button>().ToList();

    private void Refresh()
    {
        _title.Text = _viewModel.BannerTitle;
        _body.Text = _viewModel.BannerBody;
        _sectionTabs.Children.Clear();
        foreach (var section in new[]
                 {
                     (StudioTermsSection.Terms, "术语表"),
                     (StudioTermsSection.DoNotTranslate, "不译表"),
                     (StudioTermsSection.Conflicts, "冲突提示"),
                 })
        {
            var captured = section.Item1;
            var button = StudioUi.Button(section.Item2, "studio-tab", () =>
            {
                _viewModel.Section = captured;
                _ = _viewModel.LoadAsync();
            });
            StudioUi.TrackClass(button, "active", _viewModel, () => _viewModel.Section == captured);
            _sectionTabs.Children.Add(button);
        }

        _sectionLabel.Text = _viewModel.SectionText;
        _rows.ItemsSource = _viewModel.Rows;
        _rows.IsVisible = _viewModel.HasRows;
        _empty.Text = _viewModel.EmptyText;
        _empty.IsVisible = !_viewModel.HasRows;
        _status.Text = _viewModel.StatusText ?? string.Empty;
    }
}