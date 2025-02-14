import gspread
import os
import datetime
import json
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Configurar el bot de Telegram
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ ERROR: No se encontró el TOKEN de Telegram en las variables de entorno.")
app = Application.builder().token(TOKEN).build()

# 🔹 Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

# 🔹 Abrir la hoja de cálculo
SHEET_NAME = "1I6zyDy7N1vqOrq_2b6MFxL7ak8M8_FZpm0Q6cw-rkpc"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Opciones
IDIOMAS = [["🇪🇸 Español", "🇬🇧 English"]]
SERVICIOS = [["📢 Servicio 1 mes - $20"], ["📢 Servicio 1 año - $100"], ["🎥 Video personalizado - $30"]]

# 🔹 Botón "Empezar"
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup([["🚀 Empezar"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("¡Bienvenido! Presiona el botón para comenzar.", reply_markup=keyboard)

# 🔹 Manejar "Empezar"
async def empezar(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup(IDIOMAS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌍 Elige tu idioma / Choose your language:", reply_markup=keyboard)

# 🔹 Seleccionar idioma
async def seleccionar_idioma(update: Update, context: CallbackContext) -> None:
    idioma = update.message.text
    context.user_data["idioma"] = idioma
    
    mensaje = "📢 Elige una opción de alertas deportivas:" if idioma == "🇪🇸 Español" else "📢 Choose a sports alerts option:"
    
    keyboard = ReplyKeyboardMarkup(SERVICIOS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(mensaje, reply_markup=keyboard)

# 🔹 Manejar selección de servicio
async def manejar_respuesta(update: Update, context: CallbackContext) -> None:
    opcion = update.message.text
    context.user_data["opcion"] = opcion
    
    if "Servicio" in opcion:
        mensaje = "⚽ ¿Cuál es tu equipo favorito?"
        context.user_data["estado"] = "esperando_equipo"
    
    elif "Video personalizado" in opcion:
        mensaje = "🎥 Escribe el mensaje que quieres en el video"
        context.user_data["estado"] = "esperando_mensaje"

    await update.message.reply_text(mensaje)

# 🔹 Manejar respuestas de usuario según el estado
async def manejar_respuesta_usuario(update: Update, context: CallbackContext) -> None:
    estado = context.user_data.get("estado")

    if estado == "esperando_equipo":
        context.user_data["equipo"] = update.message.text
        mensaje = "🎟️ ¿El video es para ti o para un amigo?"
        context.user_data["estado"] = "esperando_servicio"
        await update.message.reply_text(mensaje)

    elif estado == "esperando_mensaje":
        context.user_data["mensaje"] = update.message.text
        mensaje = "🎟️ ¿El video es para ti o para un amigo?"
        context.user_data["estado"] = "esperando_servicio"
        await update.message.reply_text(mensaje)

    elif estado == "esperando_servicio":
        usuario = update.message.chat.username or update.message.chat.id
        opcion = context.user_data.get("opcion", "N/A")
        equipo = context.user_data.get("equipo", "N/A")
        servicio = update.message.text
        mensaje = context.user_data.get("mensaje", "N/A")
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([usuario, opcion, equipo, servicio, mensaje, fecha])

        idioma = context.user_data.get("idioma", "🇪🇸 Español")
        mensaje_final = "✅ Petición registrada. Nos pondremos en contacto contigo para completar el pago." if idioma == "🇪🇸 Español" else "✅ Request registered. We will contact you to complete the payment."
        await update.message.reply_text(mensaje_final)

        context.user_data.clear()

# 🔹 Configurar manejadores
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Text(["🚀 Empezar"]), empezar))
app.add_handler(MessageHandler(filters.Text(["🇪🇸 Español", "🇬🇧 English"]), seleccionar_idioma))
app.add_handler(MessageHandler(filters.Text(["📢 Servicio 1 mes - $20", "📢 Servicio 1 año - $100", "🎥 Video personalizado - $30"]), manejar_respuesta))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_respuesta_usuario))  # Un solo manejador para capturar respuestas

# 🔹 Iniciar bot
app.run_polling()


