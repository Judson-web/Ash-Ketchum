import logging
import os
import random
import time

import pyrogram
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram import Client as Mai_bOTs

from helper_funcs.bot_helpers import enforce_subscription, get_user_thumb_path, user_is_banned
from helper_funcs.display_progress import progress_for_pyrogram
from helper_funcs.help_Nekmo_ffmpeg import take_screen_shot
from sample_config import Config
from translation import Translation

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@Mai_bOTs.on_message(pyrogram.filters.command(["c2v"]))
async def convert_to_video(bot, update):
    if user_is_banned(update.from_user.id):
        await update.reply_text("You are banned from using this bot.")
        return
    if not await enforce_subscription(bot, update):
        return
    if update.reply_to_message is None:
        await update.reply_text(Translation.REPLY_TO_FILE_FOR_CONVERT)
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

    width, height, duration = 0, 0, 0
    metadata = extractMetadata(createParser(downloaded))
    if metadata and metadata.has("duration"):
        duration = metadata.get("duration").seconds

    thumb_image_path = get_user_thumb_path(update.from_user.id)
    remove_thumb_after = False
    if not os.path.exists(thumb_image_path):
        try:
            second = random.randint(0, max(0, duration - 1))
            thumb_image_path = await take_screen_shot(downloaded, os.path.dirname(downloaded), second)
            remove_thumb_after = True
        except Exception:
            logger.exception("Failed generating thumbnail; continuing without thumb")
            thumb_image_path = None

    if thumb_image_path and os.path.exists(thumb_image_path):
        meta = extractMetadata(createParser(thumb_image_path))
        if meta and meta.has("width"):
            width = meta.get("width")
        if meta and meta.has("height"):
            height = meta.get("height")
        img = Image.open(thumb_image_path).convert("RGB")
        img = img.resize((320, 320))
        img.save(thumb_image_path, "JPEG")

    c_time = time.time()
    await bot.send_video(
        chat_id=update.chat.id,
        video=downloaded,
        duration=duration,
        width=width,
        height=height,
        supports_streaming=True,
        thumb=thumb_image_path,
        reply_to_message_id=update.reply_to_message.message_id,
        progress=progress_for_pyrogram,
        progress_args=(Translation.UPLOAD_START, status, c_time),
    )

    for path in [downloaded, thumb_image_path if remove_thumb_after else None]:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    await status.edit_text(Translation.AFTER_SUCCESSFUL_UPLOAD_MSG)
