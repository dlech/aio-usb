# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from enum import IntEnum
from typing import Self, overload

from rubicon.objc import NSObject, NSTimeInterval
from rubicon.objc.runtime import objc_id
from typing_extensions import Protocol

from .core_foundation import CFDictionaryRef
from .foundation import NSErrorDomain, NSMutableData
from .io_kit import IOService

class IOUSBHostAbortOption(IntEnum):
    Synchronous = ...
    Asynchronous = ...

IOUSBHostErrorDomain: NSErrorDomain

class IOUSBHostInterestHandler(Protocol):
    def __call__(
        self,
        refcon: ctypes.c_void_p,
        messageType: ctypes.c_uint32,
        messageArgument: ctypes.c_void_p,
        /,
    ) -> None:
        """
        The callback that handles underlying service-state changes.

        Args:
            hostObject:
                The IOUSBHostObject of the interest notification.
            messageType:
                A messageType enumeration that IOKit/IOMessage.h or the IOService family
                defines.
            messageArgument:
                An argument for the message, dependent on the message type. If the
                message data is larger than sizeof(void*), messageArgument contains a
                pointer to the message data; otherwise, messageArgument contains the
                message data.

        This is the block for the kIOGeneralInterest handler, and handles underlying
        service-state changes, such as termination. See IOServiceInterestCallback in
        IOKit for more details. An internal serial queue separate from the input/output
        queue services all notifications.

        https://developer.apple.com/documentation/iousbhost/iousbhostinteresthandler?language=objc
        """
        ...

class IOUSBHostCompletionHandler(Protocol):
    def __call__(self, status: int, bytesTransferred: int, /) -> None:
        """
        The completion handler for asynchronous control, bulk, and interrupt transfers.

        Args:
            status: The result for the transfer.
            bytesTransferred: The number of bytes the request transferred.

        https://developer.apple.com/documentation/iousbhost/iousbhostcompletionhandler?language=objc
        """
        ...

class IOUSBHostObject(NSObject):
    def initWithIOService(
        self,
        service: IOService,
        /,
        *,
        queue: ctypes.c_void_p | None,
        error: objc_id,
        interestHandler: IOUSBHostInterestHandler | None,
    ) -> Self | None:
        """
        Creates a USB host object and sets up a default communication
        channel to the kernel.

        Args:
            service:
                The service type of the IOUSBHostDevice or IOUSBHostInterface.
                The IOUSBHostObject keeps a reference to the service type
                and releases it during destroy.
            queue:
                A serial dispatch queue for serviceable asynchronous input/output
                requests. By default, this method creates a serial queue on
                behalf of the client.
            error:
                An NSError that contains an IOReturn value on failure.
            interestHandler:
                A callback for managing internal device state changes, such
                as termination.

        Returns:
            An IOUSBHostObject instance, or nil on failure.

        If the kernel IOUSBHostDevice or IOUSBHostInterface is already open
        for exclusive access, the method returns nil. The method establishes
        exclusive ownership of the io_service_t.

        .. important::
            When done with the object, call :meth:`destroy`.
        """
        ...

    @property
    def deviceDescriptor(self) -> ctypes._Pointer[IOUSBDeviceDescriptor]: ...  # pyright: ignore[reportPrivateUsage]
    def destroy(self) -> None:
        """
        Removes underlying allocations and connections from the USB host object.

        When you no longer need the IOUSBHostObject, call destroy. This
        method destroys the connection with the kernel object and
        deregisters interest on :class:`IOService`. Calling destroy multiple
        times has no effect.
        """
        ...

    @overload
    def enqueueDeviceRequest(
        self,
        request: IOUSBDeviceRequest,
        /,
        *,
        data: NSMutableData | None,
        completionTimeout: NSTimeInterval,
        error: objc_id,
        completionHandler: IOUSBHostCompletionHandler,
    ) -> bool: ...
    @overload
    def enqueueDeviceRequest(
        self,
        request: IOUSBDeviceRequest,
        /,
        *,
        data: NSMutableData | None,
        error: objc_id,
        completionHandler: IOUSBHostCompletionHandler,
    ) -> bool: ...
    @overload
    def enqueueDeviceRequest(
        self,
        request: IOUSBDeviceRequest,
        /,
        *,
        error: objc_id,
        completionHandler: IOUSBHostCompletionHandler,
    ) -> bool: ...
    def abortDeviceRequestsWithOption(
        self, option: IOUSBHostAbortOption, /, *, error: objc_id
    ) -> bool: ...
    def abortDeviceRequestsWithError(self, error: objc_id, /) -> bool: ...

class IOUSBHostDevice(IOUSBHostObject):
    @classmethod
    def createMatchingDictionaryWithVendorID(
        cls,
        vendorID: int | None,
        /,
        *,
        productID: int | None,
        bcdDevice: int | None,
        deviceClass: int | None,
        deviceSubclass: int | None,
        deviceProtocol: int | None,
        speed: int | None,
        productIDArray: list[int] | None,
    ) -> CFDictionaryRef: ...
    # @property
    # def configurationDescriptors(self) -> "IOUSBConfigurationDescriptor": ...
    @overload
    def configureWithValue(
        self,
        value: int,
        /,
        *,
        matchInterfaces: bool,
        error: objc_id,
    ) -> None: ...
    @overload
    def configureWithValue(
        self,
        value: int,
        /,
        *,
        error: objc_id,
    ) -> None: ...

class IOUSBDeviceDescriptor(ctypes.Structure):
    """
    The structure for storing a USB device descriptor.

    For information about this descriptor type, see section 9.6.1 of the USB 3.2
    specification at http://www.usb.org.
    """

    bLength: int
    """
    The length of the descriptor in bytes.
    """
    bDescriptorType: int
    """
    The type of the descriptor.
    """
    bcdUSB: int
    """
    The USB specification release number with which the device complies.
    """
    bDeviceClass: int
    """
    The class code indicating the behavior of this device.
    """
    bDeviceSubClass: int
    """
    The subclass code that further defines the behavior of this device.
    """
    bDeviceProtocol: int
    """
    The protocol that the device supports.
    """
    bMaxPacketSize0: int
    """
    The maximum packet size for endpoint 0, specified as an exponent value.
    """
    idVendor: int
    """
    The ID of the device’s manufacturer.
    """
    idProduct: int
    """
    The product ID assigned by the manufacturer.
    """
    bcdDevice: int
    """
    The release number of the device, specified as a binary-coded decimal number.
    """
    iManufacturer: int
    """
    The index of the string descriptor that describes the manufacturer.
    """
    iProduct: int
    """
    The index of the string descriptor that describes the product.
    """
    iSerialNumber: int
    """
    The index of the string descriptor that describes the device’s serial number.
    """
    bNumConfigurations: int
    """
    The number of configurations that the device supports.
    """

class IOUSBDeviceRequest(ctypes.Structure):
    bmRequestType: int
    bRequest: int
    wValue: int
    wIndex: int
    wLength: int
    def __init__(
        self,
        bmRequestType: int = 0,
        bRequest: int = 0,
        wValue: int = 0,
        wIndex: int = 0,
        wLength: int = 0,
    ) -> None: ...
