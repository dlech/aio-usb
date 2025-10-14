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
