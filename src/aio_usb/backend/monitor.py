# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
from collections.abc import AsyncIterator

from aio_usb.discovery import UsbDeviceInfo


class UsbMonitor:
    def __init__(
        self,
        added_queue: asyncio.Queue[UsbDeviceInfo],
        removed_queue: asyncio.Queue[str],
    ) -> None:
        self._added = added_queue
        self._removed = removed_queue

    async def added(self) -> AsyncIterator[UsbDeviceInfo]:
        """
        A queue that yields USB device information objects as devices are connected.
        """
        while True:
            yield await self._added.get()

    async def removed(self) -> AsyncIterator[str]:
        """
        A queue that yields USB device ID strings as devices are disconnected.
        """
        while True:
            yield await self._removed.get()
