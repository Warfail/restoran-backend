from fastapi import APIRouter, Depends, HTTPException
from app.controllers.payment_controller import PaymentController
from app.config.database import get_db

router = APIRouter(prefix="/payment", tags=["Payment"])

def get_payment_controller(db=Depends(get_db)):
    return PaymentController(db)


@router.post("/")
async def process_payment(
    order_id: str,
    amount_paid: float,
    controller: PaymentController = Depends(get_payment_controller)
):
    result = await controller.process_payment(order_id, amount_paid)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result