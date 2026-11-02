namespace NewManga.Presentation.Avalonia.Windows;

/// <summary>The role a window plays in the presentation layer (FEA-07 / proposal §7.3).</summary>
public enum WindowRole
{
    /// <summary>The single stable native main window.</summary>
    Main = 0,

    /// <summary>Docked/floating inspector owned by the main window.</summary>
    Inspector = 1,

    /// <summary>Independent read-only or detached-session window.</summary>
    Floating = 2,
}

/// <summary>One tracked window; <see cref="Token"/> is an opaque identity for tests/diagnostics.</summary>
public sealed record WindowRegistration(WindowRole Role, string Token);

/// <summary>
/// FEA-07 window broker: keeps the native main-window identity stable while the content tree is
/// switched, and tracks secondary windows. It deliberately owns no Host lifecycle — closing a window
/// must never dispose the Host or start it (§7.3 / FEA-04 R-STATE-4).
/// </summary>
public sealed class WindowBroker
{
    private readonly List<WindowRegistration> _windows = new();
    private readonly object _sync = new();

    public WindowRegistration? Main { get; private set; }

    public IReadOnlyList<WindowRegistration> Windows
    {
        get
        {
            lock (_sync)
            {
                return _windows.ToArray();
            }
        }
    }

    /// <summary>Registers the stable main window; only one is allowed (a second registration fails).</summary>
    public WindowRegistration RegisterMain(string token)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(token);
        lock (_sync)
        {
            if (Main is not null)
            {
                throw new InvalidOperationException("the stable main window is already registered");
            }

            var registration = new WindowRegistration(WindowRole.Main, token);
            Main = registration;
            _windows.Add(registration);
            return registration;
        }
    }

    /// <summary>Registers a secondary window (inspector/floating). The main window must exist first.</summary>
    public WindowRegistration RegisterSecondary(WindowRole role, string token)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(token);
        if (role == WindowRole.Main)
        {
            throw new ArgumentOutOfRangeException(nameof(role), "use RegisterMain for the main window");
        }

        lock (_sync)
        {
            if (Main is null)
            {
                throw new InvalidOperationException("a secondary window cannot be registered before the main window");
            }

            if (_windows.Any(w => string.Equals(w.Token, token, StringComparison.Ordinal)))
            {
                throw new InvalidOperationException($"window '{token}' is already registered");
            }

            var registration = new WindowRegistration(role, token);
            _windows.Add(registration);
            return registration;
        }
    }

    /// <summary>Removes a window registration; the main window cannot be unregistered while the app runs.</summary>
    public bool Unregister(string token)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(token);
        lock (_sync)
        {
            var registration = _windows.FirstOrDefault(w => string.Equals(w.Token, token, StringComparison.Ordinal));
            if (registration is null)
            {
                return false;
            }

            if (registration.Role == WindowRole.Main)
            {
                throw new InvalidOperationException("the stable main window cannot be unregistered");
            }

            _windows.Remove(registration);
            return true;
        }
    }

    /// <summary>Number of secondary windows currently tracked.</summary>
    public int SecondaryCount
    {
        get
        {
            lock (_sync)
            {
                return _windows.Count(w => w.Role != WindowRole.Main);
            }
        }
    }
}
