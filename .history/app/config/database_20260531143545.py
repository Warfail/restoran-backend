from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()
class Settings(BaseSettings):
        MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        DATABASE_NAME: str = os.getenv("DATABASE_NAME", "restoran")
        
        class Config:
            env_file = ".env"
            
            settings = Settings()
            
            class MongoDB:
                client: AsyncIOMotorClient = None
                database = None
                
                @classmethod
                async def connect(cls):
                    if cls.client is None:
                        #koneksi ke db
                        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
                        cls.database = cls.client[settings.DATABASE_NAME]
                        printf("tersambung ke database: {settings.DATABASE_NAME}")
                        
                        #conn test
                        await cls.database.command("ping")
                        p
            