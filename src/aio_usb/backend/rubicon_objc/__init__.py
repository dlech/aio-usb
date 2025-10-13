# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
import ctypes
import sys
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, ExitStack, asynccontextmanager
from typing import Any

if sys.platform != "darwin":
    raise ImportError("This module is only available on macOS")

from rubicon.objc.runtime import objc_id
from typing_extensions import override

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.backend.monitor import UsbMonitor
from aio_usb.backend.provider import BackendProvider
from aio_usb.backend.rubicon_objc.dispatch import DispatchQueue
from aio_usb.backend.rubicon_objc.foundation import NSMutableData
from aio_usb.backend.rubicon_objc.io_kit import (
    IOIterator,
    IONotificationPortRef,
    IORegistryEntry,
    IOService,
    kIOFirstMatchNotification,
    kIOReturnAborted,
    kIOTerminatedNotification,
)
from aio_usb.backend.rubicon_objc.io_kit.usb.apple_usb_definitions import (
    IOUSBDeviceRequest,
)
from aio_usb.backend.rubicon_objc.io_usb_host import (
    IOUSBHostAbortOption,
    IOUSBHostDevice,
)
from aio_usb.backend.rubicon_objc.runtime import NSErrorError, mach_error_string
from aio_usb.ch9 import UsbConfigDescriptor, UsbControlRequest, UsbDeviceDescriptor
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo


def _marshal_device_info(service: IOService) -> UsbDeviceInfo:
    entry = service.as_(IORegistryEntry)
    props = entry.properties

    return UsbDeviceInfo(
        device_id=str(entry.id),
        name=entry.name,
        vendor_id=props["idVendor"],
        product_id=props["idProduct"],
        class_=props["bDeviceClass"],
        subclass=props["bDeviceSubClass"],
        protocol=props["bDeviceProtocol"],
    )


class RubiconObjCUsbDevice(UsbBackendDevice):
    def __init__(self, device: IOUSBHostDevice) -> None:
        self._device = device
        # This works since CPU is little-endian.
        self._device_descriptor = UsbDeviceDescriptor.from_buffer_copy(
            device.deviceDescriptor.contents
        )

    @property
    @override
    def device_descriptor(self) -> UsbDeviceDescriptor:
        return self._device_descriptor

    @property
    @override
    def configuration_descriptor(self) -> UsbConfigDescriptor:
        desc = self._device.configurationDescriptor
        assert desc, "configuration is not set"
        # This works since CPU is little-endian.
        return UsbConfigDescriptor.from_buffer_copy(desc.contents)

    @override
    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        _request = IOUSBDeviceRequest(
            request.bmRequestType,
            request.bRequest,
            request.wValue,
            request.wIndex,
            request.wLength,
        )

        data = NSMutableData.dataWithLength(request.wLength)

        err_id = objc_id()

        loop = asyncio.get_running_loop()
        future: asyncio.Future[int] = loop.create_future()

        def on_complete(status: int, bytesTransferred: int) -> None:
            if status:
                loop.call_soon_threadsafe(
                    future.set_exception, OSError(status, mach_error_string(status))
                )
            else:
                loop.call_soon_threadsafe(future.set_result, bytesTransferred)

        if not self._device.enqueueDeviceRequest(
            _request,
            data=data,
            error=err_id,
            completionHandler=on_complete,
        ):
            future.cancel()
            raise NSErrorError(err_id)

        try:
            transferred = await asyncio.shield(future)
        except asyncio.CancelledError:
            if not self._device.abortDeviceRequestsWithOption(
                IOUSBHostAbortOption.Asynchronous, error=err_id
            ):
                raise NSErrorError(err_id)

            try:
                await future
            except OSError as ex:
                # abortDeviceRequestsWithOption() will cause the request to fail
                # with kIOReturnAborted, if it hasn't already completed. This is
                # expected and in this case we ignore it an just propagate the
                # cancellation. Any other error is unexpected and we propagate it.
                if ex.errno != kIOReturnAborted:
                    raise

            raise

        return ctypes.string_at(data.mutableBytes, transferred)


@asynccontextmanager
async def _open_monitor() -> AsyncGenerator[Any, UsbMonitor]:
    with ExitStack() as stack:
        loop = asyncio.get_running_loop()

        added_queue: asyncio.Queue[UsbDeviceInfo] = asyncio.Queue()

        def on_added(iterator: IOIterator) -> None:
            for obj in iterator:
                service = obj.as_(IOService)
                added_queue.put_nowait(_marshal_device_info(service))

        removed_queue: asyncio.Queue[str] = asyncio.Queue()

        def on_removed(iterator: IOIterator) -> None:
            for obj in iterator:
                entry = obj.as_(IORegistryEntry)
                removed_queue.put_nowait(str(entry.id))

        notify_port = IONotificationPortRef.create()
        stack.callback(notify_port.destroy)

        dispatch_queue = DispatchQueue.create()
        stack.callback(dispatch_queue.release)
        notify_port.set_dispatch_queue(dispatch_queue)

        match_dict = IOUSBHostDevice.createMatchingDictionaryWithVendorID(
            None,
            productID=None,
            bcdDevice=None,
            deviceClass=None,
            deviceSubclass=None,
            deviceProtocol=None,
            speed=None,
            productIDArray=None,
        )

        def on_matched(iterator: IOIterator) -> None:
            loop.call_soon_threadsafe(on_added, iterator)

        iterator = IOService.add_matching_notification(
            notify_port,
            kIOFirstMatchNotification,
            match_dict,
            on_matched,
        )
        stack.callback(iterator.release)
        # Draining the iterator starts the notifications. This will also handle
        # any devices that were already connected.
        on_added(iterator)

        def on_terminated(iterator: IOIterator) -> None:
            loop.call_soon_threadsafe(on_removed, iterator)

        iterator = IOService.add_matching_notification(
            notify_port,
            kIOTerminatedNotification,
            match_dict,
            on_terminated,
        )
        stack.callback(iterator.release)
        # Draining the iterator starts the notifications.
        on_removed(iterator)

        yield UsbMonitor(added_queue, removed_queue)


@asynccontextmanager
async def _open_device(device_id: str) -> AsyncGenerator[Any, UsbDevice]:
    matching = IORegistryEntry.id_matching(int(device_id))
    service = IOService.get_matching_service(matching)
    if service is None:
        raise RuntimeError(f"Device with ID {device_id} not found")

    error = objc_id()
    device = IOUSBHostDevice.alloc().initWithIOService(
        service, queue=None, error=error, interestHandler=None
    )
    if device is None:
        raise NSErrorError(error)

    try:
        # macOS doesn't select a configuration automatically, so we have to do
        # it ourselves. We just select the first configuration.
        if not device.configurationDescriptor:
            desc = device.configurationDescriptorWithIndex(0, error=error)
            if not desc:
                raise NSErrorError(error)
            if not device.configureWithValue(
                desc.contents.bConfigurationValue, error=error
            ):
                raise NSErrorError(error)

        yield UsbDevice(RubiconObjCUsbDevice(device))
    finally:
        device.destroy()


class RubiconObjCBackend(BackendProvider):
    """
    Backend implementation for macOS using Rubicon-ObjC.
    """

    @override
    def open_monitor(self) -> AbstractAsyncContextManager[UsbMonitor]:
        return _open_monitor()

    @override
    async def list_devices(self) -> list[UsbDeviceInfo]:
        match_dict = IOUSBHostDevice.createMatchingDictionaryWithVendorID(
            None,
            productID=None,
            bcdDevice=None,
            deviceClass=None,
            deviceSubclass=None,
            deviceProtocol=None,
            speed=None,
            productIDArray=None,
        )
        return [
            _marshal_device_info(service)
            for service in IOService.get_matching_services(match_dict)
        ]

    @override
    def open_device(self, device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
        return _open_device(device_id)
