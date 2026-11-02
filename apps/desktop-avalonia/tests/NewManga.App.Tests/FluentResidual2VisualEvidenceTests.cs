using System.Reflection;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Controls.Templates;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Styling;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Controls;
using NewManga.DesignSystem.Icons;
using NewManga.DesignSystem.Theming;

namespace NewManga.App.Tests;

/// <summary>Both palettes use the real App resource stack and product appearance manager. Default runs write no evidence.</summary>
public sealed class FluentResidual2VisualEvidenceTests
{
    private const string CaptureCommand = "$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS='1'; dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --filter FullyQualifiedName~FluentResidual2VisualEvidenceTests --nologo";
    private sealed record Shot(string Group, string Name, string State, string Mode, string Theme, string Frame, Bitmap Image)
    {
        public string File => $"{Group}--{Name}--{State}--{Mode}--{Theme}.png";
    }
    private static void Motion(FluentShellSurface surface, MotionCategories categories = MotionCategories.All, MotionMode mode = MotionMode.Full) =>
        typeof(FluentShellSurface).GetMethod("ApplyMotion", BindingFlags.NonPublic | BindingFlags.Instance)!.Invoke(surface,
            [AppearanceDefaults.Settings with { MotionMode = mode, MotionCategories = categories }]);

    // Real transitions are settled before evidence; no local opacity overrides hide production bugs.
    internal static void Settle(int milliseconds = 300)
    {
        var until = System.Diagnostics.Stopwatch.StartNew();
        do { Thread.Sleep(20); AvaloniaHeadlessPlatform.ForceRenderTimerTick(); Dispatcher.UIThread.RunJobs(); }
        while (until.ElapsedMilliseconds < milliseconds);
    }

    [AvaloniaFact]
    public async Task Captures_Residual2_Visual_Inventory_Only_When_Opted_In()
    {
        var old = Residual2Evidence.OldEvidence();
        var statusBefore = Residual2Evidence.Git("status", "--porcelain", "--", "verification");
        var shots = new List<Shot>(); var colors = new List<Color>();
        try
        {
            foreach (var theme in new[] { "light", "dark" })
            {
                using var scope = await Residual2Evidence.Create(theme);
                colors.Add(scope.CanvasColor);
                var clock = new ManualFluentMotionClock();
                var shell = FluentShell.CreateRoot(selection: FrontendSelector.Select("builtin.fluent", null),
                    host: Residual2Evidence.Host(), appearance: scope.Appearance, themeManager: scope.Manager);
                shell.Width = 1280; shell.Height = 900; shell.Surface.MotionClock = clock;
                shell.Show(); Dispatcher.UIThread.RunJobs(); Motion(shell.Surface);
                try
                {
                    await CaptureDecor(shell, clock, scope, shots); // fresh shell/clock: first frame is really phase zero
                    Motion(shell.Surface);
                    foreach (var page in FluentShell.Pages)
                    {
                        shell.Navigate(page);
                        if (page == FluentPage.Reader)
                        {
                            await shell.ReaderView.LoadAsync("book-1", "chapter-key");
                            Assert.NotNull(shell.ReaderView.PageImage.Source);
                            Assert.Equal(2, shell.ReaderViewModel.Book!.Pages.Count);
                        }
                        if (page == FluentPage.Settings) await shell.SettingsViewModel.LoadAsync();
                        clock.Advance(1000); Settle();
                        if (page == FluentPage.Library) clock.Advance(3000); // page context at crest; decor-first is independently phase zero
                        var frame = Residual2Evidence.Capture(shell);
                        shots.Add(new("pages", page == FluentPage.Library ? "shelf" : page.ToString().ToLowerInvariant(), "default", "full", theme, "settled", frame));
                    }
                    CaptureShellStates(shell, clock, theme, shots);
                }
                finally { shell.Close(); Dispatcher.UIThread.RunJobs(); }
                CaptureComponents(theme, scope, shots);
            }
            Assert.NotEqual(colors[0], colors[1]);
            foreach (var name in new[] { "shelf", "workbench", "reader", "settings" })
            {
                var pair = shots.Where(s => s.Group == "pages" && s.Name == name).ToArray();
                // Large background patch away from the appearance.mode field or other text: palette must affect pixels.
                Assert.True(Residual2Evidence.ChangedPixels(pair[0].Image, pair[1].Image, region: new PixelRect(4, 80, 30, 600)) > 10000, name);
            }
            foreach (var theme in new[] { "light", "dark" })
            {
                var pair = shots.Where(s => s.Name == "icon-button" && s.Theme == theme && s.State is "default" or "checked").ToArray();
                Assert.True(Residual2Evidence.ChangedPixels(pair[0].Image, pair[1].Image) > 100);
            }
            Assert.Equal(shots.Count, shots.Select(s => s.File).Distinct().Count());
            var duplicateFrames = shots.GroupBy(s => Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(Residual2Evidence.Bytes(s.Image))))
                .Where(g => g.Count() > 1).Select(g => string.Join(",", g.Select(s => s.File))).ToArray();
            Assert.True(duplicateFrames.Length == 0, string.Join(";", duplicateFrames));
            Assert.Equal(statusBefore, Residual2Evidence.Git("status", "--porcelain", "--", "verification"));
            Assert.Equal(old.OrderBy(p => p.Key), Residual2Evidence.OldEvidence().OrderBy(p => p.Key));
            if (Environment.GetEnvironmentVariable("NEWMANGA_CAPTURE_RESIDUAL2_PNGS") == "1") Write(shots);
            Assert.Equal(old.OrderBy(p => p.Key), Residual2Evidence.OldEvidence().OrderBy(p => p.Key));
            Assert.Equal(Residual2Evidence.Git("status", "--porcelain", "--", "verification/FEA-06"), string.Empty);
        }
        finally { foreach (var shot in shots) shot.Image.Dispose(); }
    }

    private static void CaptureShellStates(FluentShell shell, ManualFluentMotionClock clock, string theme, List<Shot> shots)
    {
        shell.Navigate(FluentPage.Library); clock.Advance(1000); Settle();
        // TopBand, NavRail, StatusBand are the actual named product controls in each responsive layout.
        foreach (var width in new[] { 1280, 1024 })
        {
            shell.Width = width; shell.UpdateLayout(); Dispatcher.UIThread.RunJobs();
            shots.Add(new("shell", "top-nav-status", width == 1280 ? "default" : "compact", "full", theme, "settled", Residual2Evidence.Capture(shell)));
        }
        shell.Width = 1280; shell.UpdateLayout();
        foreach (var state in new[] { "result", "empty" })
        {
            shell.FindControl<Button>("CommandPaletteButton")!.RaiseEvent(new RoutedEventArgs(Avalonia.Controls.Button.ClickEvent));
            var search = Assert.IsType<TextBox>(shell.FocusManager!.GetFocusedElement());
            search.Text = state == "empty" ? "不存在的命令-zzz" : "书架";
            Settle();
            var rows = shell.GetVisualDescendants().OfType<Button>().Count(b => b.Classes.Contains("fluent-command-row"));
            if (state == "empty") Assert.Equal(0, rows); else Assert.True(rows > 0);
            shots.Add(new("components", "command-palette", state, "full", theme, "settled", Residual2Evidence.Capture(shell)));
            shell.HandleKeyForTest(Key.Escape, KeyModifiers.None); clock.Advance(160); Settle(40);
        }
    }

    private static async Task CaptureDecor(FluentShell shell, ManualFluentMotionClock clock, Residual2Evidence scope, List<Shot> shots)
    {
        var theme = scope.Theme;
        shell.Navigate(FluentPage.Library); Settle();
        // No navigation/feedback during the comparison, while decorative remains full. This is the real category policy.
        Motion(shell.Surface, MotionCategories.Decorative);
        var first = Residual2Evidence.Capture(shell);
        clock.Advance(2000); // an intermediate full frame; the static reduce frame equals the exact 4s crest by design
        var mid = Residual2Evidence.Capture(shell);
        Assert.True(Residual2Evidence.ChangedPixels(first, mid, tolerance: 1) > 1000, "gradient must change visible background pixels");
        // Crop only: original product pixels, no recolouring or enlargement. This makes the background
        // evidence inspectable and avoids reusing an identical full-page PNG for two distinct cells.
        var backgroundCrop = new PixelRect(216, 95, 1048, 720);
        shots.Add(new("decor", "shelf-gradient", "first", "full", theme, "first-crop-216,95,1048,720", Residual2Evidence.Crop(first, backgroundCrop)));
        shots.Add(new("decor", "shelf-gradient", "mid", "full", theme, "intermediate-2000ms-crop-216,95,1048,720", Residual2Evidence.Crop(mid, backgroundCrop)));
        first.Dispose(); mid.Dispose();
        Motion(shell.Surface, mode: MotionMode.Reduce);
        using var staticFrame = Residual2Evidence.Capture(shell);
        shots.Add(new("decor", "shelf-gradient", "static", "reduce", theme, "static-crop-216,95,1048,720", Residual2Evidence.Crop(staticFrame, backgroundCrop)));

        shell.Navigate(FluentPage.Reader); await shell.ReaderView.LoadAsync("book-1", "chapter-key"); Settle();
        Motion(shell.Surface, MotionCategories.Decorative);
        await shell.ReaderViewModel.NavigateAsync(1); Dispatcher.UIThread.RunJobs(); shell.UpdateLayout();
        clock.Advance(200);
        var layer = shell.ReaderView.DecorativeParticleLayer!; Assert.NotNull(layer);
        Assert.False(layer.IsHitTestVisible);
        var particles = Residual2Evidence.Capture(shell);
        // Identical content/time/layout, only remove the real decorative layer to isolate particle pixels.
        layer.IsVisible = false;
        var without = Residual2Evidence.Capture(shell); layer.IsVisible = true;
        var area = layer.TranslatePoint(default, shell)!.Value;
        var rect = new PixelRect((int)area.X, (int)area.Y, (int)layer.Bounds.Width, (int)layer.Bounds.Height);
        var changed = Residual2Evidence.ChangedPixels(particles, without, tolerance: 8, region: rect);
        Assert.InRange(changed, 25, (int)(rect.Width * rect.Height * .01)); // visible but under 1% of page pixels
        without.Dispose();
        shots.Add(new("decor", "page-turn-particles", "mid", "full", theme, "mid-200ms", particles));
        clock.Advance(200); Motion(shell.Surface, mode: MotionMode.Reduce);
        await shell.ReaderView.LoadAsync("book-1", "chapter-key"); await shell.ReaderViewModel.NavigateAsync(1);
        Assert.Null(shell.ReaderView.DecorativeParticleLayer);
        shots.Add(new("decor", "page-turn-particles", "none", "reduce", theme, "static", Residual2Evidence.Capture(shell)));
    }

    private static Button Button(string style, string text = "操作") => new() { Content = text, Classes = { style }, Width = 140, Height = 40 };
    private static void CaptureComponents(string theme, Residual2Evidence scope, List<Shot> shots)
    {
        var cases = new List<(string Name, string State, Control Control, Action<Window,Control>? Act)>();
        void Add(string name, string state, Control control, Action<Window,Control>? act = null) => cases.Add((name,state,control,act));
        static void Hover(Window w, Control c) { w.MouseMove(c.TranslatePoint(new Point(c.Bounds.Width/2,c.Bounds.Height/2),w)!.Value); Settle(250); Assert.True(c.IsPointerOver); }
        static void Press(Window w, Control c) { Hover(w,c); w.MouseDown(c.TranslatePoint(new Point(c.Bounds.Width/2,c.Bounds.Height/2),w)!.Value,MouseButton.Left); Settle(200); }
        foreach (var state in new[] { "default", "hover", "selected", "disabled" })
        {
            var card = new SurfaceCard { Width = 200, Height = 90, Child = new TextBlock { Text = "卡片内容" }, IsEnabled = state != "disabled" };
            if(state == "selected") card.Classes.Add("selected"); Add("surface-card",state,card,state=="hover"?Hover:null);
        }
        foreach (var name in new[] { "book-card", "book-row" })
        foreach (var state in new[] { "default", "disabled" })
        {
            Button book = name == "book-card" ? new BookCard() : new BookRow(); book.Content="Sample Manga"; book.Width=220; book.Height=72; book.IsEnabled=state!="disabled"; Add(name,state,book);
        }
        foreach (var kind in new[] { "primary", "secondary", "danger" })
        foreach (var state in new[] { "default", "hover", "pressed", "disabled" })
        {
            var b = Button("fluent-"+kind,kind+" 操作"); b.IsEnabled=state!="disabled";
            Add(kind+"-button",state,b,state=="hover"?Hover:state=="pressed"?Press:null);
        }
        foreach(var state in new[]{"default","hover","checked"})
        {
            var b=Button("fluent-icon"); b.Width=40; b.Content=new NmIcon { Kind=NmIconKind.Settings }; if(state=="checked") b.Classes.Add("checked"); Add("icon-button",state,b,state=="hover"?Hover:null);
        }
        foreach(var state in new[]{"off","on","disabled"}) Add("toggle-switch",state,new ToggleSwitch { Content="选项", IsChecked=state=="on", IsEnabled=state!="disabled" });
        foreach(var state in new[]{"default","hover","disabled"}) Add("slider",state,new Slider { Width=220, Minimum=0, Maximum=100, Value=40, IsEnabled=state!="disabled" },state=="hover"?Hover:null);
        foreach(var state in new[]{"selected","unselected","hover","pressed"})
        {
            var segmented=new SegmentedControl { Items=["页面","批量"], SelectedIndex=state=="selected"?0:1, Width=240 };
            Add("segmented-control",state,segmented,(w,c)=>{var b=c.GetVisualDescendants().OfType<Button>().First(); if(state=="hover") Hover(w,b); if(state=="pressed") Press(w,b);});
        }
        foreach(var state in new[]{"selected","unselected","hover"})
        {
            var tabs=new TabControl { Width=300,Height=100,Items={new TabItem{Header="页面",IsSelected=state=="selected"},new TabItem{Header="批量",IsSelected=state!="selected"}}};
            Add("tab-strip",state,tabs,state=="hover"?(w,c)=>Hover(w,c.GetVisualDescendants().OfType<TabItem>().First()):null);
        }
        foreach(var state in new[]{"default","focus","value"})
        {
            var f=new SearchField { Width=260 }; Add("search-field",state,f,(w,c)=>{var box=c.GetVisualDescendants().OfType<TextBox>().Single(); if(state=="focus")box.Focus(NavigationMethod.Tab);if(state=="value")box.Text="Sample";});
        }
        foreach(var state in new[]{"error","disabled"})
        {
            var input=new TextBox{Width=220,Text="设置值",IsEnabled=state!="disabled"};if(state=="error")input.Classes.Add("invalid");
            var f=new SettingsField{ColumnDefinitions=new ColumnDefinitions("Auto,*"),Children={new TextBlock{Text="字段"},input}};Grid.SetColumn(input,1);Add("settings-field",state,f);
        }
        foreach(var state in new[]{"default","hover"}) Add("region-box",state,new RegionBox{Width=160,Height=70,Child=new TextBlock{Text="region"}},state=="hover"?Hover:null);
        Add("reader-progress","default",new ReaderProgressBar{Width=260,Height=12,Minimum=0,Maximum=100,Value=60});
        Add("chapter-list","default",new ChapterList { Width=280, Children={new BookRow{Content="第 1 章 · 2 页"},new BookRow{Content="第 2 章 · 3 页"},new BookRow{Content="第 3 章 · 1 页"}} });
        using var image = new Bitmap(new MemoryStream(Residual2Evidence.PagePng()));
        Add("page-thumb-strip","default",new PageThumbStrip{ItemsSource=new[]{1,2},ItemTemplate=new FuncDataTemplate<int>((i,_)=>new StackPanel{Children={new Image{Source=image,Width=48,Height=72},new TextBlock{Text=$"第 {i} 页"}}})});
        Add("reader-page","single",new NewManga.DesignSystem.Controls.ReaderPage{Width=160,Height=240,Child=new Image{Source=image}});
        Add("streaming-thumb","lazy",new StreamingThumb{Width=90,Height=120,Child=new Skeleton{Variant=SkeletonVariant.BookCard}});
        Add("empty-state","default",new EmptyState{Title="暂无内容",Hint="导入漫画开始阅读",ActionText="导入"});
        foreach(var state in new[]{"retryable","unrecoverable"}) Add("error-state",state,new AlertBanner{Severity=StatusKind.Failed,Title="页面读取失败",Message="测试错误状态",ActionText=state=="retryable"?"重试":null});
        foreach(var variant in Enum.GetValues<SkeletonVariant>()) Add("skeleton",variant.ToString().ToLowerInvariant(),new Skeleton{Variant=variant,Width=180});
        foreach(var kind in Enum.GetValues<StatusKind>()) Add("alert-banner",kind.ToString().ToLowerInvariant(),new AlertBanner{Severity=kind,Title=kind.ToString(),Message="状态说明",Width=340});
        foreach(var state in new[]{"open","closed"})
        {
            var host=new Grid{Width=440,Height=260,Children={new TextBlock{Text="书架 · 新建作品",Margin=new Thickness(12)}}};
            host.Children.Add(new FluentDialog{IsOpen=state=="open",HorizontalAlignment=HorizontalAlignment.Center,VerticalAlignment=VerticalAlignment.Center,Child=new TextBlock{Text="对话框内容"}});Add("dialog",state,host);
            var drawerHost=new Grid{Width=440,Height=260,Children={new TextBlock{Text="书架 · 回收站",Margin=new Thickness(12)}}};
            drawerHost.Children.Add(new Drawer{IsOpen=state=="open",Header="详情",Content=new TextBlock{Text="抽屉内容"},Classes={"fluent-drawer"}});Add("drawer",state,drawerHost);
        }
        // Popups use Avalonia's overlay host so actual popup pixels are inside the window framebuffer.
        var overlayStyle=new Style(s=>s.OfType<Popup>()){Setters={new Setter(Popup.ShouldUseOverlayLayerProperty,true)}};
        Application.Current!.Styles.Add(overlayStyle);
        try
        {
            foreach(var item in cases)
            {
                var profile = MotionTimings.Resolve(new MotionResolver(new WindowsMotionPreferenceSource()).Resolve(AppearanceDefaults.Settings with { MotionMode = MotionMode.Full, MotionCategories = MotionCategories.All }).Settings);
                var host=new Border {Padding=new Thickness(24),Child=item.Control,Background=new SolidColorBrush(scope.CanvasColor)};
                host.SetValue(FluentMotionScope.ConfigurationProperty, new FluentMotionScope.Configuration(profile, FluentRenderClock.Instance));
                item.Control.HorizontalAlignment=HorizontalAlignment.Center;item.Control.VerticalAlignment=VerticalAlignment.Center;
                var w=new Window{Width=520,Height=340,Content=host};w.Show();Dispatcher.UIThread.RunJobs();w.MouseMove(new Point(1,1));
                try
                {
                    item.Act?.Invoke(w,item.Control);Dispatcher.UIThread.RunJobs();
                    if (item.Control is ReaderProgressBar progress)
                        Assert.True(progress.GetVisualDescendants().Any(), $"Progress theme={progress.Theme}, template={progress.Template}, bounds={progress.Bounds}, value={progress.Value}");
                    if (item.Control is PageThumbStrip strip)
                        Assert.True(strip.GetVisualDescendants().OfType<Image>().Any(), $"Thumb theme={strip.Theme}, template={strip.Template}, bounds={strip.Bounds}, items={strip.ItemCount}, children={string.Join(",", strip.GetVisualDescendants().Select(v => v.GetType().Name))}");
                    if(item.Control is Slider slider)
                    {
                        var thumb=slider.GetVisualDescendants().OfType<Thumb>().Single();
                        var key=item.State=="disabled"?"Nm.Color.Text.Disabled":item.State=="hover"?"Nm.Color.Accent.Hover":"Nm.Color.Accent.Base";
                        Assert.Equal(scope.Token(key),Assert.IsAssignableFrom<ISolidColorBrush>(thumb.Background).Color);
                        var track = slider.GetVisualDescendants().OfType<RepeatButton>().Single(b => b.Name == "PART_DecreaseButton");
                        Assert.True(scope.Token(key) == Assert.IsAssignableFrom<ISolidColorBrush>(track.Background).Color, $"state={item.State} sliderForeground={slider.Foreground}, part={track.Name}, templateParent={track.TemplatedParent}, trackBg={track.Background}");
                    }
                    var imageFrame = Residual2Evidence.Capture(w);
                    if (item.Control is ReaderProgressBar or PageThumbStrip)
                    {
                        var pixels = Residual2Evidence.Pixels(imageFrame);
                        var distinct = new HashSet<int>();
                        for (var i=0; i<pixels.Length; i+=4) distinct.Add(pixels[i] | pixels[i+1]<<8 | pixels[i+2]<<16);
                        Assert.True(distinct.Count > 2, $"{item.Name} must render actual content pixels");
                    }
                    shots.Add(new("components",item.Name,item.State,"full",theme,"settled",imageFrame));
                }
                finally{w.Close();}
            }
            foreach(var kind in new[]{"context-menu","tooltip"})
            {
                var b=Button("fluent-secondary","菜单宿主");var w=new Window{Width=520,Height=340,Content=b};w.Show();Dispatcher.UIThread.RunJobs();
                ContextMenu? menu=null;
                try
                {
                    if(kind=="context-menu"){menu=new ContextMenu{Items={new MenuItem{Header="可用"},new MenuItem{Header="不可用",IsEnabled=false}}};b.ContextMenu=menu;menu.Open(b);}
                    else {w.MouseMove(b.TranslatePoint(new Point(40,20),w)!.Value);ToolTip.SetTip(b,new ToolTip{Content="提示文本"});ToolTip.SetPlacement(b,PlacementMode.Bottom);ToolTip.SetIsOpen(b,true);}
                    Settle(300);shots.Add(new("components",kind,kind=="context-menu"?"disabled-item":"opened","full",theme,"settled",Residual2Evidence.Capture(w)));
                }
                finally{menu?.Close();ToolTip.SetIsOpen(b,false);w.Close();}
            }
        }
        finally{Application.Current!.Styles.Remove(overlayStyle);}
    }

    private static void Write(List<Shot> shots)
    {
        var output=Path.GetFullPath(Path.Combine(Residual2Evidence.Root,"verification/FEA-06-RESIDUAL-2/visuals"));
        Assert.Equal(Path.Combine(Residual2Evidence.Root,"verification","FEA-06-RESIDUAL-2","visuals"),output);
        Directory.CreateDirectory(output);
        // Replace only the owned, obsolete capture set; historical reviews retain their signed hashes.
        foreach(var path in Directory.EnumerateFiles(output,"*.png")) File.Delete(path);
        var head=Residual2Evidence.Git("rev-parse","HEAD");
        var rows=new List<string>{"# R2R2 visual inventory",$"捕获 HEAD：`{head}`；frontend=builtin.fluent；headless Skia、96 DPI。签署待独立 Reviewer，均为 NOT_RUN。",
            $"命令：`{CaptureCommand}`。EXIT=0 表示捕获测试成功，不代替视觉签署。",
            "| file | head | frontend | group | component/page | state | mode | viewport | raster-size | theme | frame | command | EXIT | SHA256 | signed_by | signed_at |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"};
        foreach(var shot in shots)
        {
            var path=Path.Combine(output,shot.File);shot.Image.Save(path);
            var sha=Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(path)));
            rows.Add($"| `{shot.File}` | `{head}` | builtin.fluent | {shot.Group} | {shot.Name} | {shot.State} | {shot.Mode} | {(shot.Group == "decor" ? "1280x900" : $"{shot.Image.PixelSize.Width}x{shot.Image.PixelSize.Height}")} | {shot.Image.PixelSize.Width}x{shot.Image.PixelSize.Height} | {shot.Theme} | {shot.Frame} | `{CaptureCommand}` | 0 | {sha} | NOT_RUN | — |");
        }
        File.WriteAllLines(Path.Combine(output,"visual-inventory.md"),rows);
        Assert.Equal(shots.Count,Directory.EnumerateFiles(output,"*.png").Count());
        Assert.Equal(shots.Count,rows.Count(r=>r.StartsWith("| `")));
        var changes=Residual2Evidence.Git("status","--porcelain","--","verification").Split('\n',StringSplitOptions.RemoveEmptyEntries);
        Assert.All(changes,line=>Assert.Contains("verification/FEA-06-RESIDUAL-2/visuals/",line));
    }
}
