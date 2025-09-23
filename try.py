import asyncio
from contextlib import AsyncExitStack

from aio_usb import find_usb_devices, open_usb_device


async def main():
    infos = await find_usb_devices()

    # print(len(infos), "devices found:")
    # for info in infos:
    #     print(info)

    if not infos:
        return

    async with AsyncExitStack() as stack:
        aenter = stack.enter_async_context

        device = await aenter(open_usb_device(infos[0].device_id))

        print(f"Opened device: {device}")
        print(f"  VID: {device.vendor_id:04x}")
        print(f"  PID: {device.product_id:04x}")
        print(f"  Version: {'.'.join(map(str, device.version))}")

        device_descriptor = await device.get_device_descriptor()
        print("Device Descriptor:", device_descriptor)

        lang_ids = await device.get_lang_ids()
        print("Supported Language IDs:", lang_ids)

        manufacturer = await device.get_string(
            device_descriptor.manufacturer_index, lang_ids[0]
        )
        product = await device.get_string(device_descriptor.product_index, lang_ids[0])
        serial_number = await device.get_string(
            device_descriptor.serial_number_index, lang_ids[0]
        )

        print(f"  Manufacturer: {manufacturer}")
        print(f"  Product: {product}")
        print(f"  Serial Number: {serial_number}")


asyncio.run(main())
