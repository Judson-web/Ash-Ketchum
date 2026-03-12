## Ash-Ketchum Telegram Bot (Refreshed)

A modernized Pyrogram Telegram bot for:
- ✅ Renaming Telegram files
- ✅ Converting files to streamable video (`/c2v`)
- ✅ Persistent custom thumbnail storage using **Firebase Firestore**
- ✅ Utility commands: `/ping`, `/stats`

---

## What's new in this update

- Migrated thumbnail persistence from SQLAlchemy/Postgres to **Firebase Firestore**.
- Improved filename safety with sanitization in `/rename`.
- Improved thumbnail processing and cleanup behavior.
- Added `/ping` (latency) and `/stats` (uptime/temp file count).
- Updated deployment metadata and removed old Heroku Postgres dependency.

---

## Environment Variables

Required:
- `TG_BOT_TOKEN`
- `APP_ID`
- `API_HASH`

Optional:
- `UPDATE_CHANNEL`
- `AUTH_USERS` (space-separated IDs)
- `BANNED_USERS` (space-separated IDs)
- `OWNER_ID`
- `SUPPORT_LINK`
- `UPDATES_LINK`
- `DOWNLOAD_LOCATION`

Firebase (for persistent thumbnails):
- `FIREBASE_PROJECT_ID`
- `FIREBASE_CREDENTIALS_PATH` **or** `FIREBASE_CREDENTIALS_JSON`

If Firebase credentials are not set, bot falls back to in-memory thumbnail mapping.

---

## Run locally

```bash
pip install -r requirements.txt
python3 bot.py
```

---

## Deploy

### Heroku (updated)
- Worker dyno uses `python3 bot.py`
- No Postgres addon required anymore
- Set Firebase credentials through config vars

### Docker
```bash
docker build -t ash-ketchum .
docker run --env-file .env ash-ketchum
```
