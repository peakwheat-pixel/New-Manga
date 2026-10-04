"""AC3：manifest 原子写+读回校验+中断恢复（桩——红绿纪律先红后绿）。"""

from __future__ import annotations

TMP_SUFFIX = ".tmp"


class ManifestValidationError(ValueError):
    """manifest 读回校验失败。"""


def atomic_write_json(path, obj):
    """原子写 JSON：tmp+fsync+os.replace，写后读回校验。"""
    raise NotImplementedError


def write_manifest(path, samples, seed=None, extra=None):
    """写 manifest 容器文件（kind/schema_version/samples/lock）。"""
    raise NotImplementedError


def load_manifest(path):
    """读 manifest 并逐样本校验，返回 (container_dict, [SampleRecord])。"""
    raise NotImplementedError


def cleanup_stale_tmp(path):
    """清理上次中断残留的 tmp 文件。"""
    raise NotImplementedError
