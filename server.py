from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone
from typing import Optional


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Telegram Stars Shop",
    version="1.0.0",
)


# =========================================================
# НАСТРОЙКИ
# =========================================================

PRICE_PER_STAR = 0.90

MIN_STARS = 1
MAX_STARS = 1_000_000


# =========================================================
# ВРЕМЕННОЕ ХРАНИЛИЩЕ
# =========================================================

orders = {}


# =========================================================
# МОДЕЛИ
# =========================================================

class CreateOrderRequest(BaseModel):

    telegram_id: int

    username: Optional[str] = None

    stars: int = Field(
        ge=MIN_STARS,
        le=MAX_STARS
    )


class OrderResponse(BaseModel):

    order_id: str

    telegram_id: int

    username: Optional[str]

    stars: int

    amount_uah: float

    status: str

    created_at: str


# =========================================================
# ГЛАВНАЯ
# =========================================================

@app.get("/")
async def root():

    return {
        "success": True,
        "service": "Telegram Stars Shop",
        "status": "online",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
async def health():

    return {
        "status": "ok"
    }


# =========================================================
# СОЗДАНИЕ ЗАКАЗА
# =========================================================

@app.post(
    "/api/order",
    response_model=OrderResponse
)
async def create_order(
    data: CreateOrderRequest
):

    amount_uah = round(
        data.stars * PRICE_PER_STAR,
        2
    )

    order_id = str(uuid4())

    created_at = datetime.now(
        timezone.utc
    ).isoformat()

    order = {
        "order_id": order_id,
        "telegram_id": data.telegram_id,
        "username": data.username,
        "stars": data.stars,
        "amount_uah": amount_uah,
        "status": "waiting_payment",
        "created_at": created_at,
    }

    orders[order_id] = order

    return order


# =========================================================
# ПОЛУЧЕНИЕ ЗАКАЗА
# =========================================================

@app.get(
    "/api/order/{order_id}",
    response_model=OrderResponse
)
async def get_order(order_id: str):

    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден."
        )

    return order


# =========================================================
# ПРОВЕРКА ОПЛАТЫ
# =========================================================

@app.post(
    "/api/order/{order_id}/check"
)
async def check_payment(order_id: str):

    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден."
        )

    # =====================================================
    # ВАЖНО:
    # Здесь пока НЕТ фальшивого подтверждения оплаты.
    #
    # Следующим этапом сюда подключим реальный
    # платёжный провайдер и проверку конкретного заказа.
    # =====================================================

    return {
        "success": True,
        "order_id": order_id,
        "status": order["status"],
        "paid": False,
        "message": "Платёж ещё не подтверждён.",
    }


# =========================================================
# ОТМЕНА ЗАКАЗА
# =========================================================

@app.post(
    "/api/order/{order_id}/cancel"
)
async def cancel_order(order_id: str):

    order = orders.get(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Заказ не найден."
        )

    if order["status"] != "waiting_payment":

        return {
            "success": False,
            "message": "Этот заказ уже нельзя отменить.",
        }

    order["status"] = "cancelled"

    return {
        "success": True,
        "order_id": order_id,
        "status": "cancelled",
    }
