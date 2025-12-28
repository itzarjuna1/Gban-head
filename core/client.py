from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus

import config
from Gban_head.logging import LOGGER


class PARTH(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot...")

        super().__init__(
            name="GbanHead",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()

        self.id = self.me.id
        self.name = f"{self.me.first_name} {(self.me.last_name or '')}".strip()
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=(
                    f"<b>» Bot Started</b>\n\n"
                    f"ID : <code>{self.id}</code>\n"
                    f"Name : {self.name}\n"
                    f"Username : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "Invalid LOGGER_ID or bot not added to log group/channel."
            )
        except Exception as ex:
            LOGGER(__name__).error(
                f"Failed to send startup log: {type(ex).__name__}"
            )

        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "Bot is not admin in LOGGER_ID chat."
                )
        except Exception:
            pass

        LOGGER(__name__).info(f"Bot started as {self.name}")

    async def stop(self):
        LOGGER(__name__).info("Stopping bot...")
        await super().stop()
