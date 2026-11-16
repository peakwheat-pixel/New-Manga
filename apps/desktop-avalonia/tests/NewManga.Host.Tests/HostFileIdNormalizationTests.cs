using NewManga.Host.Sources;
using Xunit;

namespace NewManga.Host.Tests;

/// <summary>
/// HOST-CONCURRENCY-FLAKY-1 AC6 — reviewer-hcf2 P2-4 / P2-N2.
///
/// The FILE_IDENTITY_CHANGED fix was verified by static reading only: <c>test.ps1</c> never sets
/// <c>NEWMANGA_FEA11_IPC</c>, so the end-to-end tests that exercise the source-read grant path stay
/// <c>NotExecuted</c>, and the 1579/1627 green only proved "no regression". These facts pin the two
/// mechanical halves of the fix so a revert goes red without a Python Core:
///
/// <list type="number">
/// <item>the C# mirror of the frozen Core constant must stay equal to <c>identity.py</c>'s
/// <c>_FILE_MASK</c>, and</item>
/// <item><see cref="SourceReadCoordinator.DescribeContainer"/> must put the <b>normalized</b> file id
/// on the wire, never the raw 64-bit handle index the registry stores.</item>
/// </list>
///
/// Contract source of truth: <c>src/application/importing/referenced/identity.py</c> lines 3-9 / 16 / 20
/// ("every producer and every comparator calls normalize_identity — never the raw st_ino").
/// </summary>
public sealed class HostFileIdNormalizationTests : IDisposable
{
    // Frozen values, copied from src/application/importing/referenced/identity.py:16/20. If the Core
    // contract ever changes, these three numbers must change together with S.cs and this test.
    private const ulong CoreVolumeMask = 0xFFFFFFFF;
    private const ulong CoreFileMask = (1UL << 53) - 1;

    private readonly string _root = Path.Combine(
        Path.GetTempPath(), "newmanga-file-id-" + Guid.NewGuid().ToString("N"));

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(_root)) Directory.Delete(_root, recursive: true);
        }
        catch (IOException)
        {
        }
        catch (UnauthorizedAccessException)
        {
        }
    }

    [Fact]
    public void CoreFileIdMask_MatchesTheFrozenCoreIdentityContract()
    {
        // identity.py:20  _FILE_MASK = (1 << 53) - 1
        Assert.Equal(CoreFileMask, SourceSecurity.CoreFileIdMask);

        // identity.py:16  _VOLUME_MASK = 0xFFFFFFFF -- and dwVolumeSerialNumber is already a uint,
        // so the C# side intentionally has no volume mask (a uint widened to ulong cannot overflow it).
        Assert.Equal(CoreVolumeMask, uint.MaxValue);
        Assert.True(SourceSecurity.CoreFileIdMask < (ulong)long.MaxValue,
            "the masked value must stay representable as a JSON-safe signed integer");
    }

    [Fact]
    public void NormalizeFileId_MasksTo53Bits_AndIsIdempotent()
    {
        // A file id below the mask is already normalized: the kernel reuses small MFT ids often, and
        // the repo fixture (alpha.png, st_ino = 844424931403221) sits here. Masking must not move it.
        const ulong small = 844424931403221UL;
        Assert.Equal(small, SourceSecurity.NormalizeFileId(small));

        // A raw NTFS index above the mask (observed on 6/7 freshly created files) must lose its high
        // bits -- this is the exact shape that used to reach the Python comparator unmasked.
        const ulong rawOverflowing = 36873221950633840UL;
        Assert.Equal(844424931669872UL, SourceSecurity.NormalizeFileId(rawOverflowing));
        Assert.NotEqual(rawOverflowing, SourceSecurity.NormalizeFileId(rawOverflowing));

        // Normalization is idempotent, so double-normalizing at a second boundary is harmless.
        Assert.Equal(SourceSecurity.NormalizeFileId(rawOverflowing),
            SourceSecurity.NormalizeFileId(SourceSecurity.NormalizeFileId(rawOverflowing)));

        // Every 53-bit value is a fixed point; nothing above it survives.
        Assert.Equal(0UL, SourceSecurity.NormalizeFileId(1UL << 53));
        Assert.Equal(CoreFileMask, SourceSecurity.NormalizeFileId(ulong.MaxValue));
    }

    [Fact]
    public void DescribeContainer_EmitsNormalizedFileId_NotTheRawHandleIndex()
    {
        Directory.CreateDirectory(_root);

        // The regression only reproduces when the raw NTFS file index exceeds 2^53. That depends on the
        // volume's file-id reuse sequence: measured on this project, %TEMP% (C:) hands out overflowing
        // indices for ~11/12 freshly created files while the sibling workspace volume (G:) stays below
        // the mask, so the probes are created under %TEMP% on purpose. If no sample overflows we FAIL
        // instead of silently asserting the weaker form -- a green test that never saw the regression is
        // exactly the false safety this card exists to remove (see HANDOFF discipline #7).
        (string Path, (ulong Volume, ulong Id, long Size) Raw)? strong = null;
        for (var attempt = 0; attempt < 64 && strong is null; attempt++)
        {
            var path = Path.Combine(_root, $"probe-{attempt}-{Guid.NewGuid():N}.bin");
            File.WriteAllBytes(path, [0x5A]);
            var raw = SourceSecurity.Identity(path);
            if (raw.Id > CoreFileMask) strong = (path, raw);
        }

        Assert.True(strong is not null,
            "no freshly created file under " + Path.GetTempPath() + " had a raw NTFS file index above 2^53 "
            + "within 64 attempts, so the masked-vs-raw regression cannot be observed on this volume. "
            + "Do not weaken this fact to a tautology; point the probe at a high-churn volume instead.");

        var sample = strong!.Value;
        var rawId = sample.Raw.Id;
        Assert.True(rawId > CoreFileMask,
            "precondition for the anti-regression assertion: raw index must exceed 2^53");

        var facts = SourceReadCoordinator.DescribeContainer(sample.Path, maxBytes: 1 << 20);

        // Wire contract: file_id is always the normalized value.
        var wireFileId = facts["file_id"]!.GetValue<ulong>();
        Assert.Equal(SourceSecurity.NormalizeFileId(rawId), wireFileId);
        Assert.Equal(CoreFileMask & rawId, wireFileId);

        // This is the assertion that goes red if the normalization is removed: with a raw index above
        // 2^53 the unmasked value can never equal the wire value.
        Assert.NotEqual(rawId, wireFileId);

        // The registry keeps the raw value; the wire is the only place that gets masked.
        Assert.Equal(rawId, SourceSecurity.Identity(sample.Path).Id);

        // volume_serial is a uint widened to ulong: masking it would be a no-op, so it is passed through.
        Assert.Equal(sample.Raw.Volume, facts["volume_serial"]!.GetValue<ulong>());
        Assert.Equal(sample.Raw.Size, facts["size"]!.GetValue<long>());
    }
}
