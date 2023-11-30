import pyrogram
import os
from pyrogram import Client as bot, filters, enums
from database.accept_db import Accept
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired
from info import ADMINS

approve_text = {}

@bot.on_chat_join_request(filters.group | filters.channel & ~filters.private)
async def on_join_request(bot, message):
    chat_id = message.chat.id
    chat_name = message.chat.title
    user_id = message.from_user.id
    username = message.from_user.username
    db = Accept(message.chat.id)
    status = db.get_accept_status()    
    # Check if auto-approve is enabled for this chat
    if status:
        # Approve the join request
        await bot.approve_chat_join_request(chat_id, user_id)
        await bot.send_message(user_id, f"Hello {username} !\nYour Request To Join {chat_name} was approved👍\n\n⚠️click /start to see my power⚠️\n\n__Powered By: @KOMBOTZZ .")
    else:
        # Skip the join request
        pass

@bot.on_message(filters.command("autoaccept") & filters.group)
async def grp_autoapprove(bot, m: Message):
    userid = m.from_user.id if m.from_user else None
    grp_id = m.chat.id    
    okda = await bot.get_chat_member(grp_id, userid)
    if (
            okda.status != enums.ChatMemberStatus.ADMINISTRATOR
            and okda.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        await m.reply_text("<b>Yᴏᴜ Hᴀᴠᴇ Nᴏ Rɪɢʜᴛꜱ Tᴏ Dᴏ Tʜɪꜱ ❗️</b>")
        return
    db = Accept(m.chat.id)
    status = db.get_accept_status()    
    args = m.text.split(" ", 1)

    if m and not m.from_user:
        return

    if len(args) >= 2:
        if args[1].lower() == "noformat":
            return await m.reply_text(f"Current autoaccept settings:- {status}")
        if args[1].lower() == "on":
            db.set_current_accept_settings(True)
            await m.reply_text("Turned on!")
        
        if args[1].lower() == "off":
            db.set_current_accept_settings(False)
            await m.reply_text("Turned off!")
            return
        eeh = await m.reply_text("😁")       
        await eeh.delete()
        return       
    await m.reply_text(f"Current autoaccept settings:- {status}")

@bot.on_message(filters.command("autoaccept") & filters.channel)
async def on_autoapprove(bot, m: Message):
    userid = m.from_user.id if m.from_user else None
    grp_id = m.chat.id        
    db = Accept(m.chat.id)
    status = db.get_accept_status()    
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_current_accept_settings(True)
            await m.edit("Turned on!")
        
        if args[1].lower() == "off":
            db.set_current_accept_settings(False)
            await m.edit("Turned off!")
            return
        
