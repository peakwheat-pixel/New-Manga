using System.Text;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

public sealed class SourceRegistryTests
{
    [Fact]
    public void NativeDpapiCurrentUserRoundTripAndTamperRefusal()
    {
        var protector = new DpapiSecretProtector();
        var plaintext = Encoding.UTF8.GetBytes("synthetic-registry-payload");
        var ciphertext = protector.Protect(plaintext);
        Assert.False(ciphertext.SequenceEqual(plaintext));
        Assert.Equal(plaintext, protector.Unprotect(ciphertext));
        ciphertext[^1] ^= 0x42;
        Assert.Throws<SourceAccessException>(() => protector.Unprotect(ciphertext));
    }

    [Fact]
    public void EncryptedPersistenceGenerationCorruptionAndExplicitReset()
    {
        // This retained fixture is canonical evidence, not a production data root.
        var repo = FindRepository();
        var evidence = Path.Combine(repo, "verification", "FEA-09", "native-registry", Guid.NewGuid().ToString("N"));
        var source = Path.Combine(evidence, "synthetic-source");
        Directory.CreateDirectory(source);
        File.WriteAllText(Path.Combine(source, "page.txt"), "synthetic source bytes");
        var registry = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        var entry = registry.Register("synthetic", [source]);
        Assert.Equal(1, entry.Generation);
        var reopened = new SourceAccessRegistry(Path.Combine(evidence, "isolated-data"));
        Assert.Equal(entry.RegistryId, Assert.Single(reopened.List()).RegistryId);
        Assert.Equal(1, reopened.Authorize(entry.RegistryId, 1, [Path.Combine(source, "page.txt")]).Generation);
        var revoked = reopened.Revoke(entry.RegistryId);
        Assert.Equal(2, revoked.Generation);
        Assert.Equal("SOURCE_GRANT_REVOKED", Assert.Throws<SourceAccessException>(() => reopened.Authorize(entry.RegistryId, 2, [source])).Code);
        var bytes = File.ReadAllBytes(registry.RegistryPath);
        Assert.StartsWith("NMSAR1", Encoding.ASCII.GetString(bytes, 0, 6));
        Assert.DoesNotContain(source, Encoding.UTF8.GetString(bytes));
        File.WriteAllBytes(registry.RegistryPath, [1, 2, 3]);
        Assert.Equal("SOURCE_REGISTRY_UNAVAILABLE", Assert.Throws<SourceAccessException>(() => reopened.List()).Code);
        Assert.Equal(new byte[] { 1, 2, 3 }, File.ReadAllBytes(registry.RegistryPath));
        Assert.NotEmpty(Directory.GetFiles(Path.GetDirectoryName(registry.RegistryPath)!, "*.corrupt-*"));
        Assert.Equal("INVALID_REQUEST", Assert.Throws<SourceAccessException>(() => reopened.Reset(false)).Code);
        Assert.True(Directory.Exists(reopened.Reset(true)));
        Assert.Empty(reopened.List());
    }

    private static string FindRepository()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null && !Directory.Exists(Path.Combine(directory.FullName, ".git"))) directory = directory.Parent;
        return directory?.FullName ?? throw new InvalidOperationException("isolated repository not found");
    }
}
