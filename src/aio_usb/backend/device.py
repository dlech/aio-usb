# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod

from aio_usb.ch9 import UsbDeviceDescriptor
from aio_usb.control import UsbControlTransferSetup


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

    @abstractmethod
    async def control_transfer_in(
        self, setup: UsbControlTransferSetup, length: int
    ) -> bytes:
        raise NotImplementedError
