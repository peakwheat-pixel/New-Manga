using System.Collections.Generic;
using System.Text.Json;

namespace NewManga.CoreClient;

/// <summary>
/// FEA-05-PORT-1: the Draft family DTOs (C078-C083). Field names and shapes
/// mirror the real Core payloads: ``Draft.to_json()`` returns the eleven
/// persisted SC-D01 fields with PascalCase identity keys, ``EditToken.to_json()``
/// the six PascalCase keys, and ``RegionCandidate.to_json()`` uses
/// candidateId/RegionId/BaseRevisionId/origin.
/// </summary>
public sealed record DraftLease(Draft Draft, bool CanEdit, EditToken? Token);

public sealed record Draft(
    string DraftId,
    string SessionId,
    string PageId,
    string? RegionId,
    string? BaseRevisionId,
    int PageBindingVersion,
    int DraftSequence,
    JsonElement? Patch,
    int? UndoCursor,
    string SavedAt,
    string Status);

/// <summary>
/// The patch payload is an open object: the draft patch model is owned by the
/// Core (text/style/geometry keys), so the port carries it through as-is
/// instead of re-typing a partial subset.
/// </summary>
public sealed record DraftPatchRequest(IReadOnlyDictionary<string, object?> Patch);

public sealed record EditToken(
    string TokenId,
    string DraftId,
    int DraftSequence,
    string SessionId,
    string IssuedAt,
    string ExpiresAt);

public sealed record RegionCandidate(
    string CandidateId,
    string RegionId,
    string BaseRevisionId,
    string Origin);
