import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction  # ✅ ESTA ES LA CORRECTA
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
from utils.gemini_client import responder_gemini
from telegram.ext import CommandHandler
from datetime import datetime
import pytz
import locale
from utils.weather_client import obtener_clima


# Establecer idioma español para nombres de días/meses (solo si tu sistema lo permite)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, '')  # fallback

# Función base para generar fecha con formato
def obtener_fecha(formato="completo"):
    tz = pytz.timezone('America/El_Salvador')
    ahora = datetime.now(tz)

    if formato == "corta":
        return ahora.strftime("%d/%m/%Y %H:%M")
    if formato == "normal":
        return ahora.strftime("La fecha hoy es %A %d de %B de %Y")
    else:  # completo o cualquier otro valor
        return ahora.strftime("La fecha hoy es %A %d de %B de %Y , y son las %I:%M %p (Zona: %Z)")

async def cmd_fecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = obtener_fecha("normal")
    await update.message.reply_text(texto)

async def cmd_fecha_corta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = obtener_fecha("corta")
    await update.message.reply_text(f"📌 Fecha corta: {texto}")

async def cmd_fecha_completa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = obtener_fecha("completo")
    await update.message.reply_text(f"📌 Fecha completa: {texto}")


# Configuración de logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Cargar .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Manejo de mensajes muy largos
def dividir_mensaje(texto, max_len=4000):
    partes = []
    while len(texto) > max_len:
        idx = texto.rfind("\n", 0, max_len)
        if idx == -1:
            idx = max_len
        partes.append(texto[:idx])
        texto = texto[idx:]
    partes.append(texto)
    return partes

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 ¡Hola! Soy un bot impulsado por Gemini. Envíame un mensaje y te responderé.")


async def clima(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🌍 Usa el comando así:\n`/clima Ciudad`", parse_mode="Markdown")
        return

    ciudad = " ".join(context.args)
    resultado = obtener_clima(ciudad)
    await update.message.reply_text(resultado, parse_mode="Markdown")





# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "🤖 *Comandos disponibles:*\n\n"
        "/start - Inicia la conversación\n\n"
        "/help - Muestra esta ayuda\n\n"
        "/fecha - Muestra la fecha de hoy\n\n"
        "/fecha_completa - Muestra la fecha y hora en formato largo\n\n"
        "/fecha_corta - Muestra la fecha en formato corto\n\n"
        "/clima Ciudad - Muestra el clima de la ciudad indicada\n\n"
        "También puedes escribirme cualquier pregunta y te responderé usando inteligencia artificial ✨"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

# Función principal de conversación
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        mensaje = update.message.text
        chat_id = update.message.chat_id

        # Indicador de "escribiendo"
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        respuesta = responder_gemini(mensaje)

        # Dividir y enviar si es muy larga
        partes = dividir_mensaje(respuesta)
        for parte in partes:
            await update.message.reply_text(parte)

    except Exception as e:
        logging.error(f"❌ Error inesperado: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error. Intenta de nuevo más tarde.")

# Inicializar aplicación
def main():
    print("Versión de Python:", os.sys.version)
    print("Bot iniciado...")

    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    app.add_handler(CommandHandler("fecha", cmd_fecha))
    app.add_handler(CommandHandler("fechacorta", cmd_fecha_corta))
    app.add_handler(CommandHandler("fechacompleta", cmd_fecha_completa))

    app.add_handler(CommandHandler("clima", clima))

    # Mensajes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    app.run_polling()

if __name__ == "__main__":
    main()
