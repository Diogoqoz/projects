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

PORT = int(os.environ.get("PORT", "8000"))

# Você pode configurar de 2 formas:
# A) (mais simples) WEBHOOK_URL = "https://seu-app.koyeb.app/telegram"
# B) PUBLIC_URL + WEBHOOK_PATH (ex.: PUBLIC_URL="https://seu-app.koyeb.app", WEBHOOK_PATH="telegram")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # opcional
PUBLIC_URL = os.environ.get("PUBLIC_URL")    # opcional
WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "telegram").strip("/")

# ======================
# Estado do bot (memória volátil)
# ======================
SESSION: list[str] = []
PANEL_MESSAGE_ID: int | None = None


# ======================
# Helpers
# ======================
def keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Green", callback_data="GREEN")],
            [InlineKeyboardButton("❌ Loss", callback_data="LOSS")],
            [InlineKeyboardButton("📋 Gerar mensagem", callback_data="EXPORT")],
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="RESET")],
        ]
    )


def montar_texto(entries: list[str], final: bool = False) -> str:
    greens = entries.count("✅")
    losses = entries.count("❌")
    data = datetime.now().strftime("%d/%m/%y")

    if final:
        topo = (
            "🔥 LIVE FINALIZADA 🔥\n\n"
            f"Resultado das Entradas na nossa Live de {data}\n"
            f"✅ {greens} x {losses} ❌\n\n"
        )
    else:
        topo = (
            "📊 ACOMPANHAMENTO DA LIVE\n\n"
            f"Resultado das Entradas na nossa Live de {data}\n"
            f"✅ {greens} x {losses} ❌\n\n"
        )

    if not entries:
        return topo + "(Nenhuma entrada registrada ainda)"

    linhas = [f"{i}ª Entrada: {v}" for i, v in enumerate(entries, start=1)]
    return topo + "\n".join(linhas)


def resolve_webhook_url() -> tuple[str, str]:
    """
    Retorna (webhook_url, url_path)

    Prioridade:
    1) WEBHOOK_URL (completa)
    2) PUBLIC_URL + WEBHOOK_PATH
    """
    if WEBHOOK_URL:
        url = WEBHOOK_URL.rstrip("/")
        parts = url.split("/", 3)
        url_path = parts[3] if len(parts) >= 4 else ""
        if not url_path:
            raise RuntimeError(
                "❌ WEBHOOK_URL precisa incluir um caminho. Ex: https://seu-app.koyeb.app/telegram"
            )
        return url, url_path

    if PUBLIC_URL:
        base = PUBLIC_URL.rstrip("/")
        path = WEBHOOK_PATH or "telegram"
        return f"{base}/{path}", path

    raise RuntimeError(
        "❌ Configure WEBHOOK_URL OU PUBLIC_URL.\n"
        "   Ex 1: WEBHOOK_URL=https://seu-app.koyeb.app/telegram\n"
        "   Ex 2: PUBLIC_URL=https://seu-app.koyeb.app  e WEBHOOK_PATH=telegram"
    )


# ======================
# Handlers
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PANEL_MESSAGE_ID
    chat_id = update.effective_chat.id

    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=montar_texto(SESSION),
        reply_markup=keyboard(),
    )
    PANEL_MESSAGE_ID = msg.message_id


async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PANEL_MESSAGE_ID

    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == "GREEN":
        SESSION.append("✅")
    elif query.data == "LOSS":
        SESSION.append("❌")
    elif query.data == "RESET":
        SESSION.clear()
    elif query.data == "EXPORT":
        await context.bot.send_message(chat_id=chat_id, text=montar_texto(SESSION, final=True))

    if PANEL_MESSAGE_ID:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=PANEL_MESSAGE_ID,
            text=montar_texto(SESSION),
            reply_markup=keyboard(),
        )


# ======================
# Main
# ======================
def main():
    webhook_url, url_path = resolve_webhook_url()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botoes))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=url_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
