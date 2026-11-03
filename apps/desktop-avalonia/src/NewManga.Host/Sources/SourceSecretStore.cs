using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

namespace NewManga.Host.Sources;

/// <summary>
/// C-16 v1.1 §3.1 Host-side one-shot password tokens. A token file is
/// <c>"NMSSR1\0" + DPAPI-CurrentUser(password)</c> under
/// <c>&lt;DataRoot&gt;/host/source-secrets/&lt;token&gt;.bin</c>; the Core consumes
/// it once (zero-fill + delete). Confidentiality rests on DPAPI (another user
/// cannot unprotect even if the file is read); the directory is per-user under
/// the data root, and the file name is an unpredictable 32-char token.
/// </summary>
public static class SourceSecretStore
{
    public const string Magic = "NMSSR1\0";
    private const int CryptProtectUiForbidden = 0x1;

    [StructLayout(LayoutKind.Sequential)]
    private struct DataBlob
    {
        public int cbData;
        public IntPtr pbData;
    }

    [DllImport("crypt32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    private static extern bool CryptProtectData(
        ref DataBlob pDataIn, string? szDataDescr, ref DataBlob pOptionalEntropy,
        IntPtr pvReserved, IntPtr pPromptStruct, int dwFlags, out DataBlob pDataOut);

    [DllImport("kernel32.dll")]
    private static extern IntPtr LocalFree(IntPtr hMem);

    /// <summary>Create a fresh one-shot token file and return its ref fields.</summary>
    public static (string Token, string Path) WritePassword(string dataRoot, byte[] password)
    {
        if (password.Length == 0) throw new SourceAccessException("SOURCE_PASSWORD_REQUIRED");
        var directory = Path.Combine(dataRoot, "host", "source-secrets");
        Directory.CreateDirectory(directory);
        var token = NewToken();
        var path = Path.Combine(directory, token + ".bin");
        var protectedBytes = Protect(password);
        var payload = new byte[Magic.Length + protectedBytes.Length];
        Encoding.ASCII.GetBytes(Magic, payload);
        protectedBytes.CopyTo(payload, Magic.Length);
        var temporary = path + ".tmp-" + Guid.NewGuid().ToString("N");
        try
        {
            using (var stream = new FileStream(temporary, FileMode.CreateNew, FileAccess.Write,
                       FileShare.None, 4096, FileOptions.WriteThrough))
            {
                stream.Write(payload);
                stream.Flush(true);
            }
            File.Move(temporary, path, overwrite: false);
        }
        finally
        {
            CryptographicOperations.ZeroMemory(payload);
            CryptographicOperations.ZeroMemory(protectedBytes);
            try { if (File.Exists(temporary)) File.Delete(temporary); } catch { /* best effort */ }
        }
        return (token, path);
    }

    /// <summary>Delete an unconsumed token (timeout/cancel/teardown).</summary>
    public static void DeleteIfPresent(string path)
    {
        try
        {
            if (File.Exists(path))
            {
                var length = (int)new FileInfo(path).Length;
                using (var stream = new FileStream(path, FileMode.Open, FileAccess.Write, FileShare.None))
                {
                    var zeros = new byte[Math.Min(length, 4096)];
                    var remaining = length;
                    while (remaining > 0)
                    {
                        var chunk = Math.Min(remaining, zeros.Length);
                        stream.Write(zeros, 0, chunk);
                        remaining -= chunk;
                    }
                    stream.Flush(true);
                }
                File.Delete(path);
            }
        }
        catch (IOException) { /* best effort */ }
        catch (UnauthorizedAccessException) { /* best effort */ }
    }

    private static string NewToken()
    {
        const string alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789-_";
        var buffer = RandomNumberGenerator.GetBytes(32);
        var builder = new StringBuilder(32);
        foreach (var value in buffer) builder.Append(alphabet[value % alphabet.Length]);
        return builder.ToString();
    }

    private static byte[] Protect(byte[] plaintext)
    {
        var inBlob = new DataBlob();
        var outBlob = new DataBlob();
        var buffer = GCHandle.Alloc(plaintext, GCHandleType.Pinned);
        try
        {
            inBlob.cbData = plaintext.Length;
            inBlob.pbData = buffer.AddrOfPinnedObject();
            var empty = new DataBlob();
            if (!CryptProtectData(ref inBlob, null, ref empty, IntPtr.Zero, IntPtr.Zero,
                    CryptProtectUiForbidden, out outBlob))
                throw new SourceAccessException("SOURCE_PASSWORD_INVALID");
            try
            {
                var result = new byte[outBlob.cbData];
                Marshal.Copy(outBlob.pbData, result, 0, outBlob.cbData);
                return result;
            }
            finally { LocalFree(outBlob.pbData); }
        }
        finally { buffer.Free(); }
    }
}
