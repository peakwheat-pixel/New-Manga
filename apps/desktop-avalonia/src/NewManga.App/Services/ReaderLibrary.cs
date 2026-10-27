using System.Text.Json;
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
/// </summary>
public sealed record ReaderBookData(
    string BookId,
    string BookTitle,
    string ChapterId,
    string ChapterTitle,
    string Layout,
    IReadOnlyList<ReaderPageData> Pages)
{
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
        return new ReaderBookData(
            book.BookId,
            book.Title,
            chapter.ChapterId,
            string.IsNullOrWhiteSpace(chapter.Title) ? "第 1 章" : chapter.Title,
            string.IsNullOrWhiteSpace(projection.Layout) ? "webtoon_vertical" : projection.Layout,
            pages);
    }
}
