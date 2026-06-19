from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.database import MongoDB
from app.boundaries import menu_boundary, cashier_boundary, kitchen_boundary
from app.routes import order_routes
from app.routes import menu_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    print("🚀 Server ready!")
    yield
    await MongoDB.close()
    print("👋 Server shutdown")

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(menu_boundary.router)
app.include_router(cashier_boundary.router)
app.include_router(kitchen_boundary.router)
app.include_router(order_routes.router)  # Endpoint orders di sini
app.include_router(menu_routes.router)  # Endpoint menu di sini

@app.get("/")
async def root():
    return {"message": "Restoran API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "MongoDB connected"}