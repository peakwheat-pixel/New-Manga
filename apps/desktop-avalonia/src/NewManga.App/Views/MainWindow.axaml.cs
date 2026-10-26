using Avalonia;
using Avalonia.Controls;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.Theme;

namespace NewManga.App.Views;

public partial class MainWindow : Window
{
    public const string ChineseVector = "雾港来信・日本語テスト";

    private readonly IHostController _controller;
    private readonly AppOptions _options;

    /// <summary>Design-time / XAML runtime-loader constructor (never starts a sidecar).</summary>
    public MainWindow()
        : this(NullHostController.Instance, new AppOptions())
    {
    }

    public MainWindow(IHostController controller, AppOptions options)
    {
        _controller = controller;
        _options = options;
        InitializeComponent();

        BuildLine.Text = $"S1 · Avalonia 11.3.22 · C#/.NET 9 · Python Core · data-root={DescribeDataRoot()}";
        _controller.Changed += OnControllerChanged;
        Loaded += OnLoaded;
        Closed += OnClosed;
        ApplySnapshot();
    }

    public IHostController Controller => _controller;

    private string DescribeDataRoot() =>
        string.IsNullOrWhiteSpace(_options.DataRoot) ? "（默认只读数据根）" : "（隔离数据根）";

    private async void OnLoaded(object? sender, Avalonia.Interactivity.RoutedEventArgs e)
    {
        await _controller.StartAsync();
        if (_options.AutoRoundTrip)
        {
            await _controller.TryChineseRoundTripAsync(ChineseVector);
        }

        ApplySnapshot();
    }

    private void OnControllerChanged(object? sender, EventArgs e) => Dispatcher.UIThread.Post(ApplySnapshot);

    private void OnClosed(object? sender, EventArgs e)
    {
        try
        {
            _controller.DisposeAsync().AsTask().GetAwaiter().GetResult();
        }
        catch (Exception ex) when (ex is InvalidOperationException or TimeoutException or AggregateException)
        {
            // best-effort shutdown; process exit follows
        }
    }

    private void ApplySnapshot()
    {
        var snapshot = _controller.Snapshot;
        StatusText.Text = snapshot.StatusLine;
        ModeText.Text = snapshot.ModeLine;

        var items = new List<string>(snapshot.Books.Count);
        foreach (var book in snapshot.Books)
        {
            var pages = book.PageCount is { } count ? $"{count} 页" : "页数未知";
            items.Add($"{book.Title}  ·  {pages}  ·  {book.BookId}");
        }

        BooksList.ItemsSource = items;
        if (items.Count == 0 && snapshot.State == HostViewState.Ready)
        {
            BooksList.ItemsSource = new List<string> { "（空书架：隔离数据根中尚无书目）" };
        }

        RoundTripText.Text = snapshot.LastChineseRoundTrip ?? "尚未执行";
        ErrorCodeText.Text = snapshot.ErrorCode is null ? "无错误" : $"错误码：{snapshot.ErrorCode}";
        ErrorMessageText.Text = snapshot.ErrorMessage ?? "—";
        WireText.Text = $"wire: {snapshot.WireFrameCount} frames · requests ASCII-only={snapshot.AllRequestsAsciiOnly}";
        FooterText.Text = snapshot.State switch
        {
            HostViewState.Ready => "host ready",
            HostViewState.Starting => "starting",
            HostViewState.AlreadyRunning => "already running",
            _ => "failed",
        };
    }

    private void OnRefresh(object? sender, Avalonia.Interactivity.RoutedEventArgs e) => _ = RefreshAsync();

    private async Task RefreshAsync()
    {
        await _controller.RefreshBooksAsync();
        ApplySnapshot();
    }

    private void OnRoundTrip(object? sender, Avalonia.Interactivity.RoutedEventArgs e) => _ = RoundTripAsync();

    private async Task RoundTripAsync()
    {
        await _controller.TryChineseRoundTripAsync(ChineseVector);
        ApplySnapshot();
    }

    private void OnLightTheme(object? sender, Avalonia.Interactivity.RoutedEventArgs e) => ApplyTheme(ThemeManager.Light);

    private void OnDarkTheme(object? sender, Avalonia.Interactivity.RoutedEventArgs e) => ApplyTheme(ThemeManager.Dark);

    private void OnSaberTheme(object? sender, Avalonia.Interactivity.RoutedEventArgs e) => ApplyTheme(ThemeManager.SaberPurple);

    private void ApplyTheme(ThemeTokens tokens)
    {
        if (Application.Current is { } application)
        {
            ThemeManager.Apply(application, tokens);
        }
    }
}
