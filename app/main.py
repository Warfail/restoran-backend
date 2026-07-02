from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.database import MongoDB
from app.boundaries import cashier_boundary, kitchen_boundary
from app.routes import order_routes
from app.routes import menu_routes
from app.routes import inventory_routes
from app.routes import kitchen_routes
from app.routes import user_routes
from app.routes import auth_routes
from app.routes import payment_routes
from app.routes import stock_log_routes
from app.routes import stock_stats_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    print("[OK] Server ready!")
    yield
    await MongoDB.close()
    print("[OK] Server shutdown")

app = FastAPI(lifespan=lifespan, redirect_slashes=False)  # ← TAMBAHKAN INI

# CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://restoran-frontend-nu.vercel.app",  # Domain Vercel
        "http://localhost:5173",  # Untuk development lokal
        "https://restoran-frontend-warfails-projects.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "*"  # BUAT TESTING
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router
app.include_router(cashier_boundary.router)
app.include_router(kitchen_boundary.router)
app.include_router(order_routes.router)
app.include_router(menu_routes.router)
app.include_router(inventory_routes.router)
app.include_router(kitchen_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(payment_routes.router)
app.include_router(stock_log_routes.router)
app.include_router(stock_stats_routes.router) 

@app.get("/")
async def root():
    return {"message": "Restoran API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "MongoDB connected"}