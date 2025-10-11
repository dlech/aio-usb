# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from collections.abc import Iterator
from typing import Protocol

from ._context import UDevContext
from ._lib import libudev
from ._list_entry import UDevListEntry


class UDevEnumerate(ctypes.c_void_p):
    """
    Object representing one device lookup/sort context.
    """

    @staticmethod
    def new(context: UDevContext) -> "UDevEnumerate":
        """
        Create an enumeration context to scan /sys.

        Args:
            context: The udev library context to use.

        Returns:
            a new :class:`UDevEnumerate` object.

        Raises:
            OSError: If the enumeration context could not be created.
        """
        return udev_enumerate_new(context)

    def unref(self) -> None:
        """
        Release the references on the enumerate object.

        This is used for deterministic cleanup. It is safe to call this method
        multiple times. After the first call, the enumerate object must not be
        used anymore.
        """
        if self.value:
            udev_enumerate_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    def add_match_subsystem(self, subsystem: bytes) -> None:
        """
        Match only devices belonging to a certain kernel subsystem.

        Args:
            subsystem: filter for a subsystem of the device to include in the list

        Raises:
            OSError: on failure
        """
        udev_enumerate_add_match_subsystem(self, subsystem)

    def add_match_property(self, key: bytes, value: bytes) -> None:
        """
        Match only devices with a certain property.

        Args:
            key: The property key to match.
            value: The value the property must have to match.

        Raises:
            OSError: on failure
        """
        udev_enumerate_add_match_property(self, key, value)

    def add_match_tag(self, tag: bytes) -> None:
        """
        Match only devices with a certain tag.

        Args:
            tag: The tag to match.

        Raises:
            OSError: on failure
        """
        udev_enumerate_add_match_tag(self, tag)

    def add_match_is_initialized(self) -> None:
        """
        Match only devices which udev has set up already.

        Raises:
            OSError: on failure

        This makes sure, that the device node permissions and context are
        properly set and that network devices are fully renamed.

        Usually, devices which are found in the kernel but not already
        handled by udev, have still pending events. Services should subscribe
        to monitor events and wait for these devices to become ready, instead
        of using uninitialized devices.

        For now, this will not affect devices which do not have a device node
        and are not network interfaces.
        """
        udev_enumerate_add_match_is_initialized(self)

    def scan_devices(self) -> None:
        """
        Scan /sys for all devices which match the given filters.

        Raises:
            OSError: on failure

        No matches will return all currently available devices.
        """
        udev_enumerate_scan_devices(self)

    def scan_subsystems(self) -> None:
        """
        Scan /sys for all kernel subsystems, including buses, classes, drivers.

        Raises:
            OSError: on failure
        """
        udev_enumerate_scan_subsystems(self)

    def __iter__(self) -> Iterator[bytes]:
        entry = udev_enumerate_get_list_entry(self)
        while entry:
            yield entry.name
            entry = entry.next()


class _udev_enumerate_unref(Protocol):
    def __call__(self, enumerate: UDevEnumerate) -> None: ...


udev_enumerate_unref: _udev_enumerate_unref = ctypes.CFUNCTYPE(
    ctypes.c_void_p, UDevEnumerate
)(("udev_enumerate_unref", libudev), ((1, "enumerate"),))


class _udev_enumerate_new(Protocol):
    def __call__(self, udev: UDevContext) -> UDevEnumerate: ...


udev_enumerate_new: _udev_enumerate_new = ctypes.CFUNCTYPE(
    UDevEnumerate, UDevContext, use_errno=True
)(("udev_enumerate_new", libudev))


def _errcheck_udev_enumerate_new(
    result: UDevEnumerate, func: _udev_enumerate_new, args: tuple[UDevContext]
) -> UDevEnumerate:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_enumerate_new failed")
    return result


udev_enumerate_new.errcheck = _errcheck_udev_enumerate_new  # type: ignore


class _udev_enumerate_add_match_subsystem(Protocol):
    def __call__(self, enumerate: UDevEnumerate, subsystem: bytes) -> None: ...


udev_enumerate_add_match_subsystem: _udev_enumerate_add_match_subsystem = (
    ctypes.CFUNCTYPE(ctypes.c_int, UDevEnumerate, ctypes.c_char_p)(
        ("udev_enumerate_add_match_subsystem", libudev),
        ((1, "enumerate"), (1, "subsystem")),
    )
)


def _errcheck_udev_enumerate_add_match_subsystem(
    result: int,
    func: _udev_enumerate_add_match_subsystem,
    args: tuple[UDevEnumerate, bytes],
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_add_match_subsystem failed")


udev_enumerate_add_match_subsystem.errcheck = (
    _errcheck_udev_enumerate_add_match_subsystem  # type: ignore
)


class _udev_enumerate_add_match_property(Protocol):
    def __call__(self, enumerate: UDevEnumerate, key: bytes, value: bytes) -> None: ...


udev_enumerate_add_match_property: _udev_enumerate_add_match_property = (
    ctypes.CFUNCTYPE(ctypes.c_int, UDevEnumerate, ctypes.c_char_p, ctypes.c_char_p)(
        ("udev_enumerate_add_match_property", libudev),
        ((1, "enumerate"), (1, "key"), (1, "value")),
    )
)


def _errcheck_udev_enumerate_add_match_property(
    result: int,
    func: _udev_enumerate_add_match_property,
    args: tuple[UDevEnumerate, bytes, bytes],
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_add_match_property failed")


udev_enumerate_add_match_property.errcheck = _errcheck_udev_enumerate_add_match_property  # type: ignore


class _udev_enumerate_add_match_tag(Protocol):
    def __call__(self, enumerate: UDevEnumerate, tag: bytes) -> None: ...


udev_enumerate_add_match_tag: _udev_enumerate_add_match_tag = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevEnumerate, ctypes.c_char_p
)(("udev_enumerate_add_match_tag", libudev), ((1, "enumerate"), (1, "tag")))


def _errcheck_udev_enumerate_add_match_tag(
    result: int,
    func: _udev_enumerate_add_match_tag,
    args: tuple[UDevEnumerate, bytes],
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_add_match_tag failed")


udev_enumerate_add_match_tag.errcheck = _errcheck_udev_enumerate_add_match_tag  # type: ignore


class _udev_enumerate_add_match_is_initialized(Protocol):
    def __call__(self, enumerate: UDevEnumerate) -> None: ...


udev_enumerate_add_match_is_initialized: _udev_enumerate_add_match_is_initialized = (
    ctypes.CFUNCTYPE(ctypes.c_int, UDevEnumerate)(
        ("udev_enumerate_add_match_is_initialized", libudev), ((1, "enumerate"),)
    )
)


def _errcheck_udev_enumerate_add_match_is_initialized(
    result: int,
    func: _udev_enumerate_add_match_is_initialized,
    args: tuple[UDevEnumerate],
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_add_match_is_initialized failed")


udev_enumerate_add_match_is_initialized.errcheck = (
    _errcheck_udev_enumerate_add_match_is_initialized  # type: ignore
)


class _udev_enumerate_scan_devices(Protocol):
    def __call__(self, enumerate: UDevEnumerate) -> None: ...


udev_enumerate_scan_devices: _udev_enumerate_scan_devices = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevEnumerate
)(("udev_enumerate_scan_devices", libudev), ((1, "enumerate"),))


def _errcheck_udev_enumerate_scan_devices(
    result: int, func: _udev_enumerate_scan_devices, args: tuple[UDevEnumerate]
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_scan_devices failed")


udev_enumerate_scan_devices.errcheck = _errcheck_udev_enumerate_scan_devices  # type: ignore


class _udev_enumerate_scan_subsystems(Protocol):
    def __call__(self, enumerate: UDevEnumerate) -> None: ...


udev_enumerate_scan_subsystems: _udev_enumerate_scan_subsystems = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevEnumerate
)(("udev_enumerate_scan_subsystems", libudev), ((1, "enumerate"),))


def _errcheck_udev_enumerate_scan_subsystems(
    result: int, func: _udev_enumerate_scan_subsystems, args: tuple[UDevEnumerate]
) -> None:
    if result != 0:
        raise OSError(-result, "udev_enumerate_scan_subsystems failed")


udev_enumerate_scan_subsystems.errcheck = _errcheck_udev_enumerate_scan_subsystems  # type: ignore


class _udev_enumerate_get_list_entry(Protocol):
    def __call__(self, enumerate: UDevEnumerate) -> UDevListEntry | None: ...


udev_enumerate_get_list_entry: _udev_enumerate_get_list_entry = ctypes.CFUNCTYPE(
    UDevListEntry, UDevEnumerate
)(("udev_enumerate_get_list_entry", libudev), ((1, "enumerate"),))
