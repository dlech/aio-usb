# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from enum import IntEnum

from rubicon.objc.api import ObjCClass, objc_const
from rubicon.objc.runtime import load_library
from rubicon.objc.types import with_encoding

IOUSBHost = load_library("IOUSBHost")


IOUSBHostObject = ObjCClass("IOUSBHostObject")
IOUSBHostDevice = ObjCClass("IOUSBHostDevice")

IOUSBHostErrorDomain = objc_const(IOUSBHost, "IOUSBHostErrorDomain")


class IOUSBHostAbortOption(IntEnum):
    Synchronous = 0
    Asynchronous = 1


@with_encoding(b"{IOUSBDeviceDescriptor=CCSCCCCSSSCCCC}")
class IOUSBDeviceDescriptor(ctypes.Structure):
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("bcdUSB", ctypes.c_uint16),
        ("bDeviceClass", ctypes.c_uint8),
        ("bDeviceSubClass", ctypes.c_uint8),
        ("bDeviceProtocol", ctypes.c_uint8),
        ("bMaxPacketSize0", ctypes.c_uint8),
        ("idVendor", ctypes.c_uint16),
        ("idProduct", ctypes.c_uint16),
        ("bcdDevice", ctypes.c_uint16),
        ("iManufacturer", ctypes.c_uint8),
        ("iProduct", ctypes.c_uint8),
        ("iSerialNumber", ctypes.c_uint8),
        ("bNumConfigurations", ctypes.c_uint8),
    ]

    def __repr__(self) -> str:
        return (
            "IOUSBDeviceDescriptor("
            f"bLength={self.bLength}, "
            f"bDescriptorType=0x{self.bDescriptorType:02x}, "
            f"bcdUSB=0x{self.bcdUSB:04x}, "
            f"bDeviceClass=0x{self.bDeviceClass:02x}, "
            f"bDeviceSubClass=0x{self.bDeviceSubClass:02x}, "
            f"bDeviceProtocol=0x{self.bDeviceProtocol:02x}, "
            f"bMaxPacketSize0={self.bMaxPacketSize0}, "
            f"idVendor=0x{self.idVendor:04x}, "
            f"idProduct=0x{self.idProduct:04x}, "
            f"bcdDevice=0x{self.bcdDevice:04x}, "
            f"iManufacturer={self.iManufacturer}, "
            f"iProduct={self.iProduct}, "
            f"iSerialNumber={self.iSerialNumber}, "
            f"bNumConfigurations={self.bNumConfigurations})"
        )


@with_encoding(b"{IOUSBDeviceRequest=CCSSS}")
class IOUSBDeviceRequest(ctypes.Structure):
    _fields_ = [
        ("bmRequestType", ctypes.c_uint8),
        ("bRequest", ctypes.c_uint8),
        ("wValue", ctypes.c_uint16),
        ("wIndex", ctypes.c_uint16),
        ("wLength", ctypes.c_uint16),
    ]


@with_encoding(b"{IOUSBConfigurationDescriptor=CCSCCCCC}")
class IOUSBConfigurationDescriptor(ctypes.Structure):
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("wTotalLength", ctypes.c_uint16),
        ("bNumInterfaces", ctypes.c_uint8),
        ("bConfigurationValue", ctypes.c_uint8),
        ("iConfiguration", ctypes.c_uint8),
        ("bmAttributes", ctypes.c_uint8),
        ("MaxPower", ctypes.c_uint8),
    ]
