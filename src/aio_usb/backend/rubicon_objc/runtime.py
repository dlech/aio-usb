# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol, final

from rubicon.objc.runtime import libc, objc_id

from .foundation import NSError


@final
class NSErrorError(OSError):
    """
    An :class:`OSError` exception that wraps an :class:`NSError` from Objective-C.
    """

    def __init__(self, id: objc_id) -> None:
        """
        Args:
            id: ObjC identifier for an NSError object.
        """
        self._nserror = NSError(id)
        super().__init__(self._nserror.code, str(self._nserror.localizedDescription))

        if self._nserror.localizedFailureReason:
            self.add_note(str(self._nserror.localizedFailureReason))

        if self._nserror.localizedRecoverySuggestion:
            self.add_note(str(self._nserror.localizedRecoverySuggestion))

    @property
    def nserror(self) -> NSError:
        """
        The wrapped NSError object.
        """
        return self._nserror


class _mach_error_string(Protocol):
    def __call__(self, error: int) -> bytes: ...

    """https://developer.apple.com/documentation/kernel/1514686-mach_error_string?language=objc"""


mach_error_string: _mach_error_string = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.c_int)(
    ("mach_error_string", libc), ((1, "error"),)
)
