from pyrogram import Client, filters
from database.chats import add_chat, remove_chat


@Client.on_message(filters.new_chat_members)
async def on_added(app, message):
    await add_chat(message.chat.id)


@Client.on_message(filters.left_chat_member)
async def on_left(app, message):
    if message.left_chat_member.id == app.me.id:
        await remove_chat(message.chat.id)
