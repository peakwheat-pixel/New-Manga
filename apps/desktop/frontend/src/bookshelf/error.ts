/**
 * W28: ErrorEnvelope 语义分支映射 (M2-C1 §8)
 * 严格按 code / category / retryable 语义分支，禁止按 message 文本分支。
 * 不暴露路径、堆栈或内部调用细节。
 */

export interface SemanticErrorInfo {
  code: string;
  category: "validation" | "conflict" | "unavailable" | "internal" | "unknown";
  title: string;
  message: string;
  retryable: boolean;
}

const KNOWN_CODE_MAP: Record<
  string,
  {
    category: "validation" | "conflict" | "unavailable" | "internal" | "unknown";
    title: string;
    message: string;
    retryable: boolean;
  }
> = {
  CORE_UNAVAILABLE: {
    category: "unavailable",
    title: "服务不可用",
    message: "Python Core 核心服务当前不可用，请检查服务状态并重试。",
    retryable: true,
  },
  INVALID_REQUEST: {
    category: "validation",
    title: "请求参数无效",
    message: "提交的请求参数格式不符合接口规范。",
    retryable: false,
  },
  PAGE_NOT_FOUND: {
    category: "validation",
    title: "未找到页面",
    message: "指定的页面记录不存在或已被删除。",
    retryable: false,
  },
  PAGE_NAV_MALFORMED: {
    category: "internal",
    title: "导航数据异常",
    message: "获取的章节或页面导航数据格式无法解析。",
    retryable: true,
  },
  PAGE_RESOURCE_MALFORMED: {
    category: "internal",
    title: "资源数据异常",
    message: "页面对应的资源凭证响应格式不符合规范。",
    retryable: true,
  },
  IMPORT_REPORT_MALFORMED: {
    category: "internal",
    title: "导入结果异常",
    message: "导入操作返回的数据结构无法解析。",
    retryable: false,
  },
  HOST_SESSION_INVALID: {
    category: "conflict",
    title: "会话已失效",
    message: "主机与 Core 通信会话已过期，请重启应用或重试。",
    retryable: true,
  },
  SOURCE_READ_FAILED: {
    category: "unavailable",
    title: "文件读取失败",
    message: "所选源文件或目录读取失败，可能权限不足或文件被占用。",
    retryable: true,
  },
  REF_NOT_FOUND: {
    category: "validation",
    title: "资源未找到",
    message: "请求的资源未在资源通道中注册。",
    retryable: false,
  },
  REF_REVOKED: {
    category: "conflict",
    title: "资源已撤回",
    message: "该资源引用已被撤销。",
    retryable: true,
  },
  REF_EXPIRED: {
    category: "conflict",
    title: "资源引用已过期",
    message: "该资源的临时访问凭据已过期。",
    retryable: true,
  },
  RESOURCE_TOO_LARGE: {
    category: "validation",
    title: "资源超出限制",
    message: "文件尺寸超过资源通道支持的上限（256 MiB）。",
    retryable: false,
  },
  PROTOCOL_MALFORMED: {
    category: "internal",
    title: "协议格式异常",
    message: "底层消息格式不符合协议契约。",
    retryable: false,
  },
  TAURI_BRIDGE_MISSING: {
    category: "unavailable",
    title: "Tauri 通信桥缺失",
    message: "前端无法连接到 Tauri 原生宿主运行时。",
    retryable: false,
  },
};

const SAFE_ERROR_CODE = /^[A-Z][A-Z0-9_]{0,63}$/;

export function parseSemanticError(
  rawError: unknown,
  defaultCode = "UNKNOWN_ERROR",
): SemanticErrorInfo {
  let code = defaultCode;
  if (typeof rawError === "string") {
    code = rawError;
  } else if (rawError && typeof rawError === "object") {
    const obj = rawError as { code?: unknown; message?: unknown };
    if (typeof obj.code === "string") {
      code = obj.code;
    } else if (typeof obj.message === "string") {
      // If code is not present, use defaultCode, do NOT parse message text!
      code = defaultCode;
    }
  }

  if (!SAFE_ERROR_CODE.test(code)) {
    code = SAFE_ERROR_CODE.test(defaultCode) ? defaultCode : "UNKNOWN_ERROR";
  }

  const mapped = KNOWN_CODE_MAP[code];
  if (mapped) {
    return {
      code,
      category: mapped.category,
      title: mapped.title,
      message: mapped.message,
      retryable: mapped.retryable,
    };
  }

  return {
    code,
    category: "unknown",
    title: "操作未完成",
    message: `系统报告代码：${code}`,
    retryable: true,
  };
}
