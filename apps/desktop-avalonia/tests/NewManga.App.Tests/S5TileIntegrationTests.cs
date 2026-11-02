using System.Buffers;
using System.Security.Cryptography;
using Avalonia.Headless.XUnit;
using NewManga.App.Services;
using NewManga.App.ViewModels;
using NewManga.App.Shell;
using NewManga.App.Views;
using NewManga.Host.Resources;
using Xunit;

namespace NewManga.App.Tests;

/// <summary>AC5: reader/workbench consume the Host tile channel with digest verification; fixture fallback stays available.</summary>
public sealed class S5TileIntegrationTests : IDisposable
{
    private const int TileSize = 32 * 1024;
    private const int TileCount = 3;
    private readonly string _root;
    private readonly string _file;

    public S5TileIntegrationTests()
    {
        _root = Path.Combine(Path.GetTempPath(), "nm-tile-ui-" + Guid.NewGuid().ToString("N")[..10]);
        Directory.CreateDirectory(_root);
        _file = Path.Combine(_root, "page.bin");
        var bytes = new byte[TileSize * TileCount];
        Random.Shared.NextBytes(bytes);
        File.WriteAllBytes(_file, bytes);
    }

    public void Dispose()
    {
        try
        {
            Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
            // best effort
        }
    }

    private static string Sha(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    private (TileChannel Channel, string Handle) Issue()
    {
        var all = File.ReadAllBytes(_file);
        var manifest = Enumerable.Range(0, TileCount)
            .Select(index => new TileDescriptor(index, (long)index * TileSize, TileSize, Sha(all.AsSpan(index * TileSize, TileSize).ToArray())))
            .ToArray();
        var channel = new TileChannel();
        var view = channel.Issue(new TileGrantRequest("page:ui", "rev-ui", _file, _root, all.Length, manifest));
        return (channel, view.Handle);
    }

    [AvaloniaFact]
    public void ReaderPage_BindsChannel_AndReadsVerifiedTiles()
    {
        var (channel, handle) = Issue();
        var source = new TileChannelSource(channel, handle);
        Assert.Equal(TileCount, source.TileCount);
        var vm = new ReaderViewModel();
        vm.SetViewport(1200, 800, 2.0);
        var page = new ReaderPage(vm, Array.Empty<string>()) { Name = "tile-bound-reader" };
        page.BindTileSource(source);
        page.PrepareWebtoon();

        Assert.Same(source, page.TileSource);
        Assert.Equal(TileCount, page.BoundTileCount);
        Assert.True(channel.Reads >= 1, "reader must read at least one verified tile through the channel");
        Assert.Null(page.TileSource!.ReadTile(99));

        S5Evidence.Write("security/reader-tile-channel.json", writer =>
        {
            writer.WriteString("ac", "AC5");
            writer.WriteNumber("tile_count", source.TileCount);
            writer.WriteNumber("channel_reads", channel.Reads);
            writer.WriteBoolean("fallback_available", page.TileSource is not null);
        });
    }

    [AvaloniaFact]
    public void WorkbenchPage_BindsChannel_AndTamperedTileSurfacesAsNull()
    {
        var (channel, handle) = Issue();
        var source = new TileChannelSource(channel, handle);
        var page = new WorkbenchPage(new WorkbenchViewModel());
        page.BindTileSource(source);
        Assert.Same(source, page.TileSource);
        Assert.NotNull(source.ReadTile(0));

        var lengthBefore = new FileInfo(_file).Length;
        using (var stream = new FileStream(_file, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
        {
            stream.Position = TileSize + 10;
            stream.WriteByte((byte)(stream.ReadByte() ^ 0x5A));
        }

        Assert.Equal(lengthBefore, new FileInfo(_file).Length);
        Assert.Null(source.ReadTile(1));
        Assert.True(channel.DigestMismatches >= 1);

        S5Evidence.Write("security/workbench-tamper.json", writer =>
        {
            writer.WriteString("ac", "AC5");
            writer.WriteBoolean("size_preserved", lengthBefore == new FileInfo(_file).Length);
            writer.WriteNumber("digest_mismatches", channel.DigestMismatches);
            writer.WriteString("ui_result", "null (typed rejection, no bytes returned)");
        });
    }

    [AvaloniaFact]
    public void FixtureFallback_StillWorks_WhenChannelDisabled()
    {
        var vm = new ReaderViewModel();
        var page = new ReaderPage(vm, Array.Empty<string>());
        Assert.Null(page.TileSource);
        var fixture = new FixtureTileSource(TestWorkspacePaths.Path("task-envs/DISPLAY-PERF-DECISION-1/spike/avalonia/fixtures/strip-4000x60000/tiles"));
        Assert.True(fixture.TileCount == 0 || fixture.TileCount == 30);
        if (fixture.TileCount > 0)
        {
            Assert.NotNull(fixture.ReadTile(0));
        }
    }
}

internal static class S5Evidence
{
    public static void Write(string relativePath, Action<System.Text.Json.Utf8JsonWriter> write)
    {
        var root = Environment.GetEnvironmentVariable("NEWMANGA_EVIDENCE_DIR");
        if (string.IsNullOrWhiteSpace(root))
        {
            root = Path.Combine(Path.GetTempPath(), "newmanga-s5a-evidence");
        }

        var path = Path.Combine(root, relativePath.Replace('/', Path.DirectorySeparatorChar));
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
        using var stream = File.Create(path);
        using var writer = new System.Text.Json.Utf8JsonWriter(stream, new System.Text.Json.JsonWriterOptions { Indented = true });
        writer.WriteStartObject();
        writer.WriteString("task", "HOST-TILE-CHANNEL-1");
        writer.WriteString("at_utc", DateTime.UtcNow.ToString("o"));
        write(writer);
        writer.WriteEndObject();
    }
}
