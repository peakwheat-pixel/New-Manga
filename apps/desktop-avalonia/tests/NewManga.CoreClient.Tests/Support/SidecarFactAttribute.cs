using Xunit;

namespace NewManga.CoreClient.Tests.Support;

/// <summary>
/// Integration fact that self-skips when the AC11 unlabelled sidecar copy is unavailable. This keeps
/// a bare `dotnet test` green (explicit Skip with a reason) while scripts/test.ps1 runs everything.
/// </summary>
public sealed class SidecarFactAttribute : FactAttribute
{
    public SidecarFactAttribute()
    {
        if (!SidecarFixture.TryGetSidecarDirectory(out _, out var reason))
        {
            Skip = reason;
        }
    }
}
