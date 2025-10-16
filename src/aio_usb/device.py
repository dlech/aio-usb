# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from contextlib import AbstractAsyncContextManager
from typing import overload

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.backend.interface import UsbInterfaceMatch
from aio_usb.ch9 import (
    UsbBosDescriptor,
    UsbConfigDescriptor,
    UsbControlRequest,
    UsbDescriptorType,
    bcd_to_str,
    parse_bcd,
)
from aio_usb.control import get_descriptor, get_string_descriptor
from aio_usb.descriptor import StringDescriptor, StringLangIdDescriptor
from aio_usb.interface import UsbInterface


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
        The USB device version (bcdDevice).
        """
        return parse_bcd(self._backend.bcd_device)

    @property
    def version_str(self) -> str:
        """
        The USB device version (bcdDevice) as a string.
        """
        return bcd_to_str(self._backend.bcd_device)

    @property
    def usb_version(self) -> tuple[int, int, int]:
        """
        The USB version supported by the device (bcdUSB).
        """
        return parse_bcd(self._backend.bcd_usb)

    @property
    def usb_version_str(self) -> str:
        """
        The USB version supported by the device (bcdUSB) as a string.
        """
        return bcd_to_str(self._backend.bcd_usb)

    @property
    def class_(self) -> int:
        """
        The USB device class (bDeviceClass).
        """
        return self._backend.class_

    @property
    def subclass(self) -> int:
        """
        The USB device subclass (bDeviceSubClass).
        """
        return self._backend.subclass

    @property
    def protocol(self) -> int:
        """
        The USB device protocol (bDeviceProtocol).
        """
        return self._backend.protocol

    @property
    def manufacturer_name(self) -> str | None:
        """
        The manufacturer name, if available.
        """
        return self._backend.manufacturer_name

    @property
    def product_name(self) -> str | None:
        """
        The product name, if available.
        """
        return self._backend.product_name

    @property
    def serial_number(self) -> str | None:
        """
        The serial number, if available.
        """
        return self._backend.serial_number

    @overload
    def open_interface(
        self,
        *,
        number: int | None = None,
        alternate: int = 0,
    ) -> AbstractAsyncContextManager[UsbInterface]: ...
    @overload
    def open_interface(
        self,
        *,
        class_: int | None = None,
        subclass: int | None = None,
        protocol: int | None = None,
        alternate: int = 0,
    ) -> AbstractAsyncContextManager[UsbInterface]: ...
    def open_interface(
        self,
        *,
        number: int | None = None,
        class_: int | None = None,
        subclass: int | None = None,
        protocol: int | None = None,
        alternate: int = 0,
    ) -> AbstractAsyncContextManager[UsbInterface]:
        """
        Open a USB interface for communication.

        Args:
            number: The interface number to match (bInterfaceNumber)
            class_: The interface class to match (bInterfaceClass)
            subclass: The interface subclass to match (bInterfaceSubClass)
            protocol: The interface protocol to match (bInterfaceProtocol)
            alternate: The alternate setting to select (bAlternateSetting)

        Returns:
            An asynchronous context manager that yields the opened interface.

        Either specify only ``number`` or a combination of ``class_``, ``subclass``, and
        ``protocol``.
        """
        if number is not None and (
            class_ is not None or subclass is not None or protocol is not None
        ):
            raise TypeError(
                "Specify either number or class_/subclass/protocol, not both"
            )

        match: UsbInterfaceMatch = {}
        if number is not None:
            match["number"] = number
        if class_ is not None:
            match["class_"] = class_
        if subclass is not None:
            match["subclass"] = subclass
        if protocol is not None:
            match["protocol"] = protocol

        return self._backend.open_interface(match, alternate)

    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        return await self._backend.control_transfer_in(request)

    async def get_config_descriptor(self, index: int) -> bytes:
        """
        Get a configuration descriptor.

        Args:
            index: The configuration index.

        Returns:
            The raw configuration descriptor data.
        """

        data = await self.control_transfer_in(
            get_descriptor(
                UsbDescriptorType.CONFIGURATION,
                index,
                ctypes.sizeof(UsbConfigDescriptor),
            ),
        )

        desc = UsbConfigDescriptor.from_buffer_copy(data)

        data = await self.control_transfer_in(
            get_descriptor(UsbDescriptorType.CONFIGURATION, index, desc.wTotalLength)
        )

        return data

    async def get_lang_ids(self, num: int = 1) -> list[int]:
        """
        Get the supported language IDs.

        Args:
            num: The maximum number of language IDs to retrieve.

        Returns:
            A list of supported language IDs.
        """

        data = await self.control_transfer_in(
            get_descriptor(UsbDescriptorType.STRING, 0, 2 + num * 2),
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
            get_string_descriptor(index, lang_id, 255)
        )

        desc = StringDescriptor(data)

        return desc.string

    async def get_bos_descriptor(self) -> bytes:
        """
        Get the BOS descriptor.

        Returns:
            The raw BOS descriptor data.
        """

        data = await self.control_transfer_in(
            get_descriptor(UsbDescriptorType.BOS, 0, ctypes.sizeof(UsbBosDescriptor)),
        )

        bos = UsbBosDescriptor.from_buffer_copy(data)

        data = await self.control_transfer_in(
            get_descriptor(UsbDescriptorType.BOS, 0, bos.wTotalLength),
        )

        return data
