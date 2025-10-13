import asyncio
from contextlib import AsyncExitStack

from aio_usb import find_usb_devices, open_usb_device
from aio_usb.ch9 import bcd_to_str


async def main():
    infos = await find_usb_devices()

    print(len(infos), "devices found:")
    # for info in infos:
    #     print(info)

    if not infos:
        return

    async with AsyncExitStack() as stack:
        aenter = stack.enter_async_context

        device = await aenter(open_usb_device(infos[0].device_id))

        print(f"Opened device: {device}")
        print(f"  VID: {device.device_descriptor.idVendor:04x}")
        print(f"  PID: {device.device_descriptor.idProduct:04x}")
        print(f"  Version: {bcd_to_str(device.device_descriptor.bcdDevice)}")

        lang_ids = await device.get_lang_ids()
        print("Supported Language IDs:", lang_ids)

        if device.device_descriptor.iManufacturer > 0:
            manufacturer = await device.get_string(
                device.device_descriptor.iManufacturer, lang_ids[0]
            )
            print(f"  Manufacturer: {manufacturer}")

        if device.device_descriptor.iProduct > 0:
            product = await device.get_string(
                device.device_descriptor.iProduct, lang_ids[0]
            )
            print(f"  Product: {product}")

        if device.device_descriptor.iSerialNumber > 0:
            serial_number = await device.get_string(
                device.device_descriptor.iSerialNumber, lang_ids[0]
            )
            print(f"  Serial Number: {serial_number}")

        cfg = device.configuration_descriptor

        print(f"Configuration: {cfg.bConfigurationValue}")

        if cfg.iConfiguration > 0:
            config_str = await device.get_string(cfg.iConfiguration, lang_ids[0])
            print(f"  Configuration name: {config_str}")

        print(f"  Number of Interfaces: {cfg.bNumInterfaces}")


asyncio.run(main())
