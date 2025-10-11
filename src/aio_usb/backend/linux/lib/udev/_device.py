# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from collections.abc import Iterator
from typing import Protocol

from ._context import UDevContext
from ._lib import libudev
from ._list_entry import UDevListEntry


class UDevDevice(ctypes.c_void_p):
    """
    Opaque object representing one kernel sys device.

    Representation of kernel sys devices. Devices are uniquely identified
    by their syspath, every device has exactly one path in the kernel sys
    filesystem. Devices usually belong to a kernel subsystem, and have
    a unique name inside that subsystem.
    """

    @staticmethod
    def new_from_syspath(context: UDevContext, syspath: bytes) -> "UDevDevice":
        """
        Create new udev device.

        Args:
            context: The udev library context to use.
            syspath: The sysfs absolute path of the device.

        Returns:
            A new device object.

        Raises:
            OSError: If the device could not be created.
        """
        return udev_device_new_from_syspath(context, syspath)

    def unref(self) -> None:
        """
        Release the references on the device object.

        This is used for deterministic cleanup. It is safe to call this method
        multiple times. After the first call, the device object must not be
        used anymore.
        """
        if self.value:
            udev_device_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    @property
    def devpath(self) -> bytes:
        """
        Retrieve the kernel devpath value of the udev device.

        The path does not contain the sys mount point, and starts with a ``/``.
        """
        return udev_device_get_devpath(self)

    @property
    def subsystem(self) -> bytes:
        """
        Retrieve the subsystem string of the udev device.

        The string does not contain any ``/``.
        """
        return udev_device_get_subsystem(self)

    @property
    def devtype(self) -> bytes:
        """
        Retrieve the devtype string of the udev device.
        """
        return udev_device_get_devtype(self)

    @property
    def syspath(self) -> bytes:
        """
        Retrieve the sys path of the udev device.

        The path is an absolute path and starts with the sys mount point.
        """
        return udev_device_get_syspath(self)

    @property
    def sysname(self) -> bytes:
        """
        Get the kernel device name in /sys.
        """
        return udev_device_get_sysname(self)

    @property
    def sysnum(self) -> bytes:
        """
        Get the instance number of the device.
        """
        return udev_device_get_sysnum(self)

    @property
    def devnode(self) -> bytes:
        """
        Retrieve the device node file name belonging to the udev device.

        The path is an absolute path, and starts with the device directory.
        """
        return udev_device_get_devnode(self)

    @property
    def properties(self) -> Iterator[tuple[bytes, bytes]]:
        """
        Retrieve key/value device properties of the udev device.
        """
        entry = udev_device_get_properties_list_entry(self)
        while entry:
            yield (entry.name, entry.value_)
            entry = entry.next()

    def get_property_value(self, key: bytes) -> bytes | None:
        """
        Get the value of a given property.

        Args:
            key: The property name to look up.

        Returns:
            The property value, or `None` if the property does not exist.
        """
        return udev_device_get_property_value(self, key)

    def __getitem__(self, key: bytes) -> bytes:
        value = self.get_property_value(key)
        if value is None:
            raise KeyError(key)
        return value

    @property
    def driver(self) -> bytes:
        """
        Get the kernel driver name.
        """
        return udev_device_get_driver(self)

    @property
    def action(self) -> bytes:
        """
        Get the action which triggered the event.

        This is only valid if the device was received through a monitor. Devices read from
        sys do not have an action string. Usual actions are: "add", "remove", "change", "move",
        "online", "offline".
        """
        return udev_device_get_action(self)

    def get_sysattr_value(self, key: bytes) -> bytes | None:
        """
        Get the value of a given sysattr.

        Args:
            key: The sysattr name to look up.

        Returns:
            The sysattr value, or `None` if the sysattr does not exist.

        The retrieved value is cached in the device. Repeated calls will return the same
        value and not open the attribute again.
        """
        return udev_device_get_sysattr_value(self, key)

    @property
    def sysattrs(self) -> Iterator[bytes]:
        """
        Retrieve the list of available sysattrs of the udev device.

        Returns:
            An iterator over the names of all sysattrs of the device.
        """
        entry = udev_device_get_sysattr_list_entry(self)
        while entry:
            # This doesn't read values, so only yield names.
            yield entry.name
            entry = entry.next()

    @property
    def is_initialized(self) -> bool:
        """
        Check if udev has already handled the device and has set up
        device node permissions and context, or has renamed a network
        device.

        This is only implemented for devices with a device node
        or network interfaces. All other devices return ``True`` here.
        """
        return bool(udev_device_get_is_initialized(self))

    @property
    def tags(self) -> Iterator[bytes]:
        """
        Retrieve the list of tags of the udev device.

        Returns:
            An iterator over the names of all tags of the device.
        """
        entry = udev_device_get_tags_list_entry(self)
        while entry:
            yield entry.name
            entry = entry.next()

    def has_tag(self, tag: bytes) -> bool:
        """
        Check if a given device has a certain tag associated.

        Args:
            tag: The tag to look for.

        Returns:
            `True` if the device has the tag, `False` otherwise.
        """
        return bool(udev_device_has_tag(self, tag))


class _udev_device_unref(Protocol):
    def __call__(self, device: UDevDevice) -> None: ...


udev_device_unref: _udev_device_unref = ctypes.CFUNCTYPE(ctypes.c_void_p, UDevDevice)(
    ("udev_device_unref", libudev), ((1, "device"),)
)


class _udev_device_new_from_syspath(Protocol):
    def __call__(self, udev: UDevContext, syspath: bytes) -> UDevDevice: ...


udev_device_new_from_syspath: _udev_device_new_from_syspath = ctypes.CFUNCTYPE(
    UDevDevice, UDevContext, ctypes.c_char_p, use_errno=True
)(("udev_device_new_from_syspath", libudev))


def _errcheck_udev_device_new_from_syspath(
    result: UDevDevice,
    func: _udev_device_new_from_syspath,
    args: tuple[UDevContext, bytes],
) -> UDevDevice:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_device_new_from_syspath failed")
    return result


udev_device_new_from_syspath.errcheck = _errcheck_udev_device_new_from_syspath  # type: ignore


class _udev_device_get_devpath(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_devpath: _udev_device_get_devpath = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_devpath", libudev), ((1, "device"),))


class _udev_device_get_subsystem(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_subsystem: _udev_device_get_subsystem = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_subsystem", libudev), ((1, "device"),))


class _udev_device_get_devtype(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_devtype: _udev_device_get_devtype = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_devtype", libudev), ((1, "device"),))


class _udev_device_get_syspath(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_syspath: _udev_device_get_syspath = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_syspath", libudev), ((1, "device"),))


class _udev_device_get_sysname(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_sysname: _udev_device_get_sysname = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_sysname", libudev), ((1, "device"),))


class _udev_device_get_sysnum(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_sysnum: _udev_device_get_sysnum = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_sysnum", libudev), ((1, "device"),))


class _udev_device_get_devnode(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_devnode: _udev_device_get_devnode = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_devnode", libudev), ((1, "device"),))


class _udev_device_get_properties_list_entry(Protocol):
    def __call__(self, device: UDevDevice) -> UDevListEntry | None: ...


udev_device_get_properties_list_entry: _udev_device_get_properties_list_entry = (
    ctypes.CFUNCTYPE(UDevListEntry, UDevDevice)(
        ("udev_device_get_properties_list_entry", libudev), ((1, "device"),)
    )
)


class _udev_device_get_property_value(Protocol):
    def __call__(self, device: UDevDevice, key: bytes) -> bytes | None: ...


udev_device_get_property_value: _udev_device_get_property_value = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice, ctypes.c_char_p
)(("udev_device_get_property_value", libudev), ((1, "device"), (1, "key")))


class _udev_device_get_driver(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_driver: _udev_device_get_driver = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_driver", libudev), ((1, "device"),))


class _udev_device_get_action(Protocol):
    def __call__(self, device: UDevDevice) -> bytes: ...


udev_device_get_action: _udev_device_get_action = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice
)(("udev_device_get_action", libudev), ((1, "device"),))


class _udev_device_get_sysattr_value(Protocol):
    def __call__(self, device: UDevDevice, key: bytes) -> bytes | None: ...


udev_device_get_sysattr_value: _udev_device_get_sysattr_value = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevDevice, ctypes.c_char_p
)(("udev_device_get_sysattr_value", libudev), ((1, "device"), (1, "key")))


class _udev_device_get_sysattr_list_entry(Protocol):
    def __call__(self, device: UDevDevice) -> UDevListEntry | None: ...


udev_device_get_sysattr_list_entry: _udev_device_get_sysattr_list_entry = (
    ctypes.CFUNCTYPE(UDevListEntry, UDevDevice)(
        ("udev_device_get_sysattr_list_entry", libudev), ((1, "device"),)
    )
)


class _udev_device_get_is_initialized(Protocol):
    def __call__(self, device: UDevDevice) -> int: ...


udev_device_get_is_initialized: _udev_device_get_is_initialized = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevDevice
)(("udev_device_get_is_initialized", libudev), ((1, "device"),))


class _udev_device_get_tags_list_entry(Protocol):
    def __call__(self, device: UDevDevice) -> UDevListEntry | None: ...


udev_device_get_tags_list_entry: _udev_device_get_tags_list_entry = ctypes.CFUNCTYPE(
    UDevListEntry, UDevDevice
)(("udev_device_get_tags_list_entry", libudev), ((1, "device"),))


class _udev_device_has_tag(Protocol):
    def __call__(self, device: UDevDevice, tag: bytes) -> int: ...


udev_device_has_tag: _udev_device_has_tag = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevDevice, ctypes.c_char_p
)(("udev_device_has_tag", libudev), ((1, "device"), (1, "tag")))
