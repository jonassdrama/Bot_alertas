import gspread
import os
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, 
filters, CallbackContext

# 🔹 Configurar el bot de Telegram
TOKEN = "7287863294:AAFiMdZMWBvZYfsts44s2Ig_AkycNKh5HFU"

# 🔹 Conectar con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", 
"https://www.googleapis.com/auth/drive"]
creds = 
ServiceAccountCredentials.from_json_keyfile_name("credentials.json", 
scope)
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
    await update.message.reply_text("¡Bienvenido! 📢 Elige una opción de 
alertas deportivas:", reply_markup=keyboard)

# 🔹 Manejar respuestas del usuario
async def manejar_respuesta(update: Update, context: CallbackContext) -> 
None:
    usuario = update.message.chat.username or update.message.chat.id
    opcion = update.message.text
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if opcion in ["📢 Servicio 1 mes", "📢 Servicio 1 año"]:
        await update.message.reply_text("¿Cuál es tu equipo favorito?")
        context.user_data["opcion"] = opcion  # Guardar la opción 
seleccionada
        return
    
    if opcion == "🎥 Video personalizado":
        await update.message.reply_text("Escribe el mensaje que quieres en 
el video:")
        context.user_data["opcion"] = opcion
        return

# 🔹 Capturar equipo favorito
async def capturar_equipo(update: Update, context: CallbackContext) -> 
None:
    if "opcion" in context.user_data:
        context.user_data["equipo"] = update.message.text
        await update.message.reply_text("¿Qué tipo de servicio quieres? 
(Soft $20 / Hard $40)")

# 🔹 Capturar tipo de servicio
async def capturar_tipo_servicio(update: Update, context: CallbackContext) 
-> None:
    if "opcion" in context.user_data and "equipo" in context.user_data:
        usuario = update.message.chat.username or update.message.chat.id
        opcion = context.user_data["opcion"]
        equipo = context.user_data["equipo"]
        servicio = update.message.text
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([usuario, opcion, equipo, servicio, "N/A", 
fecha])
        await update.message.reply_text("✅ Petición registrada. Nos 
pondremos en contacto contigo para completar el pago.")
        context.user_data.clear()

# 🔹 Capturar mensaje para video personalizado
async def capturar_mensaje(update: Update, context: CallbackContext) -> 
None:
    if "opcion" in context.user_data and context.user_data["opcion"] == 
"🎥 Video personalizado":
        context.user_data["mensaje"] = update.message.text
        await update.message.reply_text("¿El video es para ti o para un 
amigo?")

# 🔹 Capturar destinatario del video personalizado
async def capturar_destinatario(update: Update, context: CallbackContext) 
-> None:
    if "mensaje" in context.user_data:
        usuario = update.message.chat.username or update.message.chat.id
        opcion = context.user_data["opcion"]
        mensaje = context.user_data["mensaje"]
        destinatario = update.message.text
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([usuario, opcion, "N/A", "N/A", f"Para: 
{destinatario}, Mensaje: {mensaje}", fecha])
        await update.message.reply_text("✅ Petición registrada. Nos 
pondremos en contacto contigo para completar el pago.")
        context.user_data.clear()

# 🔹 Configurar el bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("📢 Servicio 1 mes|📢 
Servicio 1 año|🎥 Video personalizado"), manejar_respuesta))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
capturar_equipo))
    app.add_handler(MessageHandler(filters.Regex("Soft \$20|Hard \$40"), 
capturar_tipo_servicio))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
capturar_mensaje))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
capturar_destinatario))

    print("🤖 Bot en marcha...")
    app.run_polling()

if __name__ == "__main__":
    main()

