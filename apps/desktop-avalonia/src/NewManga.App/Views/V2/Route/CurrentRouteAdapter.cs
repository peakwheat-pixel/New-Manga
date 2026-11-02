using NewManga.App.Shell.V2;

namespace NewManga.App.Views.V2.Route;

/// <summary>Presentation route value mapped from the existing ShellDeepLink boundary.</summary>
public sealed record CurrentRouteAddress(
    SpaceId Space,
    StudioMode Mode,
    string? BookId,
    string? ChapterId,
    int? PageNumber,
    string? PageId,
    string? RegionId);

/// <summary>
/// Read-only route adapter for a future frontend scheme. Parsing and wire format remain owned by
/// ShellDeepLink; this mapper does not navigate, load data, or change runtime routing.
/// </summary>
public static class CurrentRouteAdapter
{
    public static bool TryMap(string? query, out CurrentRouteAddress address)
    {
        if (!ShellDeepLink.TryParse(query, out var link))
        {
            address = default!;
            return false;
        }

        address = Map(link);
        return true;
    }

    public static CurrentRouteAddress Map(ShellDeepLink link)
    {
        ArgumentNullException.ThrowIfNull(link);
        return new(link.Space, link.Mode, link.BookId, link.ChapterId, link.Page, link.PageId, link.RegionId);
    }

    public static ShellDeepLink ToShellDeepLink(CurrentRouteAddress address)
    {
        ArgumentNullException.ThrowIfNull(address);
        return new ShellDeepLink
        {
            Space = address.Space,
            Mode = address.Mode,
            BookId = address.BookId,
            ChapterId = address.ChapterId,
            Page = address.PageNumber,
            PageId = address.PageId,
            RegionId = address.RegionId,
        };
    }
}
