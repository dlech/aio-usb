# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Literal, Protocol

from ._context import UDevContext
from ._device import UDevDevice
from ._lib import libudev


class UDevMonitor(ctypes.c_void_p):
    """
    Object handling an event source.
    """

    @staticmethod
    def new_from_netlink(
        context: UDevContext, name: Literal[b"udev", b"kernel"] = b"udev"
    ) -> "UDevMonitor":
        """
        Create new udev monitor and connect to a specified event source.

        Args:
            context: The udev library context.
            name: Name of the event source.

        Returns:
            A new monitor object.

        Raises:
            OSError: If the monitor could not be created.

        Applications should usually not connect directly to the
        "kernel" events, because the devices might not be usable
        at that time, before udev has configured them, and created
        device nodes. Accessing devices at the same time as udev,
        might result in unpredictable behavior. The "udev" events
        are sent out after udev has finished its event processing,
        all rules have been processed, and needed device nodes are
        created.
        """
        return udev_monitor_new_from_netlink(context, name)

    def unref(self) -> None:
        """
        Release the references on the monitor object.

        This is used for deterministic cleanup. It is safe to call this method
        multiple times. After the first call, the monitor object must not be
        used anymore.
        """
        if self.value:
            udev_monitor_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    def udev_monitor_filter_update(self) -> None:
        """
        Update the installed socket filter.

        Raises:
            OSError: If the filter could not be updated.
        """
        udev_monitor_filter_update(self)

    @property
    def fd(self) -> int:
        """
        Retrieve the socket file descriptor associated with the monitor.
        """
        return udev_monitor_get_fd(self)

    def receive_device(self) -> "UDevDevice":
        """
        Receive data from the udev monitor socket.

        Returns: a new udev device

        Raises:
            OSError: in case of an error

        The monitor socket is by default set to ``NONBLOCK``. A variant of ``poll()``
        on the file descriptor returned by :attr:`fd` should to be used to
        wake up when new devices arrive, or alternatively the file descriptor
        switched into blocking mode.
        """
        return udev_monitor_receive_device(self)

    def filter_add_match_subsystem_devtype(
        self, subsystem: bytes, devtype: bytes
    ) -> None:
        """
        Args:
            subsystem: The subsystem value to match the incoming devices against.
            devtype: The devtype value to match the incoming devices against.

        Raises:
            OSError: If the filter could not be added.

        This filter is efficiently executed inside the kernel, and libudev subscribers
        will usually not be woken up for devices which do not match.

        The filter must be installed before the monitor is switched to listening mode.
        """
        udev_monitor_filter_add_match_subsystem_devtype(self, subsystem, devtype)

    def add_match_tag(self, tag: bytes) -> None:
        """
        Args:
            tag: The tag to match the incoming devices against.

        Raises:
            OSError: If the filter could not be added.

        This filter is efficiently executed inside the kernel, and libudev subscribers
        will usually not be woken up for devices which do not match.

        The filter must be installed before the monitor is switched to listening mode.
        """
        udev_monitor_filter_add_match_tag(self, tag)


class _udev_monitor_new_from_netlink(Protocol):
    def __call__(self, udev: UDevContext, name: bytes) -> UDevMonitor: ...


udev_monitor_new_from_netlink: _udev_monitor_new_from_netlink = ctypes.CFUNCTYPE(
    UDevMonitor, UDevContext, ctypes.c_char_p, use_errno=True
)(("udev_monitor_new_from_netlink", libudev))


def _errcheck_udev_monitor_new_from_netlink(
    result: UDevMonitor,
    func: _udev_monitor_new_from_netlink,
    args: tuple[UDevContext, bytes],
) -> UDevMonitor:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_monitor_new_from_netlink failed")
    return result


udev_monitor_new_from_netlink.errcheck = _errcheck_udev_monitor_new_from_netlink  # type: ignore


class _udev_monitor_filter_update(Protocol):
    def __call__(self, monitor: UDevMonitor) -> None: ...


udev_monitor_filter_update: _udev_monitor_filter_update = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevMonitor
)(("udev_monitor_filter_update", libudev), ((1, "monitor"),))


def _errcheck_udev_monitor_filter_update(
    result: int, func: _udev_monitor_filter_update, args: tuple[UDevMonitor]
) -> None:
    if result < 0:
        raise OSError(-result, "udev_monitor_filter_update failed")
    return None


udev_monitor_filter_update.errcheck = _errcheck_udev_monitor_filter_update  # type: ignore


class _udev_monitor_unref(Protocol):
    def __call__(self, monitor: UDevMonitor) -> None: ...


udev_monitor_unref: _udev_monitor_unref = ctypes.CFUNCTYPE(
    ctypes.c_void_p, UDevMonitor
)(("udev_monitor_unref", libudev))


class _udev_monitor_get_fd(Protocol):
    def __call__(self, monitor: UDevMonitor) -> int: ...


udev_monitor_get_fd: _udev_monitor_get_fd = ctypes.CFUNCTYPE(ctypes.c_int, UDevMonitor)(
    ("udev_monitor_get_fd", libudev), ((1, "monitor"),)
)


class _udev_monitor_receive_device(Protocol):
    def __call__(self, monitor: UDevMonitor) -> UDevDevice: ...


udev_monitor_receive_device: _udev_monitor_receive_device = ctypes.CFUNCTYPE(
    UDevDevice, UDevMonitor, use_errno=True
)(("udev_monitor_receive_device", libudev), ((1, "monitor"),))


def _errcheck_udev_monitor_receive_device(
    result: UDevDevice, func: _udev_monitor_receive_device, args: tuple[UDevMonitor]
) -> UDevDevice:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_monitor_receive_device failed")
    return result


udev_monitor_receive_device.errcheck = _errcheck_udev_monitor_receive_device  # type: ignore


class _udev_monitor_filter_add_match_subsystem_devtype(Protocol):
    def __call__(
        self, monitor: UDevMonitor, subsystem: bytes, devtype: bytes
    ) -> None: ...


udev_monitor_filter_add_match_subsystem_devtype: _udev_monitor_filter_add_match_subsystem_devtype = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevMonitor, ctypes.c_char_p, ctypes.c_char_p
)(
    ("udev_monitor_filter_add_match_subsystem_devtype", libudev),
    ((1, "monitor"), (1, "subsystem"), (1, "devtype")),
)


def _errcheck_udev_monitor_filter_add_match_subsystem_devtype(
    result: int,
    func: _udev_monitor_filter_add_match_subsystem_devtype,
    args: tuple[UDevMonitor, bytes, bytes],
) -> None:
    if result < 0:
        raise OSError(-result, "udev_monitor_filter_add_match_subsystem_devtype failed")
    return None


udev_monitor_filter_add_match_subsystem_devtype.errcheck = (  # type: ignore
    _errcheck_udev_monitor_filter_add_match_subsystem_devtype
)


class _udev_monitor_filter_add_match_tag(Protocol):
    def __call__(self, monitor: UDevMonitor, tag: bytes) -> None: ...


udev_monitor_filter_add_match_tag: _udev_monitor_filter_add_match_tag = (
    ctypes.CFUNCTYPE(ctypes.c_int, UDevMonitor, ctypes.c_char_p)(
        ("udev_monitor_filter_add_match_tag", libudev), ((1, "monitor"), (1, "tag"))
    )
)


def _errcheck_udev_monitor_filter_add_match_tag(
    result: int,
    func: _udev_monitor_filter_add_match_tag,
    args: tuple[UDevMonitor, bytes],
) -> None:
    if result < 0:
        raise OSError(-result, "udev_monitor_filter_add_match_tag failed")
    return None


udev_monitor_filter_add_match_tag.errcheck = (  # type: ignore
    _errcheck_udev_monitor_filter_add_match_tag
)
