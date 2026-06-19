from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import MongoDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    #tes koneksi ke database
    await MongoDB.connect()
    print("server online")
    yield
    #tutup koneksi ke database
    await MongoDB.close()
    print("server offline")
    
    app = FastAPI(title="restoran api", 
                  version="1.0.0", 
                  lifespan=lifespan
                  )