import ctypes
from collections.abc import Iterator
from typing import Protocol

from ._context import UDev, libudev, udev
from ._list_entry import UDevListEntry


class UDevDevice(ctypes.c_void_p):
    def unref(self) -> None:
        if self.value:
            udev_device_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    @classmethod
    def new_from_syspath(cls, syspath: bytes) -> "UDevDevice":
        return udev_device_new_from_syspath(udev, syspath)

    @property
    def devpath(self) -> bytes:
        return udev_device_get_devpath(self)

    @property
    def subsystem(self) -> bytes:
        return udev_device_get_subsystem(self)

    @property
    def devtype(self) -> bytes:
        return udev_device_get_devtype(self)

    @property
    def syspath(self) -> bytes:
        return udev_device_get_syspath(self)

    @property
    def sysname(self) -> bytes:
        return udev_device_get_sysname(self)

    @property
    def sysnum(self) -> bytes:
        return udev_device_get_sysnum(self)

    @property
    def devnode(self) -> bytes:
        return udev_device_get_devnode(self)

    @property
    def properties(self) -> Iterator[tuple[bytes, bytes]]:
        entry = udev_device_get_properties_list_entry(self)
        while entry:
            yield (entry.name, entry.value_)
            entry = entry.next()

    def get_property_value(self, key: bytes) -> bytes | None:
        return udev_device_get_property_value(self, key)

    def __getitem__(self, key: bytes) -> bytes:
        value = self.get_property_value(key)
        if value is None:
            raise KeyError(key)
        return value

    @property
    def driver(self) -> bytes:
        return udev_device_get_driver(self)

    @property
    def action(self) -> bytes:
        return udev_device_get_action(self)

    def get_sysattr_value(self, key: bytes) -> bytes | None:
        return udev_device_get_sysattr_value(self, key)

    @property
    def sysattrs(self) -> Iterator[bytes]:
        entry = udev_device_get_sysattr_list_entry(self)
        while entry:
            # This doesn't read values, so only yield names.
            yield entry.name
            entry = entry.next()


class _udev_device_unref(Protocol):
    def __call__(self, device: UDevDevice) -> None: ...


udev_device_unref: _udev_device_unref = ctypes.CFUNCTYPE(ctypes.c_void_p, UDevDevice)(
    ("udev_device_unref", libudev), ((1, "device"),)
)


class _udev_device_new_from_syspath(Protocol):
    def __call__(self, udev: UDev, syspath: bytes) -> UDevDevice: ...


udev_device_new_from_syspath: _udev_device_new_from_syspath = ctypes.CFUNCTYPE(
    UDevDevice, UDev, ctypes.c_char_p, use_errno=True
)(("udev_device_new_from_syspath", libudev))


def _errcheck_udev_device_new_from_syspath(
    result: UDevDevice, func: _udev_device_new_from_syspath, args: tuple[UDev, bytes]
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
