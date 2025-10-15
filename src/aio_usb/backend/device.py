# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from aio_usb.backend.interface import UsbInterfaceMatch
from aio_usb.ch9 import UsbConfigDescriptor, UsbControlRequest, UsbDeviceDescriptor
from aio_usb.interface import UsbInterface


class UsbBackendDevice(ABC):
    """
    An abstract base class for a USB device opened for communication.
    """

    @property
    @abstractmethod
    def device_descriptor(self) -> UsbDeviceDescriptor:
        """
        The device descriptor.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def configuration_descriptor(self) -> UsbConfigDescriptor:
        """
        The configuration descriptor of the currently selected configuration.
        """
        raise NotImplementedError

    @abstractmethod
    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def transfer_in(self, endpoint_address: int, length: int) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def transfer_out(self, endpoint_address: int, data: bytes) -> int:
        raise NotImplementedError

    @abstractmethod
    def open_interface(
        self,
        match: UsbInterfaceMatch,
        alternate: int,
    ) -> AbstractAsyncContextManager[UsbInterface]:
        raise NotImplementedError
