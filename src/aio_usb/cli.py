# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import argparse
import asyncio
import ctypes
import importlib.metadata
import sys

from aio_usb import UsbDevice, find_usb_devices, open_usb_device
from aio_usb.ch9 import (
    UsbBosDescriptor,
    UsbConfigAttributes,
    UsbConfigDescriptor,
    UsbDescriptorHeader,
    UsbDescriptorType,
    UsbDevCapHeader,
    UsbEndpointDescriptor,
    UsbInterfaceDescriptor,
    bcd_to_str,
    parse_bcd,
)
from aio_usb.class_codes import UsbClass


class Args(argparse.Namespace):
    verbose: bool
    id: tuple[int | None, int | None]


def vendor_product_id(value: str) -> tuple[int | None, int | None]:
    """
    Parse a vendor:[product] ID argument.
    """
    try:
        parts = value.split(":")

        if len(parts) == 1 or not parts[1]:
            return int(parts[0], 16), None

        if len(parts) == 2:
            return int(parts[0], 16), int(parts[1], 16)

        raise ValueError("Too many parts")
    except Exception as e:
        raise argparse.ArgumentTypeError(
            f"Invalid vendor:[product] ID '{value}'"
        ) from e


async def print_device_descriptor(device: UsbDevice, lang_id: int) -> None:
    """
    Pretty-print the device descriptor.
    """
    dd = device.device_descriptor

    print("Device Descriptor:")
    print(f"  bLength            {dd.bLength: 4d}")
    print(f"  bDescriptorType    {dd.bDescriptorType: 04d}")
    print(f"  bcdUSB          {bcd_to_str(dd.bcdUSB):>7s}")
    class_ = UsbClass(dd.bDeviceClass)
    print(f"  bDeviceClass       0x{dd.bDeviceClass:02X}  {class_.name}")
    subclass = class_.get_subclass(dd.bDeviceSubClass)
    print(f"  bDeviceSubClass    0x{dd.bDeviceSubClass:02X}  {subclass.name}")
    protocol = subclass.get_protocol(dd.bDeviceProtocol)
    print(f"  bDeviceProtocol    0x{dd.bDeviceProtocol:02X}  {protocol.name}")
    print(f"  bMaxPacketSize0    {dd.bMaxPacketSize0: 4d}")
    print(f"  idVendor         0x{dd.idVendor:04x}")
    print(f"  idProduct        0x{dd.idProduct:04x}")
    print(f"  bcdDevice       {bcd_to_str(dd.bcdDevice):>7s}")
    mfg = await device.get_string(dd.iManufacturer, lang_id) if dd.iManufacturer else ""
    print(f"  iManufacturer      {dd.iManufacturer: 4d}  {mfg}")
    product = await device.get_string(dd.iProduct, lang_id) if dd.iProduct else ""
    print(f"  iProduct           {dd.iProduct: 4d}  {product}")
    print(f"  iSerialNumber      {dd.iSerialNumber: 4d}")
    print(f"  bNumConfigurations {dd.bNumConfigurations: 4d}")

    for i in range(dd.bNumConfigurations):
        await print_config_descriptor(i, device, lang_id)

    if parse_bcd(dd.bcdUSB) >= (2, 1):
        await print_bos_descriptor(device)


async def print_config_descriptor(index: int, device: UsbDevice, lang_id: int) -> None:
    """
    Pretty-print a configuration descriptor.
    """
    config_data = await device.get_config_descriptor(index)

    config = UsbConfigDescriptor.from_buffer_copy(config_data)
    offset = ctypes.sizeof(UsbConfigDescriptor)

    print("  Configuration Descriptor:")
    print(f"    bLength             {config.bLength: 4d}")
    print(f"    bDescriptorType     {config.bDescriptorType: 04d}")
    print(f"    wTotalLength      {config.wTotalLength: 6d}")
    print(f"    bNumInterfaces      {config.bNumInterfaces: 4d}")
    print(f"    bConfigurationValue {config.bConfigurationValue: 4d}")
    if config.iConfiguration:
        config_str = await device.get_string(config.iConfiguration, lang_id)
    else:
        config_str = ""
    print(f"    iConfiguration      {config.iConfiguration: 4d}  {config_str}")
    print(f"    bmAttributes        0x{config.bmAttributes:02X}")
    config_attrs = UsbConfigAttributes(config.bmAttributes)
    config_attr_descs: list[str] = []
    if not (config_attrs & UsbConfigAttributes.ONE):
        config_attr_descs.append("(Warning: bit 7 not set)")
    if config_attrs & UsbConfigAttributes.SELF_POWERED:
        config_attr_descs.append("(Self Powered)")
    else:
        config_attr_descs.append("(Bus Powered)")
    if config_attrs & UsbConfigAttributes.CAN_WAKEUP:
        config_attr_descs.append("(Remote Wakeup)")
    if config_attrs & UsbConfigAttributes.BATTERY_POWERED:
        config_attr_descs.append("(Battery Powered)")
    print(f"      {' '.join(config_attr_descs)}")
    print(f"    bMaxPower           {config.bMaxPower: 4d}  {config.bMaxPower * 2} mA")

    while offset < config.wTotalLength:
        header = UsbDescriptorHeader.from_buffer_copy(config_data, offset)

        match header.bDescriptorType:
            case UsbDescriptorType.INTERFACE:
                iface = UsbInterfaceDescriptor.from_buffer_copy(config_data, offset)
                await print_interface_descriptor(iface, device, lang_id)
            case UsbDescriptorType.ENDPOINT:
                endpoint = UsbEndpointDescriptor.from_buffer_copy(config_data, offset)
                await print_endpoint_descriptor(endpoint)
            case UsbDescriptorType.CS_DEVICE:
                match iface.bInterfaceClass:  # pyright: ignore[reportPossiblyUnboundVariable]
                    case UsbClass.HID:
                        print("      HID Descriptor:")
                        print(f"        bLength          {header.bLength: 4d}")
                        print(f"        bDescriptorType  {header.bDescriptorType: 4d}")
                        # TODO: finish HID descriptor
                    case UsbClass.SMART_CARD:
                        print("      Smart Card Descriptor:")
                        print(f"        bLength          {header.bLength: 4d}")
                        print(f"        bDescriptorType  {header.bDescriptorType: 4d}")
                        # TODO: finish Smart Card descriptor
                    case _:
                        print("      Unknown Class-Specific Device Descriptor:")
                        print(f"        bLength          {header.bLength: 4d}")
                        print(
                            f"        bDescriptorType  {header.bDescriptorType: 4d}  (0x{header.bDescriptorType:02X})"
                        )
            case _:
                print("      Unknown Descriptor:")
                print(f"        bLength          {header.bLength: 4d}")
                print(
                    f"        bDescriptorType  {header.bDescriptorType: 4d}  (0x{header.bDescriptorType:02X})"
                )

        offset += header.bLength


async def print_interface_descriptor(
    iface: UsbInterfaceDescriptor, device: UsbDevice, lang_id: int
) -> None:
    """
    Pretty-print an interface descriptor.
    """
    print("    Interface Descriptor:")
    print(f"      bLength            {iface.bLength: 4d}")
    print(f"      bDescriptorType    {iface.bDescriptorType: 04d}")
    print(f"      bInterfaceNumber   {iface.bInterfaceNumber: 4d}")
    print(f"      bAlternateSetting  {iface.bAlternateSetting: 4d}")
    class_ = UsbClass(iface.bInterfaceClass)
    print(f"      bInterfaceClass    0x{iface.bInterfaceClass:02X}  {class_.name}")
    subclass = class_.get_subclass(iface.bInterfaceSubClass)
    print(f"      bInterfaceSubClass 0x{iface.bInterfaceSubClass:02X}  {subclass.name}")
    protocol = subclass.get_protocol(iface.bInterfaceProtocol)
    print(f"      bInterfaceProtocol 0x{iface.bInterfaceProtocol:02X}  {protocol.name}")
    if iface.iInterface:
        iface_str = await device.get_string(iface.iInterface, lang_id)
    else:
        iface_str = ""

    print(f"      iInterface         {iface.iInterface: 4d}  {iface_str}")


async def print_endpoint_descriptor(endpoint: UsbEndpointDescriptor) -> None:
    """
    Pretty-print an endpoint descriptor.
    """
    print("      Endpoint Descriptor:")
    print(f"        bLength          {endpoint.bLength: 4d}")
    print(f"        bDescriptorType  {endpoint.bDescriptorType: 04d}")
    ep_dir = "IN" if (endpoint.bEndpointAddress & 0x80) else "OUT"
    ep_num = endpoint.bEndpointAddress & 0x0F
    print(
        f"        bEndpointAddress 0x{endpoint.bEndpointAddress:02X}  EP {ep_num} {ep_dir}"
    )
    ep_type = endpoint.bmAttributes & 0x03
    match ep_type:
        case 0:
            ep_type_str = "Control"
        case 1:
            ep_type_str = "Isochronous"
        case 2:
            ep_type_str = "Bulk"
        case 3:
            ep_type_str = "Interrupt"
        case _:
            ep_type_str = "Unknown"
    print(f"        bmAttributes     0x{endpoint.bmAttributes:02X}  ({ep_type_str})")
    print(f"        wMaxPacketSize   {endpoint.wMaxPacketSize: 4d}")
    print(f"        bInterval        {endpoint.bInterval: 4d}")


async def print_bos_descriptor(device: UsbDevice) -> None:
    """
    Pretty-print the BOS descriptor.
    """
    bos_data = await device.get_bos_descriptor()

    bos = UsbBosDescriptor.from_buffer_copy(bos_data)

    print("Binary Object Store Descriptor:")
    print(f"  bLength            {bos.bLength: 4d}")
    print(f"  bDescriptorType    {bos.bDescriptorType: 4d}")
    print(f"  wTotalLength     {bos.wTotalLength: 6d}")
    print(f"  bNumDeviceCaps     {bos.bNumDeviceCaps: 4d}")

    offset = ctypes.sizeof(UsbBosDescriptor)

    for _ in range(bos.bNumDeviceCaps):
        cap = UsbDevCapHeader.from_buffer_copy(bos_data, offset)
        print("  Device Capability:")
        print(f"    bLength            {cap.bLength: 4d}")
        print(f"    bDescriptorType    {cap.bDescriptorType: 4d}")
        print(f"    bDevCapabilityType {cap.bDevCapabilityType: 4d}")
        offset += cap.bLength


async def list_usb_devices(args: Args) -> int:
    vid, pid = args.id

    infos = await find_usb_devices(vendor_id=vid, product_id=pid)
    if not infos:
        print("No matching USB devices found", file=sys.stderr)
        return 1

    for info in infos:
        print(f"{info.vendor_id:04x}:{info.product_id:04x} {info.name}")

        if args.verbose:
            async with open_usb_device(info.device_id) as device:
                lang_ids = await device.get_lang_ids()
                await print_device_descriptor(device, lang_ids[0])

    return 0


def main():
    parser = argparse.ArgumentParser(description="USB Information Tool")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"usb-info (aio-usb) v{importlib.metadata.version('aio-usb')}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase verbosity (show descriptors)",
    )
    parser.add_argument(
        "-d",
        help="Show only devices with the specified vendor and product ID numbers (in hexadecimal)",
        metavar="vendor:[product]",
        type=vendor_product_id,
        default=(None, None),
        dest="id",
    )
    args = parser.parse_args(namespace=Args())

    exit(asyncio.run(list_usb_devices(args)))


if __name__ == "__main__":
    main()
