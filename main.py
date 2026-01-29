import os
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# TOKEN vem do Koyeb
TOKEN = os.environ["BOT_TOKEN"]

# ===== Bot logic =====
SESSION = []
PANEL_MESSAGE_ID = None


def keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Green", callback_data="GREEN")],
            [InlineKeyboardButton("❌ Loss", callback_data="LOSS")],
            [InlineKeyboardButton("📋 Gerar mensagem", callback_data="EXPORT")],
            [InlineKeyboardButton("🔄 Reiniciar", callback_data="RESET")],
        ]
    )


def montar_texto(entries, final=False):
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
        await context.bot.send_message(
            chat_id=chat_id,
            text=montar_texto(SESSION, final=True),
        )

    if PANEL_MESSAGE_ID:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=PANEL_MESSAGE_ID,
            text=montar_texto(SESSION),
            reply_markup=keyboard(),
        )


def main():
    """
    Webhook = o Telegram chama sua URL quando chega mensagem.
    Isso evita depender do bot "rodando sempre" via polling, o que quebra em hibernação.
    """

    # Porta que a Koyeb expõe
    port = int(os.environ.get("PORT", 8000))

    # URL pública do seu app (ex.: https://seu-app.koyeb.app)
    public_url = os.environ["PUBLIC_URL"].rstrip("/")

    # Caminho do webhook (ex.: telegram) => endpoint final: /telegram
    path = os.environ.get("WEBHOOK_PATH", "telegram").strip("/")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botoes))

    webhook_url = f"{public_url}/{path}"

    # Inicia servidor HTTP do webhook
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=path,
        webhook_url=webhook_url,
        drop_pending_updates=True,  # evita processar backlog antigo ao subir
    )


if __name__ == "__main__":
    main()
