from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import uuid
from bson import ObjectId
from app.config.database import get_db
from app.utils import serialize_document, serialize_list, serialize_value

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/")
async def create_order(order_data: dict, db = Depends(get_db)):
    """
    Customer membuat pesanan baru dengan menuId
    """
    try:
        # Ambil data dari request
        customer_name = order_data.get("customerName", "Guest")
        table_number = order_data.get("tableNumber", 1)
        items = order_data.get("items", [])
        
        if not items:
            raise HTTPException(status_code=400, detail="Items is required")
        
        # Proses setiap item: cari menu berdasarkan menuId
        processed_items = []
        total_amount = 0
        
        for item in items:
            menu_id = item.get("menuId")
            quantity = item.get("quantity", 1)
            
            if not menu_id:
                raise HTTPException(status_code=400, detail="menuId is required for each item")
            
            # Cari menu di database
            from bson.errors import InvalidId
            try:
                query = {"$or": [{"_id": ObjectId(menu_id)}, {"menuId": menu_id}]}
            except InvalidId:
                query = {"$or": [{"menuId": menu_id}, {"kode": menu_id}, {"_id": menu_id}]}
                
            menu = await db.menus.find_one(query)
            if not menu:
                raise HTTPException(status_code=404, detail=f"Menu with ID {menu_id} not found")
            
            # Cek stok
            if menu.get("stock", 0) < quantity:
                raise HTTPException(status_code=400, detail=f"Stok {menu['name']} tidak cukup. Sisa: {menu['stock']}")
            
            # Hitung subtotal
            price = menu.get("price", 0)
            subtotal = price * quantity
            total_amount += subtotal
            
            processed_items.append({
                "menuId": menu_id,
                "name": menu.get("name"),
                "price": price,
                "quantity": quantity,
                "subtotal": subtotal
            })
        
        # Generate order ID
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Buat order baru
        new_order = {
            "orderId": order_id,
            "customerName": customer_name,
            "tableNumber": table_number,
            "orderType": order_data.get("orderType", "Makan di Tempat"),
            "items": processed_items,
            "totalAmount": total_amount,
            "status": "pending",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat()
        }
        
        result = await db.orders.insert_one(new_order)
        new_order["_id"] = str(result.inserted_id)
        
        return {
            "success": True, 
            "data": {
                "orderId": order_id,
                "status": "pending",
                "totalAmount": total_amount,
                "items": processed_items
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print("Error creating order:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}")
async def get_order(order_id: str, db = Depends(get_db)):
    """
    Customer cek status pesanan berdasarkan orderId
    """
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["_id"] = str(order["_id"])
    return {"success": True, "data": order}


@router.post("/payment")
async def process_payment(payment_data: dict, db = Depends(get_db)):
    """
    Customer melakukan pembayaran berdasarkan orderId
    """
    order_id = payment_data.get("orderId")
    if not order_id:
        raise HTTPException(status_code=400, detail="orderId is required")
    
    # Cek order
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Order already {order['status']}")
    
    # 🔥 1. UPDATE ORDERS
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {
            "status": "paid", 
            "paymentMethod": payment_data.get("method", "qris"),
            "updatedAt": datetime.now().isoformat()
        }}
    )
    
    # 🔥 2. UPDATE PAYMENTS (SINKRON!)
    await db.payments.update_one(
        {"orderId": order_id},
        {"$set": {
            "payment_status": "paid",
            "status": "paid",
            "payment_method": payment_data.get("method", "qris"),
            "updatedAt": datetime.now().isoformat()
        }},
        upsert=True
    )
    
    return {"success": True, "message": "Payment successful", "data": {"orderId": order_id, "status": "paid"}}

@router.put("/{order_id}/confirm-payment")
async def confirm_payment(order_id: str, db = Depends(get_db)):
    """
    Kasir konfirmasi pembayaran (pending → paid)
    """
    # Cek order
    order = await db.orders.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order["status"] != "pending":
        raise HTTPException(status_code=400, detail=f"Order already {order['status']}")
    
    # 🔥 1. UPDATE ORDERS
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"status": "paid", "updatedAt": datetime.now().isoformat()}}
    )
    
    # 🔥 2. UPDATE PAYMENTS (SINKRON!)
    await db.payments.update_one(
        {"orderId": order_id},
        {"$set": {
            "payment_status": "paid",
            "status": "paid",
            "payment_method": "cash",
            "updatedAt": datetime.now().isoformat()
        }},
        upsert=True  # Bikin dokumen baru kalo belum ada
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True, "message": "Payment confirmed", "data": {"orderId": order_id, "status": "paid"}}

@router.put("/{order_id}/payment-method")
async def update_payment_method(order_id: str, data: dict, db = Depends(get_db)):
    """
    Menyimpan metode pembayaran yang dipilih customer sebelum lunas
    """
    method = data.get("method")
    if not method:
        raise HTTPException(status_code=400, detail="method is required")
        
    result = await db.orders.update_one(
        {"orderId": order_id},
        {"$set": {"paymentMethod": method, "updatedAt": datetime.now().isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return {"success": True, "message": "Payment method updated", "paymentMethod": method}

