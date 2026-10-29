using NewManga.CoreClient.Diagnostics;
using NewManga.CoreClient.Transport;

namespace NewManga.CoreClient;

/// <summary>One directory holding the packaged Python Core sidecars (core_service + host_bridge).</summary>
public sealed record SidecarBundle(
    string Directory,
    string CoreServicePath,
    string HostBridgePath,
    string CatalogLoaderPath);

/// <summary>
/// Sidecar discovery order (AC7 decision record), first match wins:
/// 1. explicit override (tests / ops / packaging),
/// 2. <c>NEWMANGA_CORE_SIDECAR_DIR</c> environment variable,
/// 3. <c>&lt;app dir&gt;/core-sidecar</c> (packaged layout, see apps/desktop/src-tauri packing),
/// 4. <c>&lt;app dir&gt;/resources/core-sidecar</c> (Tauri resource layout).
/// Absolute paths never reach the UI layer: failures carry a typed code only.
/// </summary>
public static class SidecarLocator
{
    public const string DirectoryEnvironmentVariable = "NEWMANGA_CORE_SIDECAR_DIR";
    public const string CoreServiceFileName = "core_service.exe";
    public const string HostBridgeFileName = "host_bridge.exe";
    public const string CatalogLoaderFileName = "catalog_loader.exe";

    public static SidecarBundle Locate(string? explicitDirectory = null)
    {
        var candidates = new List<string>();
        if (!string.IsNullOrWhiteSpace(explicitDirectory))
        {
            candidates.Add(explicitDirectory!);
        }

        var fromEnvironment = Environment.GetEnvironmentVariable(DirectoryEnvironmentVariable);
        if (!string.IsNullOrWhiteSpace(fromEnvironment))
        {
            candidates.Add(fromEnvironment!);
        }

        candidates.Add(Path.Combine(AppContext.BaseDirectory, "core-sidecar"));
        candidates.Add(Path.Combine(AppContext.BaseDirectory, "resources", "core-sidecar"));

        foreach (var candidate in candidates)
        {
            var directory = Path.GetFullPath(candidate);
            var core = Path.Combine(directory, CoreServiceFileName);
            var bridge = Path.Combine(directory, HostBridgeFileName);
            if (File.Exists(core) && File.Exists(bridge))
            {
                var loader = Path.Combine(directory, CatalogLoaderFileName);
                return new SidecarBundle(directory, core, bridge, loader);
            }
        }

        throw new SidecarException(
            SidecarErrorCode.SidecarBundleMissing,
            "sidecar-bundle",
            $"no sidecar directory with {CoreServiceFileName} and {HostBridgeFileName} found in {candidates.Count} candidate locations");
    }
}
