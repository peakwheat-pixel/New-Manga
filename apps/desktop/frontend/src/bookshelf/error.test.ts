import { describe, expect, it } from "vitest";
import { parseSemanticError } from "./error";

describe("W28 ErrorEnvelope Semantic Mapping", () => {
  it("maps CORE_UNAVAILABLE to unavailable category with retryable true", () => {
    const err = parseSemanticError("CORE_UNAVAILABLE");
    expect(err.code).toBe("CORE_UNAVAILABLE");
    expect(err.category).toBe("unavailable");
    expect(err.title).toBe("服务不可用");
    expect(err.retryable).toBe(true);
    expect(err.message).toContain("Core");
  });

  it("maps INVALID_REQUEST to validation category with retryable false", () => {
    const err = parseSemanticError("INVALID_REQUEST");
    expect(err.code).toBe("INVALID_REQUEST");
    expect(err.category).toBe("validation");
    expect(err.title).toBe("请求参数无效");
    expect(err.retryable).toBe(false);
  });

  it("maps HOST_SESSION_INVALID to conflict category with retryable true", () => {
    const err = parseSemanticError({ code: "HOST_SESSION_INVALID" });
    expect(err.code).toBe("HOST_SESSION_INVALID");
    expect(err.category).toBe("conflict");
    expect(err.retryable).toBe(true);
  });

  it("extracts code from Error object with code property", () => {
    const errorObj = { code: "SOURCE_READ_FAILED", message: "ignored message text" };
    const err = parseSemanticError(errorObj);
    expect(err.code).toBe("SOURCE_READ_FAILED");
    expect(err.category).toBe("unavailable");
    expect(err.retryable).toBe(true);
  });

  it("strictly adheres to W28: does not parse message text string for error branching", () => {
    // If an error object only has a message without a code, it defaults to UNKNOWN_ERROR,
    // avoiding semantic branching on free-form message text.
    const messageOnlyError = new Error("Something broke inside the backend");
    const err = parseSemanticError(messageOnlyError);
    expect(err.code).toBe("UNKNOWN_ERROR");
    expect(err.category).toBe("unknown");
  });

  it("handles unknown error codes gracefully without exposing stack traces or filesystem paths", () => {
    const err = parseSemanticError("CUSTOM_ERROR_CODE");
    expect(err.code).toBe("CUSTOM_ERROR_CODE");
    expect(err.category).toBe("unknown");
    expect(err.retryable).toBe(true);
    expect(err.message).toBe("系统报告代码：CUSTOM_ERROR_CODE");
  });
});
