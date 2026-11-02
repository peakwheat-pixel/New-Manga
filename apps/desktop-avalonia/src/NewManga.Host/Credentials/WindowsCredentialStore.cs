using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace NewManga.Host.Credentials;

/// <summary>
/// CREDENTIAL-PORT-1 AC1/AC3: Windows Credential Manager adapter (generic credentials, machine
/// persistence, UTF-16LE blob) — byte-compatible with the frozen Core's
/// <c>infrastructure.credentials.windows.WindowsCredentialStore</c>, so a ref written here is
/// readable by the Core and vice versa. Secrets are only held in unmanaged buffers/UTF-16 arrays
/// for the duration of a call and zeroed afterwards; nothing is written to disk by this adapter.
/// </summary>
public sealed class WindowsCredentialStore : ICredentialStore
{
    private const uint CredTypeGeneric = 1;
    private const uint CredPersistLocalMachine = 2;
    private const int ErrorNotFound = 1168;
    private const int ErrorAlreadyExists = 1316;

    public bool Exists(string targetName)
    {
        var handle = ReadHandle(targetName, out _, out var error);
        if (handle != IntPtr.Zero)
        {
            CredFree(handle);
            return true;
        }

        return error switch
        {
            ErrorNotFound => false,
            _ => throw Failure("CREDENTIAL_STORE_UNAVAILABLE", $"CredReadW({targetName})", error),
        };
    }

    public void Store(string targetName, string secret)
    {
        if (Exists(targetName))
        {
            throw new CredentialStoreException("ALREADY_EXISTS", $"vault target already exists: {targetName}");
        }

        Write(targetName, secret, overwrite: false);
    }

    public string Read(string targetName)
    {
        var handle = ReadHandle(targetName, out var credential, out var error);
        if (handle == IntPtr.Zero)
        {
            throw error switch
            {
                ErrorNotFound => new CredentialStoreException("NOT_FOUND", $"vault target missing: {targetName}"),
                _ => Failure("CREDENTIAL_STORE_UNAVAILABLE", $"CredReadW({targetName})", error),
            };
        }

        try
        {
            var blob = new byte[credential.CredentialBlobSize];
            if (blob.Length > 0)
            {
                Marshal.Copy(credential.CredentialBlob, blob, 0, blob.Length);
            }

            try
            {
                return Encoding.Unicode.GetString(blob);
            }
            finally
            {
                CryptographicOperations.ZeroMemory(blob);
            }
        }
        finally
        {
            CredFree(handle);
        }
    }

    public void Delete(string targetName)
    {
        if (CredDeleteW(targetName, CredTypeGeneric, 0))
        {
            return;
        }

        var error = Marshal.GetLastWin32Error();
        if (error == ErrorNotFound)
        {
            throw new CredentialStoreException("NOT_FOUND", $"vault target missing: {targetName}", error);
        }

        throw Failure("CREDENTIAL_STORE_UNAVAILABLE", $"CredDeleteW({targetName})", error);
    }

    public IReadOnlyList<string> Enumerate(string prefix)
    {
        if (string.IsNullOrEmpty(prefix))
        {
            return Array.Empty<string>();
        }

        if (!CredEnumerateW(null, 0, out var count, out var array))
        {
            var error = Marshal.GetLastWin32Error();
            if (error == ErrorNotFound)
            {
                return Array.Empty<string>();
            }

            throw Failure("CREDENTIAL_STORE_UNAVAILABLE", "CredEnumerateW", error);
        }

        try
        {
            var names = new List<string>();
            for (var index = 0; index < count; index++)
            {
                var item = Marshal.ReadIntPtr(array, index * IntPtr.Size);
                if (item == IntPtr.Zero)
                {
                    continue;
                }

                var credential = Marshal.PtrToStructure<CredentialW>(item);
                if (credential.TargetName is { } name &&
                    name.StartsWith(prefix, StringComparison.Ordinal))
                {
                    names.Add(name);
                }
            }

            names.Sort(StringComparer.Ordinal);
            return names;
        }
        finally
        {
            CredFree(array);
        }
    }

    private static IntPtr ReadHandle(string targetName, out CredentialW credential, out int error)
    {
        if (CredReadW(targetName, CredTypeGeneric, 0, out var handle))
        {
            credential = Marshal.PtrToStructure<CredentialW>(handle);
            error = 0;
            return handle;
        }

        credential = default;
        error = Marshal.GetLastWin32Error();
        return IntPtr.Zero;
    }

    private static void Write(string targetName, string secret, bool overwrite)
    {
        var blob = Encoding.Unicode.GetBytes(secret);
        var blobPointer = IntPtr.Zero;
        try
        {
            blobPointer = Marshal.AllocHGlobal(blob.Length);
            Marshal.Copy(blob, 0, blobPointer, blob.Length);
            var credential = new CredentialW
            {
                Flags = 0,
                Type = CredTypeGeneric,
                TargetName = targetName,
                Comment = null,
                LastWritten = 0,
                CredentialBlobSize = (uint)blob.Length,
                CredentialBlob = blobPointer,
                Persist = CredPersistLocalMachine,
                AttributeCount = 0,
                Attributes = IntPtr.Zero,
                TargetAlias = null,
                UserName = null,
            };

            if (!CredWriteW(ref credential, 0))
            {
                var error = Marshal.GetLastWin32Error();
                if (!overwrite && error == ErrorAlreadyExists)
                {
                    throw new CredentialStoreException("ALREADY_EXISTS", $"vault target already exists: {targetName}", error);
                }

                throw Failure("CREDENTIAL_STORE_UNAVAILABLE", $"CredWriteW({targetName})", error);
            }
        }
        finally
        {
            if (blobPointer != IntPtr.Zero)
            {
                Marshal.Copy(new byte[blob.Length], 0, blobPointer, blob.Length);
                Marshal.FreeHGlobal(blobPointer);
            }

            CryptographicOperations.ZeroMemory(blob);
        }
    }

    private static CredentialStoreException Failure(string code, string what, int error) =>
        new(code, $"{what} failed with Win32 error {error}", error,
            new Win32Exception(error));

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct CredentialW
    {
        public uint Flags;
        public uint Type;
        public string? TargetName;
        public string? Comment;
        public long LastWritten;
        public uint CredentialBlobSize;
        public IntPtr CredentialBlob;
        public uint Persist;
        public uint AttributeCount;
        public IntPtr Attributes;
        public string? TargetAlias;
        public string? UserName;
    }

    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredReadW(string target, uint type, uint flags, out IntPtr credential);

    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredWriteW(ref CredentialW credential, uint flags);

    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredDeleteW(string target, uint type, uint flags);

    [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CredEnumerateW(string? filter, uint flags, out uint count, out IntPtr credentials);

    [DllImport("advapi32.dll")]
    private static extern void CredFree(IntPtr buffer);
}
