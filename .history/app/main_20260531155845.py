from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.database import MongoDB
from app.boundaries import menu_boundary, order_boundary, cashier_boundary, kitchen_boundary

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    print("🚀 Server ready!")
    yield
    await MongoDB.close()
    print("👋 Server shutdown")

app = FastAPI(lifespan=lifespan)

# Register all routers
app.include_router(menu_boundary.router)
app.include_router(order_boundary.router)
app.include_router(cashier_boundary.router)
app.include_router(kitchen_boundary.router)

@app.get("/")
async def root():
    return {"message": "Restoran API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "mockup connected"}