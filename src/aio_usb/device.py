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
    UsbDeviceDescriptor,
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

    @property
    def device_descriptor(self) -> UsbDeviceDescriptor:
        """
        The device descriptor.
        """
        return self._backend.device_descriptor

    @property
    def configuration_descriptor(self) -> UsbConfigDescriptor:
        """
        The configuration descriptor of the currently selected configuration.
        """
        return self._backend.configuration_descriptor

    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        return await self._backend.control_transfer_in(request)

    async def transfer_in(self, endpoint_address: int, length: int) -> bytes:
        """
        Perform a bulk or interrupt IN transfer (device to host).
        """
        return await self._backend.transfer_in(endpoint_address, length)

    async def transfer_out(self, endpoint_address: int, data: bytes) -> int:
        """
        Perform a bulk or interrupt OUT transfer (host to device).
        """
        return await self._backend.transfer_out(endpoint_address, data)

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
