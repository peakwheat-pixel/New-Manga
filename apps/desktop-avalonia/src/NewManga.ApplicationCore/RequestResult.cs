namespace NewManga.ApplicationCore;

/// <summary>Local request outcomes, not Core wire categories or Run states.</summary>
public enum RequestFailureKind { Rejected, Faulted, Cancelled, TimedOut }

/// <summary>Source codes are carried unchanged; only a Host adapter may interpret wire errors.</summary>
public sealed record RequestFailure(
    RequestFailureKind Kind,
    string? SourceCode = null,
    string? Detail = null,
    Exception? Cause = null);

public sealed class RequestResult<T>
{
    private RequestResult(Guid requestId, T? value, RequestFailure? error)
        => (RequestId, Value, Error) = (requestId, value, error);

    public Guid RequestId { get; }
    public T? Value { get; }
    public RequestFailure? Error { get; }
    public bool IsSuccess => Error is null;

    public static RequestResult<T> Success(Guid requestId, T value) => new(requestId, value, null);
    public static RequestResult<T> Failure(Guid requestId, RequestFailure error)
    {
        ArgumentNullException.ThrowIfNull(error);
        return new(requestId, default, error);
    }
}

/// <summary>A request-local refusal supplied by a future adapter, with no shared LastError.</summary>
public sealed class RequestRejectedException(RequestFailure failure)
    : Exception(failure.Detail ?? failure.SourceCode ?? "Request refused.")
{
    public RequestFailure Failure { get; } = failure;
}
