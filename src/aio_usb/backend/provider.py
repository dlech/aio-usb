# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from aio_usb.backend.monitor import UsbMonitor
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo


class BackendProvider(ABC):
    """
    Abstract base class for backend providers.
    """

    @abstractmethod
    def open_monitor(self) -> AbstractAsyncContextManager[UsbMonitor]:
        """
        Monitor USB devices as they are connected and disconnected.

        Returns:
            An asynchronous context manager that yields an object with an
            `iter` attribute. The `iter` attribute is an asynchronous iterator
            that yields USB device information objects as devices are connected.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_devices(self) -> list[UsbDeviceInfo]:
        """
        List all available USB devices.

        Returns:
            A list of USB device information objects.
        """
        raise NotImplementedError

    @abstractmethod
    def open_device(self, device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
        """
        Open a USB device for communication.

        Args:
            device_id: The device ID.

        Returns:
            An asynchronous context manager for the device.
        """
        raise NotImplementedError
