# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
import ctypes
import sys
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, ExitStack, asynccontextmanager
from typing import Any

from aio_usb.ch9 import (
    UsbControlRequest,
    UsbDescriptorType,
    UsbDeviceDescriptor,
    UsbRequest,
)

if sys.platform != "win32":
    raise ImportError("This module is only available on Windows")

import winrt.windows.devices.enumeration as wde
import winrt.windows.devices.usb as wdu
import winrt.windows.storage.streams as wss
from typing_extensions import override
from winrt.system import unbox_uint8, unbox_uint16

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.backend.monitor import UsbMonitor
from aio_usb.backend.provider import BackendProvider
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo

# Windows device enumeration AQS (Advanced Query Syntax) conditionals

WINUSB_DEVICE_AQS = (
    'System.Devices.InterfaceClassGuid:="{DEE824EF-729B-4A0E-9C14-B7117D33A817}"'
)
ENABLED_AQS = "System.Devices.InterfaceEnabled:=System.StructuredQueryType.Boolean#True"

# Combined AQS filter for all enabled WinUSB devices for passing to functions
AQS_FILTER = f"{WINUSB_DEVICE_AQS} AND {ENABLED_AQS}"


# Windows device enumeration property names

# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-usbvendorid
USB_VENDOR_ID = "System.DeviceInterface.WinUsb.UsbVendorId"
# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-usbproductid
USB_PRODUCT_ID = "System.DeviceInterface.WinUsb.UsbProductId"
# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-usbclass
USB_CLASS = "System.DeviceInterface.WinUsb.UsbClass"
# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-usbsubclass
USB_SUBCLASS = "System.DeviceInterface.WinUsb.UsbSubClass"
# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-usbprotocol
USB_PROTOCOL = "System.DeviceInterface.WinUsb.UsbProtocol"
# https://learn.microsoft.com/en-us/windows/win32/properties/props-system-deviceinterface-winusb-deviceinterfaceclasses
DEVICE_INTERFACE_CLASSES = "System.DeviceInterface.WinUsb.DeviceInterfaceClasses"

# List of additional properties to request when enumerating devices
ADDITIONAL_PROPERTIES = [
    USB_VENDOR_ID,
    USB_PRODUCT_ID,
    USB_CLASS,
    USB_SUBCLASS,
    USB_PROTOCOL,
    DEVICE_INTERFACE_CLASSES,
]


def _marshal_device_info(info: wde.DeviceInformation) -> UsbDeviceInfo:
    return UsbDeviceInfo(
        device_id=info.id,
        name=info.name,
        vendor_id=unbox_uint16(info.properties[USB_VENDOR_ID]),
        product_id=unbox_uint16(info.properties[USB_PRODUCT_ID]),
        class_=unbox_uint8(info.properties[USB_CLASS]),
        subclass=unbox_uint8(info.properties[USB_SUBCLASS]),
        protocol=unbox_uint8(info.properties[USB_PROTOCOL]),
    )


class WinRTUsbDevice(UsbBackendDevice):
    def __init__(
        self, device: wdu.UsbDevice, device_descriptor: UsbDeviceDescriptor
    ) -> None:
        self._device = device
        self._device_descriptor = device_descriptor

    @property
    @override
    def device_descriptor(self) -> UsbDeviceDescriptor:
        return self._device_descriptor

    @override
    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        # REVISIT: This should work, but it doesn't. Need to investigate more.
        # It could be bug in Windows or a bug in PyWinRT.
        # setup = wdu.UsbSetupPacket(request)

        setup = wdu.UsbSetupPacket()
        setup.request_type.direction = wdu.UsbTransferDirection(
            request.bmRequestType >> 7
        )
        setup.request_type.control_transfer_type = wdu.UsbControlTransferType(
            (request.bmRequestType >> 5) & 0x03
        )
        setup.request_type.recipient = wdu.UsbControlRecipient(
            request.bmRequestType & 0x1F
        )
        setup.request = request.bRequest
        setup.value = request.wValue
        setup.index = request.wIndex
        setup.length = request.wLength

        buf = wss.Buffer(request.wLength)
        await self._device.send_control_in_transfer_async(setup, buf)

        return bytes(buf)


@asynccontextmanager
async def _open_monitor() -> AsyncGenerator[Any, UsbMonitor]:
    with ExitStack() as stack:
        loop = asyncio.get_running_loop()
        watcher = (
            wde.DeviceInformation.create_watcher_aqs_filter_and_additional_properties(
                AQS_FILTER, ADDITIONAL_PROPERTIES
            )
        )

        added_queue: asyncio.Queue[UsbDeviceInfo] = asyncio.Queue()

        def on_added(sender: wde.DeviceWatcher, args: wde.DeviceInformation) -> None:
            info = _marshal_device_info(args)
            loop.call_soon_threadsafe(added_queue.put_nowait, info)

        removed_queue: asyncio.Queue[str] = asyncio.Queue()

        def on_removed(
            sender: wde.DeviceWatcher, args: wde.DeviceInformationUpdate
        ) -> None:
            loop.call_soon_threadsafe(removed_queue.put_nowait, args.id)

        added_token = watcher.add_added(on_added)
        stack.callback(watcher.remove_added, added_token)
        removed_token = watcher.add_removed(on_removed)
        stack.callback(watcher.remove_removed, removed_token)

        watcher.start()
        stack.callback(watcher.stop)

        yield UsbMonitor(added_queue, removed_queue)


@asynccontextmanager
async def _open_device(device_id: str) -> AsyncGenerator[Any, UsbDevice]:
    device = await wdu.UsbDevice.from_id_async(device_id)
    with device:
        # The WinRT API doesn't provide all of the fields we need for the device
        # descriptor, so we have to fetch it manually.
        setup = wdu.UsbSetupPacket()
        setup.request_type.direction = wdu.UsbTransferDirection.IN
        setup.request_type.recipient = wdu.UsbControlRecipient.DEVICE
        setup.request_type.control_transfer_type = wdu.UsbControlTransferType.STANDARD
        setup.request = UsbRequest.GET_DESCRIPTOR
        setup.value = (UsbDescriptorType.DEVICE << 8) | 0
        setup.index = 0
        setup.length = ctypes.sizeof(UsbDeviceDescriptor)
        buf = wss.Buffer(setup.length)
        await device.send_control_in_transfer_async(setup, buf)

        device_descriptor = UsbDeviceDescriptor.from_buffer_copy(buf)

        yield UsbDevice(WinRTUsbDevice(device, device_descriptor))


class WinRTBackend(BackendProvider):
    """
    Backend implementation for Windows using WinRT APIs.
    """

    @override
    def open_monitor(self) -> AbstractAsyncContextManager[UsbMonitor]:
        return _open_monitor()

    @override
    async def list_devices(self) -> list[UsbDeviceInfo]:
        devices = await wde.DeviceInformation.find_all_async_aqs_filter_and_additional_properties(
            AQS_FILTER, ADDITIONAL_PROPERTIES
        )

        return [_marshal_device_info(d) for d in devices]

    @override
    def open_device(self, device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
        return _open_device(device_id)
