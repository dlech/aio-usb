import ctypes
from typing import Protocol

from ._context import libudev


class UDevListEntry(ctypes.c_void_p):
    @property
    def name(self) -> bytes:
        return udev_list_entry_get_name(self)

    @property
    def value_(self) -> bytes:
        return udev_list_entry_get_value(self)

    def next(self) -> "UDevListEntry | None":
        return udev_list_entry_get_next(self)


class _udev_list_entry_get_next(Protocol):
    def __call__(self, entry: UDevListEntry) -> "UDevListEntry | None": ...


udev_list_entry_get_next: _udev_list_entry_get_next = ctypes.CFUNCTYPE(
    UDevListEntry, UDevListEntry
)(("udev_list_entry_get_next", libudev), ((1, "entry"),))


class _udev_list_entry_get_name(Protocol):
    def __call__(self, entry: UDevListEntry) -> bytes: ...


udev_list_entry_get_name: _udev_list_entry_get_name = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevListEntry
)(("udev_list_entry_get_name", libudev), ((1, "entry"),))


class _udev_list_entry_get_value(Protocol):
    def __call__(self, entry: UDevListEntry) -> bytes: ...


udev_list_entry_get_value: _udev_list_entry_get_value = ctypes.CFUNCTYPE(
    ctypes.c_char_p, UDevListEntry
)(("udev_list_entry_get_value", libudev), ((1, "entry"),))
