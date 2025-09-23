import asyncio
from contextlib import AsyncExitStack

from aio_usb import monitor_usb_devices


async def main() -> None:
    async with AsyncExitStack() as stack:
        devices: dict[str, str] = {}

        aenter = stack.enter_async_context

        monitor = await aenter(monitor_usb_devices())
        tg = await aenter(asyncio.TaskGroup())

        async def watch_added():
            async for device in monitor.added():
                devices[device.device_id] = device.name
                print("Device connected:", device.name)

        tg.create_task(watch_added())

        async def watch_removed():
            async for device_id in monitor.removed():
                name = devices.pop(device_id, device_id)
                print("Device disconnected:", name)

        tg.create_task(watch_removed())


asyncio.run(main())
