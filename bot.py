import asyncio
import signal

from Gban_head.core.client import PARTH
from Gban_head.logging import LOGGER


bot = PARTH()


async def main():
    await bot.start()
    LOGGER(__name__).info("Bot is running...")

    stop_event = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
