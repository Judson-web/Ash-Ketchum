import logging
import os
import time

import pyrogram
from pyrogram import Client as Mai_bOTs
from PIL import Image

from database.database import thumb
from helper_funcs.bot_helpers import enforce_subscription, get_user_thumb_path, sanitize_filename, user_is_banned
from helper_funcs.display_progress import progress_for_pyrogram
from sample_config import Config
from translation import Translation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@Mai_bOTs.on_message(pyrogram.filters.command(["rename"]))
async def rename_doc(bot, update):
    if user_is_banned(update.from_user.id):
        await update.reply_text("You are banned from using this bot.")
        return
    if not await enforce_subscription(bot, update):
        return

    if not ((" " in update.text) and update.reply_to_message):
        await update.reply_text(Translation.REPLY_TO_DOC_FOR_RENAME_FILE)
        return

    _, requested_name = update.text.split(" ", 1)
    file_name = sanitize_filename(requested_name)
    if not file_name:
        await update.reply_text(Translation.INVALID_FILE_NAME)
        return
    if len(file_name) > 128:
        await update.reply_text(Translation.IFLONG_FILE_NAME)
        return

    status = await bot.send_message(update.chat.id, Translation.DOWNLOAD_START, reply_to_message_id=update.message_id)
    c_time = time.time()
    downloaded = await bot.download_media(
        message=update.reply_to_message,
        file_name=f"{Config.DOWNLOAD_LOCATION}/",
        progress=progress_for_pyrogram,
        progress_args=(Translation.DOWNLOAD_START, status, c_time),
    )

    if not downloaded:
        await status.edit_text("Download failed.")
        return

    await status.edit_text(Translation.SAVED_RECVD_DOC_FILE)
    renamed = f"{Config.DOWNLOAD_LOCATION}/{file_name}"
    os.replace(downloaded, renamed)

    thumb_image_path = get_user_thumb_path(update.from_user.id)
    remove_thumb_after = False
    if not os.path.exists(thumb_image_path):
        tdoc = await thumb(update.from_user.id)
        if tdoc:
            try:
                m = await bot.get_messages(update.chat.id, tdoc.msg_id)
                await m.download(file_name=thumb_image_path)
                remove_thumb_after = True
            except Exception:
                logger.exception("Failed to download stored thumbnail")
                thumb_image_path = None
        else:
            thumb_image_path = None

    if thumb_image_path and os.path.exists(thumb_image_path):
        try:
            img = Image.open(thumb_image_path).convert("RGB")
            img = img.resize((320, 320))
            img.save(thumb_image_path, "JPEG")
        except Exception:
            logger.exception("Failed to process thumbnail")
            thumb_image_path = None

    c_time = time.time()
    await bot.send_document(
        chat_id=update.chat.id,
        document=renamed,
        thumb=thumb_image_path,
        caption=f"<b>{file_name}</b>",
        reply_to_message_id=update.reply_to_message.message_id,
        progress=progress_for_pyrogram,
        progress_args=(Translation.UPLOAD_START, status, c_time),
    )

    try:
        os.remove(renamed)
    except OSError:
        pass
    if remove_thumb_after and thumb_image_path and os.path.exists(thumb_image_path):
        try:
            os.remove(thumb_image_path)
        except OSError:
            pass

    await status.edit_text(Translation.AFTER_SUCCESSFUL_UPLOAD_MSG)
