"""Small runtime compatibility helpers for restricted Windows environments."""

import hashlib
import sys
import types
from typing import Any


def ensure_xxhash_available() -> None:
    """Provide the subset of xxhash used by LangSmith when its DLL is blocked.

    Some Windows application-control policies reject the unsigned ``xxhash``
    extension bundled by LangSmith. LangSmith currently uses ``xxh3_128`` only
    to derive deterministic UUID bytes, so BLAKE2b is a safe deterministic
    fallback for that narrow purpose.
    """
    try:
        import xxhash  # noqa: F401
    except ImportError:
        fallback = types.ModuleType("xxhash")

        def xxh3_128(data: bytes = b"", *args: Any, **kwargs: Any) -> Any:
            if args or kwargs:
                raise TypeError(
                    "LeoClaw's xxh3_128 fallback accepts only an optional bytes value"
                )
            return hashlib.blake2b(data, digest_size=16)

        fallback.xxh3_128 = xxh3_128  # type: ignore[attr-defined]
        fallback.__leoclaw_fallback__ = True  # type: ignore[attr-defined]
        sys.modules["xxhash"] = fallback
