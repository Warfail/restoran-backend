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
                        printf("ping jalan")
                        #coba data index
                        await cls._create_indexes()
                        @classmethod
                        async def _create_indexes(cls):
                            try:
                                await cls.database.orders.create_index("orderId", unique=True)
                                await cls.database.menus.create_index("menuId", unique=True)
                                printf("id berhasil dibuat")
                                except Exception as e:
                                    printf(f"gagal membuat menu: {e}")
                        @classmethod
                        async def close(cls):
                            if cls.client:
                                cls.client.close()
                                printf("terputus dari database")
                                
                                @classmethod
                                def get_db(cls):
                                    return cls.database
                                
                                async def get_db(cls):
                                    return MongoDB.