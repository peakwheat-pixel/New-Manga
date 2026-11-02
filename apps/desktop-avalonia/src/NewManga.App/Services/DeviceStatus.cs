using System.Text.Json;

namespace NewManga.App.Services;

/// <summary>
/// GPU-ORT-PROBE-1: the packaged device probe recorded in the package's
/// <c>VERSION.json</c> (written by <c>scripts/package.ps1</c> from
/// <c>scripts/gpu_probe.py</c>, i.e. ONNX Runtime's execution-provider list).
/// The settings page renders it so a torch-free packaged build reports
/// "DirectML 可用" instead of "unavailable".
/// </summary>
public sealed record DeviceStatusInfo(
    string State,
    string Name,
    int? TotalMemoryMb,
    IReadOnlyList<string> Providers,
    string Detail)
{
    public bool Available => string.Equals(State, "available", StringComparison.Ordinal);

    public bool HasDirectMl =>
        Providers.Any(provider => string.Equals(provider, "DmlExecutionProvider", StringComparison.Ordinal));

    public string DisplayText
    {
        get
        {
            if (Available)
            {
                var label = HasDirectMl ? "DirectML" : Providers.FirstOrDefault() ?? "GPU";
                var name = string.IsNullOrWhiteSpace(Name) ? "GPU" : Name;
                return $"GPU：{name} · {label} 可用";
            }

            return $"GPU：不可用（{Detail}）";
        }
    }
}

public static class DeviceStatus
{
    public const string FileName = "VERSION.json";

    /// <summary>Reads the packaged device probe; null when not a packaged build (dev run).</summary>
    public static DeviceStatusInfo? Load(string? baseDirectory = null)
    {
        foreach (var candidate in Candidates(baseDirectory ?? AppContext.BaseDirectory))
        {
            try
            {
                if (!File.Exists(candidate))
                {
                    continue;
                }

                using var document = JsonDocument.Parse(File.ReadAllText(candidate));
                if (document.RootElement.ValueKind == JsonValueKind.Object &&
                    document.RootElement.TryGetProperty("devices", out var devices) &&
                    devices.ValueKind == JsonValueKind.Object)
                {
                    return Parse(devices);
                }
            }
            catch (Exception ex) when (
                ex is IOException or UnauthorizedAccessException or JsonException or ArgumentException or NotSupportedException)
            {
                // best effort: a malformed package metadata file must not break settings
            }
        }

        return null;
    }

    private static IEnumerable<string> Candidates(string baseDirectory)
    {
        // The package layout puts VERSION.json at the stage root (<stage>/app/NewManga.App.exe),
        // while a self-contained single-file host can report its own directory here too; both
        // shapes plus the "metadata copied next to the exe" shape are covered.
        yield return Path.Combine(baseDirectory, FileName);
        var parent = Directory.GetParent(baseDirectory)?.FullName;
        if (parent is not null)
        {
            yield return Path.GetFullPath(Path.Combine(parent, FileName));
        }

        var grandParent = parent is null ? null : Directory.GetParent(parent)?.FullName;
        if (grandParent is not null)
        {
            yield return Path.GetFullPath(Path.Combine(grandParent, FileName));
        }
    }

    private static DeviceStatusInfo Parse(JsonElement devices)
    {
        string state = string.Empty;
        string name = string.Empty;
        string detail = string.Empty;
        int? memory = null;
        var providers = new List<string>();

        if (devices.TryGetProperty("gpu", out var gpu) && gpu.ValueKind == JsonValueKind.Object)
        {
            state = ReadString(gpu, "state");
            name = ReadString(gpu, "name");
            detail = ReadString(gpu, "detail");
            if (gpu.TryGetProperty("total_memory_mb", out var memoryElement) &&
                memoryElement.ValueKind == JsonValueKind.Number &&
                memoryElement.TryGetInt32(out var parsedMemory))
            {
                memory = parsedMemory;
            }
        }

        if (devices.TryGetProperty("onnxruntime_providers", out var providerArray) &&
            providerArray.ValueKind == JsonValueKind.Array)
        {
            foreach (var provider in providerArray.EnumerateArray())
            {
                if (provider.ValueKind == JsonValueKind.String && provider.GetString() is { Length: > 0 } text)
                {
                    providers.Add(text);
                }
            }
        }

        return new DeviceStatusInfo(state, name, memory, providers, detail);
    }

    private static string ReadString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString() ?? string.Empty
            : string.Empty;
}
