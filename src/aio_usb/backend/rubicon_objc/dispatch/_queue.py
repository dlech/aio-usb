# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol, TypeAlias

from rubicon.objc.runtime import libc

from ._object import dispatch_object_t


class DispatchQueue(dispatch_object_t):
    """
    https://developer.apple.com/documentation/dispatch/dispatch_queue_t?language=objc
    """

    @classmethod
    def create(cls, label: bytes | None = None, attr: None = None) -> "DispatchQueue":
        return dispatch_queue_create(label, attr)


dispatch_queue_t: TypeAlias = DispatchQueue


class _dispatch_queue_create(Protocol):
    def __call__(self, label: bytes | None, attr: None) -> dispatch_queue_t:
        """
        Creates a new dispatch queue to which you can submit blocks.

        Args:
            label:
                A string label to attach to the queue to uniquely identify it
                in debugging tools such as Instruments, sample, stackshots, and
                crash reports. Because applications, libraries, and frameworks
                can all create their own dispatch queues, a reverse-DNS naming
                style (com.example.myqueue) is recommended. This parameter is
                optional and can be NULL.
            attr:
                In macOS 10.7 and later or iOS 4.3 and later, specify
                DISPATCH_QUEUE_SERIAL (or NULL) to create a serial queue or
                specify DISPATCH_QUEUE_CONCURRENT to create a concurrent queue.
                In earlier versions, you must specify NULL for this parameter.

        Returns:
            The newly created dispatch queue.

        https://developer.apple.com/documentation/dispatch/dispatch_queue_create?language=objc
        """
        ...


dispatch_queue_create: _dispatch_queue_create = ctypes.CFUNCTYPE(
    dispatch_queue_t, ctypes.c_char_p, ctypes.c_void_p
)(("dispatch_queue_create", libc), ((1, "label"), (1, "attr")))
