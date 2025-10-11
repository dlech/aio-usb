# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol

from ._lib import libudev


class UDevContext(ctypes.c_void_p):
    """
    Object representing the library context.
    """

    @staticmethod
    def new() -> "UDevContext":
        """
        Create udev library context.

        Returns:
            A new :class:`UDevContext` object.

        Raises:
            OSError: If the context could not be created.
        """
        return udev_new()

    def unref(self) -> None:
        """
        Release the references on the context object.

        This is used for deterministic cleanup. It is safe to call this method
        multiple times. After the first call, the context object must not be
        used anymore.
        """
        if self.value:
            udev_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()


class _udev_new(Protocol):
    def __call__(self) -> UDevContext: ...


udev_new: _udev_new = ctypes.CFUNCTYPE(UDevContext, use_errno=True)(
    ("udev_new", libudev)
)


def _errcheck_udev_new(result: UDevContext, func: _udev_new, args: None) -> UDevContext:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_new failed")
    return result


udev_new.errcheck = _errcheck_udev_new  # type: ignore


class _udev_unref(Protocol):
    def __call__(self, udev: UDevContext) -> None: ...


udev_unref: _udev_unref = ctypes.CFUNCTYPE(ctypes.c_void_p, UDevContext)(
    ("udev_unref", libudev), ((1, "udev"),)
)
