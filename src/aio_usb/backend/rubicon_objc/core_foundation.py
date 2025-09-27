# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Any, Self

from rubicon.objc.runtime import load_library
from rubicon.objc.types import CFIndex, with_encoding
from typing_extensions import override

CoreFoundation = load_library("CoreFoundation")


class CFTypeRef(ctypes.c_void_p):
    def retain(self) -> Self:
        CFRetain(self)
        return self

    def release(self) -> None:
        CFRelease(self)

    def __del__(self) -> None:
        if self.value:
            self.release()
            self.value = 0

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, CFTypeRef):
            return NotImplemented
        return CFEqual(self, other)

    @property
    def retain_count(self) -> int:
        return CFGetRetainCount(self)


# NB: The return type is intentionally not `CFTypeRef` to avoid taking ownership
# of the new reference.
CFRetain = ctypes.CFUNCTYPE(ctypes.c_void_p, CFTypeRef)(
    ("CFRetain", CoreFoundation), ((1, "cf"),)
)

CFRelease = ctypes.CFUNCTYPE(None, CFTypeRef)(
    ("CFRelease", CoreFoundation), ((1, "cf"),)
)

CFGetRetainCount = ctypes.CFUNCTYPE(CFIndex, CFTypeRef)(
    ("CFGetRetainCount", CoreFoundation), ((1, "cf"),)
)

CFEqual = ctypes.CFUNCTYPE(ctypes.c_bool, CFTypeRef, CFTypeRef)(
    ("CFEqual", CoreFoundation), ((1, "cf1"), (1, "cf2"))
)


@with_encoding(b"^{__CFDictionary=}")
class CFDictionaryRef(CFTypeRef):
    pass


@with_encoding(b"^{__CFMutableDictionary=}")
class CFMutableDictionaryRef(CFDictionaryRef):
    pass


@with_encoding(b"^{__CFAllocator=}")
class CFAllocatorRef(CFTypeRef):
    pass
