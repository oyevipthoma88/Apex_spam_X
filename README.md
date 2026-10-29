# ⚡ Apex Spam X

> Powerful Telegram multi-client raid & spam engine — Mongo sudo, Heroku ready.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/oyevipthoma88/Apex_spam_X)

## Features
- ⚡ 10 parallel Telegram clients
- 🔐 MongoDB-backed dynamic sudo (`.addsudo`)
- 🛠️ 15+ raid commands (`.raid`, `.sraid`, `.loveraid`, …)
- 💬 Mass spam / echo / emoji / tagall / gcast
- 🎨 Premium inline UI (cards, dividers, buttons)
- 📊 Live stats, logs, Heroku restart

## Required Config Vars
| Key | Description |
|---|---|
| `API_ID` | Telegram API ID |
| `API_HASH` | Telegram API HASH |
| `OWNER_ID` | Your Telegram user ID |
| `MONGO_DB_URI` | MongoDB Atlas URI |
| `BOT_TOKEN1` | Bot token (from @BotFather) |

Optional: `BOT_TOKEN2…10`, `CMD_HNDLR=.`, `SUDO_USERS`, `HEROKU_APP_NAME`, `HEROKU_API_KEY`

## Deploy
1. Click **Deploy to Heroku** above
2. Fill config vars
3. **Resources** → turn `worker` dyno ON
4. DM your bot `/start`

## Prefix
`.help`, `.ping`, `.raid`, `.addsudo`

## Credits
**Developer:** [@oyevipthoma88](https://github.com/oyevipthoma88)
