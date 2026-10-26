using System.Diagnostics;
using System.Runtime.InteropServices;

namespace NewManga.CoreClient.Diagnostics;

public enum ProcessIntegrityLevel
{
    Unknown = 0,
    Untrusted = 1,
    Low = 2,
    Medium = 3,
    High = 4,
    System = 5,
}

/// <summary>Result of comparing the parent and sidecar mandatory integrity levels (IL).</summary>
public sealed record IntegrityComparison(ProcessIntegrityLevel Parent, ProcessIntegrityLevel Child)
{
    public bool Matches => Parent == Child && Parent != ProcessIntegrityLevel.Unknown;

    public string Describe() => $"parent={Parent}, child={Child}";
}

/// <summary>
/// AC4 (no panic) + AC11 (unlabelled copy): a child inheriting a *lower* mandatory integrity level
/// than the host (e.g. spawned from a repository tree that carries a Low mandatory label) is a hard
/// error with a typed code instead of a silent "core writes fail" mystery. The comparison itself is
/// pure and unit tested; the Win32 read is the only platform piece.
/// </summary>
public static class ProcessIntegrity
{
    private const uint TokenQuery = 0x0008;
    private const int TokenIntegrityLevelClass = 25;

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool OpenProcessToken(IntPtr processHandle, uint desiredAccess, out IntPtr tokenHandle);

    [DllImport("advapi32.dll", SetLastError = true)]
    private static extern bool GetTokenInformation(
        IntPtr tokenHandle,
        int tokenInformationClass,
        IntPtr tokenInformation,
        int tokenInformationLength,
        out int returnLength);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);

    /// <summary>Compares two levels; a mismatch (either direction) is a typed failure condition.</summary>
    public static IntegrityComparison Compare(ProcessIntegrityLevel parent, ProcessIntegrityLevel child) =>
        new(parent, child);

    public static ProcessIntegrityLevel GetForCurrentProcess()
    {
        using var process = Process.GetCurrentProcess();
        return GetForProcess(process.Handle);
    }

    public static ProcessIntegrityLevel GetForProcess(IntPtr processHandle)
    {
        if (processHandle == IntPtr.Zero)
        {
            return ProcessIntegrityLevel.Unknown;
        }

        if (!OpenProcessToken(processHandle, TokenQuery, out var token))
        {
            return ProcessIntegrityLevel.Unknown;
        }

        try
        {
            _ = GetTokenInformation(token, TokenIntegrityLevelClass, IntPtr.Zero, 0, out var required);
            if (required <= 0)
            {
                return ProcessIntegrityLevel.Unknown;
            }

            var buffer = Marshal.AllocHGlobal(required);
            try
            {
                if (!GetTokenInformation(token, TokenIntegrityLevelClass, buffer, required, out _))
                {
                    return ProcessIntegrityLevel.Unknown;
                }

                // TOKEN_MANDATORY_LABEL { SID_AND_ATTRIBUTES { PSID Sid; DWORD Attributes; } }
                var sid = Marshal.ReadIntPtr(buffer);
                if (sid == IntPtr.Zero)
                {
                    return ProcessIntegrityLevel.Unknown;
                }

                var subAuthorityCount = Marshal.ReadByte(sid, 1);
                if (subAuthorityCount == 0)
                {
                    return ProcessIntegrityLevel.Unknown;
                }

                // SID layout: revision(1) count(1) authority(6) subAuthorities(4 each).
                var rid = (uint)Marshal.ReadInt32(sid, 8 + (4 * (subAuthorityCount - 1)));
                return FromRid(rid);
            }
            finally
            {
                Marshal.FreeHGlobal(buffer);
            }
        }
        finally
        {
            _ = CloseHandle(token);
        }
    }

    public static ProcessIntegrityLevel FromRid(uint rid) => rid switch
    {
        0x0000 => ProcessIntegrityLevel.Untrusted,
        0x1000 => ProcessIntegrityLevel.Low,
        0x2000 => ProcessIntegrityLevel.Medium,
        0x3000 => ProcessIntegrityLevel.High,
        0x4000 => ProcessIntegrityLevel.System,
        _ => ProcessIntegrityLevel.Unknown,
    };

    /// <summary>
    /// Throws <see cref="SidecarException"/> with <see cref="SidecarErrorCode.IntegrityMismatch"/>
    /// when the child token IL differs from the host token IL. Equal Unknown counts as a mismatch
    /// because the host cannot prove the invariant (fail closed, but as a typed error, not a panic).
    /// </summary>
    public static void EnsureChildMatchesParent(string sidecarName, IntPtr childProcessHandle, string? stderrLogPath)
    {
        var parent = GetForCurrentProcess();
        var child = GetForProcess(childProcessHandle);
        var comparison = Compare(parent, child);
        if (comparison.Matches)
        {
            return;
        }

        throw new SidecarException(
            SidecarErrorCode.IntegrityMismatch,
            sidecarName,
            $"mandatory integrity level mismatch ({comparison.Describe()}); run the host from an unlabelled copy (AC11)",
            stderrLogPath);
    }
}
