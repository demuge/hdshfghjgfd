import logging
import os

import httpx

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ============================================================
# НАСТРОЙКИ
# ============================================================

BOT_TOKEN = "8746943590:AAHOgHklW3xHD6Xr7ghwqLtvveAANkmhCOw"

WEB_APP_URL = "https://demuge.github.io/qwet4wyh/"

# Когда разместим server.py на сервере,
# сюда поставим его настоящий HTTPS-адрес.
API_URL = "https://ТВОЙ-SERVER-АДРЕС"


# ============================================================
# ЛОГИ
# ============================================================

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# КЛАВИАТУРА
# ============================================================

def shop_keyboard():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⭐ Купить Stars",
                    web_app=WebAppInfo(
                        url=WEB_APP_URL
                    ),
                )
            ]
        ]
    )


# ============================================================
# /start
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    if not user:
        return

    username = (
        f"@{user.username}"
        if user.username
        else user.first_name
    )

    text = (
        "⭐ <b>Магазин Telegram Stars</b>\n\n"
        f"Привет, {username}!\n\n"
        "Здесь ты можешь выбрать нужное "
        "количество Stars и оформить заказ.\n\n"
        "Нажми кнопку ниже 👇"
    )

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=shop_keyboard(),
    )


# ============================================================
# /shop
# ============================================================

async def shop(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "⭐ Открывай магазин:",
        reply_markup=shop_keyboard(),
    )


# ============================================================
# /id
# ============================================================

async def user_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user = update.effective_user

    if not user:
        return

    await update.message.reply_text(
        f"🆔 Твой Telegram ID:\n\n"
        f"<code>{user.id}</code>",
        parse_mode="HTML",
    )


# ============================================================
# /status
# ============================================================

async def status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/status ORDER_ID"
        )
        return

    order_id = context.args[0]

    if API_URL.startswith("https://ТВОЙ"):
        await update.message.reply_text(
            "⚠️ Backend ещё не подключён."
        )
        return

    url = (
        f"{API_URL.rstrip('/')}"
        f"/api/order/{order_id}"
    )

    try:

        async with httpx.AsyncClient(
            timeout=10
        ) as client:

            response = await client.get(url)

        if response.status_code == 404:
            await update.message.reply_text(
                "❌ Заказ не найден."
            )
            return

        if response.status_code != 200:
            await update.message.reply_text(
                "⚠️ Не удалось получить статус заказа."
            )
            return

        data = response.json()

        stars = data.get("stars", 0)
        amount = data.get("amount_uah", 0)
        order_status = data.get(
            "status",
            "unknown"
        )

        await update.message.reply_text(
            "📦 <b>Заказ</b>\n\n"
            f"ID: <code>{order_id}</code>\n"
            f"⭐ Stars: <b>{stars}</b>\n"
            f"💰 Сумма: <b>{amount} грн</b>\n"
            f"📌 Статус: <b>{order_status}</b>",
            parse_mode="HTML",
        )

    except Exception:

        logger.exception(
            "Ошибка получения заказа"
        )

        await update.message.reply_text(
            "❌ Backend сейчас недоступен."
        )


# ============================================================
# НЕИЗВЕСТНЫЕ КОМАНДЫ
# ============================================================

async def unknown_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    await update.message.reply_text(
        "❓ Неизвестная команда.\n\n"
        "Используй /start."
    )


# ============================================================
# ОШИБКИ
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

    logger.error(
        "Ошибка Telegram:",
        exc_info=context.error,
    )


# ============================================================
# ЗАПУСК
# ============================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не указан."
        )

    if BOT_TOKEN == "ВСТАВЬ_ТОКЕН_БОТА":
        raise RuntimeError(
            "Вставь токен Telegram-бота "
            "в переменную BOT_TOKEN."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Команды
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "shop",
            shop,
        )
    )

    application.add_handler(
        CommandHandler(
            "id",
            user_id,
        )
    )

    application.add_handler(
        CommandHandler(
            "status",
            status,
        )
    )

    # Неизвестные команды
    application.add_handler(
        MessageHandler(
            filters.COMMAND,
            unknown_command,
        )
    )

    # Обработчик ошибок
    application.add_error_handler(
        error_handler
    )

    logger.info(
        "Telegram Stars Shop bot запускается..."
    )

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    main()
