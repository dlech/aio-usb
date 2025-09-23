# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod

from aio_usb.control import UsbControlTransferSetup


class UsbBackendDevice(ABC):
    """
    An abstract base class for a USB device opened for communication.
    """

    @property
    @abstractmethod
    def vendor_id(self) -> int:
        """
        The USB vendor ID (idVendor).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def product_id(self) -> int:
        """
        The USB product ID (idProduct).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> int:
        """
        The USB product version (bcdDevice).
        """
        raise NotImplementedError

    @abstractmethod
    async def control_transfer_in(
        self, setup: UsbControlTransferSetup, length: int
    ) -> bytes:
        raise NotImplementedError
