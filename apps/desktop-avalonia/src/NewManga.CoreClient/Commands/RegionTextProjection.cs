using System.Text.Json;

namespace NewManga.CoreClient.Commands;

/// <summary>
/// V11R-F0-2: normalized geometry read projection of one region
/// (<c>{"bbox": [x, y, w, h], "polygon": [[x, y], ...]}</c>, 0..1 floats).
/// </summary>
public sealed record RegionGeometryProjection(
    IReadOnlyList<double> Bbox,
    IReadOnlyList<IReadOnlyList<double>> Polygon);

/// <summary>
/// V11R-F0-2: the real four-level text projection (snapshot-contract shape).
/// These are the persisted values verbatim -- an unedited region legitimately
/// carries empty strings and <see cref="FinalSource"/> = "none"; the reader
/// must not substitute placeholders.
/// </summary>
public sealed record RegionFourTrackText(
    string OcrText,
    string MachineTranslation,
    string EditedTranslation,
    string FinalTranslation,
    string FinalSource,
    bool EditedConfirmed,
    bool ManualEdited,
    bool TranslationLocked);

/// <summary>V11R-F0-2: the three region-level locks (D03 §15).</summary>
public sealed record RegionLockProjection(
    bool RegionLocked,
    bool TranslationLocked,
    bool InpaintLocked);

/// <summary>
/// V11R-F0-2: one region's full read projection returned by
/// <c>list_page_region_texts</c>. Every field is a real Core projection:
/// <see cref="ReviewState"/>, <see cref="Origin"/>, <see cref="RevisionNo"/>,
/// <see cref="CurrentRevisionId"/> and <see cref="IsPinned"/> come from the
/// revision the current pointer targets; <see cref="PinnedRevisionNos"/> lists
/// every pinned revision of the history. <see cref="Geometry"/> is null only
/// when the Core could not supply the page pixel extent (unknown page row) --
/// it is never fabricated.
/// </summary>
public sealed record RegionTextDetail(
    string RegionId,
    string PageId,
    string RegionType,
    string SfxPolicy,
    int ReadingOrder,
    RegionGeometryProjection? Geometry,
    RegionFourTrackText Text,
    RegionLockProjection Locks,
    string ReviewState,
    string Origin,
    int RevisionNo,
    string CurrentRevisionId,
    bool IsPinned,
    IReadOnlyList<int> PinnedRevisionNos,
    string CreatedAt,
    string UpdatedAt)
{
    /// <summary>Strict parse of one RegionTextDetail object; throws <see cref="FormatException"/> on a missing/mistyped field.</summary>
    public static RegionTextDetail Parse(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new FormatException("region detail must be an object");
        }

        var text = RequireObject(element, "text");
        var locks = RequireObject(element, "locks");
        return new RegionTextDetail(
            RequireString(element, "region_id"),
            RequireString(element, "page_id"),
            RequireString(element, "region_type"),
            RequireString(element, "sfx_policy"),
            RequireInt(element, "reading_order"),
            ParseGeometry(element),
            new RegionFourTrackText(
                RequireString(text, "ocr_text"),
                RequireString(text, "machine_translation"),
                RequireString(text, "edited_translation"),
                RequireString(text, "final_translation"),
                RequireString(text, "final_source"),
                RequireBool(text, "edited_confirmed"),
                RequireBool(text, "manual_edited"),
                RequireBool(text, "translation_locked")),
            new RegionLockProjection(
                RequireBool(locks, "region_locked"),
                RequireBool(locks, "translation_locked"),
                RequireBool(locks, "inpaint_locked")),
            RequireString(element, "review_state"),
            RequireString(element, "origin"),
            RequireInt(element, "revision_no"),
            RequireString(element, "current_revision_id"),
            RequireBool(element, "is_pinned"),
            RequireIntArray(element, "pinned_revision_nos"),
            RequireString(element, "created_at"),
            RequireString(element, "updated_at"));
    }

    private static RegionGeometryProjection? ParseGeometry(JsonElement element)
    {
        if (!element.TryGetProperty("geometry", out var geometry) ||
            geometry.ValueKind == JsonValueKind.Null)
        {
            return null;
        }

        if (geometry.ValueKind != JsonValueKind.Object)
        {
            throw new FormatException("geometry must be an object or null");
        }

        var bbox = RequireNumberArray(geometry, "bbox");
        if (bbox.Count != 4)
        {
            throw new FormatException("geometry.bbox must hold [x, y, w, h]");
        }

        if (!geometry.TryGetProperty("polygon", out var polygon) ||
            polygon.ValueKind != JsonValueKind.Array)
        {
            throw new FormatException("geometry.polygon must be an array");
        }

        var rings = new List<IReadOnlyList<double>>();
        foreach (var point in polygon.EnumerateArray())
        {
            if (point.ValueKind != JsonValueKind.Array || point.GetArrayLength() != 2)
            {
                throw new FormatException("geometry.polygon points must be [x, y] pairs");
            }

            rings.Add(ReadNumberArray(point));
        }

        return new RegionGeometryProjection(bbox, rings);
    }

    private static IReadOnlyList<double> RequireNumberArray(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Array
            ? ReadNumberArray(value)
            : throw new FormatException($"missing number[] field '{property}'");

    private static IReadOnlyList<double> ReadNumberArray(JsonElement array)
    {
        var numbers = new List<double>(array.GetArrayLength());
        foreach (var item in array.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.Number || !item.TryGetDouble(out var number))
            {
                throw new FormatException("array element must be a number");
            }

            numbers.Add(number);
        }

        return numbers;
    }

    private static IReadOnlyList<int> RequireIntArray(JsonElement element, string property)
    {
        if (!element.TryGetProperty(property, out var value) || value.ValueKind != JsonValueKind.Array)
        {
            throw new FormatException($"missing int[] field '{property}'");
        }

        var numbers = new List<int>(value.GetArrayLength());
        foreach (var item in value.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.Number || !item.TryGetInt32(out var number))
            {
                throw new FormatException($"'{property}' must contain integers");
            }

            numbers.Add(number);
        }

        return numbers;
    }

    private static JsonElement RequireObject(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.Object
            ? value
            : throw new FormatException($"missing object field '{property}'");

    private static string RequireString(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()!
            : throw new FormatException($"missing string field '{property}'");

    private static int RequireInt(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) &&
        value.ValueKind == JsonValueKind.Number &&
        value.TryGetInt32(out var number)
            ? number
            : throw new FormatException($"missing integer field '{property}'");

    private static bool RequireBool(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) &&
        value.ValueKind is JsonValueKind.True or JsonValueKind.False
            ? value.GetBoolean()
            : throw new FormatException($"missing boolean field '{property}'");
}

/// <summary>
/// V11R-F0-2: the <c>list_page_region_texts</c> result -- one page load of
/// regions + real text/lock/review/pin/geometry projections. The Studio Page
/// mode consumes this in ONE round trip (no per-region N+1).
/// </summary>
public sealed record RegionPageTextProjection(
    string PageId,
    int? PageWidth,
    int? PageHeight,
    IReadOnlyList<RegionTextDetail> Regions)
{
    /// <summary>Strict parse of the Core result object; throws <see cref="FormatException"/> on a missing/mistyped field.</summary>
    public static RegionPageTextProjection Parse(JsonElement element)
    {
        if (element.ValueKind != JsonValueKind.Object)
        {
            throw new FormatException("list_page_region_texts result must be an object");
        }

        int? width = null;
        int? height = null;
        if (element.TryGetProperty("page_size", out var pageSize) &&
            pageSize.ValueKind != JsonValueKind.Null)
        {
            if (pageSize.ValueKind != JsonValueKind.Object)
            {
                throw new FormatException("page_size must be an object or null");
            }

            width = RequireInt(pageSize, "width");
            height = RequireInt(pageSize, "height");
        }

        if (!element.TryGetProperty("regions", out var regions) ||
            regions.ValueKind != JsonValueKind.Array)
        {
            throw new FormatException("missing regions array");
        }

        var parsed = new List<RegionTextDetail>(regions.GetArrayLength());
        foreach (var region in regions.EnumerateArray())
        {
            parsed.Add(RegionTextDetail.Parse(region));
        }

        return new RegionPageTextProjection(
            element.TryGetProperty("page_id", out var pageId) &&
            pageId.ValueKind == JsonValueKind.String
                ? pageId.GetString()!
                : throw new FormatException("missing string field 'page_id'"),
            width,
            height,
            parsed);
    }

    private static int RequireInt(JsonElement element, string property) =>
        element.TryGetProperty(property, out var value) &&
        value.ValueKind == JsonValueKind.Number &&
        value.TryGetInt32(out var number)
            ? number
            : throw new FormatException($"missing integer field '{property}'");
}
