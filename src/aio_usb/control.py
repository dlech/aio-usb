# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>


from aio_usb.ch9 import (
    UsbControlRequest,
    UsbDescriptorType,
    UsbDirection,
    UsbRecipient,
    UsbRequest,
    UsbType,
)


def get_status() -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.IN | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.GET_STATUS,
        wLength=2,
    )


def get_descriptor(
    descriptor_type: int, descriptor_index: int, length: int
) -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.IN | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.GET_DESCRIPTOR,
        wValue=(descriptor_type << 8) | descriptor_index,
        wLength=length,
    )


def set_descriptor(descriptor_type: int, descriptor_index: int) -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.OUT | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.SET_DESCRIPTOR,
        wValue=(descriptor_type << 8) | descriptor_index,
    )


def get_string_descriptor(index: int, lang_id: int, length: int) -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.IN | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.GET_DESCRIPTOR,
        wValue=(UsbDescriptorType.STRING << 8) | index,
        wIndex=lang_id,
        wLength=length,
    )


def set_string_descriptor(index: int, lang_id: int) -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.OUT | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.SET_DESCRIPTOR,
        wValue=(UsbDescriptorType.STRING << 8) | index,
        wIndex=lang_id,
    )


def get_configuration() -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.IN | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.GET_CONFIGURATION,
        wLength=1,
    )


def set_configuration(configuration_value: int) -> UsbControlRequest:
    return UsbControlRequest(
        bmRequestType=UsbDirection.OUT | UsbType.STANDARD | UsbRecipient.DEVICE,
        bRequest=UsbRequest.SET_CONFIGURATION,
        wValue=configuration_value,
    )
