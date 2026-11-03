using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// C-16 v1.1 §3.1: Host one-shot DPAPI token store (fresh-grant protocol).
/// Confidentiality is DPAPI CurrentUser; the store never leaves plaintext on
/// disk and DeleteIfPresent wipes before unlinking.
/// </summary>
public sealed class SourceSecretStoreTests
{
    [Fact]
    public void WriteCreatesPrivateOneShotTokenUnderSourceSecrets()
    {
        var root = Path.Combine(Path.GetTempPath(), "nm-secret-" + Guid.NewGuid().ToString("N")[..10]);
        try
        {
            var (token, path) = SourceSecretStore.WritePassword(root, "s3cret-pass"u8.ToArray());
            Assert.Equal(32, token.Length);
            Assert.Equal(Path.Combine(root, "host", "source-secrets"), Path.GetDirectoryName(path));
            Assert.Equal(token + ".bin", Path.GetFileName(path));
            Assert.True(File.Exists(path));
            var bytes = File.ReadAllBytes(path);
            Assert.StartsWith("NMSSR1\0", System.Text.Encoding.ASCII.GetString(bytes[..7]));
            Assert.DoesNotContain("s3cret-pass", System.Text.Encoding.UTF8.GetString(bytes));
            Assert.True(bytes.Length > 7);

            var (secondToken, secondPath) = SourceSecretStore.WritePassword(root, "other"u8.ToArray());
            Assert.NotEqual(token, secondToken);
            Assert.NotEqual(path, secondPath);

            SourceSecretStore.DeleteIfPresent(path);
            Assert.False(File.Exists(path));
            Assert.True(File.Exists(secondPath), "deleting one token must not touch another");
        }
        finally
        {
            try { Directory.Delete(root, recursive: true); } catch { /* best effort */ }
        }
    }

    [Fact]
    public void DeleteIfPresentIsIdempotentForMissingFile()
    {
        SourceSecretStore.DeleteIfPresent(
            Path.Combine(Path.GetTempPath(), "nm-secret-missing-" + Guid.NewGuid().ToString("N") + ".bin"));
    }
}
