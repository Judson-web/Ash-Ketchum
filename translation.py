class Translation(object):
    START_TEXT = (
        "<b>Hi {}, I am Ash Ketchum.</b>\n\n"
        "I can rename files, convert media to streamable video, and keep your custom thumbnail in Firebase.\n"
        "Use /help to see commands."
    )

    HELP_USER = (
        "<b>Available commands</b>\n\n"
        "/rename new_name.ext - reply to a file to rename it\n"
        "/c2v - reply to a file/video to convert it into streamable video\n"
        "/showthumb - view your saved thumbnail\n"
        "/delthumb - delete your saved thumbnail\n"
        "/ping - check bot latency\n"
        "/stats - runtime and storage stats"
    )

    DOWNLOAD_START = "<b>Downloading...</b>"
    UPLOAD_START = "<b>Uploading...</b>"
    SAVED_RECVD_DOC_FILE = "<b>Downloaded successfully. Preparing upload...</b>"
    AFTER_SUCCESSFUL_UPLOAD_MSG = "<b>Done ✅</b>"

    REPLY_TO_DOC_FOR_RENAME_FILE = "Reply to a file with: <code>/rename new_name.ext</code>"
    REPLY_TO_FILE_FOR_CONVERT = "Reply to a file with: <code>/c2v</code>"
    SAVED_CUSTOM_THUMB_NAIL = "Custom thumbnail saved ✅"
    DEL_ETED_CUSTOM_THUMB_NAIL = "Custom thumbnail deleted ✅"
    NO_THUMB_FOUND = "No thumbnail found. Send a photo to save one."
    IFLONG_FILE_NAME = "Filename too long. Maximum supported length is 128 chars."
    INVALID_FILE_NAME = "Invalid filename. Try a safer name like <code>movie.mkv</code>."

    RENAME_HELP = "Use /rename by replying to any file with the new filename."
    C2V_HELP = "Use /c2v by replying to a file/video."
    THUMBNAIL_HELP = "Send a photo to set thumbnail, /showthumb to view, /delthumb to remove."
    ABOUT_ME = "Ash Ketchum bot - refreshed build with Firebase thumbnail storage and improved reliability."
