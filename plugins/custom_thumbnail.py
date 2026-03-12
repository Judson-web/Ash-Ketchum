import logging
import os

from PIL import Image
from pyrogram import Client as MaI_BoTs, filters

import database.database as db
from helper_funcs.bot_helpers import get_user_thumb_path, user_is_banned
from sample_config import Config
from translation import Translation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@MaI_BoTs.on_message(filters.photo)
async def save_photo(bot, update):
    if user_is_banned(update.from_user.id):
        await bot.delete_messages(chat_id=update.chat.id, message_ids=update.message_id, revoke=True)
        return

    thumb_image_path = get_user_thumb_path(update.from_user.id)
    await db.df_thumb(update.from_user.id, update.message_id)
    await bot.download_media(message=update, file_name=thumb_image_path)

    try:
        img = Image.open(thumb_image_path).convert("RGB")
        img = img.resize((320, 320))
        img.save(thumb_image_path, "JPEG")
    except Exception:
        logger.exception("Failed to normalize thumbnail image")

    await bot.send_message(update.chat.id, Translation.SAVED_CUSTOM_THUMB_NAIL, reply_to_message_id=update.message_id)


@MaI_BoTs.on_message(filters.command(["delthumb"]))
async def delete_thumbnail(bot, update):
    if user_is_banned(update.from_user.id):
        await bot.delete_messages(chat_id=update.chat.id, message_ids=update.message_id, revoke=True)
        return

    thumb_image_path = get_user_thumb_path(update.from_user.id)
    await db.del_thumb(update.from_user.id)

    if os.path.exists(thumb_image_path):
        try:
            os.remove(thumb_image_path)
        except OSError:
            pass

    await bot.send_message(update.chat.id, Translation.DEL_ETED_CUSTOM_THUMB_NAIL, reply_to_message_id=update.message_id)


@MaI_BoTs.on_message(filters.command(["showthumb"]))
async def show_thumb(bot, update):
    if user_is_banned(update.from_user.id):
        await bot.delete_messages(chat_id=update.chat.id, message_ids=update.message_id, revoke=True)
        return

    thumb_image_path = get_user_thumb_path(update.from_user.id)
    if not os.path.exists(thumb_image_path):
        record = await db.thumb(update.from_user.id)
        if record:
            try:
                msg = await bot.get_messages(update.chat.id, record.msg_id)
                await msg.download(file_name=thumb_image_path)
            except Exception:
                logger.exception("Unable to restore thumbnail from message")

    if os.path.exists(thumb_image_path):
        await bot.send_photo(update.chat.id, thumb_image_path, reply_to_message_id=update.message_id)
    else:
        await bot.send_message(update.chat.id, Translation.NO_THUMB_FOUND, reply_to_message_id=update.message_id)
