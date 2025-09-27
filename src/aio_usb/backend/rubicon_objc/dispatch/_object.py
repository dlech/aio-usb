# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol, TypeAlias

from rubicon.objc.runtime import libc


class DispatchObject(ctypes.c_void_p):
    """
    https://developer.apple.com/documentation/dispatch/dispatch_object_t?language=objc
    """

    def release(self) -> None:
        if self.value:
            dispatch_release(self)
            self.value = 0

    def __del__(self) -> None:
        self.release()


dispatch_object_t: TypeAlias = DispatchObject


class _dispatch_retain(Protocol):
    def __call__(self, object: dispatch_object_t) -> None: ...


dispatch_retain: _dispatch_retain = ctypes.CFUNCTYPE(None, dispatch_object_t)(
    ("dispatch_retain", libc), ((1, "object"),)
)


class _dispatch_release(Protocol):
    def __call__(self, object: dispatch_object_t) -> None: ...


dispatch_release: _dispatch_release = ctypes.CFUNCTYPE(None, dispatch_object_t)(
    ("dispatch_release", libc), ((1, "object"),)
)
