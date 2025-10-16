import asyncio
from contextlib import AsyncExitStack

from aio_usb import find_usb_devices, open_usb_device


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
        print(f"  VID: {device.vendor_id:04x}")
        print(f"  PID: {device.product_id:04x}")
        print(f"  Version: {device.version_str}")

        if device.manufacturer_name:
            print(f"  Manufacturer: {device.manufacturer_name}")

        if device.product_name:
            print(f"  Product: {device.product_name}")

        if device.serial_number:
            print(f"  Serial Number: {device.serial_number}")

        # print(f"  Number of Interfaces: {cfg.bNumInterfaces}")

        iface = await aenter(device.open_interface(number=0))
        # iface = await aenter(
        #     device.open_interface(class_=0xFF, subclass=0xC5, protocol=0xF5)
        # )

        print(f"Opened interface: {iface}")
        print(f"  Interface Number: {iface.interface_number}")
        print(f"  Alternate Setting: {iface.alternate_setting}")
        print(f"  Class: {iface.interface_class:02x}")
        print(f"  Subclass: {iface.interface_subclass:02x}")
        print(f"  Protocol: {iface.interface_protocol:02x}")
        # print(f"  Description: {iface.description}")

        out_pipe = await aenter(iface.open_out_pipe())
        in_pipe = await aenter(iface.open_in_pipe())

        await out_pipe.transfer(b"\x01\x00")
        data = await in_pipe.transfer(64)

        print("Received data:", data)


asyncio.run(main())
