import ctypes
from collections.abc import Iterator
from typing import Protocol

from ._context import UDev, libudev, udev
from ._list_entry import UDevListEntry


class UDevEnumerate(ctypes.c_void_p):
    def unref(self) -> None:
        if self.value:
            udev_enumerate_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    @classmethod
    def new(cls) -> "UDevEnumerate":
        return udev_enumerate_new(udev)

    def add_match_subsystem(self, subsystem: bytes) -> None:
        udev_enumerate_add_match_subsystem(self, subsystem)

    def add_match_property(self, key: bytes, value: bytes) -> None:
        udev_enumerate_add_match_property(self, key, value)

    def add_match_tag(self, tag: bytes) -> None:
        udev_enumerate_add_match_tag(self, tag)

    def add_match_is_initialized(self) -> None:
        udev_enumerate_add_match_is_initialized(self)

    def scan_devices(self) -> None:
        udev_enumerate_scan_devices(self)

    def scan_subsystems(self) -> None:
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
    def __call__(self, udev: UDev) -> UDevEnumerate: ...


udev_enumerate_new: _udev_enumerate_new = ctypes.CFUNCTYPE(
    UDevEnumerate, UDev, use_errno=True
)(("udev_enumerate_new", libudev))


def _errcheck_udev_enumerate_new(
    result: UDevEnumerate, func: _udev_enumerate_new, args: tuple[UDev]
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
