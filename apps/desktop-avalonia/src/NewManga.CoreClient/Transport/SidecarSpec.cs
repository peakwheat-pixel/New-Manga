namespace NewManga.CoreClient.Transport;

/// <summary>
/// Everything needed to spawn one sidecar: executable, isolated environment (data roots and catalog),
/// diagnostic locations and timeouts. The environment is fully explicit so the Core never falls back
/// to the user's real data root during tests or a read-only S1 run.
/// </summary>
public sealed class SidecarSpec
{
    public const string CoreServiceName = "core_service";
    public const string HostBridgeName = "host_bridge";

    public required string Name { get; init; }

    public required string ExecutablePath { get; init; }

    public string? WorkingDirectory { get; init; }

    public IReadOnlyDictionary<string, string> Environment { get; init; } =
        new Dictionary<string, string>(StringComparer.Ordinal);

    public IReadOnlyList<string> AdditionalArguments { get; init; } = Array.Empty<string>();

    public required string StderrLogPath { get; init; }

    /// <summary>Optional NDJSON file capturing every request/response frame for AC3 evidence.</summary>
    public string? WireLogPath { get; init; }

    public TimeSpan StartupTimeout { get; init; } = TimeSpan.FromSeconds(30);

    public TimeSpan RequestTimeout { get; init; } = TimeSpan.FromSeconds(30);
}
