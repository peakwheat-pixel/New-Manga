"""Resource channel application package (M2-RC1)."""

from application.resource_channel.dto import (
    ALLOWED_SCOPE_CLASSES,
    USER_SOURCE_SCOPE,
    DEFAULT_TTL_SECONDS,
    MAX_ACTIVE_REFERENCES,
    MAX_RESOURCE_BYTES,
    MAX_SUBSCRIBERS_PER_RESOURCE,
    ReferenceGrant,
    ResourceFacts,
    TypedResourceChannelError,
)
from application.resource_channel.service import ResourceChannelService

__all__ = [
    "ALLOWED_SCOPE_CLASSES",
    "USER_SOURCE_SCOPE",
    "DEFAULT_TTL_SECONDS",
    "MAX_ACTIVE_REFERENCES",
    "MAX_RESOURCE_BYTES",
    "MAX_SUBSCRIBERS_PER_RESOURCE",
    "ReferenceGrant",
    "ResourceChannelService",
    "ResourceFacts",
    "TypedResourceChannelError",
]
