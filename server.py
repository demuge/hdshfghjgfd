import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bot import start_bot, stop_bot


# =========================
# НАСТРОЙКИ
# =========================

PRICE_PER_STAR = 0.90


# =========================
# ДАННЫЕ ЗАКАЗОВ
# =========================

orders = {}


class OrderCreate(BaseModel):
    username: str
    stars: int


# =========================
# ЗАПУСК БОТА + СЕРВЕРА
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Telegram bot...")
    await start_bot()

    print("Server started")

    yield

    print("Stopping Telegram bot...")
    await stop_bot()


app = FastAPI(
    title="Telegram Stars Shop",
    lifespan=lifespan
)


# =========================
# ГЛАВНАЯ
# =========================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Telegram Stars Shop"
    }


# =========================
# HEALTH CHECK
# =========================

@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


# =========================
# СОЗДАНИЕ ЗАКАЗА
# =========================

@app.post("/api/order")
async def create_order(order: OrderCreate):

    username = order.username.strip().lstrip("@")

    if not username:
        raise HTTPException(
            status_code=400,
            detail="Username is required"
        )

    if order.stars < 1:
        raise HTTPException(
            status_code=400,
            detail="Stars must be greater than 0"
        )

    if order.stars > 1_000_000:
        raise HTTPException(
            status_code=400,
            detail="Too many Stars"
        )

    amount = round(order.stars * PRICE_PER_STAR, 2)

    order_id = str(uuid.uuid4())

    orders[order_id] = {
        "id": order_id,
        "username": username,
        "stars": order.stars,
        "amount": amount,
        "currency": "UAH",
        "status": "waiting_payment",
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    print(
        f"New order: {order_id} | "
        f"@{username} | "
        f"{order.stars} Stars | "
        f"{amount} UAH"
    )

    return {
        "success": True,
        "order_id": order_id,
        "username": username,
        "stars": order.stars,
        "amount": amount,
        "currency": "UAH",
        "status": "waiting_payment"
    }


# =========================
# ПОЛУЧИТЬ ЗАКАЗ
# =========================

@app.get("/api/order/{order_id}")
async def get_order(order_id: str):

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


# =========================
# ПРОВЕРКА ОПЛАТЫ
# =========================

@app.post("/api/order/{order_id}/check")
async def check_order(order_id: str):

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Пока реальная проверка оплаты НЕ подключена.
    # Поэтому здесь ничего не подтверждаем автоматически.

    return {
        "success": True,
        "paid": order["status"] == "paid",
        "status": order["status"],
        "order_id": order_id
    }


# =========================
# ОТМЕНА ЗАКАЗА
# =========================

@app.post("/api/order/{order_id}/cancel")
async def cancel_order(order_id: str):

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    order["status"] = "cancelled"

    return {
        "success": True,
        "status": "cancelled",
        "order_id": order_id
    }
