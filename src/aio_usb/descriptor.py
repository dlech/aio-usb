# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import struct

# Standard descriptor types

DEVICE_DESCRIPTOR = 0x01
CONFIGURATION_DESCRIPTOR = 0x02
STRING_DESCRIPTOR = 0x03
INTERFACE_DESCRIPTOR = 0x04
ENDPOINT_DESCRIPTOR = 0x05

# Language ID for English (United States)

LANGID_EN_US = 0x0409

_DEVICE_DESCRIPTOR_STRUCT = struct.Struct("<BBHBBBBHHHBBBB")


class DeviceDescriptor:
    SIZE = _DEVICE_DESCRIPTOR_STRUCT.size

    def __init__(
        self,
        data: bytes,
    ) -> None:
        (
            self.length,
            self.descriptor_type,
            self.usb_version,
            self.device_class,
            self.device_subclass,
            self.device_protocol,
            self.max_packet_size,
            self.vendor_id,
            self.product_id,
            self.device_version,
            self.manufacturer_index,
            self.product_index,
            self.serial_number_index,
            self.num_configurations,
        ) = _DEVICE_DESCRIPTOR_STRUCT.unpack(data)

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} "
            f"length={self.length} "
            f"descriptor_type=0x{self.descriptor_type:02x} "
            f"usb_version=0x{self.usb_version:04x} "
            f"device_class=0x{self.device_class:02x} "
            f"device_subclass=0x{self.device_subclass:02x} "
            f"device_protocol=0x{self.device_protocol:02x} "
            f"max_packet_size={self.max_packet_size} "
            f"vendor_id=0x{self.vendor_id:04x} "
            f"product_id=0x{self.product_id:04x} "
            f"device_version=0x{self.device_version:04x} "
            f"manufacturer_index={self.manufacturer_index} "
            f"product_index={self.product_index} "
            f"serial_number_index={self.serial_number_index} "
            f"num_configurations={self.num_configurations}>"
        )


class StringLangIdDescriptor:
    def __init__(self, data: bytes) -> None:
        self.length = data[0]
        self.descriptor_type = data[1]
        self.langids: list[int] = list(
            struct.unpack_from(f"<{(self.length - 2) // 2}H", data, 2)
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} "
            f"length={self.length} "
            f"descriptor_type={self.descriptor_type:02x} "
            f"langids=[{', '.join([f'0x{langid:04x}' for langid in self.langids])}]>"
        )


class StringDescriptor:
    def __init__(self, data: bytes) -> None:
        self.length = data[0]
        self.descriptor_type = data[1]
        self.string = data[2 : self.length].decode("utf-16le")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} "
            f"length={self.length} "
            f"descriptor_type={self.descriptor_type:02x} "
            f"string={self.string!r}>"
        )
