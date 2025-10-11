# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.control import (
    UsbControlTransferSetup,
    get_descriptor,
    get_string_descriptor,
)
from aio_usb.descriptor import (
    DEVICE_DESCRIPTOR,
    STRING_DESCRIPTOR,
    DeviceDescriptor,
    StringDescriptor,
    StringLangIdDescriptor,
)


class UsbDevice:
    """
    A USB device.
    """

    def __init__(self, backend: UsbBackendDevice) -> None:
        """
        Args:
            backend: The backend-specific device object.
        """
        self._backend = backend

    @property
    def vendor_id(self) -> int:
        """
        The USB vendor ID (idVendor).
        """
        return self._backend.vendor_id

    @property
    def product_id(self) -> int:
        """
        The USB product ID (idProduct).
        """
        return self._backend.product_id

    @property
    def version(self) -> tuple[int, int, int]:
        """
        The USB product version (bcdDevice).
        """
        bcd_version = self._backend.version
        major = (bcd_version >> 8) & 0xFF
        minor = (bcd_version >> 4) & 0x0F
        patch = bcd_version & 0x0F
        return major, minor, patch

    async def control_transfer_in(
        self, setup: UsbControlTransferSetup, length: int
    ) -> bytes:
        return await self._backend.control_transfer_in(setup, length)

    async def get_device_descriptor(self) -> DeviceDescriptor:
        """
        Get the device descriptor.

        Returns:
            The device descriptor.
        """

        data = await self.control_transfer_in(
            get_descriptor(DEVICE_DESCRIPTOR, 0), DeviceDescriptor.SIZE
        )

        return DeviceDescriptor(data)

    async def get_lang_ids(self, num: int = 1) -> list[int]:
        """
        Get the supported language IDs.

        Args:
            num: The maximum number of language IDs to retrieve.

        Returns:
            A list of supported language IDs.
        """

        data = await self.control_transfer_in(
            get_descriptor(STRING_DESCRIPTOR, 0), 2 + num * 2
        )

        desc = StringLangIdDescriptor(data)

        return desc.langids

    async def get_string(self, index: int, lang_id: int) -> str:
        """
        Get a string descriptor.

        Args:
            index: The string index.
            lang_id: The language ID.

        Returns:
            The string descriptor.
        """

        assert index != 0, "String index 0 is reserved"

        data = await self.control_transfer_in(
            get_string_descriptor(index, lang_id), 255
        )

        desc = StringDescriptor(data)

        return desc.string
