import os
import re
from typing import Optional

from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sample_config import Config

SAFE_FILE_RE = re.compile(r"[^A-Za-z0-9._()\-\[\] ]+")


def sanitize_filename(name: str) -> str:
    clean = os.path.basename(name.strip())
    clean = SAFE_FILE_RE.sub("_", clean)
    return clean[:128]


async def enforce_subscription(bot, message) -> bool:
    if not Config.UPDATE_CHANNEL:
        return True
    try:
        user = await bot.get_chat_member(Config.UPDATE_CHANNEL, message.from_user.id)
        if user.status == "kicked":
            await message.reply_text("Sorry, you are banned from updates channel usage.")
            return False
        return True
    except UserNotParticipant:
        await message.reply_text(
            text="Please join our updates channel first.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{Config.UPDATE_CHANNEL}")]]
            ),
        )
        return False


def user_is_banned(user_id: int) -> bool:
    return user_id in Config.BANNED_USERS


def get_user_thumb_path(user_id: int) -> str:
    return f"{Config.DOWNLOAD_LOCATION}/{user_id}.jpg"
