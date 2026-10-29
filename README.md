# Apex Spam X

Telegram multi-client bot — Termux se push, Heroku pe host.
MongoDB-backed sudo, inline ping/help UI, 8 raid commands + utilities.

## Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/oyevipthoma88/Apex_spam_X)

After the app is created, open **Resources** and turn **worker** dyno ON.

## Required Config Vars

`API_ID`, `API_HASH`, `OWNER_ID`, `MONGO_DB_URI`, `BOT_TOKEN1`
Optional: `BOT_TOKEN2`, `BOT_TOKEN3`, `CMD_HNDLR=.`

## Commands

- `.ping` — latency + uptime (inline refresh)
- `.help` — category menu
- `.addsudo` / `.delsudo` / `.listsudo` — Mongo sudo
- `.raid` `.mraid` `.sraid` `.craid` `.qraid` `.loveraid` `.hrraid` `.shayriraid` `<count> <user|reply>`
- `.spam` `.echo` `.emoji` `.purge` `.tagall` `.kick` `.gcast`
