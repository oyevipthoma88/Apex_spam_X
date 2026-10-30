"""Apex Spam X — central rate-limited sender (Telegram-safe).

Official limits (2026):
- ~30 req/sec globally per bot
- 1 msg/sec per chat
- 20 msg/min per group  ← critical
"""
import asyncio
import logging
import time

from telethon.errors import (
    ChatWriteForbiddenError,
    FloodWaitError,
    SlowModeWaitError,
)

log = logging.getLogger("ApexSpam.sender")

GROUP_GAP = 3.2   # 18.75/min, under 20/min group cap
DM_GAP = 1.15     # 1/sec + safety
BOT_GAP = 0.05    # 20/sec, under 30/sec global

_chat_locks = {}
_chat_next = {}
_bot_next = {}
_bot_paused = {}
_registry = asyncio.Lock()


async def _lock(cid):
    async with _registry:
        if cid not in _chat_locks:
            _chat_locks[cid] = asyncio.Lock()
        return _chat_locks[cid]


def _paused(client):
    return time.time() < _bot_paused.get(id(client), 0)


def stats():
    now = time.time()
    return {
        "paused": sum(1 for t in _bot_paused.values() if t > now),
        "chats": len(_chat_locks),
    }


async def send(client, chat_id, text, is_private=False, **kw):
    if _paused(client):
        log.debug(f"bot {id(client)} paused")
        return False
    cid = chat_id
    gap = DM_GAP if is_private else GROUP_GAP
    lk = await _lock(cid)
    async with lk:
        now = time.time()
        bw = _bot_next.get(id(client), 0) - now
        if bw > 0:
            await asyncio.sleep(bw)
        now = time.time()
        cw = _chat_next.get(cid, 0) - now
        if cw > 0:
            await asyncio.sleep(cw)
        try:
            await client.send_message(chat_id, text, **kw)
            _bot_next[id(client)] = time.time() + BOT_GAP
            _chat_next[cid] = time.time() + gap
            return True
        except FloodWaitError as fe:
            wait = fe.seconds + 1
            if wait >= 30:
                _bot_paused[id(client)] = time.time() + wait
                log.warning(f"bot {id(client)} paused {wait}s (heavy flood)")
            else:
                await asyncio.sleep(wait)
                _chat_next[cid] = time.time() + max(gap, wait)
            return False
        except (ChatWriteForbiddenError, SlowModeWaitError) as e:
            log.warning(f"blocked: {e}")
            return False
        except Exception as e:
            log.warning(f"send fail {type(e).__name__}: {e}")
            return False


async def send_file(client, chat_id, file, is_private=False, **kw):
    if _paused(client):
        return False
    cid = chat_id
    gap = DM_GAP if is_private else GROUP_GAP
    lk = await _lock(cid)
    async with lk:
        now = time.time()
        cw = _chat_next.get(cid, 0) - now
        if cw > 0:
            await asyncio.sleep(cw)
        try:
            await client.send_file(chat_id, file, **kw)
            _chat_next[cid] = time.time() + gap
            return True
        except FloodWaitError as fe:
            wait = fe.seconds + 1
            if wait >= 30:
                _bot_paused[id(client)] = time.time() + wait
            else:
                await asyncio.sleep(wait)
            return False
        except Exception as e:
            log.warning(f"file fail {type(e).__name__}: {e}")
            return False


def reset():
    _chat_locks.clear()
    _chat_next.clear()
    _bot_next.clear()
    _bot_paused.clear()
