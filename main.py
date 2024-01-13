# (c) @AbirHasan2005

import os
import random
import logging
import aiohttp
import asyncio
from configs import Config
from pyrogram import Client, filters
from pyrogram.errors import UserNotParticipant
from helpers.captcha import make_captcha
from helpers.generate_id import generate_rnd_id
from helpers.markup_maker import make_captcha_markup
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery, ChatPermissions

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("log.txt")],
)

CaptchaBot = Client(
    Config.SESSION_NAME,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)
CaptchaDB = {}


@CaptchaBot.on_message(filters.command("start"))
async def start_handler(_, event: Message):
    await event.reply_text("Hi, I am captcha bot by @AbirHasan2005.")


@CaptchaBot.on_chat_member_updated()
async def welcome_handler(bot: Client, event: Message):
    if (event.chat.id != Config.GROUP_CHAT_ID) or (event.from_user.is_bot is True):
        return
    try:
        user_ = await bot.get_chat_member(event.chat.id, event.from_user.id)
        if (user_.is_member is False) and (CaptchaDB.get(event.from_user.id, None) is not None):
            try:
                await bot.delete_messages(
                    chat_id=event.chat.id,
                    message_ids=CaptchaDB[event.from_user.id]["message_id"]
                )
            except:
                pass
            return
        elif (user_.is_member is False) and (CaptchaDB.get(event.from_user.id, None) is None):
            return
    except UserNotParticipant:
        return
    try:
        if CaptchaDB.get(event.from_user.id, None) is not None:
            try:
                await bot.send_message(
                    chat_id=event.chat.id,
                    text=f"{event.from_user.mention} again joined group without verifying!\n\n"
                         f"He can try again after 10 minutes.",
                    disable_web_page_preview=True
                )
                await bot.restrict_chat_member(
                    chat_id=event.chat.id,
                    user_id=event.from_user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                await bot.delete_messages(chat_id=event.chat.id,
                                          message_ids=CaptchaDB[event.from_user.id]["message_id"])
            except:
                pass
            await asyncio.sleep(600)
            del CaptchaDB[event.from_user.id]
        else:
            await bot.restrict_chat_member(
                chat_id=event.chat.id,
                user_id=event.from_user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await bot.send_message(
                chat_id=event.chat.id,
                text=f"{event.from_user.mention}, to chat here, please verify that you are not a robot.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Verify Now", callback_data=f"startVerify_{str(event.from_user.id)}")]
                ])
            )
    except:
        pass


@CaptchaBot.on_callback_query()
async def buttons_handlers(bot: Client, cb: CallbackQuery):
    if cb.data.startswith("startVerify_"):
        __user = cb.data.split("_", 1)[-1]
        if cb.from_user.id != int(__user):
            await cb.answer("This Message is Not For You!", show_alert=True)
            return
        await cb.message.edit("Generating Captcha ...")
        print("Fetching Captcha ...")
        data, emoji_path_ = make_captcha(generate_rnd_id())
        print("Done!")
        markup = [[], [], []]
        __emojis = data.split(": ", 1)[-1].split()
        print(__emojis)
        _emojis = ['🐻', '🐔', '☁️', '🔮', '🌀', '🌚', '💎', '🐶', '🍩', '🌏', '🐸', '🌕', '🍏', '🐵', '🌙',
                   '🐧', '🍎', '😀', '🐍', '❄️', '🐚', '🐢', '🌝', '🍺', '🍔', '🍒', '🍫', '🍡', '🌑', '🍟',
                   '☕️', '🍑', '🍷', '🍧', '🍕', '🍵', '🐋', '🐱', '💄', '👠', '💰', '💸', '🎹', '📦', '📍',
                   '🐊', '🦕', '🐬', '💋', '🦎', '🦈', '🦷', '🦖', '🐠', '🐟','💀', '🎃', '👮', '⛑', '🪢', '🧶',
                   '🧵', '🪡', '🧥', '🥼', '🥻', '🎩', '👑', '🎒', '🙊', '🐗', '🦋', '🦐', '🐀', '🐿', '🦔', '🦦', 
                   '🦫', '🦡', '🦨', '🐇']
        random.shuffle(_emojis)
        _emojis = _emojis[:20]
        print("Cleaning Answer Emojis from Emojis List ...")
        for a in range(len(__emojis)):
            if __emojis[a] in _emojis:
                _emojis.remove(__emojis[a])
        show = __emojis
        print("Appending New Emoji List ...")
        for b in range(9):
            show.append(_emojis[b])
        print("Randomizing ...")
        random.shuffle(show)
        count = 0
        print("Appending to ROW - 1")
        for _ in range(5):
            markup[0].append(InlineKeyboardButton(f"{show[count]}",
                                                  callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
            count += 1
        print("Appending to ROW - 2")
        for _ in range(5):
            markup[1].append(InlineKeyboardButton(f"{show[count]}",
                                                  callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
            count += 1
        print("Appending to ROW - 3")
        for _ in range(5):
            markup[2].append(InlineKeyboardButton(f"{show[count]}",
                                                  callback_data=f"verify_{str(cb.from_user.id)}_{show[count]}"))
            count += 1
        print("Setting Up in Database ...")
        CaptchaDB[cb.from_user.id] = {
            "emojis": data.split(": ", 1)[-1].split(),
            "mistakes": 0,
            "group_id": cb.message.chat.id,
            "message_id": None
        }
        print("Sending Captcha ...")
        __message = await bot.send_photo(
            chat_id=cb.message.chat.id,
            photo=emoji_path_,
            caption=f"{cb.from_user.mention}, select all the emojis you can see in the picture. "
                    f"You are allowed only (3) mistakes.",
            reply_markup=InlineKeyboardMarkup(markup)
        )
        os.remove(emoji_path_)
        CaptchaDB[cb.from_user.id]["message_id"] = __message.id
        await cb.message.delete(revoke=True)

    elif cb.data.startswith("verify_"):
        __emoji = cb.data.rsplit("_", 1)[-1]
        __user = cb.data.split("_")[1]
        if cb.from_user.id != int(__user):
            await cb.answer("This Message is Not For You!", show_alert=True)
            return
        if cb.from_user.id not in CaptchaDB:
            await cb.answer("Try Again After Re-Join!", show_alert=True)
            await cb.message.delete()
        if __emoji not in CaptchaDB.get(cb.from_user.id).get("emojis"):
            CaptchaDB[cb.from_user.id]["mistakes"] += 1
            await cb.answer("You pressed wrong emoji!", show_alert=True)
            n = 3 - CaptchaDB[cb.from_user.id]['mistakes']
            if n == 0:
                await cb.message.delete(True)
                await bot.send_message(
                    chat_id=cb.message.chat.id,
                    text=f"{cb.from_user.mention}, you failed to solve the captcha!\n\n"
                         f"You can try again after 10 minutes."
                )
                await asyncio.sleep(600)
                del CaptchaDB[cb.from_user.id]
                return
            markup = make_captcha_markup(cb.message.reply_markup.inline_keyboard, __emoji, "❌")
            await cb.message.edit_caption(
                caption=f"{cb.from_user.mention}, select all the emojis you can see in the picture. "
                        f"You are allowed only ({n}) mistakes.",
                reply_markup=InlineKeyboardMarkup(markup)
            )
            return
        else:
            CaptchaDB.get(cb.from_user.id).get("emojis").remove(__emoji)
            markup = make_captcha_markup(cb.message.reply_markup.inline_keyboard, __emoji, "✅")
            await cb.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(markup))
            if not CaptchaDB.get(cb.from_user.id).get("emojis"):
                await cb.answer("You Passed the Captcha!", show_alert=True)
                del CaptchaDB[cb.from_user.id]
                try:
                    UserOnChat = await bot.get_chat_member(user_id=cb.from_user.id, chat_id=cb.message.chat.id)
                    if UserOnChat.restricted_by.id == (await bot.get_me()).id:
                        await bot.unban_chat_member(chat_id=cb.message.chat.id, user_id=cb.from_user.id)
                except:
                    pass
                await cb.message.delete(True)
            await cb.answer()


CaptchaBot.run()
