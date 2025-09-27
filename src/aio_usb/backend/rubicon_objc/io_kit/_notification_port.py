# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol, final

from ..dispatch._queue import DispatchQueue, dispatch_queue_t
from ._driver_kit import mach_port_t
from ._runtime import IOKitLib


@final
class IONotificationPortRef(ctypes.c_void_p):
    """
    https://developer.apple.com/documentation/iokit/ionotificationportref?language=objc
    """

    @classmethod
    def create(cls, port: int = 0) -> "IONotificationPortRef":
        return IONotificationPortCreate(port)

    def destroy(self) -> None:
        if self.value:
            IONotificationPortDestroy(self)
            self.value = 0

    def __del__(self) -> None:
        self.destroy()

    def set_dispatch_queue(self, queue: DispatchQueue) -> None:
        IONotificationPortSetDispatchQueue(self, queue)


class _IONotificationPortCreate(Protocol):
    def __call__(self, port: int) -> IONotificationPortRef: ...


IONotificationPortCreate: _IONotificationPortCreate = ctypes.CFUNCTYPE(
    IONotificationPortRef, mach_port_t
)(("IONotificationPortCreate", IOKitLib), ((1, "port"),))


class _IONotificationPortDestroy(Protocol):
    def __call__(self, notify: IONotificationPortRef) -> None: ...


IONotificationPortDestroy: _IONotificationPortDestroy = ctypes.CFUNCTYPE(
    None, IONotificationPortRef
)(("IONotificationPortDestroy", IOKitLib), ((1, "notify"),))


class _IONotificationPortSetDispatchQueue(Protocol):
    def __call__(self, notify: IONotificationPortRef, queue: DispatchQueue) -> None: ...


IONotificationPortSetDispatchQueue: _IONotificationPortSetDispatchQueue = (
    ctypes.CFUNCTYPE(None, IONotificationPortRef, dispatch_queue_t)(
        ("IONotificationPortSetDispatchQueue", IOKitLib), ((1, "notify"), (1, "queue"))
    )
)
