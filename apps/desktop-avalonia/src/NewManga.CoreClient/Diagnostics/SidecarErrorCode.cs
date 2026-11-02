namespace NewManga.CoreClient.Diagnostics;

/// <summary>
/// Stable, typed failure codes for the sidecar transport. The UI never sees OS paths; it sees one
/// of these codes plus a human message, while the full diagnostic (including the stderr log) stays
/// in the host log / handoff evidence.
/// </summary>
public enum SidecarErrorCode
{
    SidecarBundleMissing,
    SidecarExeMissing,
    SpawnFailed,
    StartupTimeout,
    RequestTimeout,
    ProcessExited,
    ProtocolMismatch,
    MalformedResponse,
    IntegrityMismatch,
    HandshakeFailed,
    IoFailure,
    AlreadyRunning,
    InvalidArguments,
}
