using System.Text.Json;
using NewManga.App.Shell;

namespace NewManga.App.Tests;

/// <summary>
/// V11R-A-2 (Lead ruling): <c>ShellCommandCatalog.WriteEvidence</c> must create missing evidence
/// parents itself, so a fresh <c>NEWMANGA_EVIDENCE_DIR</c> can never fail the S3 shell gate with a
/// bare <see cref="DirectoryNotFoundException"/>.
/// </summary>
public sealed class ShellEvidenceWriteTests
{
    [Fact]
    public void WriteEvidence_CreatesMissingParentDirectory()
    {
        var root = Path.Combine(Path.GetTempPath(), "newmanga-shell-evidence-" + Guid.NewGuid().ToString("N")[..10]);
        var path = Path.Combine(root, "commands", "wiring.json");
        try
        {
            Assert.False(Directory.Exists(Path.Combine(root, "commands")));

            ShellCommandCatalog.WriteEvidence(path, "test-scope", 3, new List<double> { 1, 2, 3 }, 3);

            Assert.True(File.Exists(path));
            using var document = JsonDocument.Parse(File.ReadAllText(path));
            Assert.Equal("test-scope", document.RootElement.GetProperty("scope").GetString());
            Assert.Equal(
                ShellCommandCatalog.WiredCommandCount,
                document.RootElement.GetProperty("wired_implemented_count").GetInt32());
        }
        finally
        {
            try
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // best effort; temp dirs are disposable
            }
        }
    }
}
