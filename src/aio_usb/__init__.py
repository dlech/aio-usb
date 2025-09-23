# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any

from typing_extensions import Unpack

from aio_usb.backend import get_backend
from aio_usb.backend.monitor import UsbMonitor
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo, UsbDeviceMatch

__all__ = [
    "find_usb_devices",
    "open_usb_device",
    "UsbDevice",
    "UsbDeviceInfo",
    "UsbDeviceMatch",
]

_backend = get_backend()


def _match_device(device: UsbDeviceInfo, match: UsbDeviceMatch) -> bool:
    for key, value in match.items():
        if getattr(device, key) != value:
            return False
    return True


@asynccontextmanager
async def _monitor_usb_devices() -> AsyncGenerator[Any, UsbMonitor]:
    """
    Monitor USB devices as they are connected and disconnected.
    """
    async with _backend.open_monitor() as monitor:
        yield monitor


def monitor_usb_devices() -> AbstractAsyncContextManager[UsbMonitor]:
    """
    Monitor USB devices as they are connected and disconnected.

    Yields:
        An asynchronous iterator that yields USB device information objects
        as devices are connected.
    """
    return _monitor_usb_devices()


async def find_usb_devices(
    **kwargs: Unpack[UsbDeviceMatch],
) -> list[UsbDeviceInfo]:
    """
    Find USB devices that match the given criteria.
    Args:
        **kwargs: The device match criteria.

    Returns:
        A list of matching USB devices.
    """
    devices = await _backend.list_devices()
    return list(filter(lambda d: _match_device(d, kwargs), devices))


def open_usb_device(device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
    """
    Open a USB device for communication.
    Args:
        device_id: The device ID.

    Returns:
        An asynchronous context manager for the device.
    """
    return _backend.open_device(device_id)
