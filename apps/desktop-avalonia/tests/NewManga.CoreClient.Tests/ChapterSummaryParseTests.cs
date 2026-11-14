using System.Text.Json;
using NewManga.CoreClient;
using Xunit;

namespace NewManga.CoreClient.Tests;

/// <summary>
/// MAINT-2-C1-BATCH-1 AC4 (C1-4 / L-L1-1) + AC5 (C1-5 / L-L1-2), M2-C1 rev 2.16: the frozen
/// four-key <c>list_chapters</c> row gained two OPTIONAL fields (<c>kind</c>,
/// <c>custom_rank</c>). <see cref="ChapterSummary.Parse"/> is the single place that maps one wire
/// row, so these tests pin the widening WITHOUT a live sidecar (same convention as
/// <c>RegionTextDetail.Parse</c>). They discriminate in both directions:
/// reverting the widening (absent fields) leaves the values null and fails the value assertions,
/// while dropping/renaming a frozen key throws.
/// </summary>
public sealed class ChapterSummaryParseTests
{
    [Fact]
    public void Parse_FourKeyLegacyRow_KeepsOptionalFieldsNull()
    {
        // An older Core (pre-2.16) returns exactly the frozen four keys; that must stay legal.
        var summary = ChapterSummary.Parse(Args(
            """{"chapter_id":"c1","title":"第 1 话","chapter_number":"1","sort_order":3}"""));

        Assert.Equal("c1", summary.ChapterId);
        Assert.Equal("第 1 话", summary.Title);
        Assert.Equal("1", summary.ChapterNumber);
        Assert.Equal(3, summary.SortOrder);
        Assert.Null(summary.Kind);
        Assert.Null(summary.CustomRank);
    }

    [Fact]
    public void Parse_WidenedRow_ReadsKindAndCustomRank()
    {
        var summary = ChapterSummary.Parse(Args(
            """{"chapter_id":"c2","title":"C2","chapter_number":"","sort_order":1,"kind":"webtoon","custom_rank":7}"""));

        Assert.Equal("webtoon", summary.Kind);
        Assert.Equal(7L, summary.CustomRank);
        // The frozen fields are unaffected by the widening.
        Assert.Equal("c2", summary.ChapterId);
        Assert.Equal(1, summary.SortOrder);
    }

    [Fact]
    public void Parse_ExplicitNullRank_And_Int64RankBothWork()
    {
        var explicitNull = ChapterSummary.Parse(Args(
            """{"chapter_id":"c3","title":"C3","chapter_number":"","sort_order":1,"kind":"paged","custom_rank":null}"""));
        Assert.Null(explicitNull.CustomRank);

        // The Core column is a signed 64-bit integer: a rank above int.MaxValue must survive
        // (an int-typed projection would throw or truncate here).
        var large = ChapterSummary.Parse(Args(
            """{"chapter_id":"c4","title":"C4","chapter_number":"","sort_order":2,"kind":"paged","custom_rank":1099511627776}"""));
        Assert.Equal(1_099_511_627_776L, large.CustomRank);
        Assert.True(large.CustomRank > int.MaxValue);
    }

    [Fact]
    public void Parse_MissingFrozenKey_Throws()
    {
        // The frozen four keys stay REQUIRED: a missing/mistyped one is a malformed row, not
        // "no metadata". This guards against silently degrading the frozen contract.
        Assert.Throws<FormatException>(() => ChapterSummary.Parse(Args(
            """{"title":"C","chapter_number":"","sort_order":1,"kind":"paged"}""")));
        Assert.Throws<FormatException>(() => ChapterSummary.Parse(Args(
            """{"chapter_id":"c1","title":"C","chapter_number":"","sort_order":"1"}""")));
    }

    private static JsonElement Args(string json)
    {
        using var document = JsonDocument.Parse(json);
        return document.RootElement.Clone();
    }
}
