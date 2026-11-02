using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using Avalonia.Threading;
using NewManga.Appearance;
using NewManga.App.Services;
using NewManga.CoreClient;
using NewManga.DesignSystem.Theming;
using Xunit;
using DsAppearanceMode = NewManga.DesignSystem.Theming.AppearanceMode;

namespace NewManga.App.Tests;

/// <summary>Real App resource manifest, isolated appearance store and deterministic reader input.</summary>
internal sealed class Residual2Evidence : IDisposable
{
    public static string Root
    {
        get
        {
            var cursor = new DirectoryInfo(AppContext.BaseDirectory);
            while (cursor is not null && !File.Exists(Path.Combine(cursor.FullName, "doc/tasks/FEA-06-RESIDUAL-2.md"))) cursor = cursor.Parent;
            return cursor?.FullName ?? throw new DirectoryNotFoundException();
        }
    }
    private readonly string _temporaryRoot;
    public DesignSystemThemeManager Manager { get; }
    public AppearanceCoordinator Appearance { get; }
    public string Theme { get; }
    public Color CanvasColor => Token("Nm.Color.Bg.Canvas");

    private Residual2Evidence(string theme)
    {
        Theme = theme;
        var app = Application.Current!;
        app.Resources.MergedDictionaries.Clear();
        var manifest = File.ReadAllText(Path.Combine(Root, "apps/desktop-avalonia/src/NewManga.App/App.axaml"));
        var includes = Regex.Matches(manifest, "ResourceInclude\\s+Source=\"(avares://[^\"]+)\"");
        Assert.True(includes.Count >= 3);
        foreach (Match match in includes)
            app.Resources.MergedDictionaries.Add((ResourceDictionary)AvaloniaXamlLoader.Load(new Uri(match.Groups[1].Value)));
        Manager = new DesignSystemThemeManager(app);
        Assert.True(Manager.Initialize(theme == "light" ? DsAppearanceMode.Light : DsAppearanceMode.Dark), Manager.LastError);
        _temporaryRoot = Path.Combine(Root + ".workspace", "task-env", "FEA-06-RESIDUAL-2", Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_temporaryRoot);
        Appearance = new AppearanceCoordinator(new AppearanceStore(Path.Combine(_temporaryRoot, AppearanceStore.FileName)));
        Appearance.Reload();
    }

    public static async Task<Residual2Evidence> Create(string theme)
    {
        var scope = new Residual2Evidence(theme);
        await scope.Appearance.SaveAsync(AppearanceDefaults.Settings with
        {
            Mode = theme == "light" ? NewManga.Appearance.AppearanceMode.Light : NewManga.Appearance.AppearanceMode.Dark,
            MotionMode = MotionMode.Full, MotionCategories = MotionCategories.All,
        });
        return scope;
    }
    public Color Token(string key)
    {
        var app = Application.Current!;
        Assert.True(app.TryGetResource(key, app.ActualThemeVariant, out var value));
        return Assert.IsAssignableFrom<ISolidColorBrush>(value).Color;
    }
    public static FakeHostController Host()
    {
        var host = new FakeHostController(FakeHostController.ReadySnapshot("Sample Manga"));
        var png = PagePng();
        host.ReaderBooksByChapterId["chapter-key"] = new ReaderBookData("book-1", "Sample Manga", "chapter-key", "Chapter 1", "fit-page",
        [new ReaderPageData("page-1", 0, 320, 480, _ => Task.FromResult<byte[]?>(png)),
         new ReaderPageData("page-2", 1, 320, 480, _ => Task.FromResult<byte[]?>(png))]);
        return host;
    }
    // Test-owned line-art fixture, generated in memory; no production image asset or user path.
    public static byte[] PagePng()
    {
        using var bitmap = new WriteableBitmap(new PixelSize(320, 480), new Vector(96, 96), PixelFormat.Bgra8888, AlphaFormat.Opaque);
        using (var buffer = bitmap.Lock())
        {
            var data = new byte[buffer.RowBytes * 480];
            for (var y = 0; y < 480; y++) for (var x = 0; x < 320; x++)
            {
                var panel = x >= 18 && x < 302 && y >= 18 && y < 462;
                var ink = panel && (x < 22 || x >= 298 || y < 22 || y >= 458 || (y >= 232 && y < 238)
                    || (y < 232 && x >= 156 && x < 162) || (y > 270 && y < 410 && Math.Abs(x - 160) < (y - 265) / 3));
                byte c = ink ? (byte)35 : (byte)245;
                var i = y * buffer.RowBytes + x * 4;
                data[i] = data[i + 1] = data[i + 2] = c; data[i + 3] = 255;
            }
            Marshal.Copy(data, 0, buffer.Address, data.Length);
        }
        using var stream = new MemoryStream(); bitmap.Save(stream); return stream.ToArray();
    }
    public static byte[] Bytes(Bitmap bitmap)
    {
        using var stream = new MemoryStream(); bitmap.Save(stream); return stream.ToArray();
    }
    public static byte[] Pixels(Bitmap bitmap)
    {
        var data = new byte[bitmap.PixelSize.Width * bitmap.PixelSize.Height * 4];
        var pin = GCHandle.Alloc(data, GCHandleType.Pinned);
        try { bitmap.CopyPixels(new PixelRect(bitmap.PixelSize), pin.AddrOfPinnedObject(), data.Length, bitmap.PixelSize.Width * 4); }
        finally { pin.Free(); }
        return data;
    }
    public static int ChangedPixels(Bitmap first, Bitmap second, int tolerance = 8, PixelRect? region = null)
    {
        Assert.Equal(first.PixelSize, second.PixelSize);
        var a = Pixels(first); var b = Pixels(second); var r = (region ?? new PixelRect(first.PixelSize)).Intersect(new PixelRect(first.PixelSize)); var count = 0;
        for (var y = r.Y; y < r.Bottom; y++) for (var x = r.X; x < r.Right; x++)
        {
            var i = (y * first.PixelSize.Width + x) * 4;
            if (Enumerable.Range(0, 3).Any(c => Math.Abs(a[i + c] - b[i + c]) > tolerance)) count++;
        }
        return count;
    }
    public static Bitmap Capture(Window window)
    {
        window.UpdateLayout(); Dispatcher.UIThread.RunJobs();
        return window.CaptureRenderedFrame() ?? throw new InvalidOperationException("frame capture failed");
    }
    public static string Git(params string[] arguments)
    {
        var start = new ProcessStartInfo("git") { WorkingDirectory = Root, RedirectStandardOutput = true, UseShellExecute = false, CreateNoWindow = true };
        foreach (var arg in arguments) start.ArgumentList.Add(arg);
        using var process = Process.Start(start)!; var output = process.StandardOutput.ReadToEnd(); process.WaitForExit(); Assert.Equal(0, process.ExitCode); return output.Trim();
    }
    public static Dictionary<string,string> OldEvidence() => Directory.EnumerateFiles(Path.Combine(Root, "verification/FEA-06"), "*", SearchOption.AllDirectories)
        .ToDictionary(path => Path.GetRelativePath(Root, path), path => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path))));
    public void Dispose()
    {
        Manager.ResetToDefaults(); Manager.Dispose();
        Directory.Delete(_temporaryRoot, recursive: true);
    }
}
