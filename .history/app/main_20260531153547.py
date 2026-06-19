from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import MongoDB
from app.boundaries.menu_boundary import router as menu_

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await MongoDB.connect()
    print("🚀 Server ready!")
    yield
    # Shutdown
    await MongoDB.close()
    print("👋 Server shutdown")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Restoran API is running"}

@app.get("/health")
async def health():
    try:
        # Cek kalo database mockup ada datanya (misal menu)
        db = MongoDB.get_db()
        if db and "menus" in db:
            return {"status": "healthy", "database": "connected (mockup)"}
        else:
            return {"status": "unhealthy", "database": "mockup not ready"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}