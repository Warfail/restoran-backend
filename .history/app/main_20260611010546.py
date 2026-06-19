from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from bson import ObjectId
import json

from app.config.database import MongoDB
from app.boundaries import menu_boundary, order_boundary, cashier_boundary, kitchen_boundary


# Custom JSON encoder buat handle ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


# Fungsi buat convert response
def parse_json(data):
    return json.loads(json.dumps(data, cls=CustomJSONEncoder))


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
app.include_router(order_boundary.router)
app.include_router(cashier_boundary.router)
app.include_router(kitchen_boundary.router)


@app.get("/")
async def root():
    return {"message": "Restoran API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "database": "MongoDB connected"}