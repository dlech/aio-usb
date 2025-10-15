# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
import ctypes
import sys
from collections.abc import AsyncGenerator, Iterable
from contextlib import AbstractAsyncContextManager, ExitStack, asynccontextmanager
from typing import Any

from aio_usb.backend.interface import UsbBackendInterface, UsbInterfaceMatch
from aio_usb.interface import UsbInterface

if sys.platform != "darwin":
    raise ImportError("This module is only available on macOS")

from rubicon.objc.runtime import objc_id
from rubicon.objc.types import NSRange
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
    IOUSBConfigurationDescriptorPtr,
    IOUSBDescriptorHeaderPtr,
    IOUSBDeviceRequest,
    IOUSBEndpointDescriptorPtr,
    IOUSBInterfaceDescriptorPtr,
)
from aio_usb.backend.rubicon_objc.io_usb_host import (
    IOUSBGetNextEndpointDescriptor,
    IOUSBGetNextInterfaceDescriptor,
    IOUSBHostAbortOption,
    IOUSBHostDevice,
    IOUSBHostInterface,
)
from aio_usb.backend.rubicon_objc.runtime import NSErrorError, mach_error_string
from aio_usb.ch9 import UsbControlRequest
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


def _iterate_interface_descriptors(
    cfg_desc: IOUSBConfigurationDescriptorPtr,
) -> Iterable[IOUSBInterfaceDescriptorPtr]:
    iface_desc = IOUSBGetNextInterfaceDescriptor(cfg_desc, None)
    while iface_desc:
        yield iface_desc

        iface_desc = IOUSBGetNextInterfaceDescriptor(
            cfg_desc,
            ctypes.cast(iface_desc, IOUSBDescriptorHeaderPtr),
        )


def _iterate_endpoint_descriptors(
    cfg_desc: IOUSBConfigurationDescriptorPtr,
    iface_desc: IOUSBInterfaceDescriptorPtr,
) -> Iterable[IOUSBEndpointDescriptorPtr]:
    ep_desc = IOUSBGetNextEndpointDescriptor(cfg_desc, iface_desc, None)
    while ep_desc:
        yield ep_desc

        ep_desc = IOUSBGetNextEndpointDescriptor(
            cfg_desc,
            iface_desc,
            ctypes.cast(ep_desc, IOUSBDescriptorHeaderPtr),
        )


class RubiconObjCUsbInterface(UsbBackendInterface):
    def __init__(self, iface: IOUSBHostInterface) -> None:
        self._iface = iface

    @property
    @override
    def interface_number(self) -> int:
        return self._iface.interfaceDescriptor.contents.bInterfaceNumber

    @property
    @override
    def alternate_setting(self) -> int:
        return self._iface.interfaceDescriptor.contents.bAlternateSetting

    @property
    @override
    def interface_class(self) -> int:
        return self._iface.interfaceDescriptor.contents.bInterfaceClass

    @property
    @override
    def interface_subclass(self) -> int:
        return self._iface.interfaceDescriptor.contents.bInterfaceSubClass

    @property
    @override
    def interface_protocol(self) -> int:
        return self._iface.interfaceDescriptor.contents.bInterfaceProtocol

    @property
    @override
    def description(self) -> str | None:
        raise NotImplementedError(
            "Need to find a way to get this from the IORegistryEntry"
        )


@asynccontextmanager
async def _open_interface(
    device: IOUSBHostDevice,
    match: UsbInterfaceMatch,
    alternate: int,
) -> AsyncGenerator[Any, UsbInterface]:
    interface_number = match.get("number")
    interface_class = match.get("class_")
    interface_subclass = match.get("subclass")
    interface_protocol = match.get("protocol")

    # NB: This won't match anything if we don't follow the specific rules for
    # combinations of keys in the dictionary.
    vendor_id = (
        device.deviceDescriptor.contents.idVendor
        if interface_number is not None or interface_class == 0xFF
        else None
    )
    product_id = (
        device.deviceDescriptor.contents.idProduct
        if interface_number is not None
        else None
    )
    configuration_value = (
        device.configurationDescriptor.contents.bConfigurationValue
        if interface_number is not None
        else None
    )

    match_dict = IOUSBHostInterface.createMatchingDictionaryWithVendorID(
        vendor_id,
        productID=product_id,
        bcdDevice=None,
        interfaceNumber=interface_number,
        configurationValue=configuration_value,
        interfaceClass=interface_class,
        interfaceSubclass=interface_subclass,
        interfaceProtocol=interface_protocol,
        speed=None,
        productIDArray=None,
    )

    for child in IORegistryEntry.from_handle(device.ioService).get_child_iterator():
        service = child.as_(IOService)
        if service.match_property_table(match_dict):
            break
    else:
        raise ValueError("No such interface found")

    error = objc_id()
    iface = IOUSBHostInterface.alloc().initWithIOService(
        service, options=0, queue=None, error=error, interestHandler=None
    )
    if iface is None:
        raise NSErrorError(error)

    try:
        if not iface.selectAlternateSetting(alternate, error=error):
            raise NSErrorError(error)

        yield UsbInterface(RubiconObjCUsbInterface(iface))
    finally:
        iface.destroy()


class RubiconObjCUsbDevice(UsbBackendDevice):
    def __init__(self, device: IOUSBHostDevice) -> None:
        self._device = device
        self._properties = IORegistryEntry.from_handle(device.ioService).properties

    @property
    @override
    def vendor_id(self) -> int:
        return self._properties["idVendor"]

    @property
    @override
    def product_id(self) -> int:
        return self._properties["idProduct"]

    @property
    @override
    def bcd_device(self) -> int:
        return self._properties["bcdDevice"]

    @property
    @override
    def bcd_usb(self) -> int:
        return self._properties["bcdUSB"]

    @property
    @override
    def class_(self) -> int:
        return self._properties["bDeviceClass"]

    @property
    @override
    def subclass(self) -> int:
        return self._properties["bDeviceSubClass"]

    @property
    @override
    def protocol(self) -> int:
        return self._properties["bDeviceProtocol"]

    @property
    @override
    def manufacturer_name(self) -> str | None:
        return self._properties.get("kUSBVendorString")

    @property
    @override
    def product_name(self) -> str | None:
        return self._properties.get("kUSBProductString")

    @property
    @override
    def serial_number(self) -> str | None:
        return self._properties.get("kUSBSerialNumberString")

    @override
    def open_interface(
        self, match: UsbInterfaceMatch, alternate: int
    ) -> AbstractAsyncContextManager[UsbInterface, bool | None]:
        return _open_interface(self._device, match, alternate)

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

    @override
    async def transfer_in(self, endpoint_address: int, length: int) -> bytes:
        # Find the interface that contains the endpoint address.
        for iface_desc in _iterate_interface_descriptors(
            self._device.configurationDescriptor
        ):
            for ep_desc in _iterate_endpoint_descriptors(
                self._device.configurationDescriptor, iface_desc
            ):
                if ep_desc.contents.bEndpointAddress == endpoint_address:
                    break
            else:
                # no match found, check next interface
                continue

            # match found, break out of outer loop as well
            break
        else:
            raise ValueError("No such endpoint found")

        match = IOUSBHostInterface.createMatchingDictionaryWithVendorID(
            self.vendor_id,
            productID=self.product_id,
            bcdDevice=None,
            interfaceNumber=iface_desc.contents.bInterfaceNumber,
            configurationValue=self._device.configurationDescriptor.contents.bConfigurationValue,
            interfaceClass=None,
            interfaceSubclass=None,
            interfaceProtocol=None,
            speed=None,
            productIDArray=None,
        )

        # REVISIT: This could cause problems if there are multiple devices with
        # the same VID/PID/interface number/configuration value. We either need
        # to add another property to the dictionary to match the parent IOService
        # or we should use an IORegistry iterator to find the IOService.
        iface_svc = IOService.get_matching_service(match)
        if iface_svc is None:
            raise RuntimeError("Interface service not found")

        error = objc_id()

        # REVISIT: we probably don't want to be creating a new object every time.
        iface_obj = IOUSBHostInterface.alloc().initWithIOService(
            iface_svc, options=0, queue=None, error=error, interestHandler=None
        )
        if iface_obj is None:
            raise NSErrorError(error)

        try:
            pipe = iface_obj.copyPipeWithAddress(endpoint_address, error=error)
            if pipe is None:
                raise NSErrorError(error)

            loop = asyncio.get_running_loop()
            future: asyncio.Future[int] = loop.create_future()

            def on_complete(status: int, bytesTransferred: int) -> None:
                if status:
                    loop.call_soon_threadsafe(
                        future.set_exception, OSError(status, mach_error_string(status))
                    )
                else:
                    loop.call_soon_threadsafe(future.set_result, bytesTransferred)

            data = iface_obj.ioDataWithCapacity(length, error=error)
            if data is None:
                raise NSErrorError(error)

            if not pipe.enqueueIORequestWithData(
                data,
                completionTimeout=5,
                error=error,
                completionHandler=on_complete,
            ):
                raise NSErrorError(error)

            try:
                transferred = await asyncio.shield(future)
            except asyncio.CancelledError:
                if not pipe.abortWithOption(
                    IOUSBHostAbortOption.Asynchronous, error=error
                ):
                    raise NSErrorError(error)

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
        finally:
            iface_obj.destroy()

    async def transfer_out(self, endpoint_address: int, data: bytes) -> int:
        # Find the interface that contains the endpoint address.
        for iface_desc in _iterate_interface_descriptors(
            self._device.configurationDescriptor
        ):
            for ep_desc in _iterate_endpoint_descriptors(
                self._device.configurationDescriptor, iface_desc
            ):
                if ep_desc.contents.bEndpointAddress == endpoint_address:
                    break
            else:
                continue
            break
        else:
            raise ValueError("No such endpoint found")

        match = IOUSBHostInterface.createMatchingDictionaryWithVendorID(
            self.vendor_id,
            productID=self.product_id,
            bcdDevice=None,
            interfaceNumber=iface_desc.contents.bInterfaceNumber,
            configurationValue=self._device.configurationDescriptor.contents.bConfigurationValue,
            interfaceClass=None,
            interfaceSubclass=None,
            interfaceProtocol=None,
            speed=None,
            productIDArray=None,
        )

        # REVISIT: This could cause problems if there are multiple devices with
        # the same VID/PID/interface number/configuration value. We either need
        # to add another property to the dictionary to match the parent IOService
        # or we should use an IORegistry iterator to find the IOService.
        iface_svc = IOService.get_matching_service(match)
        if iface_svc is None:
            raise RuntimeError("Interface service not found")

        error = objc_id()

        # REVISIT: we probably don't want to be creating a new object every time.
        iface_obj = IOUSBHostInterface.alloc().initWithIOService(
            iface_svc, options=0, queue=None, error=error, interestHandler=None
        )
        if iface_obj is None:
            raise NSErrorError(error)

        try:
            pipe = iface_obj.copyPipeWithAddress(endpoint_address, error=error)
            if pipe is None:
                raise NSErrorError(error)

            loop = asyncio.get_running_loop()
            future: asyncio.Future[int] = loop.create_future()

            def on_complete(status: int, bytesTransferred: int) -> None:
                if status:
                    loop.call_soon_threadsafe(
                        future.set_exception, OSError(status, mach_error_string(status))
                    )
                else:
                    loop.call_soon_threadsafe(future.set_result, bytesTransferred)

            data_ = iface_obj.ioDataWithCapacity(len(data), error=error)
            if data_ is None:
                raise NSErrorError(error)

            data_.replaceBytesInRange(NSRange(0, len(data)), withBytes=data)

            if not pipe.enqueueIORequestWithData(
                data_,
                completionTimeout=5,
                error=error,
                completionHandler=on_complete,
            ):
                raise NSErrorError(error)

            try:
                transferred = await asyncio.shield(future)
            except asyncio.CancelledError:
                if not pipe.abortWithOption(
                    IOUSBHostAbortOption.Asynchronous, error=error
                ):
                    raise NSErrorError(error)

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

            return transferred
        finally:
            iface_obj.destroy()


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
