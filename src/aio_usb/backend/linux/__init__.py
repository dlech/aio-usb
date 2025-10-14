# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import asyncio
import ctypes
import errno
import functools
import io
import sys
from collections.abc import AsyncGenerator, Callable
from contextlib import AbstractAsyncContextManager, ExitStack, asynccontextmanager
from typing import Any, ParamSpec, Protocol, TypeVar
from weakref import WeakValueDictionary

if sys.platform != "linux":
    raise ImportError("This module is only available on Linux")

from typing_extensions import override

from aio_usb.backend.device import UsbBackendDevice
from aio_usb.backend.monitor import UsbMonitor
from aio_usb.backend.provider import BackendProvider
from aio_usb.ch9 import UsbControlRequest, UsbDeviceDescriptor
from aio_usb.device import UsbDevice
from aio_usb.discovery import UsbDeviceInfo

from .lib.linux.usbdevice_fs import (
    USBDEVFS_DISCARDURB,
    USBDEVFS_REAPURBNDELAY,
    USBDEVFS_SUBMITURB,
    USBDEVFS_URB_TYPE_CONTROL,
    usbdevfs_urb,
)
from .lib.udev import UDevContext, UDevDevice, UDevEnumerate, UDevMonitor

# same as Apple's IOUSBHostDefaultControlCompletionTimeout
_DEFAULT_CONTROL_TIMEOUT = 5

_udev = UDevContext.new()
_weak_refs = WeakValueDictionary[int, asyncio.Event]()

_libc = ctypes.CDLL("libc.so.6")

_P = ParamSpec("_P")
_TReturn = TypeVar("_TReturn")


# Syscalls can be interrupted by signals, which raises InterruptedError.
# We need to retry the syscall in that case.
def _retry_on_eintr(func: Callable[_P, _TReturn]) -> Callable[_P, _TReturn]:
    @functools.wraps(func)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except InterruptedError:
                continue

    return wrapper


class _simple_ioctl_(Protocol):
    def __call__(self, fd: int, request: int, urb: Any) -> int: ...


_simple_ioctl: _simple_ioctl_ = _retry_on_eintr(
    ctypes.CFUNCTYPE(
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        use_errno=True,
    )(("ioctl", _libc), ((1, "fd"), (1, "op"), (1, "arg")))
)


def _errcheck_simple_ioctl(
    result: int,
    func: _simple_ioctl_,
    args: tuple[ctypes.c_int, ctypes.c_int, Any],
) -> int:
    if result < 0:
        err = ctypes.get_errno()
        raise OSError(err, "ioctl failed")
    return result


_simple_ioctl.errcheck = _errcheck_simple_ioctl  # type: ignore


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
    def __init__(self, dev_file: io.FileIO) -> None:
        self._dev_file = dev_file
        # Reading the usbdev file returns the device descriptor and the
        # current configuration descriptor. We just need the device descriptor.
        self._device_descriptor = UsbDeviceDescriptor.from_buffer_copy(
            dev_file.read(ctypes.sizeof(UsbDeviceDescriptor))
        )

    @property
    def device_descriptor(self) -> UsbDeviceDescriptor:
        return self._device_descriptor

    @override
    async def control_transfer_in(self, request: UsbControlRequest) -> bytes:
        class Transfer(ctypes.Structure):
            ctrl_req: UsbControlRequest
            data: ctypes.Array[ctypes.c_uint8]
            # _pack_ requires _layout_ = "ms" since Python 3.14
            _layout_ = "ms"
            _pack_ = 1
            _fields_ = [
                ("ctrl_req", UsbControlRequest),
                ("data", ctypes.c_uint8 * request.wLength),
            ]

        transfer = Transfer(request)

        urb = usbdevfs_urb()
        urb.type = USBDEVFS_URB_TYPE_CONTROL
        urb.endpoint = 0
        urb.buffer = ctypes.addressof(transfer)
        urb.buffer_length = ctypes.sizeof(transfer)

        # Use the id of an asyncio.Event as the usercontext so that the write
        # poll handler can find the event to set when the URB completes.
        event = asyncio.Event()
        _weak_refs[id(event)] = event
        urb.usercontext = id(event)

        # NB: Python's ioctl.ioctl() copies the buffer sent as the third argument
        # onto the C stack. However, the kernel expects the buffer to remain valid
        # until the URB is reaped. So we have to use ctypes to call ioctl directly.
        _simple_ioctl(self._dev_file.fileno(), USBDEVFS_SUBMITURB, ctypes.byref(urb))

        try:
            async with asyncio.timeout(_DEFAULT_CONTROL_TIMEOUT):
                await event.wait()
        finally:
            # The kernel has a pointer to urb. We need to discard it so the
            # kernel doesn't try to access memory that gets freed when this
            # method returns.
            try:
                _simple_ioctl(
                    self._dev_file.fileno(), USBDEVFS_DISCARDURB, ctypes.byref(urb)
                )
            except OSError as e:
                # If the URB has already been removed from the kernel, this will
                # fail with EINVAL, which we can ignore.
                if e.errno != errno.EINVAL:
                    raise

        if urb.status < 0:
            raise OSError(-urb.status, "USB transfer failed")

        return bytes(transfer.data[: urb.actual_length])


@asynccontextmanager
async def _open_monitor() -> AsyncGenerator[Any, UsbMonitor]:
    with ExitStack() as stack:
        added_queue: asyncio.Queue[UsbDeviceInfo] = asyncio.Queue()
        removed_queue: asyncio.Queue[str] = asyncio.Queue()

        monitor = UDevMonitor.new_from_netlink(_udev)
        stack.callback(monitor.unref)

        monitor.filter_add_match_subsystem_devtype(b"usb", b"usb_device")
        monitor.add_match_tag(b"uaccess")
        monitor.udev_monitor_filter_update()

        def on_monitor_reader() -> None:
            try:
                device = monitor.receive_device()
            except OSError as e:
                # This will happen e.g. if the device is a USB hub, so we just
                # ignore it.
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
        enumerator = UDevEnumerate.new(_udev)
        stack.callback(enumerator.unref)

        enumerator.add_match_subsystem(b"usb")
        enumerator.add_match_property(b"DEVTYPE", b"usb_device")
        enumerator.add_match_tag(b"uaccess")
        enumerator.add_match_is_initialized()

        loop = asyncio.get_running_loop()
        enumerator.scan_devices()

        for syspath in enumerator:
            device = UDevDevice.new_from_syspath(_udev, syspath)
            added_queue.put_nowait(_marshal_device_info(device))

        yield UsbMonitor(added_queue, removed_queue)


@asynccontextmanager
async def _open_device(device_id: str) -> AsyncGenerator[Any, UsbDevice]:
    with ExitStack() as stack:
        udev_device = UDevDevice.new_from_syspath(_udev, device_id.encode())
        stack.callback(udev_device.unref)

        dev_file = stack.enter_context(open(udev_device.devnode, "rb+", buffering=0))

        usbdevfs_urb_ptr = ctypes.POINTER(usbdevfs_urb)

        def on_usbdev_writer(fd: int) -> None:
            # Kernel USB async completion events will wake the poll selector and
            # set the OUT event. This means there is at least one URB that has
            # completed and is waiting to be reaped.
            urb_ptr = usbdevfs_urb_ptr()
            _simple_ioctl(fd, USBDEVFS_REAPURBNDELAY, ctypes.byref(urb_ptr))

            # The URB's usercontext is the id of an asyncio.Event that we stored
            # when we submitted the URB. We can use that to find the event and
            # set it to wake up the coroutine that is waiting for the URB to
            # complete.
            _weak_refs.pop(urb_ptr.contents.usercontext).set()

        loop = asyncio.get_running_loop()
        loop.add_writer(dev_file, on_usbdev_writer, dev_file.fileno())
        stack.callback(loop.remove_writer, dev_file)

        yield UsbDevice(LinuxUsbDevice(dev_file))


class LinuxBackend(BackendProvider):
    """
    Backend implementation for Windows using Linux APIs.
    """

    @override
    def open_monitor(self) -> AbstractAsyncContextManager[UsbMonitor]:
        return _open_monitor()

    @override
    async def list_devices(self) -> list[UsbDeviceInfo]:
        enumerator = UDevEnumerate.new(_udev)
        enumerator.add_match_subsystem(b"usb")
        enumerator.add_match_property(b"DEVTYPE", b"usb_device")
        enumerator.add_match_tag(b"uaccess")
        enumerator.add_match_is_initialized()
        enumerator.scan_devices()

        return [
            _marshal_device_info(UDevDevice.new_from_syspath(_udev, d))
            for d in enumerator
        ]

    @override
    def open_device(self, device_id: str) -> AbstractAsyncContextManager[UsbDevice]:
        return _open_device(device_id)
