using System.Diagnostics;
using NewManga.ApplicationCore;
using Xunit.Abstractions;

namespace NewManga.ApplicationCore.Tests;

public sealed class DraftBufferTests(ITestOutputHelper output)
{
    private static DraftSnapshot CreateDraft() => DraftSnapshot.Create(
        "draft-1", "session-1", "page-1", "region-1", "revision-1", 19,
        DateTimeOffset.UnixEpoch);

    [Fact]
    public void Projection_contains_exactly_eleven_fields_and_starts_at_zero()
    {
        var draft = CreateDraft();
        Assert.Equal(11, typeof(DraftSnapshot).GetProperties().Length);
        Assert.Equal(0, draft.DraftSequence);
        Assert.Equal(19, draft.PageBindingVersion);
    }

    [Fact]
    public async Task Patch_queue_is_serial_and_merges_geometry_and_style_by_key()
    {
        await using var buffer = new DraftBuffer(CreateDraft(), (_, _) => Task.CompletedTask,
            TimeSpan.FromHours(1));
        await Task.WhenAll(
            buffer.ApplyPatchAsync(new(Geometry: Map(("x", 1)), Style: Map(("font_size", 12)))),
            buffer.ApplyPatchAsync(new(Geometry: Map(("y", 2)), Style: Map(("text_color", "red")))),
            buffer.ApplyPatchAsync(new(Geometry: Map(("x", 9)), Style: Map(("font_size", 14)))));

        var snapshot = buffer.Snapshot;
        Assert.Equal(3, snapshot.DraftSequence);
        var geometry = Assert.IsAssignableFrom<IReadOnlyDictionary<string, object?>>(snapshot.Patch["geometry"]);
        var style = Assert.IsAssignableFrom<IReadOnlyDictionary<string, object?>>(snapshot.Patch["style"]);
        Assert.Equal(9, geometry["x"]);
        Assert.Equal(2, geometry["y"]);
        Assert.Equal(14, style["font_size"]);
        Assert.Equal("red", style["text_color"]);
    }

    [Fact]
    public async Task Debounce_coalesces_rapid_patches_into_one_flush()
    {
        var calls = 0;
        var flushed = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
        await using var buffer = new DraftBuffer(CreateDraft(), (_, _) =>
        {
            Interlocked.Increment(ref calls);
            flushed.TrySetResult();
            return Task.CompletedTask;
        }, TimeSpan.FromMilliseconds(80));

        for (var index = 0; index < 4; index++)
            await buffer.ApplyPatchAsync(new(Style: Map(("size", index))));
        await flushed.Task.WaitAsync(TimeSpan.FromSeconds(3));
        Assert.Equal(1, calls);
        Assert.Equal(4, buffer.Snapshot.DraftSequence);
    }

    [Fact]
    public async Task All_five_forced_flush_triggers_call_the_injected_seam()
    {
        var calls = 0;
        await using var buffer = new DraftBuffer(CreateDraft(), (_, _) =>
        {
            Interlocked.Increment(ref calls);
            return Task.CompletedTask;
        }, TimeSpan.FromHours(1));

        foreach (var trigger in new[]
        {
            DraftFlushTrigger.PageChange,
            DraftFlushTrigger.WorkspaceSwitch,
            DraftFlushTrigger.Exit,
            DraftFlushTrigger.WindowClose,
            DraftFlushTrigger.RunSubmit
        })
        {
            await buffer.ApplyPatchAsync(new(Style: Map(("index", calls))));
            var result = await buffer.FlushAsync(trigger);
            Assert.True(result.Succeeded);
            Assert.Equal(DraftBufferStatus.Flushed, result.Snapshot.Status);
        }
        Assert.Equal(5, calls);
    }

    [Fact]
    public async Task Failed_flush_keeps_patch_and_marks_conflicted()
    {
        await using var buffer = new DraftBuffer(CreateDraft(),
            (_, _) => throw new IOException("injected"), TimeSpan.FromHours(1));
        await buffer.ApplyPatchAsync(new(Text: Map(("edited_translation", "keep me"))));
        var result = await buffer.FlushAsync(DraftFlushTrigger.RunSubmit);
        Assert.False(result.Succeeded);
        Assert.Equal("DRAFT_FLUSH_FAILED", result.ErrorCode);
        Assert.Equal(DraftBufferStatus.Conflicted, result.Snapshot.Status);
        var text = Assert.IsAssignableFrom<IReadOnlyDictionary<string, object?>>(result.Snapshot.Patch["text"]);
        Assert.Equal("keep me", text["edited_translation"]);
    }

    [Fact]
    public async Task Default_debounce_measures_programmatic_edit_to_flush_latency()
    {
        const int samples = 12;
        var latencies = new List<double>();
        Stopwatch? current = null;
        TaskCompletionSource? flushed = null;
        await using var buffer = new DraftBuffer(CreateDraft(), (_, _) =>
        {
            if (current is not null && flushed is not null)
            {
                latencies.Add(current.Elapsed.TotalMilliseconds);
                flushed.TrySetResult();
            }
            return Task.CompletedTask;
        });

        for (var index = 0; index < samples; index++)
        {
            current = Stopwatch.StartNew();
            flushed = new(TaskCreationOptions.RunContinuationsAsynchronously);
            await buffer.ApplyPatchAsync(new(Style: Map(("sample", index))));
            await flushed.Task.WaitAsync(TimeSpan.FromSeconds(3));
            current.Stop();
        }
        var sorted = latencies.Order().ToArray();
        var p50 = sorted[(int)Math.Ceiling(samples * 0.50) - 1];
        var p95 = sorted[(int)Math.Ceiling(samples * 0.95) - 1];
        output.WriteLine($"Debounce measurement: n={samples}, p50={p50:F1}ms, p95={p95:F1}ms; method=12 sequential ApplyPatchAsync calls through default 400ms timer, measured from call start to injected flush seam.");
        Assert.Equal(samples, latencies.Count);
        Assert.InRange(p50, 350, 1500);
        Assert.InRange(p95, p50, 2000);
    }

    private static IReadOnlyDictionary<string, object?> Map((string Key, object? Value) pair) =>
        new Dictionary<string, object?> { [pair.Key] = pair.Value };
}
