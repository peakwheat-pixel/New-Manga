using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Principal;
using System.Security.Cryptography;
using Microsoft.Win32.SafeHandles;

namespace NewManga.Host.Sources;

public sealed class SourceAccessException(string code) : Exception(code)
{
    public string Code { get; } = code;
}

public interface ISecretProtector
{
    byte[] Protect(byte[] plaintext);
    byte[] Unprotect(byte[] ciphertext);
}

/// <summary>DPAPI CurrentUser, UI forbidden, no machine-scope fallback.</summary>
public sealed class DpapiSecretProtector : ISecretProtector
{
    public byte[] Protect(byte[] plaintext) => Transform(plaintext, true);
    public byte[] Unprotect(byte[] ciphertext) => Transform(ciphertext, false);
    private static byte[] Transform(byte[] bytes, bool protect)
    {
        var input = new Blob { Size = bytes.Length, Data = Marshal.AllocHGlobal(bytes.Length) };
        var output = new Blob();
        try
        {
            Marshal.Copy(bytes, 0, input.Data, bytes.Length);
            var ok = protect
                ? CryptProtectData(ref input, null, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero, 1, out output)
                : CryptUnprotectData(ref input, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero, IntPtr.Zero, 1, out output);
            if (!ok) throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
            var result = new byte[output.Size];
            Marshal.Copy(output.Data, result, 0, result.Length);
            return result;
        }
        finally
        {
            Marshal.Copy(new byte[bytes.Length], 0, input.Data, bytes.Length);
            Marshal.FreeHGlobal(input.Data);
            if (output.Data != IntPtr.Zero)
            {
                Marshal.Copy(new byte[output.Size], 0, output.Data, output.Size);
                LocalFree(output.Data);
            }
        }
    }
    [StructLayout(LayoutKind.Sequential)] private struct Blob { public int Size; public IntPtr Data; }
    [DllImport("crypt32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CryptProtectData(ref Blob input, string? description, IntPtr entropy, IntPtr reserved, IntPtr prompt, uint flags, out Blob output);
    [DllImport("crypt32.dll", SetLastError = true)]
    private static extern bool CryptUnprotectData(ref Blob input, IntPtr description, IntPtr entropy, IntPtr reserved, IntPtr prompt, uint flags, out Blob output);
    [DllImport("kernel32.dll")] private static extern IntPtr LocalFree(IntPtr memory);
}

internal static class SourceSecurity
{
    public static void PrivateDirectory(string directory)
    {
        RejectReparseAncestors(directory, allowMissing: true);
        var info = Directory.CreateDirectory(directory);
        var user = WindowsIdentity.GetCurrent().User ?? throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        var acl = new DirectorySecurity();
        acl.SetOwner(user);
        acl.SetAccessRuleProtection(true, false);
        acl.AddAccessRule(new FileSystemAccessRule(user, FileSystemRights.FullControl,
            InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit, PropagationFlags.None, AccessControlType.Allow));
        info.SetAccessControl(acl);
        var actual = info.GetAccessControl();
        if (actual.GetOwner(typeof(SecurityIdentifier)) is not SecurityIdentifier owner || !owner.Equals(user))
            throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
        foreach (FileSystemAccessRule rule in actual.GetAccessRules(true, true, typeof(SecurityIdentifier)))
            if (rule.AccessControlType == AccessControlType.Allow && !rule.IdentityReference.Equals(user))
                throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE");
    }

    public static string Normalize(string path)
    {
        if (!Path.IsPathFullyQualified(path) || path.Split('\\', '/').Any(p => p is "." or ".."))
            throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        return Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
    }
    public static void RejectReparseAncestors(string path, bool allowMissing = false)
    {
        var full = Normalize(path);
        var anchor = Path.GetPathRoot(full)!;
        var probe = anchor;
        foreach (var part in full[anchor.Length..].Split('\\', '/'))
        {
            if (part.Length == 0) continue;
            probe = Path.Combine(probe, part);
            if (!File.Exists(probe) && !Directory.Exists(probe))
            {
                if (allowMissing) continue;
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
            }
            if ((File.GetAttributes(probe) & FileAttributes.ReparsePoint) != 0)
                throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        }
    }
    public static bool Contains(string root, string path) => string.Equals(root, path, StringComparison.OrdinalIgnoreCase)
        || path.StartsWith(Path.TrimEndingDirectorySeparator(root) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);

    public static (ulong Volume, ulong Id, long Size) Identity(SafeFileHandle handle)
    {
        if (!GetFileInformationByHandle(handle, out var info) || (info.Attributes & 0x400) != 0)
            throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        return (info.Volume, ((ulong)info.IndexHigh << 32) | info.IndexLow, ((long)info.SizeHigh << 32) | info.SizeLow);
    }
    public static (ulong Volume, ulong Id, long Size) Identity(string path)
    {
        RejectReparseAncestors(path);
        using var handle = CreateFileW(path, 0x80, 1, IntPtr.Zero, 3, 0x02000000 | 0x00200000, IntPtr.Zero);
        if (handle.IsInvalid) throw new SourceAccessException("SOURCE_ACCESS_DENIED");
        return Identity(handle);
    }
    [StructLayout(LayoutKind.Sequential)] private struct FileInfo
    {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME Creation, Access, Write;
        public uint Volume, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(string path, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetFileInformationByHandle(SafeFileHandle handle, out FileInfo info);
}
