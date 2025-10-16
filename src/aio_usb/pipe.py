# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from typing import final

from aio_usb.backend.pipe import UsbBackendInPipe, UsbBackendOutPipe


@final
class UsbInPipe:
    """
    A USB IN pipe (bulk or interrupt endpoint).
    """

    def __init__(self, backend: UsbBackendInPipe) -> None:
        self._backend = backend

    async def transfer(self, length: int) -> bytes:
        return await self._backend.transfer(length=length)


@final
class UsbOutPipe:
    """
    A USB OUT pipe (bulk or interrupt endpoint).
    """

    def __init__(self, backend: UsbBackendOutPipe) -> None:
        self._backend = backend

    async def transfer(self, data: bytes) -> int:
        return await self._backend.transfer(data=data)
