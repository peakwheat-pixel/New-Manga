using System.Text.Json;
using System.Text.Json.Serialization;

namespace NewManga.Presentation.Avalonia.Windows;

/// <summary>One window's persisted placement (FEA-07 AC5 / proposal §7.3).</summary>
public sealed record WindowStateMemento(
    int X,
    int Y,
    int Width,
    int Height,
    string? DisplayId,
    double Scale,
    bool IsMaximized);

/// <summary>
/// FEA-07 AC5: persists per-window placement next to the theme home so a restart on the same or a
/// different display topology restores a safe position (atomic write, corrupt file tolerated).
/// </summary>
public sealed class WindowStateMementoStore
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
        DefaultIgnoreCondition = JsonIgnoreCondition.Never,
        Converters = { new JsonStringEnumConverter() },
    };

    private readonly string _path;

    public WindowStateMementoStore(string path)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(path);
        _path = Path.GetFullPath(path);
    }

    public string FilePath => _path;

    public WindowStateMemento? TryLoad(out string? error)
    {
        error = null;
        if (!File.Exists(_path))
        {
            return null;
        }

        try
        {
            var json = File.ReadAllText(_path);
            return JsonSerializer.Deserialize<WindowStateMemento>(json, JsonOptions);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException)
        {
            error = ex.Message;
            return null;
        }
    }

    public void Save(WindowStateMemento memento)
    {
        ArgumentNullException.ThrowIfNull(memento);
        var directory = Path.GetDirectoryName(_path);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        var temp = _path + ".tmp";
        File.WriteAllText(temp, JsonSerializer.Serialize(memento, JsonOptions));
        File.Move(temp, _path, overwrite: true);
    }
}
