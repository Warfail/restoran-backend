from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

    class Settings(BaseSettings):
        MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        DATABASE_NAME: str = os.get