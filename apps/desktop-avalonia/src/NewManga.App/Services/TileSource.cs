using NewManga.Host.Resources;

namespace NewManga.App.Services;

/// <summary>S5-A: UI-facing tile source. Bytes come from the Host tile channel (digest verified); no path/digest here.</summary>
public interface ITileSource
{
    int TileCount { get; }

    byte[]? ReadTile(int index);
}

public sealed class TileChannelSource : ITileSource
{
    private readonly TileChannel _channel;
    private readonly string _handle;

    public TileChannelSource(TileChannel channel, string handle)
    {
        _channel = channel;
        _handle = handle;
        TileCount = channel.Describe(handle)?.TileCount ?? 0;
    }

    public int TileCount { get; }

    public byte[]? ReadTile(int index)
    {
        try
        {
            return _channel.ReadTile(_handle, index).Bytes;
        }
        catch (TileAccessException)
        {
            return null;
        }
    }
}

/// <summary>Fallback source for local fixtures when the Host tile channel is disabled.</summary>
public sealed class FixtureTileSource : ITileSource
{
    private readonly IReadOnlyList<string> _files;

    public FixtureTileSource(string directory)
    {
        _files = Directory.Exists(directory)
            ? Directory.GetFiles(directory, "*.jpg").OrderBy(path => path, StringComparer.Ordinal).ToArray()
            : Array.Empty<string>();
    }

    public int TileCount => _files.Count;

    public byte[]? ReadTile(int index) =>
        index >= 0 && index < _files.Count ? File.ReadAllBytes(_files[index]) : null;
}
