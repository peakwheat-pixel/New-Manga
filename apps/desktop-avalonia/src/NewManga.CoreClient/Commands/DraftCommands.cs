using System.Collections.Generic;

namespace NewManga.CoreClient;

/// <summary>
/// FEA-05-PORT-1: the Draft family DTOs (C078-C083). Strongly typed mirrors of the
/// frozen Core payloads; the dispatcher converts the wire camelCase to these records.
/// </summary>
public sealed record DraftLease(Draft Draft, bool CanEdit, EditToken? Token);

public sealed record Draft(
    string DraftId,
    string SessionId,
    string PageId,
    string? RegionId,
    int DraftSequence,
    string Status);

public sealed record DraftPatchRequest(string? Text, string? RegionType);

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
