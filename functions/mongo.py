import motor.motor_asyncio
import sys

class MongoDB:
    def __init__(self):
        self.uri = ""
        self.client = None
        self.db = None
        
    async def connect_mongo(self):
        if not self.uri:
            print("⚠️ [Database] URI do MongoDB vazia, pulando conexão")
            return False
        
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.uri)
            await self.client.server_info()
            self.db = self.client.get_database("hakari_db")
            print("🍃 [Database] Conectado ao MongoDB com sucesso!")
            return True
        except Exception as err:
            print(f"❌ [Database] Erro ao conectar ao MongoDB: {err}")
            return False
    
    def get_collection(self, collection_name: str):
        if not self.db:
            raise Exception("Database não conectado. Chame connect_mongo() primeiro.")
        return self.db[collection_name]
    
    async def close(self):
        if self.client:
            self.client.close()
            print("🔌 [Database] Conexão com MongoDB encerrada.")

mongo = MongoDB()

async def connect_mongo():
    return await mongo.connect_mongo()