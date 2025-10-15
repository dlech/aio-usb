# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>


import ctypes
from typing import Any, Protocol, TypeAlias

from rubicon.objc import (
    NSDictionary,
    py_from_ns,  # pyright: ignore[reportUnknownVariableType]
)

from ..core_foundation import CFAllocatorRef, CFMutableDictionaryRef
from ..runtime import mach_error_string
from ._driver_kit import IOOptionBits, kern_return_t
from ._io_kit_keys import kIOServicePlane
from ._iterator import IOIterator, io_iterator_t
from ._kernel import io_name_t
from ._object import IOObject
from ._runtime import IOKitLib


class IORegistryEntry(IOObject):
    """
    https://developer.apple.com/documentation/iokit/io_registry_entry_t?language=objc
    """

    @staticmethod
    def from_handle(handle: int) -> "IORegistryEntry":
        """
        Create an IORegistryEntry object from a raw handle.
        """
        entry = IORegistryEntry(handle)
        entry.retain()
        return entry

    @property
    def name(self) -> str:
        """
        Gets the name of the registry entry.
        """
        name = IORegistryEntryGetName(self)
        return name.decode("utf-8")

    @property
    def id(self) -> int:
        """
        Gets the registry entry ID.
        """
        return IORegistryEntryGetRegistryEntryID(self)

    @classmethod
    def id_matching(cls, entry_id: int) -> CFMutableDictionaryRef:
        """
        Create a matching dictionary that specifies an IOService match based on
        a registry entry ID.

        Args:
            entry_id: The registry entry ID to be found.

        Returns:
            The matching dictionary created. The dictionary is commonly passed
            to :meth:`IOService.get_matching_services` or :meth:`IOService.add_notification`.

        This function creates a matching dictionary that will match a registered,
        active IOService found with the given registry entry ID. The entry ID
        for a registry entry is returned by :attr:`id`.
        """
        return IORegistryEntryIDMatching(entry_id)

    @property
    def properties(self) -> dict[str, Any]:
        """
        Gets the properties of the registry.
        """
        return py_from_ns(
            NSDictionary(IORegistryEntryCreateCFProperties(self, None, 0))
        )

    def get_child_iterator(self, plane: bytes = kIOServicePlane) -> IOIterator:
        return IORegistryEntryGetChildIterator(self, plane)


# Alias to match the C type name for use in function signatures to match
# the Apple documentation.
io_registry_entry_t: TypeAlias = IORegistryEntry


class _IORegistryEntryGetName(Protocol):
    def __call__(self, entry: IORegistryEntry) -> bytes:
        """
        Returns a C-string name assigned to a registry entry.

        Args:
            entry: The registry entry handle whose name to look up.

        Returns:
            The name of the entry.

        Raises:
            OSError: A kern_return_t error code.

        Registry entries can be named in a particular plane, or globally. This
        function returns the entry's global name. The global name defaults to
        the entry's meta class name if it has not been named.

        https://developer.apple.com/documentation/iokit/1514323-ioregistryentrygetname?language=objc
        """
        ...


IORegistryEntryGetName: _IORegistryEntryGetName = ctypes.CFUNCTYPE(
    kern_return_t, io_registry_entry_t, io_name_t
)(("IORegistryEntryGetName", IOKitLib), ((1, "entry"), (2, "name")))


def _errcheck_IORegistryEntryGetName(
    result: kern_return_t,
    func: _IORegistryEntryGetName,
    args: tuple[io_registry_entry_t, ctypes.Array[ctypes.c_char]],
) -> bytes:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[1].raw.split(b"\0", 1)[0]


IORegistryEntryGetName.errcheck = _errcheck_IORegistryEntryGetName  # type: ignore


class _IORegistryEntryGetRegistryEntryID(Protocol):
    def __call__(self, entry: IORegistryEntry) -> int:
        """
        Returns an ID for the registry entry that is global to all tasks.

        Args:
            entry: The registry entry handle whose ID to look up.

        Returns:
            The resulting ID.

        Raises:
            OSError: A kern_return_t error code.

        The entry ID returned by IORegistryEntryGetRegistryEntryID can be used
        to identify a registry entry across all tasks. A registry entry may be
        looked up by its entryID by creating a matching dictionary with
        :meth:`id_matching()` to be used with the IOKit matching functions. The
        ID is valid only until the machine reboots.

        https://developer.apple.com/documentation/iokit/1514719-ioregistryentrygetregistryentryi?language=objc
        """
        ...


IORegistryEntryGetRegistryEntryID: _IORegistryEntryGetRegistryEntryID = (
    ctypes.CFUNCTYPE(
        kern_return_t, io_registry_entry_t, ctypes.POINTER(ctypes.c_uint64)
    )(("IORegistryEntryGetRegistryEntryID", IOKitLib), ((1, "entry"), (2, "entryID")))
)


def _errcheck_IORegistryEntryGetRegistryEntryID(
    result: kern_return_t,
    func: _IORegistryEntryGetRegistryEntryID,
    args: tuple[io_registry_entry_t, ctypes.c_uint64],
) -> int:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[1].value


IORegistryEntryGetRegistryEntryID.errcheck = (  # type: ignore
    _errcheck_IORegistryEntryGetRegistryEntryID
)


class _IORegistryEntryIDMatching(Protocol):
    def __call__(self, entryID: int) -> CFMutableDictionaryRef:
        """
        Create a matching dictionary that specifies an IOService match based on
        a registry entry ID.

        Args:
            entryID: The registry entry ID to be found.

        Returns:
            The matching dictionary created, is returned on success, or zero on
            failure. The dictionary is commonly passed to IOServiceGetMatchingServices
            or IOServiceAddNotification which will consume a reference, otherwise
            it should be released with CFRelease by the caller.

        This function creates a matching dictionary that will match a registered,
        active IOService found with the given registry entry ID. The entry ID
        for a registry entry is returned by IORegistryEntryGetRegistryEntryID().

        https://developer.apple.com/documentation/iokit/1514880-ioregistryentryidmatching?language=objc
        """
        ...


IORegistryEntryIDMatching: _IORegistryEntryIDMatching = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_uint64
)(("IORegistryEntryIDMatching", IOKitLib), ((1, "entryID"),))


def _errcheck_IORegistryEntryIDMatching(
    result: int,
    func: _IORegistryEntryIDMatching,
    args: tuple[int],
) -> CFMutableDictionaryRef:
    # REVISIT: Does this set errno on failure?
    if not result:
        raise RuntimeError("Failed to create matching dictionary")

    return CFMutableDictionaryRef(result)


IORegistryEntryIDMatching.errcheck = _errcheck_IORegistryEntryIDMatching  # type: ignore


class _IORegistryEntryCreateCFProperties(Protocol):
    def __call__(
        self,
        entry: IORegistryEntry,
        allocator: None,
        options: int,
    ) -> CFMutableDictionaryRef:
        """
        Create a CF dictionary representation of a registry entry's property table.

        Args:
            entry:
                The registry entry handle whose property table to copy.

            allocator:
                    The CF allocator to use when creating the CF containers.

            options:
                No options are currently defined.

        Returns:
            A CFDictionary is created and returned the caller on success. The
            caller should release with CFRelease.

        Raises:
            OSError: A kern_return_t error code.

        This function creates an instantaneous snapshot of a registry entry's
        property table, creating a CFDictionary analogue in the caller's task.
        Not every object available in the kernel is represented as a CF container;
        currently OSDictionary, OSArray, OSSet, OSSymbol, OSString, OSData,
        OSNumber, OSBoolean are created as their CF counterparts.

        https://developer.apple.com/documentation/iokit/1514310-ioregistryentrycreatecfpropertie?language=objc
        """
        ...


IORegistryEntryCreateCFProperties: _IORegistryEntryCreateCFProperties = (
    ctypes.CFUNCTYPE(
        kern_return_t,
        io_registry_entry_t,
        ctypes.POINTER(CFMutableDictionaryRef),
        CFAllocatorRef,
        IOOptionBits,
    )(
        ("IORegistryEntryCreateCFProperties", IOKitLib),
        ((1, "entry"), (2, "properties"), (1, "allocator"), (1, "options")),
    )
)


def _errcheck_IORegistryEntryCreateCFProperties(
    result: kern_return_t,
    func: _IORegistryEntryCreateCFProperties,
    args: tuple[io_registry_entry_t, CFMutableDictionaryRef, CFAllocatorRef, int],
) -> CFMutableDictionaryRef:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[1]


IORegistryEntryCreateCFProperties.errcheck = (  # type: ignore
    _errcheck_IORegistryEntryCreateCFProperties
)


class _IORegistryEntryGetChildIterator(Protocol):
    def __call__(
        self,
        entry: IORegistryEntry,
        plane: bytes,
    ) -> IOIterator:
        """
        Returns an iterator over a registry entry’s child entries in a plane.

        Args:
            entry:
                The registry entry whose children to iterate over.

            plane:
                The name of an existing registry plane. Plane names are defined
                in IOKitKeys.h, for example, kIOServicePlane.

            iterator:
                The created iterator over the children of the entry.

        Raises:
            OSError: On failure.

        This method creates an iterator which will return each of a registry entry's child entries in a specified plane.

        https://developer.apple.com/documentation/iokit/1514703-ioregistryentrygetchilditerator?language=objc
        """
        ...


IORegistryEntryGetChildIterator: _IORegistryEntryGetChildIterator = ctypes.CFUNCTYPE(
    kern_return_t,
    io_registry_entry_t,
    ctypes.c_char_p,
    ctypes.POINTER(io_iterator_t),
)(
    ("IORegistryEntryGetChildIterator", IOKitLib),
    ((1, "entry"), (1, "plane"), (2, "iterator")),
)


def _errcheck_IORegistryEntryGetChildIterator(
    result: kern_return_t,
    func: _IORegistryEntryGetChildIterator,
    args: tuple[io_registry_entry_t, bytes, io_iterator_t],
) -> IOIterator:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[2]


IORegistryEntryGetChildIterator.errcheck = (  # type: ignore
    _errcheck_IORegistryEntryGetChildIterator
)
