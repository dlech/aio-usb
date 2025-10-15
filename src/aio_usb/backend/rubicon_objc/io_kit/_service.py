# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from __future__ import annotations

import ctypes
import weakref
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias

from ..core_foundation import CFDictionaryRef
from ..io_kit._kernel import boolean_t
from ..runtime import mach_error_string
from ._driver_kit import kern_return_t, mach_port_t
from ._iterator import IOIterator, io_iterator_t
from ._notification_port import IONotificationPortRef
from ._object import IOObject
from ._runtime import IOKitLib

kIOPublishNotification = b"IOServicePublish"
kIOFirstPublishNotification = b"IOServiceFirstPublish"
kIOMatchedNotification = b"IOServiceMatched"
kIOFirstMatchNotification = b"IOServiceFirstMatch"
kIOTerminatedNotification = b"IOServiceTerminate"

_IOServiceMatchingCallback = ctypes.CFUNCTYPE(None, ctypes.c_void_p, io_iterator_t)

if TYPE_CHECKING:
    c_IOServiceMatchingCallback: TypeAlias = ctypes._CFunctionType  # pyright: ignore[reportPrivateUsage]


class IOServiceMatchingCallback(Protocol):
    def __call__(self, iterator: IOIterator, /) -> None:
        """
        Callback function to be notified of IOService publication.

        Args:
            iterator:
                The notification iterator which now has new objects.

        https://developer.apple.com/documentation/iokit/ioservicematchingcallback?language=objc
        """


class IOService(IOObject):
    """
    https://developer.apple.com/documentation/iokit/io_service_t?language=objc
    """

    @staticmethod
    def from_handle(handle: int) -> "IOService":
        """
        Create an IOService object from a raw handle.
        """
        service = IOService(handle)
        service.retain()
        return service

    @staticmethod
    def add_matching_notification(
        notify_port: IONotificationPortRef,
        notification_type: bytes,
        matching: CFDictionaryRef,
        callback: IOServiceMatchingCallback,
    ) -> IOIterator:
        # Wrap the callback so that caller doesn't need to know about retaining
        # the iterator.
        def wrapped_callback(ref_con: ctypes.c_void_p, iterator: IOIterator, /) -> None:
            # We received a borrowed reference to the iterator, so retain it
            # before passing it to the caller's callback.
            iterator.retain()
            callback(iterator)

        c_callback = _IOServiceMatchingCallback(wrapped_callback)

        iterator = IOServiceAddMatchingNotification(
            notify_port,
            notification_type,
            # IOServiceAddMatchingNotification steals reference from matching.
            matching.retain(),
            c_callback,
            # Since Python has closures, we don't need to pass a refCon.
            None,
        )

        # Ensure the C callback is not garbage collected while the iterator
        # exists. When the iterator is released, the notification is removed and
        # the callback will never be called again.
        weakref.finalize(iterator, list[Any].clear, [c_callback])

        return iterator

    @staticmethod
    def get_matching_service(
        matching: CFDictionaryRef, port: int = 0
    ) -> "IOService | None":
        """
        Looks up a registered IOService object that matches a matching dictionary.

        Args:
            matching:
                A CF dictionary containing matching information. IOKitLib can
                construct matching dictionaries for common criteria with helper
                functions such as :meth:`matching()`, :meth:`name_matching()`.
            port:
                The primary port obtained from IOMasterPort.

        Returns:
            An IOService object if found, otherwise None.
        """
        # IOServiceGetMatchingService steals reference from matching
        return IOServiceGetMatchingService(port, matching.retain())

    @staticmethod
    def get_matching_services(
        matching: CFDictionaryRef, port: int = 0
    ) -> Iterable["IOService"]:
        """
        Looks up registered IOService objects that match a matching dictionary.

        Args:
            matching:
                A CF dictionary containing matching information. IOKitLib can
                construct matching dictionaries for common criteria with helper
                functions such as :meth:`matching()`, :meth:`name_matching()`.

        Returns:
            An iterator of IOService objects.
        """
        # IOServiceGetMatchingServices steals reference from matching
        iterator = IOServiceGetMatchingServices(port, matching.retain())

        if iterator is None:
            return iter(())

        return (obj.as_(IOService) for obj in iterator)

    def match_property_table(self, matching: CFDictionaryRef) -> bool:
        """
        Match an IOService objects with matching dictionary.

        Args:
            matching:
                A CF dictionary containing matching information.

        Returns:
            ``True`` if the service matches, ``False`` otherwise.

        Raises:
            OSError: On failure.
        """
        return IOServiceMatchPropertyTable(self, matching)


# Alias to match the C type name for use in function signatures to match
# the Apple documentation.
io_service_t: TypeAlias = IOService


class _IOServiceAddMatchingNotification(Protocol):
    def __call__(
        self,
        notifyPort: IONotificationPortRef,
        notificationType: bytes,
        matching: CFDictionaryRef,
        callback: c_IOServiceMatchingCallback,
        refCon: ctypes.c_void_p | None,
    ) -> IOIterator:
        """
        Look up registered IOService objects that match a matching dictionary,
        and install a notification request of new IOServices that match.

        Args:
            notifyPort:
                A IONotificationPortRef object that controls how messages will
                be sent when the armed notification is fired. When the
                notification is delivered, the io_iterator_t representing the
                notification should be iterated through to pick up all
                outstanding objects. When the iteration is finished the
                notification is rearmed. See IONotificationPortCreate.

            notificationType:
                A notification type from IOKitKeys.h
                - kIOPublishNotification Delivered when an IOService is
                  registered.
                - kIOFirstPublishNotification Delivered when an IOService is
                  registered, but only once per IOService instance. Some
                  IOService's may be reregistered when their state is changed.
                - kIOMatchedNotification Delivered when an IOService has had
                  all matching drivers in the kernel probed and started.
                - kIOFirstMatchNotification Delivered when an IOService has had
                  all matching drivers in the kernel probed and started, but
                  only once per IOService instance. Some IOService's may be
                  reregistered when their state is changed.
                - kIOTerminatedNotification Delivered after an IOService has
                  been terminated.

            matching:
                A CF dictionary containing matching information, of which one
                reference is always consumed by this function (Note prior to
                the Tiger release there was a small chance that the dictionary
                might not be released if there was an error attempting to
                serialize the dictionary). IOKitLib can construct matching
                dictionaries for common criteria with helper functions such as
                IOServiceMatching, IOServiceNameMatching, IOBSDNameMatching.

            callback:
                A callback function called when the notification fires.

            refCon:
                A reference value passed to the callback function when it is called.
                This parameter may be NULL.

        Returns:
            An iterator handle is returned on success, and should be released
            by the caller when the notification is to be destroyed. The
            notification is armed when the iterator is emptied by calls to
            IOIteratorNext - when no more objects are returned, the notification
            is armed. Note the notification is not armed when first created.

        Raises:
            OSError: A kern_return_t error code.

        This is the preferred method of finding IOService objects that may
        arrive at any time. The type of notification specifies the state change
        the caller is interested in, on IOService's that match the match
        dictionary. Notification types are identified by name, and are defined
        in IOKitKeys.h. The matching information used in the matching dictionary
        may vary depending on the class of service being looked up.

        https://developer.apple.com/documentation/iokit/1514362-ioserviceaddmatchingnotification?language=objc
        """
        ...


IOServiceAddMatchingNotification: _IOServiceAddMatchingNotification = ctypes.CFUNCTYPE(
    kern_return_t,
    IONotificationPortRef,
    ctypes.c_char_p,
    CFDictionaryRef,
    _IOServiceMatchingCallback,
    ctypes.c_void_p,
    ctypes.POINTER(io_iterator_t),
)(
    ("IOServiceAddMatchingNotification", IOKitLib),
    (
        (1, "notifyPort"),
        (1, "notificationType"),
        (1, "matching"),
        (1, "callback"),
        (1, "refCon"),
        (2, "notification"),
    ),
)


def _errcheck_IOServiceAddMatchingNotification(
    result: kern_return_t,
    func: _IOServiceAddMatchingNotification,
    args: tuple[
        IONotificationPortRef,
        bytes,
        CFDictionaryRef,
        c_IOServiceMatchingCallback,
        ctypes.c_void_p,
        io_iterator_t,
    ],
) -> io_iterator_t:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[5]


IOServiceAddMatchingNotification.errcheck = _errcheck_IOServiceAddMatchingNotification  # type: ignore


class _IOServiceGetMatchingService(Protocol):
    def __call__(self, mainPort: int, matching: CFDictionaryRef) -> IOService | None:
        """
        Look up a registered IOService object that matches a matching dictionary.

        Args:
            mainPort:
                The primary port obtained from IOMasterPort. Pass
                kIOMasterPortDefault to look up the default primary port.

            matching:
                A CF dictionary containing matching information. IOKitLib can
                construct matching dictionaries for common criteria with helper
                functions such as IOServiceMatching, IOServiceNameMatching,
                IOBSDNameMatching.

        Returns:
            The first service matched is returned on success. The service must
            be released by the caller.

        This is the preferred method of finding IOService objects currently
        registered by IOKit (that is, objects that have had their
        registerService() methods invoked). To find IOService objects that
        aren't yet registered, use an iterator as created by
        IORegistryEntryCreateIterator(). IOServiceAddMatchingNotification can
        also supply this information and install a notification of new
        IOServices. The matching information used in the matching dictionary
        may vary depending on the class of service being looked up.

        https://developer.apple.com/documentation/iokit/1514535-ioservicegetmatchingservice?language=objc
        """
        ...


IOServiceGetMatchingService: _IOServiceGetMatchingService = ctypes.CFUNCTYPE(
    io_service_t, mach_port_t, CFDictionaryRef
)(("IOServiceGetMatchingService", IOKitLib), ((1, "mainPort"), (1, "matching")))


def _errcheck_IOServiceGetMatchingService(
    result: io_service_t,
    func: _IOServiceGetMatchingService,
    args: tuple[mach_port_t, CFDictionaryRef],
) -> IOService | None:
    if result.value == 0:
        return None

    return result


IOServiceGetMatchingService.errcheck = _errcheck_IOServiceGetMatchingService  # type: ignore


class _IOServiceGetMatchingServices(Protocol):
    def __call__(self, mainPort: int, matching: CFDictionaryRef) -> IOIterator | None:
        """
        Look up registered IOService objects that match a matching dictionary.

        Args:
            mainPort:
                The primary port obtained from IOMasterPort. Pass
                kIOMasterPortDefault to look up the default primary port.

            matching:
                A CF dictionary containing matching information, of which one
                reference is always consumed by this function (Note prior to the
                Tiger release there was a small chance that the dictionary might
                not be released if there was an error attempting to serialize
                the dictionary). IOKitLib can construct matching dictionaries
                for common criteria with helper functions such as
                IOServiceMatching, IOServiceNameMatching, IOBSDNameMatching.

        Returns:
            An iterator handle is returned on success, and should be released by
            the caller when the iteration is finished.

        Raises:
            OSError: A kern_return_t error code.

        This is the preferred method of finding IOService objects currently
        registered by IOKit (that is, objects that have had their
        registerService() methods invoked). To find IOService objects that
        aren't yet registered, use an iterator as created by
        IORegistryEntryCreateIterator(). IOServiceAddMatchingNotification can
        also supply this information and install a notification of new
        IOServices. The matching information used in the matching dictionary may
        vary depending on the class of service being looked up.

        https://developer.apple.com/documentation/iokit/1514494-ioservicegetmatchingservices?language=objc
        """
        ...


IOServiceGetMatchingServices: _IOServiceGetMatchingServices = ctypes.CFUNCTYPE(
    kern_return_t, mach_port_t, CFDictionaryRef, ctypes.POINTER(io_iterator_t)
)(
    ("IOServiceGetMatchingServices", IOKitLib),
    (
        (1, "mainPort"),
        (1, "matching"),
        (2, "existing"),
    ),
)


def _errcheck_IOServiceGetMatchingServices(
    result: kern_return_t,
    func: _IOServiceGetMatchingServices,
    args: tuple[mach_port_t, CFDictionaryRef, io_iterator_t],
) -> io_iterator_t | None:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    if args[2].value == 0:
        return None

    return args[2]


IOServiceGetMatchingServices.errcheck = _errcheck_IOServiceGetMatchingServices  # type: ignore


class _IOServiceMatchPropertyTable(Protocol):
    def __call__(self, service: IOService, matching: CFDictionaryRef) -> bool:
        """
        Match an IOService objects with matching dictionary.

        Args:
            service:
                The IOService object to match.
            matching:
                A CF dictionary containing matching information. IOKitLib can
            construct matching dictionaries for common criteria with helper functions such as IOServiceMatching, IOServiceNameMatching, IOBSDNameMatching.

        Returns:
            ``True`` if the service matches, ``False`` otherwise.

        Raises:
            OSError: On failure.

        This function calls the matching method of an IOService object and returns the boolean result.
        """
        ...


IOServiceMatchPropertyTable: _IOServiceMatchPropertyTable = ctypes.CFUNCTYPE(
    kern_return_t, io_service_t, CFDictionaryRef, ctypes.POINTER(boolean_t)
)(
    ("IOServiceMatchPropertyTable", IOKitLib),
    ((1, "service"), (1, "matching"), (2, "matches")),
)


def _errcheck_IOServiceMatchPropertyTable(
    result: kern_return_t,
    func: _IOServiceMatchPropertyTable,
    args: tuple[io_service_t, CFDictionaryRef, boolean_t],
) -> bool:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return bool(args[2].value)


IOServiceMatchPropertyTable.errcheck = _errcheck_IOServiceMatchPropertyTable  # type: ignore
