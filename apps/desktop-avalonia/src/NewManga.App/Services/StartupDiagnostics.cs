using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;

namespace NewManga.App.Services;

/// <summary>
/// FEA-07 AC4（A07「safe startup 可诊断」）的最小 sink：把组合根已经用 <see cref="Trace"/> 写出的
/// 启动诊断（planner 诊断行 / fail-safe 警告 / 启动恢复行）落盘到 <c>&lt;log-dir&gt;/startup.log</c>。
/// </summary>
/// <remarks>
/// 设计口径（冻结卡 `FEA-07-RESIDUAL-3` 实现口径 3）：
/// <list type="bullet">
/// <item>只有一条落盘路径：<c>Install(logDirectory)</c> 挂一个 <see cref="TraceListener"/>，
/// 之后**既有**的 <c>Trace.TraceInformation</c>/<c>Trace.TraceWarning</c> 调用原样复用，不改组合根语义；</item>
/// <item>sink 自身**永不抛**：日志目录不可写时降级为「无 sink」，启动流程继续（与
/// <c>Program.WriteFatal</c> 的 best-effort 口径一致）；</item>
/// <item>不新建第二套诊断通道：<see cref="Report"/> 只往 <see cref="Trace"/> 写一行摘要，经同一个
/// listener 落盘，因此 `startup.log` 与 Trace 输出内容一致（Trace 兼容）。</item>
/// </list>
/// </remarks>
public static class StartupDiagnostics
{
    /// <summary>AC4 冻结文件名（与 <c>Program.WriteFatal</c> 的 <c>fatal.log</c> 同目录）。</summary>
    public const string FileName = "startup.log";

    private static readonly object Gate = new();

    private static TextWriterTraceListener? _listener;
    private static StreamWriter? _writer;
    private static string? _path;

    /// <summary>实际写入的绝对路径（未安装时为 null）。</summary>
    public static string? LogPath
    {
        get
        {
            lock (Gate)
            {
                return _path;
            }
        }
    }

    /// <summary>True 表示本进程已有落盘 sink。</summary>
    public static bool IsInstalled
    {
        get
        {
            lock (Gate)
            {
                return _listener is not null;
            }
        }
    }

    /// <summary>
    /// 安装 sink（进程内幂等）。空/非法目录只返回 false，绝不抛出：诊断不能成为新的启动失败面。
    /// </summary>
    public static bool Install(string? logDirectory)
    {
        lock (Gate)
        {
            if (_listener is not null)
            {
                return false;
            }

            if (string.IsNullOrWhiteSpace(logDirectory))
            {
                return false;
            }

            try
            {
                Directory.CreateDirectory(logDirectory);
                var path = Path.Combine(logDirectory, FileName);
                var stream = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.Read);
                var writer = new StreamWriter(stream, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false))
                {
                    AutoFlush = true,
                };
                var listener = new StartupLogListener(writer);
                Trace.Listeners.Add(listener);
                Trace.AutoFlush = true;
                _writer = writer;
                _listener = listener;
                _path = path;

                // 首行固定版本标记：证据侧据此判定 sink 真的接上了（而不是「文件恰好存在」）。
                Trace.TraceInformation($"startup-diagnostics: sink v1 installed ({path})");
                return true;
            }
            catch (Exception ex) when (ex is IOException
                or UnauthorizedAccessException
                or ArgumentException
                or NotSupportedException
                or DirectoryNotFoundException
                or PathTooLongException)
            {
                _writer = null;
                _listener = null;
                _path = null;
                return false;
            }
        }
    }

    /// <summary>
    /// 写一行可诊断的启动摘要（AC4：「safe startup 可诊断」）。只走 <see cref="Trace"/>，
    /// 因此有无 sink 都不会改变启动行为。
    /// </summary>
    public static void Report(StartupPlan? plan)
    {
        if (plan is null)
        {
            Trace.TraceInformation("startup: plan=<null> (composition root produced no plan)");
            return;
        }

        Trace.TraceInformation(
            string.Create(
                CultureInfo.InvariantCulture,
                $"startup: shell={plan.ShellKind} requested={plan.RequestedFrontendId ?? "<none>"} " +
                $"effective={plan.EffectiveFrontendId} fallback={plan.IsFallback}"));
    }

    /// <summary>测试用：卸载并关闭 sink（生产路径不调用；进程内只安装一次）。</summary>
    internal static void ResetForTests()
    {
        lock (Gate)
        {
            if (_listener is { } listener)
            {
                Trace.Listeners.Remove(listener);
                listener.Flush();
                listener.Close();
                listener.Dispose();
            }

            _writer = null;
            _listener = null;
            _path = null;
        }
    }

    /// <summary>
    /// 把 <see cref="Trace"/> 事件（Information/Warning/Error/Verbose）写成一行
    /// <c>&lt;utc 时间戳&gt; &lt;级别&gt; &lt;消息&gt;</c>；原始 <c>Trace.Write</c> 原样追加。
    /// 写入加锁且吞掉 IO 异常：<see cref="Trace"/> 是进程级全局通道，sink 不允许把并发写或磁盘错误
    /// 变成调用方（组合根/其它组件）的异常。
    /// </summary>
    private sealed class StartupLogListener : TextWriterTraceListener
    {
        private readonly object _sync = new();

        public StartupLogListener(TextWriter writer)
            : base(writer)
        {
        }

        public override void Write(string? message) => Guard(() => base.Write(message));

        public override void WriteLine(string? message) => Guard(() => base.WriteLine(message));

        public override void Flush() => Guard(base.Flush);

        private void Guard(Action write)
        {
            lock (_sync)
            {
                try
                {
                    write();
                }
                catch (Exception ex) when (ex is IOException or ObjectDisposedException or UnauthorizedAccessException)
                {
                    // 诊断落盘失败绝不影响启动/运行：Trace 的其它 listener 仍可用。
                }
            }
        }

        public override void TraceEvent(
            TraceEventCache? eventCache,
            string source,
            TraceEventType eventType,
            int id,
            string? message)
        {
            TraceEvent(eventCache, source, eventType, id, "{0}", message);
        }

        public override void TraceEvent(
            TraceEventCache? eventCache,
            string source,
            TraceEventType eventType,
            int id,
            string? format,
            params object?[]? args)
        {
            var text = format is null
                ? string.Empty
                : args is { Length: > 0 } ? string.Format(CultureInfo.InvariantCulture, format, args) : format;
            WriteLine($"{Stamp()} {Level(eventType)} {text}");
        }

        private static string Stamp() =>
            DateTimeOffset.UtcNow.ToString("yyyy-MM-ddTHH:mm:ss.fffZ", CultureInfo.InvariantCulture);

        private static string Level(TraceEventType eventType) => eventType switch
        {
            TraceEventType.Critical or TraceEventType.Error => "FATAL",
            TraceEventType.Warning => "WARN",
            TraceEventType.Information => "INFO",
            TraceEventType.Verbose => "DEBUG",
            _ => "TRACE",
        };
    }
}
