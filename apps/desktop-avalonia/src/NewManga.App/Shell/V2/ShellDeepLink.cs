namespace NewManga.App.Shell.V2;

/// <summary>
/// V11R-B-1: deep-link / evidence entry point. Accepts the screen-spec query shape
/// <c>?space=&amp;mode=&amp;book=&amp;chapter=&amp;page=&amp;region=</c> so screenshots and the
/// integration task (V11R-INT-1) can land on an exact object instead of only a space (FUSION_SPEC §3
/// "寻址唯一性"). Parsing is pure and fully unit-tested.
/// </summary>
public sealed record ShellDeepLink
{
    public SpaceId Space { get; init; } = SpaceId.Library;

    public StudioMode Mode { get; init; } = StudioMode.Page;

    public string? BookId { get; init; }

    public string? ChapterId { get; init; }

    /// <summary>1-based human page number (page 1 = first page).</summary>
    public int? Page { get; init; }

    public string? PageId { get; init; }

    public string? RegionId { get; init; }

    public static ShellDeepLink Empty { get; } = new();

    public static bool TryParse(string? query, out ShellDeepLink link)
    {
        link = Empty;
        if (string.IsNullOrWhiteSpace(query))
        {
            return false;
        }

        var text = query.Trim();
        var question = text.IndexOf('?', StringComparison.Ordinal);
        if (question >= 0)
        {
            text = text[(question + 1)..];
        }

        if (text.StartsWith('?') || text.StartsWith('&'))
        {
            text = text[1..];
        }

        if (text.Length == 0)
        {
            return false;
        }

        var values = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        foreach (var pair in text.Split('&', StringSplitOptions.RemoveEmptyEntries))
        {
            var separator = pair.IndexOf('=', StringComparison.Ordinal);
            if (separator <= 0)
            {
                continue;
            }

            var key = pair[..separator].Trim();
            var value = Uri.UnescapeDataString(pair[(separator + 1)..].Trim());
            if (key.Length > 0 && value.Length > 0)
            {
                values[key] = value;
            }
        }

        if (values.Count == 0)
        {
            return false;
        }

        var space = SpaceId.Library;
        if (values.TryGetValue("space", out var spaceText))
        {
            if (!TryParseSpace(spaceText, out space))
            {
                return false;
            }
        }

        var mode = StudioMode.Page;
        if (values.TryGetValue("mode", out var modeText))
        {
            if (!TryParseMode(modeText, out mode))
            {
                return false;
            }
        }

        int? page = null;
        if (values.TryGetValue("page", out var pageText))
        {
            if (!int.TryParse(pageText, out var pageNumber) || pageNumber < 0)
            {
                return false;
            }

            page = pageNumber == 0 ? 1 : pageNumber;
        }

        values.TryGetValue("book", out var book);
        values.TryGetValue("chapter", out var chapter);
        values.TryGetValue("page_id", out var pageId);
        values.TryGetValue("region", out var region);

        link = new ShellDeepLink
        {
            Space = space,
            Mode = mode,
            BookId = Normalize(book),
            ChapterId = Normalize(chapter),
            Page = page,
            PageId = Normalize(pageId),
            RegionId = Normalize(region),
        };
        return true;
    }

    public string ToQuery()
    {
        var parts = new List<string>
        {
            $"space={Space.ToString().ToLowerInvariant()}",
            $"mode={Mode.ToString().ToLowerInvariant()}",
        };
        if (BookId is not null)
        {
            parts.Add($"book={Uri.EscapeDataString(BookId)}");
        }

        if (ChapterId is not null)
        {
            parts.Add($"chapter={Uri.EscapeDataString(ChapterId)}");
        }

        if (Page is { } page)
        {
            parts.Add($"page={page}");
        }

        if (PageId is not null)
        {
            parts.Add($"page_id={Uri.EscapeDataString(PageId)}");
        }

        if (RegionId is not null)
        {
            parts.Add($"region={Uri.EscapeDataString(RegionId)}");
        }

        return "?" + string.Join("&", parts);
    }

    private static bool TryParseSpace(string text, out SpaceId space)
    {
        switch (text.Trim().ToLowerInvariant())
        {
            case "library":
            case "资料柜":
                space = SpaceId.Library;
                return true;
            case "studio":
            case "工位":
                space = SpaceId.Studio;
                return true;
            case "console":
            case "控制台":
                space = SpaceId.Console;
                return true;
            default:
                space = SpaceId.Library;
                return false;
        }
    }

    private static bool TryParseMode(string text, out StudioMode mode)
    {
        switch (text.Trim().ToLowerInvariant())
        {
            case "page":
            case "页面":
                mode = StudioMode.Page;
                return true;
            case "batch":
            case "批次":
                mode = StudioMode.Batch;
                return true;
            default:
                mode = StudioMode.Page;
                return false;
        }
    }

    private static string? Normalize(string? value) =>
        string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}
