# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from enum import IntEnum

from rubicon.objc.api import ObjCClass, objc_const
from rubicon.objc.runtime import load_library

from aio_usb.backend.rubicon_objc.io_kit.usb.apple_usb_definitions import (
    IOUSBConfigurationDescriptorPtr,
    IOUSBDescriptorHeaderPtr,
    IOUSBEndpointDescriptorPtr,
    IOUSBInterfaceDescriptorPtr,
)

IOUSBHost = load_library("IOUSBHost")


IOUSBHostObject = ObjCClass("IOUSBHostObject")
IOUSBHostDevice = ObjCClass("IOUSBHostDevice")
IOUSBHostInterface = ObjCClass("IOUSBHostInterface")

IOUSBHostErrorDomain = objc_const(IOUSBHost, "IOUSBHostErrorDomain")


class IOUSBHostAbortOption(IntEnum):
    Synchronous = 0
    Asynchronous = 1


IOUSBGetNextInterfaceDescriptor = ctypes.CFUNCTYPE(
    IOUSBInterfaceDescriptorPtr,
    IOUSBConfigurationDescriptorPtr,
    IOUSBDescriptorHeaderPtr,
)(
    ("IOUSBGetNextInterfaceDescriptor", IOUSBHost),
    ((1, "configurationDescriptor"), (1, "currentDescriptor")),
)

IOUSBGetNextEndpointDescriptor = ctypes.CFUNCTYPE(
    IOUSBEndpointDescriptorPtr,
    IOUSBConfigurationDescriptorPtr,
    IOUSBInterfaceDescriptorPtr,
    IOUSBDescriptorHeaderPtr,
)(
    ("IOUSBGetNextEndpointDescriptor", IOUSBHost),
    (
        (1, "configurationDescriptor"),
        (1, "interfaceDescriptor"),
        (1, "currentDescriptor"),
    ),
)

# Registry property names

IOUSBHostMatchingPropertyKeyVendorID = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyVendorID"
)
IOUSBHostMatchingPropertyKeyProductID = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyProductID"
)
IOUSBHostMatchingPropertyKeyProductIDMask = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyProductIDMask"
)
IOUSBHostMatchingPropertyKeyProductIDArray = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyProductIDArray"
)
IOUSBHostMatchingPropertyKeyInterfaceNumber = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyInterfaceNumber"
)
IOUSBHostMatchingPropertyKeyConfigurationValue = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyConfigurationValue"
)
IOUSBHostMatchingPropertyKeyDeviceReleaseNumber = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyDeviceReleaseNumber"
)
IOUSBHostMatchingPropertyKeyInterfaceClass = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyInterfaceClass"
)
IOUSBHostMatchingPropertyKeyInterfaceSubClass = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyInterfaceSubClass"
)
IOUSBHostMatchingPropertyKeyInterfaceProtocol = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyInterfaceProtocol"
)
IOUSBHostMatchingPropertyKeyProductIDMask = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyProductIDMask"
)
IOUSBHostMatchingPropertyKeyDeviceClass = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyDeviceClass"
)
IOUSBHostMatchingPropertyKeyDeviceSubClass = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyDeviceSubClass"
)
IOUSBHostMatchingPropertyKeyDeviceProtocol = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeyDeviceProtocol"
)
IOUSBHostMatchingPropertyKeySpeed = objc_const(
    IOUSBHost, "IOUSBHostMatchingPropertyKeySpeed"
)


IOUSBHostPropertyKeyLocationID = objc_const(IOUSBHost, "IOUSBHostPropertyKeyLocationID")

IOUSBHostDevicePropertyKeyVendorString = objc_const(
    IOUSBHost, "IOUSBHostDevicePropertyKeyVendorString"
)
IOUSBHostDevicePropertyKeySerialNumberString = objc_const(
    IOUSBHost, "IOUSBHostDevicePropertyKeySerialNumberString"
)
IOUSBHostDevicePropertyKeyContainerID = objc_const(
    IOUSBHost, "IOUSBHostDevicePropertyKeyContainerID"
)
IOUSBHostDevicePropertyKeyCurrentConfiguration = objc_const(
    IOUSBHost, "IOUSBHostDevicePropertyKeyCurrentConfiguration"
)
