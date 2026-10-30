using Avalonia;
using Avalonia.Automation;
using Avalonia.Controls;
using Avalonia.Controls.Templates;
using Avalonia.Controls.Primitives;
using Avalonia.Data;
using Avalonia.Layout;
using NewManga.App.ViewModels.V2.Studio;

namespace NewManga.App.Views.V2.Studio.Controls;

/// <summary>One track chip of the four-track strip (原图 / 文本 / 修复 / 排版).</summary>
public sealed record StudioTrackChip(string Key, string Label, StudioStateKind? State, string Detail, string Tooltip)
{
    public string Glyph => State is { } state ? StudioStates.Glyph(state) : "–";
}

/// <summary>
/// V11R-B-3 <c>TrackStrip</c>: the four tracks (原图/文本/修复/排版) and their completion/stale state.
/// Only 原图 is backed by a real read today (page image + page extent); the other three have no read
/// command on the frozen face, so they render a neutral dot and the explicit "状态待接入" detail —
/// never a made-up completion percentage (DESIGN_SYSTEM §9 rule 5: stale ≠ unfinished).
/// </summary>
public sealed class StudioTrackStrip : StackPanel
{
    private readonly StudioPageViewModel _viewModel;
    private readonly Dictionary<string, (TextBlock Glyph, TextBlock Detail, Border Chip)> _chips = new();

    public StudioTrackStrip(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        Orientation = Orientation.Horizontal;
        Spacing = 8;
        VerticalAlignment = VerticalAlignment.Center;
        Margin = new Thickness(8, 0);

        foreach (var (key, label) in new[] { ("source", "原图"), ("text", "文本"), ("inpaint", "修复"), ("render", "排版") })
        {
            var glyph = StudioUi.Text("·", "data", "studio-state-nodata");
            var detail = StudioUi.Text("—", "meta", "muted");
            var row = StudioUi.Row(4);
            row.Children.Add(glyph);
            row.Children.Add(StudioUi.Text(label, "label"));
            row.Children.Add(detail);
            var chip = StudioUi.Box(row, "studio-track-chip");
            _chips[key] = (glyph, detail, chip);
            Children.Add(chip);
        }

        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.HasPageImage)
                or nameof(StudioPageViewModel.PageSizeText)
                or nameof(StudioPageViewModel.RegionCountText)
                or nameof(StudioPageViewModel.PageImageMissing)
                or nameof(StudioPageViewModel.LoadState)
                or null)
            {
                Refresh();
            }
        };

        Refresh();
    }

    /// <summary>Chips in design order; headless tests assert the four labels and their state symbols.</summary>
    public IReadOnlyList<StudioTrackChip> Tracks => BuildTracks();

    public Border? ChipFor(string key) => _chips.TryGetValue(key, out var chip) ? chip.Chip : null;

    public TextBlock? GlyphFor(string key) => _chips.TryGetValue(key, out var chip) ? chip.Glyph : null;

    public void Refresh()
    {
        foreach (var track in BuildTracks())
        {
            if (!_chips.TryGetValue(track.Key, out var chip))
            {
                continue;
            }

            chip.Glyph.Text = track.Glyph;
            chip.Detail.Text = track.Detail;
            foreach (var state in Enum.GetValues<StudioStateKind>())
            {
                chip.Glyph.Classes.Set(StudioStates.StyleClass(state), track.State == state);
            }

            chip.Glyph.Classes.Set("studio-state-nodata", track.State is null);
            ToolTip.SetTip(chip.Chip, track.Tooltip);
        }
    }

    private IReadOnlyList<StudioTrackChip> BuildTracks()
    {
        var sourceState = _viewModel.HasPageImage
            ? StudioStateKind.Done
            : _viewModel.PageImageMissing
                ? StudioStateKind.Failed
                : _viewModel.LoadState is StudioLoadState.Loading
                    ? StudioStateKind.Running
                    : StudioStateKind.NotStarted;
        var sourceDetail = _viewModel.HasPageImage
            ? _viewModel.PageSizeText
            : _viewModel.PageImageMissing
                ? "读取失败"
                : "—";

        return new[]
        {
            new StudioTrackChip(
                "source",
                "原图",
                sourceState,
                sourceDetail,
                $"原图轨：{StudioStates.Label(sourceState)} · 页面图来自 Host 资源通道"),
            new StudioTrackChip(
                "text",
                "文本",
                null,
                $"{_viewModel.RegionCount} 区 · 状态待接入",
                "文本轨状态读取命令未接入（V11R-F0-1）"),
            new StudioTrackChip(
                "inpaint",
                "修复",
                null,
                "状态待接入",
                "修复轨状态读取命令未接入（V11R-F0-1）"),
            new StudioTrackChip(
                "render",
                "排版",
                null,
                "状态待接入",
                "排版轨状态读取命令未接入（V11R-A-2 / F0-1）"),
        };
    }
}

/// <summary>
/// V11R-B-3 pipeline band (28px collapsed ⇄ 240px expanded): the ten canonical stage dots, the current
/// page and the run controls. Stage state comes exclusively from the run projection; while
/// <see cref="IRunDataSource"/> is NOT_WIRED every dot renders "no projection data" and the header says
/// NOT_WIRED — the band can never show invented progress.
/// </summary>
public sealed class StudioPipelineBand : Border
{
    private const double CollapsedHeight = 28;
    private const double ExpandedHeight = 240;

    private readonly StudioPageViewModel _viewModel;
    private readonly Button _toggle;
    private readonly StackPanel _dots;
    private readonly ItemsControl _stageList;
    private readonly TextBlock _header;
    private readonly TextBlock _pageText;

    public StudioPipelineBand(StudioPageViewModel viewModel)
    {
        _viewModel = viewModel;
        Classes.Add("studio-band");
        Height = CollapsedHeight;
        BorderThickness = new Thickness(0, 1, 0, 0);

        _toggle = StudioUi.Button("▸ 展开 10 阶段", "ghost sm", () => _viewModel.TogglePipelineExpanded());
        _toggle.Bind(ContentControl.ContentProperty, new Binding(nameof(StudioPageViewModel.PipelineToggleLabel)));
        _header = StudioUi.BoundText(nameof(StudioPageViewModel.PipelineHeaderText), "label");
        _pageText = StudioUi.BoundText(nameof(StudioPageViewModel.PageCounterText), "data", "muted");

        _dots = StudioUi.Row(4);
        RebuildDots();
        viewModel.PipelineStages.CollectionChanged += (_, _) => RebuildDots();

        var notWiredChip = StudioUi.Box(
            StudioUi.Text("NOT_WIRED", "meta"),
            "studio-chip");
        StudioUi.TrackVisible(notWiredChip, viewModel, () => viewModel.PipelineNotWired);

        var headerRow = StudioUi.Row(8);
        headerRow.Margin = new Thickness(0);
        headerRow.Children.Add(_toggle);
        headerRow.Children.Add(_header);
        headerRow.Children.Add(notWiredChip);
        headerRow.Children.Add(_pageText);

        var collapsed = new Grid { ColumnDefinitions = new ColumnDefinitions("Auto,Auto,*") };
        Grid.SetColumn(headerRow, 0);
        Grid.SetColumn(_dots, 1);
        collapsed.Children.Add(headerRow);
        collapsed.Children.Add(_dots);

        _stageList = new ItemsControl
        {
            ItemTemplate = new FuncDataTemplate<StudioPipelineStageItem>((item, _) => BuildStageRow(item), true),
            ItemsSource = viewModel.PipelineStages,
            IsVisible = false,
        };
        var scroll = new ScrollViewer
        {
            Content = _stageList,
            VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
            Height = ExpandedHeight - CollapsedHeight - 8,
            IsVisible = false,
        };

        var root = new Grid { RowDefinitions = new RowDefinitions("Auto,*") };
        Grid.SetRow(collapsed, 0);
        Grid.SetRow(scroll, 1);
        root.Children.Add(collapsed);
        root.Children.Add(scroll);
        Child = root;
        _stageScroll = scroll;

        viewModel.PropertyChanged += (_, args) =>
        {
            if (args.PropertyName is nameof(StudioPageViewModel.PipelineExpanded) or null)
            {
                Height = viewModel.PipelineExpanded ? ExpandedHeight : CollapsedHeight;
                scroll.IsVisible = viewModel.PipelineExpanded;
            }
        };
    }

    private readonly ScrollViewer _stageScroll;

    /// <summary>Rebuilds the ten/dynamic dots; each dot is a real button (Page → Batch drill-up).</summary>
    private void RebuildDots()
    {
        _dots.Children.Clear();
        foreach (var stage in _viewModel.PipelineStages)
        {
            var dot = StudioUi.Dot(stage.State);
            var button = StudioUi.Button(string.Empty, "icon ghost", () => _viewModel.ActivatePipelineStage(stage.Key));
            AutomationProperties.SetName(button, $"流水线阶段：{stage.Key}（跳到批次并高亮）");
            button.Content = dot;
            button.Width = 14;
            button.Height = 14;
            button.Padding = new Thickness(0);
            ToolTip.SetTip(button, $"{stage.Tooltip} · 点击回到 Batch 并高亮该阶段");
            _dots.Children.Add(button);
            var captured = stage;
            stage.PropertyChanged += (_, _) =>
            {
                foreach (var state in Enum.GetValues<StudioStateKind>())
                {
                    dot.Classes.Set(StudioUi.FillClass(state), captured.State == state);
                }

                dot.Classes.Set("studio-fill-nodata", captured.State is null);
                ToolTip.SetTip(button, captured.Tooltip);
            };
        }
    }

    public ItemsControl StageList => _stageList;

    public StackPanel Dots => _dots;

    public Button ToggleButton => _toggle;

    public TextBlock HeaderText => _header;

    public ScrollViewer StageScroll => _stageScroll;

    private static Control BuildStageRow(StudioPipelineStageItem item)
    {
        var row = StudioUi.Row(8);
        row.Margin = new Thickness(0, 2);
        var index = StudioUi.Text(item.Index.ToString("00"), "data", "muted");
        index.Width = 20;
        var glyph = StudioUi.Glyph(item.State);
        var label = StudioUi.BoundText(nameof(StudioPipelineStageItem.Label), "label");
        label.Width = 64;
        var state = StudioUi.BoundText(nameof(StudioPipelineStageItem.StateLabel), "meta", "muted");
        row.Children.Add(index);
        row.Children.Add(glyph);
        row.Children.Add(label);
        row.Children.Add(state);
        ToolTip.SetTip(row, item.Tooltip);
        return row;
    }
}
