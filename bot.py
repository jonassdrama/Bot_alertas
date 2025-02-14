import gspread
import os
import datetime
import json
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Configurar el bot de Telegram
TOKEN = os.getenv("TOKEN")  # Asegúrate de que está en las variables de entorno

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

# 🔹 Opciones de idioma
# 🔹 Opciones de idioma
IDIOMAS = [["🇪🇸 Español", "🇬🇧 English"]]

# 🔹 Opciones del bot con precios
SERVICIOS = [
    ["📢 Servicio 1 mes - $20"],
    ["📢 Servicio 1 año - $100"],
    ["🎥 Video personalizado - $30"]
]

# 🔹 Botón "Empezar"
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup([["🚀 Empezar"]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("¡Bienvenido! Presiona el botón para comenzar.", reply_markup=keyboard)

# 🔹 Manejar el botón "Empezar"
async def empezar(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup(IDIOMAS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌍 Elige tu idioma / Choose your language:", reply_markup=keyboard)

# 🔹 Manejar selección de idioma
async def seleccionar_idioma(update: Update, context: CallbackContext) -> None:
    idioma = update.message.text
    context.user_data["idioma"] = idioma
    
    if idioma == "🇪🇸 Español":
        mensaje = "📢 Elige una opción de alertas deportivas:"
    else:
        mensaje = "📢 Choose a sports alerts option:"
    
    keyboard = ReplyKeyboardMarkup(SERVICIOS, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(mensaje, reply_markup=keyboard)

# 🔹 Manejar respuestas del usuario
async def manejar_respuesta(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = update.message.text
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    idioma = context.user_data.get("idioma", "🇪🇸 Español")  # Idioma por defecto español

    if "Servicio 1 mes" in opcion or "Servicio 1 año" in opcion:
        mensaje = "¿Cuál es tu equipo favorito?" if idioma == "🇪🇸 Español" else "What is your favorite team?"
        await update.message.reply_text(mensaje)
        context.user_data["opcion"] = opcion
    
    elif "Video personalizado" in opcion:
        mensaje = "Escribe el mensaje que quieres en el video" if idioma == "🇪🇸 Español" else "Write the message you want in the video"
        await update.message.reply_text(mensaje)
        context.user_data["opcion"] = opcion

# 🔹 Capturar equipo favorito
async def capturar_equipo(update: Update, context: CallbackContext) -> None:
    context.user_data["equipo"] = update.message.text
    idioma = context.user_data.get("idioma", "🇪🇸 Español")

    mensaje = "¿Qué tipo de servicio quieres? (Soft $20 / Hard $40)" if idioma == "🇪🇸 Español" else "What type of service do you want? (Soft $20 / Hard $40)"
    await update.message.reply_text(mensaje)

# 🔹 Capturar mensaje para video personalizado
async def capturar_mensaje(update: Update, context: CallbackContext) -> None:
    context.user_data["mensaje"] = update.message.text
    idioma = context.user_data.get("idioma", "🇪🇸 Español")

    mensaje = "¿El video es para ti o para un amigo?" if idioma == "🇪🇸 Español" else "Is the video for you or a friend?"
    await update.message.reply_text(mensaje)

# 🔹 Capturar tipo de servicio y registrar en Google Sheets
async def capturar_tipo_servicio(update: Update, context: CallbackContext) -> None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = context.user_data.get("opcion", "N/A")
    equipo = context.user_data.get("equipo", "N/A")
    servicio = update.message.text
    mensaje = context.user_data.get("mensaje", "N/A")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([usuario, opcion, equipo, servicio, mensaje, fecha])

    idioma = context.user_data.get("idioma", "🇪🇸 Español")
    mensaje_final = "✅ Petición registrada. Nos pondremos en contacto contigo para completar el pago." if idioma == "🇪🇸 Español" else "✅ Request registered. We will contacyou to complete the payment."
    await update.message.reply_text(mensaje_final)

    context.user_data.clear()

# 🔹 Configurar el bot de Telegram
TOKEN = os.getenv("TOKEN")  # Asegúrate de que está en las variables de entorno
app = Application.builder().token(TOKEN).build()

# 🔹 Manejo de comandos
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Text(["🚀 Empezar"]), empezar))
app.add_handler(MessageHandler(filters.Text(["🇪🇸 Español", "🇬🇧 English"]), seleccionar_idioma))
app.add_handler(MessageHandler(filters.Text(["📢 Servicio 1 mes - $20", "📢 Servicio 1 año - $100", "🎥 Video personalizado - $30"]), manejar_respuesta))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capturar_equipo))  # Captura el equipo
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capturar_mensaje))  # Captura mensaje del video
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capturar_tipo_servicio))  # Captura tipo de servicio y registra

# 🔹 Iniciar el bot
app.run_polling()

