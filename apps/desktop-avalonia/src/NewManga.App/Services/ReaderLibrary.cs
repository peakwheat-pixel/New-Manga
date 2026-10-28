using NewManga.CoreClient;

namespace NewManga.App.Services;

/// <summary>
/// READER-LIBRARY-WIRE-1 AC1: one page of a real library book as the UI needs it (no OS path,
/// no digest: bytes are loaded through the Host resource channel on demand).
/// </summary>
public sealed record ReaderPageData(
    string PageId,
    int Order,
    int WidthPx,
    int HeightPx,
    Func<CancellationToken, Task<byte[]?>>? LoadImageAsync = null)
{
    public string Label => $"{Order + 1} · {WidthPx}×{HeightPx}";
}

/// <summary>
/// READER-LIBRARY-WIRE-1 AC1: real reader payload from Host/CoreClient
/// (ListBooks → list_chapters → GetReaderProjection), pages load lazily.
/// READER-PROGRESS-1: carries the Core-provided initial position so the page opens where the
/// (book, chapter, mode) progress left off.
/// </summary>
public sealed record ReaderBookData(
    string BookId,
    string BookTitle,
    string ChapterId,
    string ChapterTitle,
    string Layout,
    IReadOnlyList<ReaderPageData> Pages)
{
    /// <summary>READER-PROGRESS-1: page index to open on (0 = chapter start).</summary>
    public int InitialPageIndex { get; init; }

    /// <summary>READER-PROGRESS-1: webtoon logical-page scroll offset in original image pixels.</summary>
    public double InitialScrollOffsetY { get; init; }

    /// <summary>READER-PROGRESS-1: persisted page id echoed by the projection (null = never read).</summary>
    public string? SavedPageId { get; init; }

    /// <summary>READER-PROGRESS-1: true when the Core had a durable row for this (book, chapter, mode).</summary>
    public bool HasSavedProgress => !string.IsNullOrEmpty(SavedPageId);

    public bool IsWebtoon => Layout.Contains("webtoon", StringComparison.OrdinalIgnoreCase);

    public string Summary =>
        $"{BookTitle} · {ChapterTitle} · {Pages.Count} 页 · {(IsWebtoon ? "webtoon 长滚动" : Layout)}";

    public static ReaderBookData FromProjection(
        BookSummary book,
        ChapterSummary chapter,
        ReaderProjection projection,
        Func<string, CancellationToken, Task<byte[]?>> loadPage)
    {
        var pages = projection.Pages
            .OrderBy(page => page.Order)
            .Select(page => new ReaderPageData(
                page.PageId,
                page.Order,
                page.WidthPx,
                page.HeightPx,
                cancellationToken => loadPage(page.PageId, cancellationToken)))
            .ToList();

        // READER-PROGRESS-1 AC2: clamp. The Core already falls back to the first page when the saved
        // page left the chapter; the client repeats the index clamp defensively (page count shrink).
        var initialIndex = 0;
        var savedPageId = (string?)null;
        if (!string.IsNullOrEmpty(projection.InitialPageId))
        {
            var found = -1;
            for (var index = 0; index < pages.Count; index++)
            {
                if (string.Equals(pages[index].PageId, projection.InitialPageId, StringComparison.Ordinal))
                {
                    found = index;
                    break;
                }
            }

            if (found >= 0)
            {
                initialIndex = Math.Clamp(found, 0, Math.Max(0, pages.Count - 1));
                savedPageId = pages[initialIndex].PageId;
            }
        }

        return new ReaderBookData(
            book.BookId,
            book.Title,
            chapter.ChapterId,
            string.IsNullOrWhiteSpace(chapter.Title) ? "第 1 章" : chapter.Title,
            string.IsNullOrWhiteSpace(projection.Layout) ? "webtoon_vertical" : projection.Layout,
            pages)
        {
            InitialPageIndex = initialIndex,
            InitialScrollOffsetY = Math.Max(0, projection.InitialScrollOffsetY),
            SavedPageId = savedPageId,
        };
    }
}
