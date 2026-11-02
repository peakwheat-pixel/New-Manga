using Xunit;

namespace NewManga.Host.Tests.Support;

/// <summary>
/// Host integration fact that self-skips when the sidecar fixture (or its env var) is unavailable.
/// </summary>
public sealed class HostSidecarFactAttribute : FactAttribute
{
    public HostSidecarFactAttribute()
    {
        if (!HostFixture.TryGetSidecarDirectory(out _, out var reason))
        {
            Skip = reason;
        }
    }
}
