"""
Definitions from
System/Library/Frameworks/IOKit.framework/Headers/usb/AppleUSBDefinitions.h
"""

import ctypes
from typing import TYPE_CHECKING, TypeAlias

from rubicon.objc.types import with_encoding


@with_encoding(b"{IOUSBDescriptorHeader=CC}")
class IOUSBDescriptorHeader(ctypes.Structure):
    bLength: int
    bDescriptorType: int

    # _pack_ requires _layout_ = "ms" since Python 3.14
    _layout_ = "ms"
    _pack_ = 1
    _fields_ = [
        ("bLength", ctypes.c_uint8),
        ("bDescriptorType", ctypes.c_uint8),
    ]


if TYPE_CHECKING:
    IOUSBDescriptorHeaderPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBDescriptorHeader
    ]
else:
    IOUSBDescriptorHeaderPtr = ctypes.POINTER(IOUSBDescriptorHeader)


@with_encoding(b"{IOUSBDeviceDescriptor=CCSCCCCSSSCCCC}")
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


if TYPE_CHECKING:
    IOUSBDeviceDescriptorPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBDeviceDescriptor
    ]
else:
    IOUSBDeviceDescriptorPtr = ctypes.POINTER(IOUSBDeviceDescriptor)


@with_encoding(b"{IOUSBConfigurationDescriptor=CCSCCCCC}")
class IOUSBConfigurationDescriptor(ctypes.Structure):
    """
    The structure for storing a USB configuration descriptor.

    This descriptor contains information about a specific configuration of a
    device, including the interfaces that configuration provides. This structure
    has a variable length, so it defines only the known fields. Use the
    wTotalLength field to read the entire descriptor.

    For more information about this descriptor type, see section 9.6.3 of the
    USB 2.0 specification at http://www.usb.org.
    """

    bLength: int
    """
    The size of the descriptor in bytes.
    """
    bDescriptorType: int
    """
    The type of the descriptor.
    """
    wTotalLength: int
    """
    The total length of the descriptor, including the length of all related 
    interface, endpoint, and vendor-specific descriptors.
    """
    bNumInterfaces: int
    """
    The number of interfaces this configuration supports.
    """
    bConfigurationValue: int
    """
    The value to use when selecting this configuration.
    """
    iConfiguration: int
    """
    The index of the string descriptor that describes this configuration.
    """
    bmAttributes: int
    """
    A bitmask indicating the configuration's characteristics.
    """
    MaxPower: int
    """
    The maximum power consumption of the USB device expressed in 2mA units.
    """

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
        ("MaxPower", ctypes.c_uint8),
    ]


if TYPE_CHECKING:
    IOUSBConfigurationDescriptorPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBConfigurationDescriptor
    ]
else:
    IOUSBConfigurationDescriptorPtr = ctypes.POINTER(IOUSBConfigurationDescriptor)


@with_encoding(b"{IOUSBInterfaceDescriptor=CCCCCCCCC}")
class IOUSBInterfaceDescriptor(ctypes.Structure):
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


if TYPE_CHECKING:
    IOUSBInterfaceDescriptorPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBInterfaceDescriptor
    ]
else:
    IOUSBInterfaceDescriptorPtr = ctypes.POINTER(IOUSBInterfaceDescriptor)


@with_encoding(b"{IOUSBEndpointDescriptor=CCCCSCC}")
class IOUSBEndpointDescriptor(ctypes.Structure):
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


if TYPE_CHECKING:
    IOUSBEndpointDescriptorPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBEndpointDescriptor
    ]
else:
    IOUSBEndpointDescriptorPtr = ctypes.POINTER(IOUSBEndpointDescriptor)


@with_encoding(b"{IOUSBDeviceRequest=CCSSS}")
class IOUSBDeviceRequest(ctypes.Structure):
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


class IOUSBBOSDescriptor(ctypes.Structure):
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


if TYPE_CHECKING:
    IOUSBBOSDescriptorPtr: TypeAlias = ctypes._Pointer[  # pyright: ignore[reportPrivateUsage]
        IOUSBBOSDescriptor
    ]
else:
    IOUSBBOSDescriptorPtr = ctypes.POINTER(IOUSBBOSDescriptor)
