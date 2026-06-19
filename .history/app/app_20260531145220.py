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
    
    app = FastAPI(
        title="restoran api", 
        description="backend resto", 
        version="1.0.0", 
        lifespan=lifespan
        )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "welcome to restoran api"}
    
    @app.get("/health")
    async def health_check():
        try:
            await MongoDB.get_database().command("ping")
            return {"status": "healthy", "database"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}