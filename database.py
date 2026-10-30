"""Apex Spam X — Mongo connection (never crashes the process)."""
import logging
import os

from motor.motor_asyncio import AsyncIOMotorClient

log = logging.getLogger("ApexSpam.db")

MONGO_DB_URI = (os.getenv("MONGO_DB_URI") or "").strip()

mongo_client = None
db = None

if MONGO_DB_URI:
    try:
        mongo_client = AsyncIOMotorClient(
            MONGO_DB_URI,
            serverSelectionTimeoutMS=8000,
            connectTimeoutMS=8000,
        )
        db = mongo_client["apex_spam"]
    except Exception as e:
        log.exception(f"mongo init failed: {e}")
else:
    log.error("MONGO_DB_URI missing — DB features disabled")
