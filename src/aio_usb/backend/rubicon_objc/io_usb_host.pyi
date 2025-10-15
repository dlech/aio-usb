# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from enum import IntEnum
from typing import Self, TypeAlias, overload

from rubicon.objc import NSObject, NSTimeInterval
from rubicon.objc.runtime import objc_id
from typing_extensions import Protocol

from .core_foundation import CFDictionaryRef
from .dispatch._queue import DispatchQueue
from .foundation import NSErrorDomain, NSMutableData
from .io_kit import IOService
from .io_kit.usb.apple_usb_definitions import (
    IOUSBBOSDescriptorPtr,
    IOUSBConfigurationDescriptorPtr,
    IOUSBDescriptorHeaderPtr,
    IOUSBDeviceDescriptorPtr,
    IOUSBDeviceRequest,
    IOUSBEndpointDescriptorPtr,
    IOUSBInterfaceDescriptorPtr,
)

class IOUSBHostAbortOption(IntEnum):
    Synchronous = ...
    Asynchronous = ...

IOUSBHostErrorDomain: NSErrorDomain

IOUSBHostObjectInitOptions: TypeAlias = int

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

class IOUSBHostInterface(IOUSBHostObject):
    @classmethod
    def createMatchingDictionaryWithVendorID(
        cls,
        vendorID: int | None,
        /,
        *,
        productID: int | None,
        bcdDevice: int | None,
        interfaceNumber: int | None,
        configurationValue: int | None,
        interfaceClass: int | None,
        interfaceSubclass: int | None,
        interfaceProtocol: int | None,
        speed: int | None,
        productIDArray: list[int] | None,
    ) -> CFDictionaryRef: ...
    @property
    def configurationDescriptor(
        self,
    ) -> IOUSBConfigurationDescriptorPtr: ...
    @property
    def interfaceDescriptor(
        self,
    ) -> IOUSBInterfaceDescriptorPtr: ...
    def selectAlternateSetting(
        self, alternateSetting: int, /, *, error: objc_id
    ) -> bool: ...
    def copyPipeWithAddress(
        self, address: int, /, *, error: objc_id
    ) -> IOUSBHostPipe | None: ...
    @property
    def idleTimeout(self) -> float: ...
    def setIdleTimeout(self, timeout: float, /, *, error: objc_id) -> bool: ...
    @overload
    def initWithIOService(
        self,
        service: IOService,
        /,
        *,
        options: IOUSBHostObjectInitOptions,
        queue: DispatchQueue | None,
        error: objc_id,
        interestHandler: IOUSBHostInterestHandler | None,
    ) -> Self | None: ...
    @overload
    def initWithIOService(
        self,
        service: IOService,
        /,
        *,
        queue: DispatchQueue | None,
        error: objc_id,
        interestHandler: IOUSBHostInterestHandler | None,
    ) -> Self | None: ...

class IOUSBHostPipe(IOUSBHostIOSource):
    def enqueueIORequestWithData(
        self,
        data: NSMutableData,
        /,
        *,
        completionTimeout: float,
        error: objc_id,
        completionHandler: IOUSBHostCompletionHandler | None,
    ) -> bool: ...
    def sendIORequestWithData(
        self,
        data: NSMutableData,
        /,
        *,
        completionTimeout: float,
        error: objc_id,
    ) -> bool: ...
    def abortWithOption(
        self, option: IOUSBHostAbortOption, /, *, error: objc_id
    ) -> bool: ...
    def abortWithError(self, error: objc_id, /) -> bool: ...
    def clearStallWithError(self, error: objc_id, /) -> bool: ...

class IOUSBHostObject(NSObject):
    @overload
    def initWithIOService(
        self,
        service: IOService,
        /,
        *,
        options: IOUSBHostObjectInitOptions,
        queue: DispatchQueue | None,
        error: objc_id,
        interestHandler: IOUSBHostInterestHandler | None,
    ) -> Self | None: ...
    @overload
    def initWithIOService(
        self,
        service: IOService,
        /,
        *,
        queue: DispatchQueue | None,
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
    def ioService(self) -> int: ...
    @property
    def queue(self) -> DispatchQueue: ...
    def destroy(self) -> None:
        """
        Removes underlying allocations and connections from the USB host object.

        When you no longer need the IOUSBHostObject, call destroy. This
        method destroys the connection with the kernel object and
        deregisters interest on :class:`IOService`. Calling destroy multiple
        times has no effect.
        """
        ...
    def ioDataWithCapacity(
        self, capacity: int, /, *, error: objc_id
    ) -> NSMutableData | None: ...
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
    @property
    def deviceAddress(self) -> int: ...
    def frameNumberWithTime(self, time: int, /) -> int: ...
    @property
    def capabilityDescriptors(self) -> IOUSBBOSDescriptorPtr: ...
    @property
    def deviceDescriptor(self) -> IOUSBDeviceDescriptorPtr: ...
    def configurationDescriptorWithIndex(
        self, index: int, /, *, error: objc_id
    ) -> IOUSBConfigurationDescriptorPtr: ...

class IOUSBHostIOSource(NSObject):
    @property
    def deviceAddress(self) -> int: ...
    @property
    def endpointAddress(self) -> int: ...
    @property
    def hostInterface(self) -> IOUSBHostInterface: ...

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
    @property
    def configurationDescriptor(
        self,
    ) -> IOUSBConfigurationDescriptorPtr: ...
    @overload
    def configureWithValue(
        self,
        value: int,
        /,
        *,
        matchInterfaces: bool,
        error: objc_id,
    ) -> bool: ...
    @overload
    def configureWithValue(
        self,
        value: int,
        /,
        *,
        error: objc_id,
    ) -> bool: ...

def IOUSBGetNextInterfaceDescriptor(
    configurationDescriptor: IOUSBConfigurationDescriptorPtr,
    currentDescriptor: IOUSBDescriptorHeaderPtr | None,
) -> IOUSBInterfaceDescriptorPtr: ...
def IOUSBGetNextEndpointDescriptor(
    configurationDescriptor: IOUSBConfigurationDescriptorPtr,
    interfaceDescriptor: IOUSBInterfaceDescriptorPtr,
    currentDescriptor: IOUSBDescriptorHeaderPtr | None,
) -> IOUSBEndpointDescriptorPtr: ...
