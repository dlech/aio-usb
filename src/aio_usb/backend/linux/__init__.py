# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
import errno
import io
import sys
from collections.abc import AsyncGenerator
from contextlib import AbstractAsyncContextManager, ExitStack, asynccontextmanager
from typing import Any

if sys.platform != "linux":
    raise ImportError("This module is only available on Linux")

from typing_extensions import override

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.backend.monitor import UsbMonitor
from aio_usb.backend.provider import BackendProvider
from aio_usb.control import UsbControlTransferSetup
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo

from .lib.linux.usbdevice_fs import usbdevfs_ctrltransfer
from .lib.udev import UDevDevice, UDevEnumerate, UDevMonitor


def _marshal_device_info(device: UDevDevice) -> UsbDeviceInfo:
    class_, subclass, protocol = device[b"TYPE"].split(b"/")

    return UsbDeviceInfo(
        device_id=device.syspath.decode(),
        name=device[b"ID_MODEL_ENC"].decode("unicode_escape"),
        vendor_id=int(device[b"ID_VENDOR_ID"], 16),
        product_id=int(device[b"ID_MODEL_ID"], 16),
        class_=int(class_),
        subclass=int(subclass),
        protocol=int(protocol),
    )


class LinuxUsbDevice(UsbBackendDevice):
    def __init__(self, device: UDevDevice, dev_file: io.FileIO) -> None:
        self._udev_device = device
        self._dev_file = dev_file

    @property
    @override
    def vendor_id(self) -> int:
        return int(self._udev_device[b"ID_USB_VENDOR_ID"], 16)

    @property
    @override
    def product_id(self) -> int:
        return int(self._udev_device[b"ID_USB_MODEL_ID"], 16)

    @property
    @override
    def version(self) -> int:
        return int(self._udev_device[b"ID_USB_REVISION"], 16)

    @override
    async def control_transfer_in(
        self, setup: UsbControlTransferSetup, length: int
    ) -> bytes:
        transfer = usbdevfs_ctrltransfer()

        transfer.bRequestType = wdu.UsbTransferDirection.IN

        match setup["request_type"]:
            case "standard":
                _setup.value = wdu.UsbControlTransferType.STANDARD
            case "class":
                _setup.value = wdu.UsbControlTransferType.CLASS
            case "vendor":
                _setup.value = wdu.UsbControlTransferType.VENDOR
            case _:
                raise TypeError(f"Invalid request_type: {setup.request_type}")

        match setup["recipient"]:
            case "device":
                _setup.request_type.recipient = wdu.UsbControlRecipient.DEVICE
            case "interface":
                _setup.request_type.recipient = (
                    wdu.UsbControlRecipient.SPECIFIED_INTERFACE
                )
            case "endpoint":
                _setup.request_type.recipient = wdu.UsbControlRecipient.ENDPOINT
            case "other":
                _setup.request_type.recipient = wdu.UsbControlRecipient.OTHER
            case _:
                raise TypeError(f"Invalid recipient: {setup.recipient}")

        _setup.request = setup["request"]
        _setup.value = setup["value"]
        _setup.index = setup["index"]
        _setup.length = length

        buf = wss.Buffer(length)

        await self._udev_device.send_control_in_transfer_async(_setup, buf)

        return bytes(buf)


@asynccontextmanager
async def _open_monitor() -> AsyncGenerator[Any, UsbMonitor]:
    with ExitStack() as stack:
        added_queue: asyncio.Queue[UsbDeviceInfo] = asyncio.Queue()
        removed_queue: asyncio.Queue[str] = asyncio.Queue()

        monitor = UDevMonitor.from_netlink()
        stack.callback(monitor.unref)

        monitor.filter_add_match_subsystem_devtype(b"usb", b"usb_device")
        monitor.add_match_tag(b"uaccess")
        monitor.enable_receiving()

        def on_monitor_reader() -> None:
            try:
                device = monitor.receive_device()
            except OSError as e:
                if e.errno == errno.EPERM:
                    return
                raise

            match device.action:
                case b"add":
                    added_queue.put_nowait(_marshal_device_info(device))
                case b"remove":
                    removed_queue.put_nowait(device.devnode.decode())
                case _:
                    pass

        loop = asyncio.get_running_loop()

        loop.add_reader(monitor.fd, on_monitor_reader)
        stack.callback(loop.remove_reader, monitor.fd)

        # REVISIT: possible race condition since we start monitor before
        # enumerating, we could emit an added device twice.
        enumerator = UDevEnumerate.new()
        stack.callback(enumerator.unref)

        enumerator.add_match_subsystem(b"usb")
        enumerator.add_match_property(b"DEVTYPE", b"usb_device")
        enumerator.add_match_tag(b"uaccess")
        enumerator.add_match_is_initialized()

        enumerator.scan_devices()

        for syspath in enumerator:
            device = UDevDevice.new_from_syspath(syspath)
            added_queue.put_nowait(_marshal_device_info(device))

        yield UsbMonitor(added_queue, removed_queue)


@asynccontextmanager
async def _open_device(device_id: str) -> AsyncGenerator[Any, UsbDevice]:
    udev_device = UDevDevice.new_from_syspath(device_id.encode())
    with open(udev_device.devnode, "rb+", buffering=0) as dev_file:
        yield UsbDevice(LinuxUsbDevice(udev_device, dev_file))


class LinuxBackend(BackendProvider):
    """
    Backend implementation for Windows using Linux APIs.
    """

    @override
    def open_monitor(self) -> AbstractAsyncContextManager[UsbMonitor]:
        return _open_monitor()

    @override
    async def list_devices(self) -> list[UsbDeviceInfo]:
        enumerator = UDevEnumerate.new()
        enumerator.add_match_subsystem(b"usb")
        enumerator.add_match_property(b"DEVTYPE", b"usb_device")
        enumerator.add_match_tag(b"uaccess")
        enumerator.scan_devices()

        return [
            _marshal_device_info(UDevDevice.new_from_syspath(d)) for d in enumerator
        ]

    @override
    def open_device(self, device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
        return _open_device(device_id)
