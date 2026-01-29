import os
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ======================
# Config
# ======================
TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Defina a variável de ambiente BOT_TOKEN (token do BotFather).")

# Você pode configurar de 2 formas:
# 1) (mais simples) WEBHOOK_URL = "https://seu-app.koyeb.app/telegram"
# 2) PUBLIC_URL + WEBHOOK_PATH (ex.: PUBLIC_URL="https://seu-app.koyeb.app", WEBHOOK_PATH="telegram")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # opcional
PUBLIC_URL = os.environ.get("PUBLIC_URL")    # opcional
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "telegram").strip("/")

PORT
