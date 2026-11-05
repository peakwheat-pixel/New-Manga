using System;
using System.Collections.Generic;

namespace NewManga.Host.Sources;

/// <summary>C-17 §8 retryable projection for codes the Host journals itself
/// (the Core returns its own value for Core-originated failures).</summary>
public static class HostErrorCodes
{
    private static readonly HashSet<string> RetryableCodes = new(StringComparer.Ordinal)
    {
        "SOURCE_PLAN_STALE",
        "SOURCE_GRANT_EXPIRED",
        "SOURCE_REGISTRY_UNAVAILABLE",
        "SOURCE_REGISTRY_BUSY",
        "FILE_IDENTITY_CHANGED",
        "STALE_BASE_REVISION",
        "SOURCE_SYNC_UNSTABLE",
        "SOURCE_SYNC_STORAGE_FAILED",
    };

    public static bool IsKnown(string code) => code is
        "INVALID_REQUEST" or "CORE_CAPABILITY_MISSING" or "PROTOCOL_VERSION_UNSUPPORTED"
        or "HOST_ONLY_REQUIRED" or "HOST_SESSION_INVALID" or "CORE_SESSION_MISMATCH"
        or "SOURCE_PLAN_STALE" or "SOURCE_OPERATION_CONFLICT" or "SOURCE_OPERATION_NOT_FOUND"
        or "SOURCE_ACCESS_DENIED" or "SOURCE_GRANT_EXPIRED" or "SOURCE_GRANT_REVOKED"
        or "SOURCE_REGISTRY_UNAVAILABLE" or "SOURCE_REGISTRY_BUSY" or "SOURCE_PASSWORD_REQUIRED"
        or "SOURCE_PASSWORD_INVALID" or "SOURCE_FORMAT_UNSUPPORTED" or "SOURCE_ENTRY_MISSING"
        or "SOURCE_BUDGET_EXCEEDED" or "SOURCE_PROJECT_MISMATCH" or "FILE_IDENTITY_CHANGED"
        or "REF_SIGNATURE_INVALID" or "STALE_BASE_REVISION" or "SOURCE_SYNC_STATE_CONFLICT"
        or "SOURCE_SYNC_UNSTABLE" or "SOURCE_SYNC_CANCELLED" or "SOURCE_SYNC_STORAGE_FAILED"
        or "SOURCE_MIGRATION_FAILED";

    public static bool RetryableOf(string code) => RetryableCodes.Contains(code);
}
