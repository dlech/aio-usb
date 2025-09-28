import ctypes
from typing import Literal, Protocol

from ._context import UDev, libudev, udev
from ._device import UDevDevice


class UDevMonitor(ctypes.c_void_p):
    @classmethod
    def from_netlink(cls, name: Literal[b"udev", b"kernel"] = b"udev") -> "UDevMonitor":
        return udev_monitor_new_from_netlink(udev, name)

    def unref(self) -> None:
        if self.value:
            udev_monitor_unref(self)
            self.value = 0

    def __del__(self) -> None:
        self.unref()

    def enable_receiving(self) -> None:
        udev_monitor_enable_receiving(self)

    @property
    def fd(self) -> int:
        return udev_monitor_get_fd(self)

    def receive_device(self) -> "UDevDevice":
        return udev_monitor_receive_device(self)

    def filter_add_match_subsystem_devtype(
        self, subsystem: bytes, devtype: bytes
    ) -> None:
        udev_monitor_filter_add_match_subsystem_devtype(self, subsystem, devtype)

    def add_match_tag(self, tag: bytes) -> None:
        udev_monitor_filter_add_match_tag(self, tag)


class _udev_monitor_new_from_netlink(Protocol):
    def __call__(self, udev: UDev, name: bytes) -> UDevMonitor: ...


udev_monitor_new_from_netlink: _udev_monitor_new_from_netlink = ctypes.CFUNCTYPE(
    UDevMonitor, UDev, ctypes.c_char_p, use_errno=True
)(("udev_monitor_new_from_netlink", libudev))


def _errcheck_udev_monitor_new_from_netlink(
    result: UDevMonitor, func: _udev_monitor_new_from_netlink, args: tuple[UDev, bytes]
) -> UDevMonitor:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_monitor_new_from_netlink failed")
    return result


udev_monitor_new_from_netlink.errcheck = _errcheck_udev_monitor_new_from_netlink  # type: ignore


class _udev_monitor_unref(Protocol):
    def __call__(self, monitor: UDevMonitor) -> None: ...


udev_monitor_unref: _udev_monitor_unref = ctypes.CFUNCTYPE(
    ctypes.c_void_p, UDevMonitor
)(("udev_monitor_unref", libudev))


class _udev_monitor_enable_receiving(Protocol):
    def __call__(self, monitor: UDevMonitor) -> None: ...


udev_monitor_enable_receiving: _udev_monitor_enable_receiving = ctypes.CFUNCTYPE(
    ctypes.c_int, UDevMonitor
)(("udev_monitor_enable_receiving", libudev), ((1, "monitor"),))


def _errcheck_udev_monitor_enable_receiving(
    result: int, func: _udev_monitor_enable_receiving, args: tuple[UDevMonitor]
) -> None:
    if result < 0:
        raise OSError(-result, "udev_monitor_enable_receiving failed")
    return None


udev_monitor_enable_receiving.errcheck = _errcheck_udev_monitor_enable_receiving  # type: ignore


class _udev_monitor_get_fd(Protocol):
    def __call__(self, monitor: UDevMonitor) -> int: ...


udev_monitor_get_fd: _udev_monitor_get_fd = ctypes.CFUNCTYPE(ctypes.c_int, UDevMonitor)(
    ("udev_monitor_get_fd", libudev), ((1, "monitor"),)
)


class _udev_monitor_receive_device(Protocol):
    def __call__(self, monitor: UDevMonitor) -> UDevDevice: ...


udev_monitor_receive_device: _udev_monitor_receive_device = ctypes.CFUNCTYPE(
    UDevDevice, UDevMonitor
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
