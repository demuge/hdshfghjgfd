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
)


# =========================
# НАСТРОЙКИ
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

WEB_APP_URL = os.getenv(
    "WEB_APP_URL",
    "https://demuge.github.io/qwet4wyh/"
)

API_URL = os.getenv("API_URL", "").rstrip("/")


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment variable is not set"
    )


# =========================
# TELEGRAM BOT
# =========================

application = Application.builder().token(BOT_TOKEN).build()


# =========================
# /START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                text="⭐ Купить Stars",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "⭐ Добро пожаловать!\n\n"
        "Здесь ты можешь купить Telegram Stars.\n\n"
        "Нажми кнопку ниже, чтобы открыть магазин.",
        reply_markup=reply_markup
    )


# =========================
# /SHOP
# =========================

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton(
                text="⭐ Открыть магазин",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        ]
    ]

    await update.message.reply_text(
        "⭐ Открывай магазин:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# /ID
# =========================

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        f"Твой Telegram ID:\n\n"
        f"`{update.effective_user.id}`",
        parse_mode="Markdown"
    )


# =========================
# /STATUS
# =========================

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Использование:\n"
            "/status ORDER_ID"
        )
        return

    order_id = context.args[0]

    if not API_URL:
        await update.message.reply_text(
            "API_URL ещё не настроен."
        )
        return

    try:

        async with httpx.AsyncClient(timeout=10) as client:

            response = await client.get(
                f"{API_URL}/api/order/{order_id}"
            )

        if response.status_code == 404:
            await update.message.reply_text(
                "Заказ не найден."
            )
            return

        response.raise_for_status()

        data = response.json()

        await update.message.reply_text(
            f"Заказ: `{data['id']}`\n"
            f"Username: @{data['username']}\n"
            f"Stars: {data['stars']} ⭐\n"
            f"Сумма: {data['amount']} {data['currency']}\n"
            f"Статус: {data['status']}",
            parse_mode="Markdown"
        )

    except Exception as e:

        print(f"Status error: {e}")

        await update.message.reply_text(
            "Не удалось получить статус заказа."
        )


# =========================
# КОМАНДЫ
# =========================

application.add_handler(
    CommandHandler("start", start)
)

application.add_handler(
    CommandHandler("shop", shop)
)

application.add_handler(
    CommandHandler("id", get_id)
)

application.add_handler(
    CommandHandler("status", status)
)


# =========================
# ЗАПУСК БОТА
# =========================

_bot_started = False


async def start_bot():

    global _bot_started

    if _bot_started:
        return

    print("Initializing Telegram bot...")

    await application.initialize()

    await application.start()

    await application.updater.start_polling(
        drop_pending_updates=True
    )

    _bot_started = True

    print("Telegram bot is running")


# =========================
# ОСТАНОВКА БОТА
# =========================

async def stop_bot():

    global _bot_started

    if not _bot_started:
        return

    print("Stopping Telegram bot...")

    await application.updater.stop()

    await application.stop()

    await application.shutdown()

    _bot_started = False

    print("Telegram bot stopped")


# =========================
# ЛОКАЛЬНЫЙ ЗАПУСК
# =========================

if __name__ == "__main__":
    import asyncio

    async def main():
        await start_bot()

        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            pass
        finally:
            await stop_bot()

    asyncio.run(main())
