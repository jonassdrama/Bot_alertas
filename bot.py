import gspread
import os
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Configurar el bot de Telegram
TOKEN = "7287863294:AAFiMdZMWBvZYfsts44s2Ig_AkycNKh5HFU"

# 🔹 Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
"https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# 🔹 Abrir la hoja de cálculo
SHEET_NAME = "1I6zyDy7N1vqOrq_2b6MFxL7ak8M8_FZpm0Q6cw-rkpc"
sheet = client.open_by_key(SHEET_NAME).sheet1

# 🔹 Opciones del bot
SERVICIOS = [
    ["📢 Servicio 1 mes"],
    ["📢 Servicio 1 año"],
    ["🎥 Video personalizado"]
]

# 🔹 Comando /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = ReplyKeyboardMarkup(SERVICIOS, one_time_keyboard=True,
resize_keyboard=True)
    await update.message.reply_text("¡Bienvenido! 📢 Elige una opción de alertas deportivas:", reply_markup=keyboard)

# 🔹 Manejar respuestas del usuario
async def manejar_respuesta(update: Update, context: CallbackContext) ->
None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = update.message.text
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if opcion == "📢 Servicio 1 mes" or opcion == "📢 Servicio 1 año":
        await update.message.reply_text("¿Cuál es tu equipo favorito?")
        context.user_data["opcion"] = opcion  # Guardar la opción
seleccionada
    elif opcion == "🎥 Video personalizado":
        await update.message.reply_text("Escribe el mensaje que quieres en el video")
        context.user_data["opcion"] = opcion
    else:
        equipo = context.user_data.get("equipo", "N/A")
        mensaje = context.user_data.get("mensaje", "N/A")
        sheet.append_row([usuario, context.user_data["opcion"], equipo,
"N/A", mensaje, fecha])
        await update.message.reply_text("✅ Petición registrada. Nos pondremos en contacto contigo para completar el pago.")
        context.user_data.clear()

# 🔹 Capturar equipo favorito
async def capturar_equipo(update: Update, context: CallbackContext) ->
None:
    context.user_data["equipo"] = update.message.text
    await update.message.reply_text("¿Qué tipo de servicio quieres? (Soft $20 / Hard $40)")

# 🔹 Capturar tipo de servicio
async def capturar_tipo_servicio(update: Update, context: CallbackContext)
-> None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = context.user_data.get("opcion", "N/A")
    equipo = context.user_data.get("equipo", "N/A")
    servicio = update.message.text
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([usuario, opcion, equipo, servicio, "N/A", fecha])
    await update.message.reply_text("✅ Petición registrada. Nos pondremos en contacto contigo para completar el pago.")
    context.user_data.clear()

# 🔹 Capturar mensaje para video personalizado
async def capturar_mensaje(update: Update, context: CallbackContext) ->
None:
    context.user_data["mensaje"] = update.message.text
    await update.message.reply_text("¿El video es para ti o para un amigo?")

# 🔹 Configurar el bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
manejar_respuesta))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
capturar_equipo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
capturar_tipo_servicio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,
capturar_mensaje))

    print("🤖 Bot en marcha...")
    app.run_polling()

if __name__ == "__main__":
    main()

