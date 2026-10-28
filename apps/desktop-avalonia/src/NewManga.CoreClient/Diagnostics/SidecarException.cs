namespace NewManga.CoreClient.Diagnostics;

/// <summary>
/// Typed sidecar failure. The transport never lets a spawn/IO/protocol fault escape as an
/// unhandled exception (no panic), never dumps a raw stack trace at the user, and always records
/// the stderr log path for diagnostics.
/// </summary>
public sealed class SidecarException : Exception
{
    public SidecarException(
        SidecarErrorCode code,
        string sidecar,
        string message,
        string? stderrLogPath = null,
        Exception? inner = null)
        : base($"[{code}] {sidecar}: {message}", inner)
    {
        Code = code;
        Sidecar = sidecar;
        StderrLogPath = stderrLogPath;
    }

    public SidecarErrorCode Code { get; }

    public string Sidecar { get; }

    /// <summary>Diagnostic only (host log / evidence). Never rendered in the UI.</summary>
    public string? StderrLogPath { get; }

    /// <summary>Message safe for the UI: no absolute paths, no raw exception text.</summary>
    public string UserMessage => UserMessages.Describe(Code, Sidecar);
}

public static class UserMessages
{
    public static string Describe(SidecarErrorCode code, string sidecar) => code switch
    {
        SidecarErrorCode.SidecarBundleMissing => "核心服务目录缺失，无法启动 Python Core。",
        SidecarErrorCode.SidecarExeMissing => $"核心服务程序缺失（{sidecar}.exe）。",
        SidecarErrorCode.SpawnFailed => $"核心服务启动失败（{sidecar}）。已记录诊断日志。",
        SidecarErrorCode.StartupTimeout => $"核心服务启动超时（{sidecar}）。",
        SidecarErrorCode.RequestTimeout => $"核心服务响应超时（{sidecar}）。",
        SidecarErrorCode.ProcessExited => $"核心服务意外退出（{sidecar}）。已记录诊断日志。",
        SidecarErrorCode.ProtocolMismatch => $"核心服务协议版本不匹配（{sidecar}）。",
        SidecarErrorCode.MalformedResponse => $"核心服务返回了无法解析的响应（{sidecar}）。",
        SidecarErrorCode.IntegrityMismatch => $"核心服务完整性级别与主进程不一致（{sidecar}），已拒绝运行。",
        SidecarErrorCode.HandshakeFailed => $"核心服务握手失败（{sidecar}）。",
        SidecarErrorCode.IoFailure => $"核心服务管道读写失败（{sidecar}）。",
        SidecarErrorCode.AlreadyRunning => "New Manga 已在运行（全局单实例互斥）。",
        SidecarErrorCode.InvalidArguments => "启动参数无效。",
        _ => "核心服务发生未知错误。",
    };
}
