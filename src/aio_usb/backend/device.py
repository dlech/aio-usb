# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager

from aio_usb.backend.interface import UsbInterfaceMatch
from aio_usb.ch9 import UsbControlRequest
from aio_usb.interface import UsbInterface


class UsbBackendDevice(ABC):
    """
    An abstract base class for a USB device opened for communication.
    """

    @property
    @abstractmethod
    def vendor_id(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def product_id(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def bcd_device(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def bcd_usb(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def class_(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def subclass(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def protocol(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def manufacturer_name(self) -> str | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def product_name(self) -> str | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def serial_number(self) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def open_interface(
        self,
        match: UsbInterfaceMatch,
        alternate: int,
    ) -> AbstractAsyncContextManager[UsbInterface]:
        raise NotImplementedError
