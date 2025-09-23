# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from dataclasses import dataclass
from typing import TypedDict


class UsbDeviceMatch(TypedDict, total=False):
    """
    A device match dictionary.

    This is used to specify which USB devices should be discovered.
    """

    vendor_id: int
    """
    The USB vendor ID (idVendor).
    """
    product_id: int
    """
    The USB product ID (idProduct).
    """
    class_: int
    """
    The USB interface class (bDeviceClass).
    """
    subclass: int
    """
    The USB interface subclass (bDeviceSubClass).
    """
    protocol: int
    """
    The USB interface protocol (bDeviceProtocol).
    """


@dataclass(eq=False, frozen=True, slots=True)
class UsbDeviceInfo:
    device_id: str
    """
    The unique identifier for the USB device.
    """
    name: str
    """
    The OS name of the device (suitable for display to user).
    """
    vendor_id: int
    """
    The USB vendor ID (idVendor).
    """
    product_id: int
    """
    The USB product ID (idProduct).
    """
    class_: int
    """
    The USB interface class (bDeviceClass).
    """
    subclass: int
    """
    The USB interface subclass (bDeviceSubClass).
    """
    protocol: int
    """
    The USB interface protocol (bDeviceProtocol).
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UsbDeviceInfo):
            return NotImplemented

        return self.device_id == other.device_id
