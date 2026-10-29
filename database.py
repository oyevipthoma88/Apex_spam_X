import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DB_URI = os.getenv("MONGO_DB_URI", "").strip()
if not MONGO_DB_URI:
    raise SystemExit("[!] MONGO_DB_URI missing")

mongo_client = AsyncIOMotorClient(MONGO_DB_URI)
db = mongo_client["apex_spam"]
