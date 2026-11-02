using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace NewManga.App.ViewModels.Fluent;

public enum FluentPageState
{
    Loading,
    Error,
    Empty,
    Ready,
    Partial,
    ReadOnly,
    Running,
    Conflict,
}

public abstract class FluentViewModel : INotifyPropertyChanged
{
    private FluentPageState _state;
    private string _status = string.Empty;
    private string _error = string.Empty;

    public event PropertyChangedEventHandler? PropertyChanged;

    public FluentPageState State
    {
        get => _state;
        protected set => Set(ref _state, value);
    }

    public string Status
    {
        get => _status;
        protected set => Set(ref _status, value);
    }

    public string Error
    {
        get => _error;
        protected set => Set(ref _error, value);
    }

    protected bool Set<T>(ref T field, T value, [CallerMemberName] string? name = null)
    {
        if (EqualityComparer<T>.Default.Equals(field, value))
        {
            return false;
        }

        field = value;
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
        return true;
    }

    protected void Changed([CallerMemberName] string? name = null) =>
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
}
