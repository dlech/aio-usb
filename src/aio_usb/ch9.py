# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from enum import IntEnum, IntFlag


def parse_bcd(bcd: int) -> tuple[int, int, int]:
    """Parse a binary-coded decimal (BCD) value into a version tuple.

    Args:
        bcd: The BCD value.

    Returns:
        A tuple of (major, minor, patch) version numbers.
    """
    major = (bcd >> 8) & 0xFF
    minor = (bcd >> 4) & 0x0F
    patch = bcd & 0x0F

    return major, minor, patch


def bcd_to_str(bcd: int) -> str:
    """Convert a binary-coded decimal (BCD) value to a string.

    Args:
        bcd: The BCD value.

    Returns:
        A string representation of the version.
    """
    major, minor, patch = parse_bcd(bcd)
    return f"{major}.{minor}.{patch}"


class UsbDirection(IntEnum):
    """
    USB transfer directions.

    The first of three bmRequestType fields.
    """

    OUT = 0  # to device
    IN = 0x80  # to host


class UsbType(IntEnum):
    """
    USB transfer types.

    The second of three bmRequestType fields.
    """

    STANDARD = 0x00 << 5
    CLASS = 0x01 << 5
    VENDOR = 0x02 << 5
    RESERVED = 0x03 << 5


class UsbRecipient(IntEnum):
    """
    USB recipients.

    The third of three bmRequestType fields.
    """

    DEVICE = 0x00
    INTERFACE = 0x01
    ENDPOINT = 0x02
    OTHER = 0x03
    PORT = 0x04
    RPIPE = 0x05


class UsbRequest(IntEnum):
    """
    Standard requests, for the bRequest field of a SETUP packet.

    These are qualified by the bmRequestType field, so that for example
    TYPE_CLASS or TYPE_VENDOR specific feature flags could be retrieved
    by a GET_STATUS request.
    """

    GET_STATUS = 0x00
    CLEAR_FEATURE = 0x01
    SET_FEATURE = 0x03
    SET_ADDRESS = 0x05
    GET_DESCRIPTOR = 0x06
    SET_DESCRIPTOR = 0x07
    GET_CONFIGURATION = 0x08
    SET_CONFIGURATION = 0x09
    GET_INTERFACE = 0x0A
    SET_INTERFACE = 0x0B
    SYNCH_FRAME = 0x0C
    SET_SEL = 0x30
    SET_ISOCH_DELAY = 0x31


class UsbControlRequest(ctypes.LittleEndianStructure):
    bmRequestType: int
    bRequest: int
    wValue: int
    wIndex: int
    wLength: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bmRequestType", ctypes.c_uint8),
        ("bRequest", ctypes.c_uint8),
        ("wValue", ctypes.c_uint16),
        ("wIndex", ctypes.c_uint16),
        ("wLength", ctypes.c_uint16),
    ]


class UsbDescriptorType(IntEnum):
    """
    Descriptor types

    USB 3.2 spec table 9-6
    """

    DEVICE = 1
    CONFIGURATION = 2
    STRING = 3
    INTERFACE = 4
    ENDPOINT = 5
    INTERFACE_POWER = 8
    OTG = 9
    DEBUG = 10
    INTERFACE_ASSOCIATION = 11
    BOS = 15
    DEVICE_CAPABILITY = 16
    SUPERSPEED_USB_ENDPOINT_COMPANION = 48
    SUPERSPEEDPLUS_ISOCHRONOUS_ENDPOINT_COMPANION = 49

    # Conventional codes for class-specific descriptors.  The convention is
    # defined in the USB "Common Class" Spec (3.11).  Individual class specs
    # are authoritative for their usage, not the "common class" writeup.
    CS_DEVICE = UsbType.CLASS | DEVICE
    CS_CONFIG = UsbType.CLASS | CONFIGURATION
    CS_STRING = UsbType.CLASS | STRING
    CS_INTERFACE = UsbType.CLASS | INTERFACE
    CS_ENDPOINT = UsbType.CLASS | ENDPOINT


# All standard descriptors have these 2 fields at the beginning
class UsbDescriptorHeader(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
    ]


class UsbDeviceDescriptor(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    bcdUSB: int
    bDeviceClass: int
    bDeviceSubClass: int
    bDeviceProtocol: int
    bMaxPacketSize0: int
    idVendor: int
    idProduct: int
    bcdDevice: int
    iManufacturer: int
    iProduct: int
    iSerialNumber: int
    bNumConfigurations: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
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


class UsbConfigDescriptor(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    wTotalLength: int
    bNumInterfaces: int
    bConfigurationValue: int
    iConfiguration: int
    bmAttributes: int
    bMaxPower: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("wTotalLength", ctypes.c_uint16),
        ("bNumInterfaces", ctypes.c_uint8),
        ("bConfigurationValue", ctypes.c_uint8),
        ("iConfiguration", ctypes.c_uint8),
        ("bmAttributes", ctypes.c_uint8),
        ("bMaxPower", ctypes.c_uint8),
    ]


class UsbConfigAttributes(IntFlag):
    """
    Configuration characteristics (bmAttributes).
    """

    ONE = 1 << 7  # must be set
    SELF_POWERED = 1 << 6
    CAN_WAKEUP = 1 << 5
    BATTERY_POWERED = 1 << 4


class UsbInterfaceDescriptor(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    bInterfaceNumber: int
    bAlternateSetting: int
    bNumEndpoints: int
    bInterfaceClass: int
    bInterfaceSubClass: int
    bInterfaceProtocol: int
    iInterface: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("bInterfaceNumber", ctypes.c_uint8),
        ("bAlternateSetting", ctypes.c_uint8),
        ("bNumEndpoints", ctypes.c_uint8),
        ("bInterfaceClass", ctypes.c_uint8),
        ("bInterfaceSubClass", ctypes.c_uint8),
        ("bInterfaceProtocol", ctypes.c_uint8),
        ("iInterface", ctypes.c_uint8),
    ]


class UsbEndpointDescriptor(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    bEndpointAddress: int
    bmAttributes: int
    wMaxPacketSize: int
    bInterval: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("bEndpointAddress", ctypes.c_uint8),
        ("bmAttributes", ctypes.c_uint8),
        ("wMaxPacketSize", ctypes.c_uint16),
        ("bInterval", ctypes.c_uint8),
    ]


class UsbBosDescriptor(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    wTotalLength: int
    bNumDeviceCaps: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("wTotalLength", ctypes.c_uint16),
        ("bNumDeviceCaps", ctypes.c_uint8),
    ]


class UsbDevCapHeader(ctypes.LittleEndianStructure):
    bLength: int
    bDescriptorType: int
    bDevCapabilityType: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
        ("bDevCapabilityType", ctypes.c_uint8),
    ]
