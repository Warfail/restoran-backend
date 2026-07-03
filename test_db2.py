import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()
async def main():
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client.get_database("restoran")
    orders = await db.orders.find({"status": {"$in": ["pending", "paid"]}}).sort("createdAt", -1).to_list(10)
    for o in orders:
        print(f"ID: {o.get('orderId')}, Status: {o.get('status')}, PM: {o.get('paymentMethod')}, PS: {o.get('payment_status')}")

if __name__ == "__main__":
    asyncio.run(main())
