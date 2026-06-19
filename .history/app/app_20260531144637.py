from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import MongoDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    #tes 