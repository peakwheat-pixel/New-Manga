using System;
using System.IO;
using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// E9-NEGATIVE-TEST-1: pins the fail-closed half of the E-9 unlock.
///
/// E9-FILE-ROOT-RECOVERY-1 widened `MintRecoveryGrantsAsync` so a container source (zip/cbz/pdf/image)
/// may re-mint when its registry root really is the container FILE. Production always registers exactly
/// that (`SourceImportModels.IssueGrantsAsync` passes the same `path` to both `FindOrRegisterRootAsync`
/// and `IssueAsync`), so the happy path is the normal case.
///
/// The risk this file guards is the OTHER direction: widening the guard to accept anything. If someone
/// drops the `File.Exists` check, a caller that registered a DIRECTORY for a container kind would hand
/// that directory to `DescribeContainer`, which surfaces as a misleading file-system error instead of an
/// honest typed refusal.
///
/// These tests exercise the extracted predicate directly so they stay fast and deterministic.
/// </summary>
public sealed class RecoveryRootPredicateTests
{
    [Fact]
    public void FolderRoot_IsAlwaysUsable_BecauseTheRootIsTheContainer()
    {
        // A folder source's registry root *is* its container, so it does not need to be a file.
        var directory = Directory.CreateTempSubdirectory("nm-e9-neg-");
        try
        {
            Assert.True(SourceOperationCoordinator.IsRecoverableRoot("folder", directory.FullName));
        }
        finally
        {
            directory.Delete(recursive: true);
        }
    }

    [Fact]
    public void ContainerRoot_MustBeAnExistingFile()
    {
        var temp = Path.Combine(Path.GetTempPath(), "nm-e9-" + Guid.NewGuid().ToString("N") + ".zip");
        try
        {
            // Not created yet: a container kind whose root is a missing path must stay rejected.
            Assert.False(SourceOperationCoordinator.IsRecoverableRoot("zip", temp));

            File.WriteAllBytes(temp, Array.Empty<byte>());
            // Once the root really is the container file, the root is usable -- this is the E-9 unlock.
            Assert.True(SourceOperationCoordinator.IsRecoverableRoot("zip", temp));
        }
        finally
        {
            if (File.Exists(temp))
            {
                File.Delete(temp);
            }
        }
    }

    [Theory]
    [InlineData("zip")]
    [InlineData("cbz")]
    [InlineData("pdf")]
    [InlineData("image")]
    public void DirectoryRoot_ForAContainerKind_StaysRejected(string sourceKind)
    {
        // THIS is the negative case the ZCode adjudication required to be pinned: a caller that (incorrectly)
        // registered a directory for a container kind must still get a typed refusal, never a guessed path.
        var directory = Directory.CreateTempSubdirectory("nm-e9-neg-" + sourceKind + "-");
        try
        {
            Assert.False(
                SourceOperationCoordinator.IsRecoverableRoot(sourceKind, directory.FullName),
                $"{sourceKind}: a DIRECTORY root must not be treated as a container");

            // ... and the same kind with a real file root must be accepted, so the test cannot pass
            // merely by rejecting everything.
            var file = Path.Combine(directory.FullName, "container." + sourceKind);
            File.WriteAllBytes(file, Array.Empty<byte>());
            Assert.True(
                SourceOperationCoordinator.IsRecoverableRoot(sourceKind, file),
                $"{sourceKind}: a FILE root must be accepted (otherwise the guard is too strict)");
        }
        finally
        {
            directory.Delete(recursive: true);
        }
    }
}
