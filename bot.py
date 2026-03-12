import logging
import os

import pyrogram

from sample_config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)

    plugins = {"root": "plugins"}
    app = pyrogram.Client(
        "AshKetchumBot",
        bot_token=Config.TG_BOT_TOKEN,
        api_id=Config.APP_ID,
        api_hash=Config.API_HASH,
        plugins=plugins,
    )

    if Config.OWNER_ID:
        Config.AUTH_USERS.add(Config.OWNER_ID)

    logger.info("Starting bot with %s plugins", plugins["root"])
    app.run()
