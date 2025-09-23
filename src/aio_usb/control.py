# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from typing import Literal, TypedDict

from aio_usb.descriptor import STRING_DESCRIPTOR


class UsbControlTransferSetup(TypedDict):
    request_type: Literal["standard", "class", "vendor"]
    recipient: Literal["device", "interface", "endpoint", "other"]
    request: int
    value: int
    index: int


# Standard device requests

GET_STATUS = 0x00
CLEAR_FEATURE = 0x01
SET_FEATURE = 0x03
SET_ADDRESS = 0x05
GET_DESCRIPTOR = 0x06
SET_DESCRIPTOR = 0x07
GET_CONFIGURATION = 0x08
SET_CONFIGURATION = 0x09


def get_status() -> tuple[UsbControlTransferSetup, int]:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=GET_STATUS,
        value=0,
        index=0,
    ), 2


def get_descriptor(
    descriptor_type: int, descriptor_index: int
) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=GET_DESCRIPTOR,
        value=(descriptor_type << 8) | descriptor_index,
        index=0,
    )


def set_descriptor(
    descriptor_type: int, descriptor_index: int
) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=SET_DESCRIPTOR,
        value=(descriptor_type << 8) | descriptor_index,
        index=0,
    )


def get_string_descriptor(index: int, lang_id: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=GET_DESCRIPTOR,
        value=(STRING_DESCRIPTOR << 8) | index,
        index=lang_id,
    )


def set_string_descriptor(index: int, lang_id: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=SET_DESCRIPTOR,
        value=(STRING_DESCRIPTOR << 8) | index,
        index=lang_id,
    )


def get_configuration() -> tuple[UsbControlTransferSetup, int]:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=GET_CONFIGURATION,
        value=0,
        index=0,
    ), 1


def set_configuration(configuration_value: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=SET_CONFIGURATION,
        value=configuration_value,
        index=0,
    )
