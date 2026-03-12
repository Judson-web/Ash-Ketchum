import logging
import os
import time

import pyrogram
from pyrogram import Client as Mai_bOTs
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from sample_config import Config
from translation import Translation
from helper_funcs.bot_helpers import enforce_subscription, user_is_banned

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BOT_START_TIME = time.time()


def main_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Rename", callback_data="rnme"), InlineKeyboardButton("File -> Video", callback_data="f2v")],
            [InlineKeyboardButton("Thumbnail", callback_data="cthumb"), InlineKeyboardButton("About", callback_data="about")],
        ]
    )


@Mai_bOTs.on_message(pyrogram.filters.command(["start"]))
async def start_me(bot, update):
    if user_is_banned(update.from_user.id):
        await update.reply_text("You are banned from using this bot.")
        return
    if not await enforce_subscription(bot, update):
        return

    await update.reply_text(
        Translation.START_TEXT.format(update.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Help", callback_data="ghelp")],
                [InlineKeyboardButton("Updates", url=Config.UPDATES_LINK), InlineKeyboardButton("Support", url=Config.SUPPORT_LINK)],
            ]
        ),
        reply_to_message_id=update.message_id,
    )


@Mai_bOTs.on_message(pyrogram.filters.command(["help"]))
async def help_user(bot, update):
    if not await enforce_subscription(bot, update):
        return
    await update.reply_text(Translation.HELP_USER, reply_markup=main_keyboard())


@Mai_bOTs.on_message(pyrogram.filters.command(["ping"]))
async def ping(bot, update):
    start = time.time()
    msg = await update.reply_text("Pinging...")
    latency = (time.time() - start) * 1000
    await msg.edit_text(f"🏓 Pong: <code>{latency:.2f} ms</code>")


@Mai_bOTs.on_message(pyrogram.filters.command(["stats"]))
async def stats(bot, update):
    uptime = int(time.time() - BOT_START_TIME)
    files = 0
    for _, _, filenames in os.walk(Config.DOWNLOAD_LOCATION):
        files += len(filenames)
    await update.reply_text(f"Uptime: <code>{uptime}s</code>\nTemp files: <code>{files}</code>")


@Mai_bOTs.on_callback_query()
async def cb_handler(client: Mai_bOTs, query: CallbackQuery):
    data = query.data
    mapping = {
        "rnme": Translation.RENAME_HELP,
        "f2v": Translation.C2V_HELP,
        "cthumb": Translation.THUMBNAIL_HELP,
        "ghelp": Translation.HELP_USER,
        "about": Translation.ABOUT_ME,
    }
    if data == "close":
        await query.message.delete()
        return
    if data in mapping:
        await query.message.edit_text(
            text=mapping[data],
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Back", callback_data="ghelp"), InlineKeyboardButton("Close", callback_data="close")]]
            ),
        )
