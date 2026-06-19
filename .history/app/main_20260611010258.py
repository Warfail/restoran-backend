from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import json
from contextlib import asynccontextmanager
from app.config.database import MongoDB

# Custom JSON encoder untuk handle ObjectId
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await MongoDB.connect()
    print("🚀 Server ready!")
    yield
    await MongoDB.close()
    print("👋 Server shutdown")

app = FastAPI(lifespan=lifespan)

# Middleware untuk konversi ObjectId di semua response
@app.middleware("http")
async def convert_objectid_middleware(request, call_next):
    response = await call_next(request)
    return response

# Override jsonable_encoder untuk handle ObjectId
def custom_jsonable_encoder(obj, *args, **kwargs):
    return jsonable_encoder(obj, custom_encoder={ObjectId: str}, *args, **kwargs)

# Patch jsonable_encoder (optional, biar global)
import fastapi.encoders as encoders
encoders.jsonable_encoder = custom_jsonable_encoder

# Import routers
from app.boundaries import menu_boundary, order_boundary, cashier_boundary, kitchen_boundary

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