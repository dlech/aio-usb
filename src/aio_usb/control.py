# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from typing import Literal, TypedDict

from aio_usb.ch9 import UsbDescriptorType, UsbRequest


class UsbControlTransferSetup(TypedDict):
    request_type: Literal["standard", "class", "vendor"]
    recipient: Literal["device", "interface", "endpoint", "other"]
    request: int
    value: int
    index: int


def get_status() -> tuple[UsbControlTransferSetup, int]:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.GET_STATUS,
        value=0,
        index=0,
    ), 2


def get_descriptor(
    descriptor_type: int, descriptor_index: int
) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.GET_DESCRIPTOR,
        value=(descriptor_type << 8) | descriptor_index,
        index=0,
    )


def set_descriptor(
    descriptor_type: int, descriptor_index: int
) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.SET_DESCRIPTOR,
        value=(descriptor_type << 8) | descriptor_index,
        index=0,
    )


def get_string_descriptor(index: int, lang_id: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.GET_DESCRIPTOR,
        value=(UsbDescriptorType.STRING << 8) | index,
        index=lang_id,
    )


def set_string_descriptor(index: int, lang_id: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.SET_DESCRIPTOR,
        value=(UsbDescriptorType.STRING << 8) | index,
        index=lang_id,
    )


def get_configuration() -> tuple[UsbControlTransferSetup, int]:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.GET_CONFIGURATION,
        value=0,
        index=0,
    ), 1


def set_configuration(configuration_value: int) -> UsbControlTransferSetup:
    return UsbControlTransferSetup(
        request_type="standard",
        recipient="device",
        request=UsbRequest.SET_CONFIGURATION,
        value=configuration_value,
        index=0,
    )
