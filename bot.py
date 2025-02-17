import gspread
import os
import datetime
import json
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 CONFIGURACIÓN DEL BOT
TOKEN = os.getenv("TOKEN")
ADMIN_ID = 1570729026  # ⚠️ REEMPLAZA con tu ID de Telegram

if not TOKEN:
    raise ValueError("❌ ERROR: No se encontró el TOKEN de Telegram en las variables de entorno.")

print("✅ TOKEN cargado correctamente.")

# 🔹 CONECTAR CON GOOGLE SHEETS
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    SHEET_NAME = "1I6zyDy7N1vqOrq_2b6MFxL7ak8M8_FZpm0Q6cw-rkpc"
    sheet = client.open_by_key(SHEET_NAME).sheet1
    print("✅ Conectado a Google Sheets.")
except Exception as e:
    print(f"❌ ERROR al conectar con Google Sheets: {e}")
    exit(1)

# 🔹 INICIALIZAR EL BOT
try:
    app = Application.builder().token(TOKEN).build()
    print("✅ Bot inicializado correctamente.")
except Exception as e:
    print(f"❌ ERROR al inicializar el bot: {e}")
    exit(1)

# 🔹 MANEJAR COMANDO /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("¡Bienvenido! 👋")

# 🔹 ENVIAR MENSAJES MANUALMENTE COMO ADMIN
async def enviar(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/enviar ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Mensaje enviado a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar mensaje: {e}")

# 🔹 RECIBIR RESPUESTAS DEL USUARIO Y ENVIARLAS AL ADMIN
async def reenviar_respuesta(update: Update, context: CallbackContext) -> None:
    user_id = update.message.chat.id
    username = update.message.chat.username or f"ID: {user_id}"

    if update.message.text:
        mensaje_admin = f"📩 *Nueva respuesta de un usuario*\n👤 Usuario: {username}\n🆔 ID: {user_id}\n💬 Mensaje: {update.message.text}"
        await context.bot.send_message(chat_id=ADMIN_ID, text=mensaje_admin, parse_mode="Markdown")

# 🔹 RESPONDER AL USUARIO DESDE EL ADMIN
async def responder(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Uso correcto: `/responder ID mensaje`")
        return

    chat_id = context.args[0]
    mensaje = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=chat_id, text=mensaje)
        await update.message.reply_text(f"✅ Respuesta enviada a {chat_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al enviar respuesta: {e}")

# 🔹 CONFIGURAR MANEJADORES
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("enviar", enviar))
app.add_handler(CommandHandler("responder", responder))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reenviar_respuesta))

# 🔹 INICIAR EL BOT
print("🤖 Bot en marcha...")
app.run_polling()










