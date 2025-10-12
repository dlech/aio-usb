# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from enum import IntEnum

from typing_extensions import Self, override


class _IntEnumWithMissing(IntEnum):
    @classmethod
    def _missing_(cls, value: object) -> Self:
        member = int.__new__(cls, value)  # type: ignore[call-overload]
        member._name_ = "[unknown]"
        return member


class UsbProtocol(_IntEnumWithMissing):
    pass


class _UsbUnknownProtocol(UsbProtocol):
    _ = -1


class UsbSyncProtocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x01.
    """

    ACTIVE_SYNC = 0x01
    PALM_SYNC = 0x02


class UsbSc2Protocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x02.
    """

    INTERFACE_ASSOCIATION = 0x01
    WIRE_ADAPTER_MULTIFUNCTION = 0x02


class UsbSc3Protocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x03.
    """

    CABLE_BASED_ASSOCIATION = 0x01


class UsbRndisProtocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x04.
    """

    OVER_ETHERNET = 0x01
    OVER_WIFI = 0x02
    OVER_WIMAX = 0x03
    OVER_WWAN = 0x04
    FOR_RAW_IPV4 = 0x05
    FOR_RAW_IPV6 = 0x06
    FOR_GPS = 0x07


class Usb3VisionProtocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x05.
    """

    CONTROL_INTERFACE = 0x00
    EVENT_INTERFACE = 0x01
    STREAMING_INTERFACE = 0x02


class UsbSc7Protocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x07.
    """

    COMMAND_INTERFACE_IN_IAD = 0x01
    COMMAND_INTERFACE = 0x02
    MEDIA_INTERFACE = 0x03


class UsbStepProtocol(UsbProtocol):
    """
    Protocol codes for class: 0xEF, subclass: 0x06.
    """

    STEP = 0x01
    STEP_RAW = 0x02


class UsbSubclass(_IntEnumWithMissing):
    def get_protocol(self, protocol: int) -> UsbProtocol:
        return _UsbUnknownProtocol(protocol)


class _UsbUnknownSubclass(UsbSubclass):
    _ = -1


class UsbSubclassMiscellaneous(UsbSubclass):
    """
    Subclass codes for the Miscellaneous device class (0xEF)
    """

    SYNC = 0x01
    SC2 = 0x02
    SC3 = 0x03
    RNDIS = 0x04
    USB3_VISION = 0x05
    STEP = 0x06
    SC7 = 0x07

    @override
    def get_protocol(self, protocol: int) -> UsbProtocol:
        match self:
            case UsbSubclassMiscellaneous.SYNC:
                return UsbSyncProtocol(protocol)
            case UsbSubclassMiscellaneous.SC2:
                return UsbSc2Protocol(protocol)
            case UsbSubclassMiscellaneous.SC3:
                return UsbSc3Protocol(protocol)
            case UsbSubclassMiscellaneous.RNDIS:
                return UsbRndisProtocol(protocol)
            case UsbSubclassMiscellaneous.USB3_VISION:
                return Usb3VisionProtocol(protocol)
            case UsbSubclassMiscellaneous.STEP:
                return UsbStepProtocol(protocol)
            case UsbSubclassMiscellaneous.SC7:
                return UsbSc7Protocol(protocol)
            case _:
                return super().get_protocol(protocol)


class UsbClass(_IntEnumWithMissing):
    """
    Device and/or Interface Class codes as found in bDeviceClass or bInterfaceClass
    and defined by www.usb.org documents

    https://www.usb.org/defined-class-codes
    """

    PER_INTERFACE = 0x00
    AUDIO = 0x01
    COMMUNICATION = 0x02
    HID = 0x03
    PHYSICAL = 0x05
    IMAGE = 0x06
    PRINTER = 0x07
    MASS_STORAGE = 0x08
    HUB = 0x09
    CDC_DATA = 0x0A
    SMART_CARD = 0x0B
    CONTENT_SECURITY = 0x0D
    VIDEO = 0x0E
    PERSONAL_HEALTHCARE = 0x0F
    AUDIO_VIDEO = 0x10
    BILLBOARD = 0x11
    USB_TYPE_C_BRIDGE = 0x12
    USB_BULK_DISPLAY_PROTOCOL = 0x13
    MCTP_OVER_USB = 0x14
    I3C = 0x3C
    DIAGNOSTIC = 0xDC
    WIRELESS_CONTROLLER = 0xE0
    MISC = 0xEF
    APP_SPEC = 0xFE
    VENDOR_SPEC = 0xFF

    def get_subclass(self, subclass: int) -> UsbSubclass:
        """
        Get the subclass enum for this class.

        Args:
            subclass: The subclass code.
        """
        match self:
            case UsbClass.MISC:
                return UsbSubclassMiscellaneous(subclass)
            case _:
                return _UsbUnknownSubclass(subclass)
