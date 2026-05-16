import json
from pathlib import Path

try:
    from motor.motor_asyncio import AsyncIOMotorClient
except Exception:
    AsyncIOMotorClient = None

CONFIG_PATH = Path('config.json')
SETTINGS_PATH = Path('storage/settings.json')

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

DEFAULT_SETTINGS = {
    'mistral_api_key': '',
    'prompt': '',
    'model': 'mistral-medium-latest',
    'mode': 'mention',
    'channel_id': '',
    'mention_target_id': ''
}


class Settings:
    def __init__(self):
        self.mongo = None
        uri = CONFIG.get('mongodb_uri')
        if uri and AsyncIOMotorClient:
            self.mongo = AsyncIOMotorClient(uri).base_py
        SETTINGS_PATH.parent.mkdir(exist_ok=True)
        if not SETTINGS_PATH.exists():
            SETTINGS_PATH.write_text(json.dumps(DEFAULT_SETTINGS, indent=4, ensure_ascii=False), encoding='utf-8')

    async def get(self):
        if self.mongo:
            data = await self.mongo.settings.find_one({'_id': 'bot'})
            if data:
                data.pop('_id', None)
                merged = DEFAULT_SETTINGS.copy()
                merged.update(data)
                return merged
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding='utf-8'))
        except Exception:
            data = {}
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged

    async def update(self, data):
        current = await self.get()
        current.update(data)
        if self.mongo:
            await self.mongo.settings.update_one({'_id': 'bot'}, {'$set': current}, upsert=True)
        SETTINGS_PATH.write_text(json.dumps(current, indent=4, ensure_ascii=False), encoding='utf-8')
        return current

    async def reset(self):
        current = DEFAULT_SETTINGS.copy()
        if self.mongo:
            await self.mongo.settings.update_one({'_id': 'bot'}, {'$set': current}, upsert=True)
        SETTINGS_PATH.write_text(json.dumps(current, indent=4, ensure_ascii=False), encoding='utf-8')
        return current


settings = Settings()
