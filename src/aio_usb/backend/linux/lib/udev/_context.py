import ctypes
from typing import Protocol

libudev = ctypes.CDLL("libudev.so.1")


class UDev(ctypes.c_void_p):
    def __del__(self) -> None:
        if self.value:
            udev_unref(self)
            self.value = 0


class _udev_new(Protocol):
    def __call__(self) -> UDev: ...


udev_new: _udev_new = ctypes.CFUNCTYPE(UDev, use_errno=True)(("udev_new", libudev))


def _errcheck_udev_new(result: UDev, func: _udev_new, args: None) -> UDev:
    if not result.value:
        errno = ctypes.get_errno()
        raise OSError(errno, "udev_new failed")
    return result


udev_new.errcheck = _errcheck_udev_new  # type: ignore


class _udev_unref(Protocol):
    def __call__(self, udev: UDev) -> None: ...


udev_unref: _udev_unref = ctypes.CFUNCTYPE(ctypes.c_void_p, UDev)(
    ("udev_unref", libudev), ((1, "udev"),)
)


try:
    udev = udev_new()
except OSError as e:
    raise ImportError("Failed to initialize udev") from e
