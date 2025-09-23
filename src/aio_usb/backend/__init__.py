# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import sys

from aio_usb.backend.provider import BackendProvider


def get_backend() -> BackendProvider:
    """
    Get the backend implementation for USB device communication.
    """
    if sys.platform == "win32":
        from .winrt import WinRTBackend

        return WinRTBackend()

    raise NotImplementedError(f"No backend for platform: {sys.platform}")
