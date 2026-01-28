from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import os
TOKEN = os.environ["BOT_TOKEN"]

# Sessão única (compartilhada)
SESSION = []

# Guardamos o id da "mensagem painel" para editar sempre a mesma
PANEL_MESSAGE_ID = None

def keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Green", callback_data="GREEN")],
        [InlineKeyboardButton("❌ Loss", callback_data="LOSS")],
        [InlineKeyboardButton("📋 Gerar mensagem", callback_data="EXPORT")],
        [InlineKeyboardButton("🔄 Reiniciar", callback_data="RESET")],
    ])

def montar_texto(entries, modo="ACOMPANHAMENTO"):
    greens = entries.count("✅")
    losses = entries.count("❌")
    data = datetime.now().strftime("%d/%m/%y")

    if modo == "ACOMPANHAMENTO":
        topo = (
            "📊 ACOMPANHAMENTO DA LIVE\n\n"
            f"Resultado das Entradas na nossa Live de {data}\n"
            f"✅ {greens} x {losses} ❌\n\n"
        )
    else:  # FINAL
        topo = (
            "🔥 LIVE FINALIZADA 🔥\n\n"
            f"Resultado das Entradas na nossa Live de {data}\n"
            f"✅ {greens} x {losses} ❌\n\n"
        )

    if not entries:
        return topo + "(Nenhuma entrada registrada ainda)"

    linhas = [f"{i}ª Entrada: {v}" for i, v in enumerate(entries, start=1)]
    return topo + "\n".join(linhas)

async def garantir_painel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cria o painel (uma mensagem) se ainda não existir.
    Depois a gente só edita ela.
    """
    global PANEL_MESSAGE_ID

    chat_id = update.effective_chat.id

    if PANEL_MESSAGE_ID is None:
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=montar_texto(SESSION, modo="ACOMPANHAMENTO"),
            reply_markup=keyboard()
        )
        PANEL_MESSAGE_ID = msg.message_id
    else:
        # Se já existe, só atualiza
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=PANEL_MESSAGE_ID,
            text=montar_texto(SESSION, modo="ACOMPANHAMENTO"),
            reply_markup=keyboard()
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Cria/mostra o painel
    await garantir_painel(update, context)

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global PANEL_MESSAGE_ID

    query = update.callback_query
    await query.answer()

    acao = query.data
    chat_id = query.message.chat.id

    if acao == "GREEN":
        SESSION.append("✅")
    elif acao == "LOSS":
        SESSION.append("❌")
    elif acao == "RESET":
        SESSION.clear()
    elif acao == "EXPORT":
        # Envia a mensagem final pronta pra copiar
        await context.bot.send_message(
            chat_id=chat_id,
            text=montar_texto(SESSION, modo="FINAL")
        )

    # Atualiza o painel SEMPRE, pra acompanhar ao vivo
    # Se por algum motivo o painel ainda não existe, cria.
    if PANEL_MESSAGE_ID is None:
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=montar_texto(SESSION, modo="ACOMPANHAMENTO"),
            reply_markup=keyboard()
        )
        PANEL_MESSAGE_ID = msg.message_id
    else:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=PANEL_MESSAGE_ID,
            text=montar_texto(SESSION, modo="ACOMPANHAMENTO"),
            reply_markup=keyboard()
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(botoes))
    app.run_polling()

if __name__ == "__main__":
    main()